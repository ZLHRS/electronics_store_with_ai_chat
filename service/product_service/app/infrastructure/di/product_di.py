from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service.brand_service import BrandService
from app.application.service.category_service import CategoryService
from app.application.service.product_service import ProductService
from app.config import Config, JWTConfig
from app.domain.repo.brand_repo_protocol import BrandRepository
from app.domain.repo.category_repo_protocol import CategoryRepository
from app.domain.repo.product_repo_protocol import ProductRepository
from app.infrastructure.db.repo.brand_repo import SQLAlchemyBrandRepo
from app.infrastructure.db.repo.category_repo import SQLAlchemyCategoryRepo
from app.infrastructure.db.repo.product_repo import SQLAlchemyProductRepo
from app.infrastructure.jwt_service import JWTService


class ProductProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def provide_jwt_config(self, config: Config) -> JWTConfig:
        return config.jwt

    @provide(scope=Scope.APP)
    def provide_jwt_service(self, jwt_config: JWTConfig) -> JWTService:
        return JWTService(jwt_config)

    @provide(scope=Scope.REQUEST)
    def provide_product_repo(self, session: AsyncSession) -> ProductRepository:
        return SQLAlchemyProductRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_category_repo(self, session: AsyncSession) -> CategoryRepository:
        return SQLAlchemyCategoryRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_brand_repo(self, session: AsyncSession) -> BrandRepository:
        return SQLAlchemyBrandRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_product_service(self, product_repository: ProductRepository) -> ProductService:
        return ProductService(product_repository)

    @provide(scope=Scope.REQUEST)
    def provide_category_service(self, category_repository: CategoryRepository) -> CategoryService:
        return CategoryService(category_repository)

    @provide(scope=Scope.REQUEST)
    def provide_brand_service(self, brand_repository: BrandRepository) -> BrandService:
        return BrandService(brand_repository)
