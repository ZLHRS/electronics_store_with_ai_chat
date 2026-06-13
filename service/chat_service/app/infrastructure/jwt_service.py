import uuid

import jwt

from app.config import JWTConfig
from app.exceptions import InvalidTokenError, TokenExpiredError


class JWTService:
    def __init__(self, config: JWTConfig):
        self._config = config

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
