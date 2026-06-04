import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.config import AuthConfig
from app.exceptions import InvalidTokenError, TokenExpiredError

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_BCRYPT_MAX_BYTES = 72


class SecurityService:
    def __init__(self, config: AuthConfig):
        self._config = config

    def hash_password(self, password: str) -> str:
        if len(password.encode()) > _BCRYPT_MAX_BYTES:
            raise ValueError("Password must be at most 72 characters")
        return _pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        if len(plain.encode()) > _BCRYPT_MAX_BYTES:
            return False
        return _pwd_context.verify(plain, hashed)

    def create_access_token(self, user_id: uuid.UUID) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self._config.access_token_expire_minutes)
        return self._encode({"sub": str(user_id), "exp": expire, "type": "access"})

    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        expire = datetime.now(UTC) + timedelta(days=self._config.refresh_token_expire_days)
        return self._encode(
            {
                "sub": str(user_id),
                "exp": expire,
                "type": "refresh",
                "jti": str(uuid.uuid4()),
            }
        )

    def decode_access_token(self, token: str) -> uuid.UUID:
        try:
            payload = jwt.decode(
                token,
                self._config.secret_key.get_secret_value(),
                algorithms=[self._config.algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Access token expired")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Invalid access token")
        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")
        return uuid.UUID(payload["sub"])

    def decode_refresh_token(self, token: str) -> uuid.UUID:
        try:
            payload = jwt.decode(
                token,
                self._config.secret_key.get_secret_value(),
                algorithms=[self._config.algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Refresh token expired")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Invalid refresh token")
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")
        return uuid.UUID(payload["sub"])

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _encode(self, payload: dict) -> str:
        return jwt.encode(
            payload,
            self._config.secret_key.get_secret_value(),
            algorithm=self._config.algorithm,
        )
