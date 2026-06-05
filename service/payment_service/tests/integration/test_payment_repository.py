import uuid
from decimal import Decimal

import pytest

from app.domain.entity.payment_entity import PaymentProvider, PaymentStatus
from app.domain.repo.payment_event_repo_protocol import CreatePaymentEvent
from app.domain.repo.payment_repo_protocol import CreatePayment
from app.infrastructure.db.repo.payment_event_repo import SQLAlchemyPaymentEventRepo
from app.infrastructure.db.repo.payment_repo import SQLAlchemyPaymentRepo


def _create_payment_data(
    order_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> CreatePayment:
    return CreatePayment(
        order_id=order_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        provider=PaymentProvider.KASPI,
        amount=Decimal("5000.00"),
        currency="KZT",
        provider_payment_id=str(uuid.uuid4()),
        payment_url="https://pay.kaspi.kz/pay/test",
    )


@pytest.mark.asyncio
async def test_create_and_get_payment(db_session):
    repo = SQLAlchemyPaymentRepo(db_session)
    data = _create_payment_data()

    payment = await repo.create(data)

    assert payment.id is not None
    assert payment.order_id == data.order_id
    assert payment.status == PaymentStatus.CREATED
    assert payment.amount == Decimal("5000.00")

    fetched = await repo.get_by_id(payment.id)
    assert fetched is not None
    assert fetched.id == payment.id


@pytest.mark.asyncio
async def test_get_active_by_order_id(db_session):
    repo = SQLAlchemyPaymentRepo(db_session)
    order_id = uuid.uuid4()
    data = _create_payment_data(order_id=order_id)

    await repo.create(data)
    active = await repo.get_active_by_order_id(order_id)

    assert active is not None
    assert active.order_id == order_id
    assert active.status == PaymentStatus.CREATED


@pytest.mark.asyncio
async def test_update_status(db_session):
    repo = SQLAlchemyPaymentRepo(db_session)
    payment = await repo.create(_create_payment_data())

    updated = await repo.update_status(payment.id, PaymentStatus.PAID)

    assert updated.status == PaymentStatus.PAID
    assert updated.failure_reason is None


@pytest.mark.asyncio
async def test_update_status_with_failure_reason(db_session):
    repo = SQLAlchemyPaymentRepo(db_session)
    payment = await repo.create(_create_payment_data())

    updated = await repo.update_status(payment.id, PaymentStatus.FAILED, "Insufficient funds")

    assert updated.status == PaymentStatus.FAILED
    assert updated.failure_reason == "Insufficient funds"


@pytest.mark.asyncio
async def test_get_by_provider_payment_id(db_session):
    repo = SQLAlchemyPaymentRepo(db_session)
    provider_payment_id = str(uuid.uuid4())
    data = CreatePayment(
        order_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        provider=PaymentProvider.STRIPE,
        amount=Decimal("2000"),
        currency="USD",
        provider_payment_id=provider_payment_id,
        payment_url="https://checkout.stripe.com/pay/test",
    )
    await repo.create(data)

    found = await repo.get_by_provider_payment_id(PaymentProvider.STRIPE, provider_payment_id)

    assert found is not None
    assert found.provider_payment_id == provider_payment_id


@pytest.mark.asyncio
async def test_create_payment_event(db_session):
    payment_repo = SQLAlchemyPaymentRepo(db_session)
    event_repo = SQLAlchemyPaymentEventRepo(db_session)

    payment = await payment_repo.create(_create_payment_data())

    event = await event_repo.create(
        CreatePaymentEvent(
            payment_id=payment.id,
            provider=PaymentProvider.KASPI,
            event_type="payment.success",
            payload={"txn_id": "123", "status": "paid"},
        )
    )

    assert event.id is not None
    assert event.payment_id == payment.id
    assert event.event_type == "payment.success"

    events = await event_repo.get_by_payment_id(payment.id)
    assert len(events) == 1
    assert events[0].payload == {"txn_id": "123", "status": "paid"}
