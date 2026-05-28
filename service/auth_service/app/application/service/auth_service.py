from datetime import datetime, timedelta, timezone

from app.application.dto.auth_dto import (
    LoginCommand,
    LoginResult,
    LoginTokens,
    RegisterCommand,
    RegisterResult,
    SessionContext,
)
from app.config import AuthConfig
from app.domain.entity.session_entity import CreateSession
from app.domain.entity.user_entity import RegisterApplication
from app.domain.repo.session_repo_protocol import SessionRepository
from app.domain.repo.user_repo_protocol import UserRepository
from app.infrastructure.security import SecurityService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        security: SecurityService,
        auth_config: AuthConfig,
    ):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.security = security
        self._config = auth_config

    async def register(self, command: RegisterCommand) -> RegisterResult:
        hashed_password = self.security.hash_password(command.password)
        entity = RegisterApplication(email=command.email, password=hashed_password)
        result = await self.user_repository.register(entity)
        return RegisterResult(id=result.id, email=result.email)

    async def login(self, command: LoginCommand, context: SessionContext) -> LoginTokens:
        user = await self.user_repository.get_by_email(command.email)
        if user is None or not self.security.verify_password(command.password, user.password):
            raise ValueError("Invalid credentials")

        refresh_token = self.security.create_refresh_token(user.id)
        expires_at = datetime.now(timezone.utc) + timedelta(days=self._config.refresh_token_expire_days)

        await self.session_repository.create(CreateSession(
            user_id=user.id,
            refresh_token_hash=self.security.hash_token(refresh_token),
            device_id=context.device_id,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            expires_at=expires_at,
        ))

        return LoginTokens(
            access_token=self.security.create_access_token(user.id),
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str, context: SessionContext) -> LoginTokens:
        user_id = self.security.decode_refresh_token(refresh_token)
        token_hash = self.security.hash_token(refresh_token)

        session = await self.session_repository.get_by_token_hash(token_hash)
        if session is None:
            raise ValueError("Invalid refresh token")
        if session.revoked:
            await self.session_repository.revoke_all_by_user_id(session.user_id)
            raise ValueError("Token reuse detected")
        if session.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token expired")

        await self.session_repository.update_last_used(session.id)
        await self.session_repository.revoke(session.id)

        new_refresh_token = self.security.create_refresh_token(user_id)
        expires_at = datetime.now(timezone.utc) + timedelta(days=self._config.refresh_token_expire_days)

        await self.session_repository.create(CreateSession(
            user_id=user_id,
            refresh_token_hash=self.security.hash_token(new_refresh_token),
            device_id=context.device_id,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            expires_at=expires_at,
        ))

        return LoginTokens(
            access_token=self.security.create_access_token(user_id),
            refresh_token=new_refresh_token,
        )

    async def logout(self, refresh_token: str) -> None:
        token_hash = self.security.hash_token(refresh_token)
        session = await self.session_repository.get_by_token_hash(token_hash)
        if session is not None and not session.revoked:
            await self.session_repository.revoke(session.id)

    async def logout_all(self, access_token: str) -> None:
        user_id = self.security.decode_access_token(access_token)
        await self.session_repository.revoke_all_by_user_id(user_id)
