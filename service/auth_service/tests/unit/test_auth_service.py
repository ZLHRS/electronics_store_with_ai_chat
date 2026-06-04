import uuid
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr

from app.application.dto.auth_dto import LoginCommand, RegisterCommand, SessionContext
from app.application.service.auth_service import AuthService
from app.config import AuthConfig
from app.domain.entity.session_entity import SessionEntity
from app.domain.entity.user_entity import UserEntity
from app.exceptions import (
    AlreadyLoggedInError,
    DuplicateEntryError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenReuseError,
    UserAlreadyExistsError,
)
from app.infrastructure.security import SecurityService

_TEST_CONFIG = AuthConfig(
    secret_key=SecretStr("test-secret-key-at-least-32-characters-long"),
    algorithm="HS256",
    access_token_expire_minutes=15,
    refresh_token_expire_days=7,
    access_token_name="access_token",
    refresh_token_name="refresh_token",
    cookie_secure=False,
    cookie_samesite="lax",
)

_CONTEXT = SessionContext(ip_address=None, user_agent=None, device_id=None)

_USER_PERMISSIONS = frozenset({"users.read", "orders.read.own"})


class FakeUserRepo:
    def __init__(self, user: UserEntity | None = None, raise_duplicate: bool = False):
        self._user = user
        self._raise_duplicate = raise_duplicate

    async def get_by_id(self, user_id):
        return self._user

    async def get_by_email(self, email):
        return self._user

    async def register(self, application_data):
        if self._raise_duplicate:
            raise DuplicateEntryError("Email already registered")
        return UserEntity(
            id=uuid.uuid4(),
            email=application_data.email,
            password=application_data.password,
            is_active=True,
            created_at=datetime.now(UTC),
        )


class FakeSessionRepo:
    def __init__(self, session: SessionEntity | None = None, has_active: bool = False):
        self._session = session
        self._has_active = has_active
        self.revoked_ids: list[uuid.UUID] = []
        self.revoked_user_ids: list[uuid.UUID] = []

    async def create(self, data):
        return SessionEntity(
            id=uuid.uuid4(),
            user_id=data.user_id,
            refresh_token_hash=data.refresh_token_hash,
            device_id=data.device_id,
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            created_at=datetime.now(UTC),
            expires_at=data.expires_at,
            last_used_at=None,
            revoked=False,
        )

    async def get_by_token_hash(self, token_hash):
        return self._session

    async def revoke(self, session_id):
        self.revoked_ids.append(session_id)

    async def revoke_all_by_user_id(self, user_id):
        self.revoked_user_ids.append(user_id)

    async def update_last_used(self, session_id):
        pass

    async def has_active_session(self, user_id):
        return self._has_active


class FakePermissionRepo:
    def __init__(self, permissions: frozenset[str] = _USER_PERMISSIONS):
        self._permissions = permissions

    async def get_user_permissions(self, user_id):
        return self._permissions

    async def get_user_roles(self, user_id):
        return ["user"]

    async def assign_role(self, user_id, role_name):
        pass


class FakePermissionCache:
    def __init__(self):
        self._store: dict[uuid.UUID, frozenset[str]] = {}

    async def get(self, user_id):
        return self._store.get(user_id)

    async def set(self, user_id, permissions, ttl_seconds):
        self._store[user_id] = permissions

    async def delete(self, user_id):
        self._store.pop(user_id, None)


@pytest.fixture
def security():
    return SecurityService(_TEST_CONFIG)


def _make_service(
    user=None, session=None, raise_duplicate=False, security=None, has_active_session=False
):
    if security is None:
        security = SecurityService(_TEST_CONFIG)
    return AuthService(
        user_repository=FakeUserRepo(user=user, raise_duplicate=raise_duplicate),
        session_repository=FakeSessionRepo(session=session, has_active=has_active_session),
        permission_repository=FakePermissionRepo(),
        permission_cache=FakePermissionCache(),
        security=security,
        auth_config=_TEST_CONFIG,
    )


async def test_register_success():
    service = _make_service()
    result = await service.register(
        RegisterCommand(email="new@example.com", password="password123")
    )
    assert result.email == "new@example.com"
    assert result.id is not None


async def test_register_duplicate_email_raises():
    service = _make_service(raise_duplicate=True)
    with pytest.raises(UserAlreadyExistsError):
        await service.register(RegisterCommand(email="dup@example.com", password="password123"))


async def test_login_user_not_found_raises():
    service = _make_service(user=None)
    with pytest.raises(InvalidCredentialsError):
        await service.login(LoginCommand(email="no@example.com", password="any"), _CONTEXT)


async def test_login_wrong_password_raises(security):
    hashed = security.hash_password("correct")
    user = UserEntity(
        id=uuid.uuid4(),
        email="u@example.com",
        password=hashed,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    service = _make_service(user=user, security=security)
    with pytest.raises(InvalidCredentialsError):
        await service.login(LoginCommand(email="u@example.com", password="wrong"), _CONTEXT)


async def test_login_inactive_user_raises(security):
    hashed = security.hash_password("secret")
    user = UserEntity(
        id=uuid.uuid4(),
        email="u@example.com",
        password=hashed,
        is_active=False,
        created_at=datetime.now(UTC),
    )
    service = _make_service(user=user, security=security)
    with pytest.raises(InvalidCredentialsError):
        await service.login(LoginCommand(email="u@example.com", password="secret"), _CONTEXT)


async def test_login_success_returns_tokens(security):
    hashed = security.hash_password("secret123")
    user = UserEntity(
        id=uuid.uuid4(),
        email="u@example.com",
        password=hashed,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    service = _make_service(user=user, security=security)
    tokens = await service.login(
        LoginCommand(email="u@example.com", password="secret123"), _CONTEXT
    )
    assert tokens.access_token
    assert tokens.refresh_token


async def test_login_already_logged_in_raises(security):
    hashed = security.hash_password("secret")
    user = UserEntity(
        id=uuid.uuid4(),
        email="u@example.com",
        password=hashed,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    service = _make_service(user=user, security=security, has_active_session=True)
    with pytest.raises(AlreadyLoggedInError):
        await service.login(LoginCommand(email="u@example.com", password="secret"), _CONTEXT)


async def test_refresh_token_not_in_db(security):
    service = _make_service(session=None, security=security)
    token = security.create_refresh_token(uuid.uuid4())
    with pytest.raises(InvalidTokenError):
        await service.refresh(token, _CONTEXT)


async def test_refresh_revoked_token_raises_reuse(security):
    user_id = uuid.uuid4()
    token = security.create_refresh_token(user_id)
    session = SessionEntity(
        id=uuid.uuid4(),
        user_id=user_id,
        refresh_token_hash=security.hash_token(token),
        device_id=None,
        ip_address=None,
        user_agent=None,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=7),
        last_used_at=None,
        revoked=True,
    )
    service = _make_service(session=session, security=security)
    with pytest.raises(TokenReuseError):
        await service.refresh(token, _CONTEXT)
