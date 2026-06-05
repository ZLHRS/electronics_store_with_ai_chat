from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service.cart_service import CartService
from app.config import Config, JWTConfig
from app.domain.repo.cart_item_repo_protocol import CartItemRepository
from app.domain.repo.cart_repo_protocol import CartRepository
from app.infrastructure.db.repo.cart_item_repo import SQLAlchemyCartItemRepo
from app.infrastructure.db.repo.cart_repo import SQLAlchemyCartRepo
from app.infrastructure.jwt_service import JWTService
from app.infrastructure.product_client import ProductServiceClient


class CartProvider(Provider):
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
            base_url=config.product_service.url, timeout=5.0
        ) as client:
            yield client

    @provide(scope=Scope.APP)
    def provide_product_client(self, client: httpx.AsyncClient) -> ProductServiceClient:
        return ProductServiceClient(client)

    @provide(scope=Scope.REQUEST)
    def provide_cart_repo(self, session: AsyncSession) -> CartRepository:
        return SQLAlchemyCartRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_cart_item_repo(self, session: AsyncSession) -> CartItemRepository:
        return SQLAlchemyCartItemRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_cart_service(
        self,
        cart_repository: CartRepository,
        cart_item_repository: CartItemRepository,
        product_client: ProductServiceClient,
    ) -> CartService:
        return CartService(cart_repository, cart_item_repository, product_client)
