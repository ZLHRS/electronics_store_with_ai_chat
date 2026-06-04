from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service.auth_service import AuthService
from app.config import AuthConfig, Config
from app.domain.repo.permission_repo_protocol import PermissionRepository
from app.domain.repo.session_repo_protocol import SessionRepository
from app.domain.repo.user_repo_protocol import UserRepository
from app.infrastructure.cache.permission_cache import PermissionCache
from app.infrastructure.db.repo.permission_repo import SQLAlchemyPermissionRepo
from app.infrastructure.db.repo.session_repo import SQLAlchemySessionRepo
from app.infrastructure.db.repo.user_repo import SQLAlchemyUserRepo
from app.infrastructure.security import SecurityService


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def provide_auth_config(self, config: Config) -> AuthConfig:
        return config.auth

    @provide(scope=Scope.APP)
    def provide_security(self, auth_config: AuthConfig) -> SecurityService:
        return SecurityService(auth_config)

    @provide(scope=Scope.REQUEST)
    def provide_user_repo(self, session: AsyncSession) -> UserRepository:
        return SQLAlchemyUserRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_session_repo(self, session: AsyncSession) -> SessionRepository:
        return SQLAlchemySessionRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_permission_repo(self, session: AsyncSession) -> PermissionRepository:
        return SQLAlchemyPermissionRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_auth_service(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        permission_repository: PermissionRepository,
        permission_cache: PermissionCache,
        security: SecurityService,
        auth_config: AuthConfig,
    ) -> AuthService:
        return AuthService(
            user_repository,
            session_repository,
            permission_repository,
            permission_cache,
            security,
            auth_config,
        )
