import logging
import uuid
from decimal import Decimal

from app.application.dto.payment_dto import CreatePaymentCommand, PaymentResult, WebhookPayload
from app.domain.entity.payment_entity import PaymentProvider, PaymentStatus
from app.domain.repo.payment_event_repo_protocol import CreatePaymentEvent, PaymentEventRepository
from app.domain.repo.payment_repo_protocol import CreatePayment, PaymentRepository
from app.exceptions import (
    InvalidOrderStatusError,
    InvalidPaymentStatusError,
    OrderForbiddenError,
    OrderNotFoundError,
    PaymentAlreadyExistsError,
    PaymentForbiddenError,
    PaymentNotFoundError,
)
from app.infrastructure.order_client import OrderServiceClient

logger = logging.getLogger(__name__)

_PAID_EVENT_TYPES = {
    PaymentProvider.KASPI: {"payment.success"},
    PaymentProvider.STRIPE: {"payment_intent.succeeded", "charge.succeeded"},
    PaymentProvider.FREEDOMPAY: {"payment.success"},
}

_FAILED_EVENT_TYPES = {
    PaymentProvider.KASPI: {"payment.failed", "payment.cancelled"},
    PaymentProvider.STRIPE: {"payment_intent.payment_failed", "charge.failed"},
    PaymentProvider.FREEDOMPAY: {"payment.failed"},
}


def _extract_provider_payment_id(provider: str, payload: dict) -> str | None:
    if provider == PaymentProvider.KASPI:
        return str(payload.get("txn_id") or payload.get("payment_id") or "")
    if provider == PaymentProvider.STRIPE:
        data_obj = payload.get("data", {}).get("object", {})
        return data_obj.get("id") or payload.get("id")
    if provider == PaymentProvider.FREEDOMPAY:
        return str(payload.get("pg_payment_id") or "")
    return None


def _extract_failure_reason(provider: str, payload: dict) -> str | None:
    if provider == PaymentProvider.KASPI:
        return payload.get("error_message")
    if provider == PaymentProvider.STRIPE:
        data_obj = payload.get("data", {}).get("object", {})
        last_err = data_obj.get("last_payment_error", {})
        return last_err.get("message") if last_err else None
    if provider == PaymentProvider.FREEDOMPAY:
        return payload.get("pg_error_description")
    return None


def _build_mock_payment_url(provider: str, provider_payment_id: str) -> str:
    domains = {
        PaymentProvider.KASPI: "pay.kaspi.kz",
        PaymentProvider.STRIPE: "checkout.stripe.com",
        PaymentProvider.FREEDOMPAY: "pay.freedompay.kz",
    }
    domain = domains.get(provider, "payment.example.com")
    return f"https://{domain}/pay/{provider_payment_id}"


class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        payment_event_repository: PaymentEventRepository,
        order_client: OrderServiceClient,
    ):
        self._payments = payment_repository
        self._events = payment_event_repository
        self._orders = order_client

    async def create_payment(
        self, user_id: uuid.UUID, command: CreatePaymentCommand
    ) -> PaymentResult:
        order = await self._orders.get_order(command.order_id)
        if order is None:
            raise OrderNotFoundError("Order not found")
        if order.user_id != user_id:
            raise OrderForbiddenError("Order does not belong to this user")
        if order.status != "pending_payment":
            raise InvalidOrderStatusError(
                f"Order cannot be paid in status '{order.status}'"
            )

        existing = await self._payments.get_active_by_order_id(command.order_id)
        if existing and existing.status in (PaymentStatus.CREATED, PaymentStatus.PENDING):
            raise PaymentAlreadyExistsError("Active payment already exists for this order")

        provider_payment_id = str(uuid.uuid4())
        payment_url = _build_mock_payment_url(command.provider, provider_payment_id)

        payment = await self._payments.create(
            CreatePayment(
                order_id=command.order_id,
                user_id=user_id,
                provider=command.provider,
                amount=order.total,
                currency=command.currency,
                provider_payment_id=provider_payment_id,
                payment_url=payment_url,
            )
        )
        logger.info(
            "Payment created payment_id=%s order_id=%s provider=%s",
            payment.id,
            command.order_id,
            command.provider,
        )
        return _entity_to_result(payment)

    async def get_payment(self, payment_id: uuid.UUID, user_id: uuid.UUID) -> PaymentResult:
        payment = await self._payments.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError("Payment not found")
        if payment.user_id != user_id:
            raise PaymentForbiddenError("Payment does not belong to this user")
        return _entity_to_result(payment)

    async def refund_payment(self, payment_id: uuid.UUID, user_id: uuid.UUID) -> PaymentResult:
        payment = await self._payments.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError("Payment not found")
        if payment.user_id != user_id:
            raise PaymentForbiddenError("Payment does not belong to this user")
        if payment.status != PaymentStatus.PAID:
            raise InvalidPaymentStatusError(
                f"Cannot refund payment in status '{payment.status}'"
            )

        updated = await self._payments.update_status(payment_id, PaymentStatus.REFUNDED)
        logger.info("Payment refunded payment_id=%s", payment_id)
        return _entity_to_result(updated)

    async def handle_webhook(self, webhook: WebhookPayload) -> None:
        provider_payment_id = _extract_provider_payment_id(webhook.provider, webhook.raw)
        if not provider_payment_id:
            logger.warning("Webhook missing provider_payment_id provider=%s", webhook.provider)
            return

        payment = await self._payments.get_by_provider_payment_id(
            webhook.provider, provider_payment_id
        )
        if payment is None:
            logger.warning(
                "Webhook for unknown payment provider=%s provider_payment_id=%s",
                webhook.provider,
                provider_payment_id,
            )
            return

        await self._events.create(
            CreatePaymentEvent(
                payment_id=payment.id,
                provider=webhook.provider,
                event_type=webhook.event_type,
                payload=webhook.raw,
            )
        )

        paid_types = _PAID_EVENT_TYPES.get(webhook.provider, set())
        failed_types = _FAILED_EVENT_TYPES.get(webhook.provider, set())

        if webhook.event_type in paid_types:
            await self._payments.update_status(payment.id, PaymentStatus.PAID)
            await self._orders.notify_payment_paid(payment.order_id, payment.id)
            logger.info(
                "Payment confirmed payment_id=%s order_id=%s", payment.id, payment.order_id
            )
        elif webhook.event_type in failed_types:
            reason = _extract_failure_reason(webhook.provider, webhook.raw)
            await self._payments.update_status(payment.id, PaymentStatus.FAILED, reason)
            await self._orders.notify_payment_failed(payment.order_id)
            logger.info("Payment failed payment_id=%s order_id=%s", payment.id, payment.order_id)
        else:
            logger.info(
                "Unhandled webhook event provider=%s event_type=%s",
                webhook.provider,
                webhook.event_type,
            )


def _entity_to_result(entity) -> PaymentResult:
    return PaymentResult(
        id=entity.id,
        order_id=entity.order_id,
        user_id=entity.user_id,
        provider=entity.provider,
        amount=entity.amount,
        currency=entity.currency,
        status=entity.status,
        provider_payment_id=entity.provider_payment_id,
        payment_url=entity.payment_url,
        failure_reason=entity.failure_reason,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
