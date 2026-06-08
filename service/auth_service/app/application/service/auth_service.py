import logging
import uuid
from datetime import UTC, datetime, timedelta

from app.application.dto.auth_dto import (
    LoginCommand,
    LoginTokens,
    RegisterCommand,
    RegisterResult,
    SessionContext,
    UserResult,
)
from app.config import AuthConfig
from app.domain.entity.session_entity import CreateSession
from app.domain.entity.user_entity import RegisterApplication
from app.domain.repo.permission_repo_protocol import PermissionRepository
from app.domain.repo.session_repo_protocol import SessionRepository
from app.domain.repo.user_repo_protocol import UserRepository
from app.exceptions import (
    DuplicateEntryError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    TokenReuseError,
    UserAlreadyExistsError,
)
from app.infrastructure.cache.permission_cache import PermissionCache
from app.infrastructure.security import SecurityService

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        permission_repository: PermissionRepository,
        permission_cache: PermissionCache,
        security: SecurityService,
        auth_config: AuthConfig,
    ):
        self._users = user_repository
        self._sessions = session_repository
        self._permissions = permission_repository
        self._cache = permission_cache
        self._security = security
        self._config = auth_config

    async def register(self, command: RegisterCommand) -> RegisterResult:
        hashed = self._security.hash_password(command.password)
        try:
            user = await self._users.register(
                RegisterApplication(email=command.email, password=hashed)
            )
        except DuplicateEntryError:
            raise UserAlreadyExistsError("Email already registered")
        await self._permissions.assign_role(user.id, "user")
        logger.info("User registered: %s", user.email)
        return RegisterResult(id=user.id, email=user.email)

    async def login(self, command: LoginCommand, context: SessionContext) -> LoginTokens:
        user = await self._users.get_by_email(command.email)
        if (
            user is None
            or not user.is_active
            or not self._security.verify_password(command.password, user.password)
        ):
            logger.warning("Failed login for email=%s ip=%s", command.email, context.ip_address)
            raise InvalidCredentialsError("Invalid credentials")

        if await self._sessions.has_active_session(user.id):
            await self._sessions.revoke_all_by_user_id(user.id)
            await self._cache.delete(user.id)

        permissions = await self._permissions.get_user_permissions(user.id)
        ttl = self._config.access_token_expire_minutes * 60
        await self._cache.set(user.id, permissions, ttl)

        refresh_token = self._security.create_refresh_token(user.id)
        await self._sessions.create(
            CreateSession(
                user_id=user.id,
                refresh_token_hash=self._security.hash_token(refresh_token),
                device_id=context.device_id,
                ip_address=context.ip_address,
                user_agent=context.user_agent,
                expires_at=datetime.now(UTC)
                + timedelta(days=self._config.refresh_token_expire_days),
            )
        )

        logger.info("User logged in: %s ip=%s", user.email, context.ip_address)
        return LoginTokens(
            access_token=self._security.create_access_token(user.id),
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str, context: SessionContext) -> LoginTokens:
        user_id = self._security.decode_refresh_token(refresh_token)
        token_hash = self._security.hash_token(refresh_token)

        session = await self._sessions.get_by_token_hash(token_hash)
        if session is None:
            raise InvalidTokenError("Invalid refresh token")
        if session.revoked:
            logger.warning(
                "Token reuse detected user_id=%s ip=%s", session.user_id, context.ip_address
            )
            await self._sessions.revoke_all_by_user_id(session.user_id)
            raise TokenReuseError("Token reuse detected")
        if session.expires_at < datetime.now(UTC):
            raise TokenExpiredError("Refresh token expired")

        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError("User not found or inactive")

        await self._sessions.update_last_used(session.id)
        await self._sessions.revoke(session.id)

        permissions = await self._permissions.get_user_permissions(user_id)
        ttl = self._config.access_token_expire_minutes * 60
        await self._cache.set(user_id, permissions, ttl)

        new_refresh_token = self._security.create_refresh_token(user_id)
        await self._sessions.create(
            CreateSession(
                user_id=user_id,
                refresh_token_hash=self._security.hash_token(new_refresh_token),
                device_id=context.device_id,
                ip_address=context.ip_address,
                user_agent=context.user_agent,
                expires_at=datetime.now(UTC)
                + timedelta(days=self._config.refresh_token_expire_days),
            )
        )

        logger.info("Token refreshed user_id=%s", user_id)
        return LoginTokens(
            access_token=self._security.create_access_token(user_id),
            refresh_token=new_refresh_token,
        )

    async def logout(self, refresh_token: str) -> None:
        token_hash = self._security.hash_token(refresh_token)
        session = await self._sessions.get_by_token_hash(token_hash)
        if session is not None and not session.revoked:
            await self._sessions.revoke(session.id)
            await self._cache.delete(session.user_id)
            logger.info("User logged out user_id=%s", session.user_id)

    async def get_me(self, user_id: uuid.UUID) -> UserResult:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise InvalidTokenError("User not found")
        roles = await self._permissions.get_user_roles(user_id)
        return UserResult(id=user.id, email=user.email, is_active=user.is_active, roles=roles)

    async def logout_all(self, user_id: uuid.UUID) -> None:
        await self._sessions.revoke_all_by_user_id(user_id)
        await self._cache.delete(user_id)
        logger.info("All sessions revoked user_id=%s", user_id)
