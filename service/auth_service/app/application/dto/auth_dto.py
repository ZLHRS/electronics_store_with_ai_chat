import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterCommand:
    email: str
    password: str


@dataclass(frozen=True)
class RegisterResult:
    id: uuid.UUID
    email: str


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class SessionContext:
    ip_address: str | None
    user_agent: str | None
    device_id: str | None


@dataclass(frozen=True)
class LoginTokens:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class LoginResult:
    access_token: str


@dataclass(frozen=True)
class UserResult:
    id: uuid.UUID
    email: str
    is_active: bool
    roles: list[str]
