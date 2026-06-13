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


class JWTConfig(BaseModel):
    secret_key: SecretStr = Field(min_length=32)
    algorithm: str = Field(min_length=1)
    access_token_name: str = Field(default="access_token")


class RedisConfig(BaseModel):
    url: str


class ProductServiceConfig(BaseModel):
    url: str


class AIConfig(BaseModel):
    openai_api_key: SecretStr
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    llm_model: str = "gpt-4o-mini"


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
    auth_access_token_name: str = Field(
        default="access_token", validation_alias="AUTH_ACCESS_TOKEN_NAME"
    )

    redis_url: str = Field(default="redis://localhost:6379", validation_alias="REDIS_URL")

    product_service_url: str = Field(
        default="http://product_service:8002", validation_alias="PRODUCT_SERVICE_URL"
    )

    openai_api_key: SecretStr = Field(validation_alias="OPENAI_API_KEY")
    embedding_model: str = Field(
        default="text-embedding-3-small", validation_alias="EMBEDDING_MODEL"
    )
    llm_model: str = Field(
        default="gpt-4o-mini", validation_alias="LLM_MODEL"
    )

    cors_origins: str = Field(default="", validation_alias="CORS_ORIGINS")
    level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


class Config(BaseModel):
    postgres: PostgresConfig
    jwt: JWTConfig
    redis: RedisConfig
    product_service: ProductServiceConfig
    ai: AIConfig
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
        jwt=JWTConfig(
            secret_key=env.auth_secret_key,
            algorithm=env.auth_algorithm,
            access_token_name=env.auth_access_token_name,
        ),
        redis=RedisConfig(url=env.redis_url),
        product_service=ProductServiceConfig(url=env.product_service_url),
        ai=AIConfig(
            openai_api_key=env.openai_api_key,
            embedding_model=env.embedding_model,
            llm_model=env.llm_model,
        ),
        cors=CorsConfig(
            origins=[o.strip() for o in env.cors_origins.split(",") if o.strip()],
        ),
        logging=LoggingConfig(level=env.level),
    )
