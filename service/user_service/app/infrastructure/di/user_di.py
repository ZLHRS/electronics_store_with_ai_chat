from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service.address_service import AddressService
from app.application.service.favorite_service import FavoriteService
from app.application.service.preferences_service import PreferencesService
from app.application.service.user_service import UserProfileService
from app.application.service.view_history_service import ViewHistoryService
from app.config import Config, JWTConfig
from app.domain.repo.address_repo_protocol import AddressRepository
from app.domain.repo.favorite_repo_protocol import FavoriteRepository
from app.domain.repo.preferences_repo_protocol import PreferencesRepository
from app.domain.repo.user_repo_protocol import UserProfileRepository
from app.domain.repo.view_history_repo_protocol import ViewHistoryRepository
from app.infrastructure.db.repo.address_repo import SQLAlchemyAddressRepo
from app.infrastructure.db.repo.favorite_repo import SQLAlchemyFavoriteRepo
from app.infrastructure.db.repo.preferences_repo import SQLAlchemyPreferencesRepo
from app.infrastructure.db.repo.user_repo import SQLAlchemyUserProfileRepo
from app.infrastructure.db.repo.view_history_repo import SQLAlchemyViewHistoryRepo
from app.infrastructure.jwt_service import JWTService


class UserProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def provide_jwt_config(self, config: Config) -> JWTConfig:
        return config.jwt

    @provide(scope=Scope.APP)
    def provide_jwt_service(self, jwt_config: JWTConfig) -> JWTService:
        return JWTService(jwt_config)

    @provide(scope=Scope.REQUEST)
    def provide_user_repo(self, session: AsyncSession) -> UserProfileRepository:
        return SQLAlchemyUserProfileRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_address_repo(self, session: AsyncSession) -> AddressRepository:
        return SQLAlchemyAddressRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_favorite_repo(self, session: AsyncSession) -> FavoriteRepository:
        return SQLAlchemyFavoriteRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_view_history_repo(self, session: AsyncSession) -> ViewHistoryRepository:
        return SQLAlchemyViewHistoryRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_preferences_repo(self, session: AsyncSession) -> PreferencesRepository:
        return SQLAlchemyPreferencesRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_user_service(self, user_repository: UserProfileRepository) -> UserProfileService:
        return UserProfileService(user_repository)

    @provide(scope=Scope.REQUEST)
    def provide_address_service(self, address_repository: AddressRepository) -> AddressService:
        return AddressService(address_repository)

    @provide(scope=Scope.REQUEST)
    def provide_favorite_service(self, favorite_repository: FavoriteRepository) -> FavoriteService:
        return FavoriteService(favorite_repository)

    @provide(scope=Scope.REQUEST)
    def provide_view_history_service(
        self, view_history_repository: ViewHistoryRepository
    ) -> ViewHistoryService:
        return ViewHistoryService(view_history_repository)

    @provide(scope=Scope.REQUEST)
    def provide_preferences_service(
        self, preferences_repository: PreferencesRepository
    ) -> PreferencesService:
        return PreferencesService(preferences_repository)
