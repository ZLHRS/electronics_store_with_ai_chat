from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseModel):
    host: str
    port: int = Field(gt=0, lt=65536)
    user: str
    password: SecretStr
    db: str
    echo: bool = False
    pool_size: int = Field(default=30, ge=1)
    pool_timeout: int = Field(default=30, ge=0)
    pool_recycle: int = Field(default=3600, ge=0)
    max_overflow: int = Field(default=20, ge=0)
    pool_pre_ping: bool = True
    echo_pool: bool = False

    def get_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"
        )


class AuthConfig(BaseModel):
    secret_key: SecretStr = Field(min_length=32)
    algorithm: str = Field(min_length=1)
    access_token_expire_minutes: int = Field(gt=0)
    refresh_token_expire_days: int = Field(gt=0)
    access_token_name: str = Field(default="access_token")
    refresh_token_name: str = Field(default="refresh_token")
    cookie_secure: bool = Field(default=True)
    cookie_samesite: str = Field(default="strict")


class RedisConfig(BaseModel):
    url: str


class CorsConfig(BaseModel):
    origins: list[str] = Field(default_factory=list)


class LoggingConfig(BaseModel):
    level: str = Field(min_length=1)


class EnvConfig(BaseSettings):
    db_host: str = Field(validation_alias="DB_HOST")
    db_port: int = Field(default=5432, gt=0, lt=65536, validation_alias="DB_PORT")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: SecretStr = Field(validation_alias="DB_PASSWORD")
    db_name: str = Field(validation_alias="DB_NAME")
    db_echo: bool = Field(default=False, validation_alias="DB_ECHO")
    db_pool_size: int = Field(default=30, ge=1, validation_alias="DB_POOL_SIZE")
    db_pool_timeout: int = Field(default=30, ge=0, validation_alias="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=3600, ge=0, validation_alias="DB_POOL_RECYCLE")
    db_max_overflow: int = Field(default=20, ge=0, validation_alias="DB_MAX_OVERFLOW")
    db_pool_pre_ping: bool = Field(default=True, validation_alias="DB_POOL_PRE_PING")
    db_echo_pool: bool = Field(default=False, validation_alias="DB_ECHO_POOL")

    auth_secret_key: SecretStr = Field(min_length=32, validation_alias="AUTH_SECRET_KEY")
    auth_algorithm: str = Field(min_length=1, validation_alias="AUTH_ALGORITHM")
    auth_access_token_expire_minutes: int = Field(
        gt=0, validation_alias="AUTH_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    auth_refresh_token_expire_days: int = Field(
        gt=0, validation_alias="AUTH_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    auth_access_token_name: str = Field(
        default="access_token", validation_alias="AUTH_ACCESS_TOKEN_NAME"
    )
    auth_refresh_token_name: str = Field(
        default="refresh_token", validation_alias="AUTH_REFRESH_TOKEN_NAME"
    )
    auth_cookie_secure: bool = Field(default=True, validation_alias="AUTH_COOKIE_SECURE")
    auth_cookie_samesite: str = Field(default="strict", validation_alias="AUTH_COOKIE_SAMESITE")

    redis_url: str = Field(default="redis://localhost:6379", validation_alias="REDIS_URL")

    cors_origins: str = Field(default="", validation_alias="CORS_ORIGINS")

    level: str = Field(validation_alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


class Config(BaseModel):
    postgres: PostgresConfig
    auth: AuthConfig
    redis: RedisConfig
    cors: CorsConfig
    logging: LoggingConfig


def setup_config() -> Config:
    env = EnvConfig()  # type: ignore[call-arg]
    return Config(
        postgres=PostgresConfig(
            host=env.db_host,
            port=env.db_port,
            user=env.db_user,
            password=env.db_password,
            db=env.db_name,
            echo=env.db_echo,
            pool_size=env.db_pool_size,
            pool_timeout=env.db_pool_timeout,
            pool_recycle=env.db_pool_recycle,
            max_overflow=env.db_max_overflow,
            pool_pre_ping=env.db_pool_pre_ping,
            echo_pool=env.db_echo_pool,
        ),
        auth=AuthConfig(
            secret_key=env.auth_secret_key,
            algorithm=env.auth_algorithm,
            access_token_expire_minutes=env.auth_access_token_expire_minutes,
            refresh_token_expire_days=env.auth_refresh_token_expire_days,
            access_token_name=env.auth_access_token_name,
            refresh_token_name=env.auth_refresh_token_name,
            cookie_secure=env.auth_cookie_secure,
            cookie_samesite=env.auth_cookie_samesite,
        ),
        redis=RedisConfig(url=env.redis_url),
        cors=CorsConfig(
            origins=[o.strip() for o in env.cors_origins.split(",") if o.strip()],
        ),
        logging=LoggingConfig(level=env.level),
    )
