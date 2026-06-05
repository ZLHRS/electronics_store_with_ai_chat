import datetime
import uuid
from decimal import Decimal

import pytest

from app.application.dto.payment_dto import CreatePaymentCommand, WebhookPayload
from app.application.service.payment_service import PaymentService
from app.domain.entity.payment_entity import PaymentEntity, PaymentEventEntity, PaymentProvider, PaymentStatus
from app.domain.repo.payment_event_repo_protocol import CreatePaymentEvent
from app.domain.repo.payment_repo_protocol import CreatePayment
from app.exceptions import (
    InvalidOrderStatusError,
    InvalidPaymentStatusError,
    OrderForbiddenError,
    OrderNotFoundError,
    PaymentAlreadyExistsError,
    PaymentForbiddenError,
    PaymentNotFoundError,
)
from app.infrastructure.order_client import OrderInfo


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def _make_payment(
    order_id: uuid.UUID,
    user_id: uuid.UUID,
    status: str = PaymentStatus.CREATED,
    provider: str = PaymentProvider.KASPI,
    provider_payment_id: str = "pp-001",
) -> PaymentEntity:
    return PaymentEntity(
        id=uuid.uuid4(),
        order_id=order_id,
        user_id=user_id,
        provider=provider,
        amount=Decimal("10000"),
        currency="KZT",
        status=status,
        provider_payment_id=provider_payment_id,
        payment_url="https://pay.kaspi.kz/pay/pp-001",
        failure_reason=None,
        created_at=_now(),
        updated_at=_now(),
    )


class FakePaymentRepo:
    def __init__(self):
        self._payments: dict[uuid.UUID, PaymentEntity] = {}

    async def get_by_id(self, payment_id: uuid.UUID) -> PaymentEntity | None:
        return self._payments.get(payment_id)

    async def get_active_by_order_id(self, order_id: uuid.UUID) -> PaymentEntity | None:
        return next(
            (
                p
                for p in self._payments.values()
                if p.order_id == order_id
                and p.status in (PaymentStatus.CREATED, PaymentStatus.PENDING)
            ),
            None,
        )

    async def get_by_provider_payment_id(
        self, provider: str, provider_payment_id: str
    ) -> PaymentEntity | None:
        return next(
            (
                p
                for p in self._payments.values()
                if p.provider == provider and p.provider_payment_id == provider_payment_id
            ),
            None,
        )

    async def create(self, data: CreatePayment) -> PaymentEntity:
        payment = PaymentEntity(
            id=uuid.uuid4(),
            order_id=data.order_id,
            user_id=data.user_id,
            provider=data.provider,
            amount=data.amount,
            currency=data.currency,
            status=PaymentStatus.CREATED,
            provider_payment_id=data.provider_payment_id,
            payment_url=data.payment_url,
            failure_reason=None,
            created_at=_now(),
            updated_at=_now(),
        )
        self._payments[payment.id] = payment
        return payment

    async def update_status(
        self,
        payment_id: uuid.UUID,
        status: str,
        failure_reason: str | None = None,
    ) -> PaymentEntity:
        p = self._payments[payment_id]
        updated = PaymentEntity(
            id=p.id,
            order_id=p.order_id,
            user_id=p.user_id,
            provider=p.provider,
            amount=p.amount,
            currency=p.currency,
            status=status,
            provider_payment_id=p.provider_payment_id,
            payment_url=p.payment_url,
            failure_reason=failure_reason,
            created_at=p.created_at,
            updated_at=_now(),
        )
        self._payments[payment_id] = updated
        return updated


class FakePaymentEventRepo:
    def __init__(self):
        self._events: list[PaymentEventEntity] = []

    async def create(self, data: CreatePaymentEvent) -> PaymentEventEntity:
        event = PaymentEventEntity(
            id=uuid.uuid4(),
            payment_id=data.payment_id,
            provider=data.provider,
            event_type=data.event_type,
            payload=data.payload,
            created_at=_now(),
        )
        self._events.append(event)
        return event

    async def get_by_payment_id(self, payment_id: uuid.UUID) -> list[PaymentEventEntity]:
        return [e for e in self._events if e.payment_id == payment_id]


class FakeOrderClient:
    def __init__(self, orders: dict[uuid.UUID, OrderInfo]):
        self._orders = orders
        self.paid_notifications: list[tuple[uuid.UUID, uuid.UUID]] = []
        self.failed_notifications: list[uuid.UUID] = []

    async def get_order(self, order_id: uuid.UUID) -> OrderInfo | None:
        return self._orders.get(order_id)

    async def notify_payment_paid(self, order_id: uuid.UUID, payment_id: uuid.UUID) -> None:
        self.paid_notifications.append((order_id, payment_id))

    async def notify_payment_failed(self, order_id: uuid.UUID) -> None:
        self.failed_notifications.append(order_id)


def _make_order(user_id: uuid.UUID, status: str = "pending_payment") -> OrderInfo:
    return OrderInfo(
        id=uuid.uuid4(),
        user_id=user_id,
        status=status,
        total=Decimal("10000"),
    )


def _make_service(
    orders: dict | None = None,
) -> tuple[PaymentService, FakePaymentRepo, FakePaymentEventRepo, FakeOrderClient]:
    repo = FakePaymentRepo()
    event_repo = FakePaymentEventRepo()
    order_client = FakeOrderClient(orders or {})
    service = PaymentService(repo, event_repo, order_client)
    return service, repo, event_repo, order_client


@pytest.mark.asyncio
async def test_create_payment_success():
    user_id = uuid.uuid4()
    order = _make_order(user_id)
    service, repo, _, _ = _make_service({order.id: order})

    result = await service.create_payment(
        user_id, CreatePaymentCommand(order_id=order.id, provider=PaymentProvider.KASPI)
    )

    assert result.order_id == order.id
    assert result.user_id == user_id
    assert result.status == PaymentStatus.CREATED
    assert result.amount == Decimal("10000")
    assert result.payment_url is not None


@pytest.mark.asyncio
async def test_create_payment_order_not_found():
    service, _, _, _ = _make_service()

    with pytest.raises(OrderNotFoundError):
        await service.create_payment(
            uuid.uuid4(), CreatePaymentCommand(order_id=uuid.uuid4(), provider=PaymentProvider.KASPI)
        )


@pytest.mark.asyncio
async def test_create_payment_order_belongs_to_other_user():
    order = _make_order(uuid.uuid4())
    service, _, _, _ = _make_service({order.id: order})

    with pytest.raises(OrderForbiddenError):
        await service.create_payment(
            uuid.uuid4(), CreatePaymentCommand(order_id=order.id, provider=PaymentProvider.KASPI)
        )


@pytest.mark.asyncio
async def test_create_payment_wrong_order_status():
    user_id = uuid.uuid4()
    order = _make_order(user_id, status="paid")
    service, _, _, _ = _make_service({order.id: order})

    with pytest.raises(InvalidOrderStatusError):
        await service.create_payment(
            user_id, CreatePaymentCommand(order_id=order.id, provider=PaymentProvider.KASPI)
        )


@pytest.mark.asyncio
async def test_create_payment_already_exists():
    user_id = uuid.uuid4()
    order = _make_order(user_id)
    service, repo, _, _ = _make_service({order.id: order})

    existing = _make_payment(order.id, user_id, status=PaymentStatus.CREATED)
    repo._payments[existing.id] = existing

    with pytest.raises(PaymentAlreadyExistsError):
        await service.create_payment(
            user_id, CreatePaymentCommand(order_id=order.id, provider=PaymentProvider.KASPI)
        )


@pytest.mark.asyncio
async def test_get_payment_not_found():
    service, _, _, _ = _make_service()

    with pytest.raises(PaymentNotFoundError):
        await service.get_payment(uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_get_payment_forbidden():
    user_id = uuid.uuid4()
    order_id = uuid.uuid4()
    service, repo, _, _ = _make_service()
    payment = _make_payment(order_id, user_id)
    repo._payments[payment.id] = payment

    with pytest.raises(PaymentForbiddenError):
        await service.get_payment(payment.id, uuid.uuid4())


@pytest.mark.asyncio
async def test_refund_payment_success():
    user_id = uuid.uuid4()
    order_id = uuid.uuid4()
    service, repo, _, _ = _make_service()
    payment = _make_payment(order_id, user_id, status=PaymentStatus.PAID)
    repo._payments[payment.id] = payment

    result = await service.refund_payment(payment.id, user_id)

    assert result.status == PaymentStatus.REFUNDED


@pytest.mark.asyncio
async def test_refund_payment_wrong_status():
    user_id = uuid.uuid4()
    order_id = uuid.uuid4()
    service, repo, _, _ = _make_service()
    payment = _make_payment(order_id, user_id, status=PaymentStatus.CREATED)
    repo._payments[payment.id] = payment

    with pytest.raises(InvalidPaymentStatusError):
        await service.refund_payment(payment.id, user_id)


@pytest.mark.asyncio
async def test_webhook_kaspi_paid_notifies_order():
    user_id = uuid.uuid4()
    order_id = uuid.uuid4()
    service, repo, event_repo, order_client = _make_service()
    payment = _make_payment(order_id, user_id, provider=PaymentProvider.KASPI, provider_payment_id="txn-42")
    repo._payments[payment.id] = payment

    await service.handle_webhook(
        WebhookPayload(
            provider=PaymentProvider.KASPI,
            event_type="payment.success",
            raw={"txn_id": "txn-42", "status": "payment.success"},
        )
    )

    assert repo._payments[payment.id].status == PaymentStatus.PAID
    assert len(event_repo._events) == 1
    assert (order_id, payment.id) in order_client.paid_notifications


@pytest.mark.asyncio
async def test_webhook_kaspi_failed_notifies_order():
    user_id = uuid.uuid4()
    order_id = uuid.uuid4()
    service, repo, _, order_client = _make_service()
    payment = _make_payment(order_id, user_id, provider=PaymentProvider.KASPI, provider_payment_id="txn-99")
    repo._payments[payment.id] = payment

    await service.handle_webhook(
        WebhookPayload(
            provider=PaymentProvider.KASPI,
            event_type="payment.failed",
            raw={"txn_id": "txn-99", "status": "payment.failed", "error_message": "Insufficient funds"},
        )
    )

    assert repo._payments[payment.id].status == PaymentStatus.FAILED
    assert repo._payments[payment.id].failure_reason == "Insufficient funds"
    assert order_id in order_client.failed_notifications


@pytest.mark.asyncio
async def test_webhook_unknown_provider_payment_id_ignored():
    service, repo, event_repo, _ = _make_service()

    await service.handle_webhook(
        WebhookPayload(
            provider=PaymentProvider.KASPI,
            event_type="payment.success",
            raw={"txn_id": "nonexistent"},
        )
    )

    assert len(event_repo._events) == 0
