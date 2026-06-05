import datetime
import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.entity.payment_entity import PaymentEntity, PaymentStatus
from app.domain.repo.payment_repo_protocol import CreatePayment, PaymentRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.payment_model import PaymentModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.payment_mapper import payment_model_to_entity


class SQLAlchemyPaymentRepo(SQLAlchemyBaseRepo, PaymentRepository):
    async def get_by_id(self, payment_id: uuid.UUID) -> PaymentEntity | None:
        stmt = select(PaymentModel).where(PaymentModel.id == payment_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get payment") from e
        return payment_model_to_entity(result) if result else None

    async def get_active_by_order_id(self, order_id: uuid.UUID) -> PaymentEntity | None:
        stmt = select(PaymentModel).where(
            PaymentModel.order_id == order_id,
            PaymentModel.status.in_([PaymentStatus.CREATED, PaymentStatus.PENDING]),
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get active payment") from e
        return payment_model_to_entity(result) if result else None

    async def get_by_provider_payment_id(
        self, provider: str, provider_payment_id: str
    ) -> PaymentEntity | None:
        stmt = select(PaymentModel).where(
            PaymentModel.provider == provider,
            PaymentModel.provider_payment_id == provider_payment_id,
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get payment by provider id") from e
        return payment_model_to_entity(result) if result else None

    async def create(self, data: CreatePayment) -> PaymentEntity:
        model = PaymentModel(
            order_id=data.order_id,
            user_id=data.user_id,
            provider=data.provider,
            amount=data.amount,
            currency=data.currency,
            status=PaymentStatus.CREATED,
            provider_payment_id=data.provider_payment_id,
            payment_url=data.payment_url,
        )
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            raise DatabaseError("Failed to create payment") from e
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create payment") from e
        return payment_model_to_entity(model)

    async def update_status(
        self,
        payment_id: uuid.UUID,
        status: str,
        failure_reason: str | None = None,
    ) -> PaymentEntity:
        stmt = (
            update(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .values(
                status=status,
                failure_reason=failure_reason,
                updated_at=datetime.datetime.now(datetime.UTC),
            )
            .returning(PaymentModel)
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update payment status") from e
        return payment_model_to_entity(result)
