from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service.payment_service import PaymentService
from app.config import Config, JWTConfig
from app.domain.repo.payment_event_repo_protocol import PaymentEventRepository
from app.domain.repo.payment_repo_protocol import PaymentRepository
from app.infrastructure.db.repo.payment_event_repo import SQLAlchemyPaymentEventRepo
from app.infrastructure.db.repo.payment_repo import SQLAlchemyPaymentRepo
from app.infrastructure.jwt_service import JWTService
from app.infrastructure.order_client import OrderServiceClient


class PaymentProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def provide_jwt_config(self, config: Config) -> JWTConfig:
        return config.jwt

    @provide(scope=Scope.APP)
    def provide_jwt_service(self, jwt_config: JWTConfig) -> JWTService:
        return JWTService(jwt_config)

    @provide(scope=Scope.APP)
    async def provide_http_client(self, config: Config) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            base_url=config.order_service.url, timeout=5.0
        ) as client:
            yield client

    @provide(scope=Scope.APP)
    def provide_order_client(self, client: httpx.AsyncClient) -> OrderServiceClient:
        return OrderServiceClient(client)

    @provide(scope=Scope.REQUEST)
    def provide_payment_repo(self, session: AsyncSession) -> PaymentRepository:
        return SQLAlchemyPaymentRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_payment_event_repo(self, session: AsyncSession) -> PaymentEventRepository:
        return SQLAlchemyPaymentEventRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_payment_service(
        self,
        payment_repository: PaymentRepository,
        payment_event_repository: PaymentEventRepository,
        order_client: OrderServiceClient,
    ) -> PaymentService:
        return PaymentService(payment_repository, payment_event_repository, order_client)
