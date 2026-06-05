from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service.order_service import OrderService
from app.config import Config, JWTConfig
from app.domain.repo.order_repo_protocol import OrderRepository
from app.infrastructure.cart_client import CartServiceClient
from app.infrastructure.db.repo.order_repo import SQLAlchemyOrderRepo
from app.infrastructure.jwt_service import JWTService
from app.infrastructure.product_client import ProductServiceClient


class OrderProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def provide_jwt_config(self, config: Config) -> JWTConfig:
        return config.jwt

    @provide(scope=Scope.APP)
    def provide_jwt_service(self, jwt_config: JWTConfig) -> JWTService:
        return JWTService(jwt_config)

    @provide(scope=Scope.APP)
    async def provide_cart_http_client(self, config: Config) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient(base_url=config.cart_service.url, timeout=5.0) as client:
            yield client

    @provide(scope=Scope.APP)
    async def provide_product_http_client(
        self, config: Config
    ) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            base_url=config.product_service.url, timeout=5.0
        ) as client:
            yield client

    @provide(scope=Scope.APP)
    def provide_cart_client(
        self, client: httpx.AsyncClient, config: Config
    ) -> CartServiceClient:
        return CartServiceClient(client, config.jwt.access_token_name)

    @provide(scope=Scope.APP)
    def provide_product_client(self, client: httpx.AsyncClient) -> ProductServiceClient:
        return ProductServiceClient(client)

    @provide(scope=Scope.REQUEST)
    def provide_order_repo(self, session: AsyncSession) -> OrderRepository:
        return SQLAlchemyOrderRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_order_service(
        self,
        order_repository: OrderRepository,
        cart_client: CartServiceClient,
        product_client: ProductServiceClient,
    ) -> OrderService:
        return OrderService(order_repository, cart_client, product_client)
