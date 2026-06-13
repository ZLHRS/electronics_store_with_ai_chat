from collections.abc import AsyncIterable

import anthropic
import httpx
import openai
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service.chat_service import ChatService
from app.application.service.rag_service import RAGService
from app.config import AIConfig, Config, JWTConfig
from app.domain.repo.chat_repo import ChatSessionRepository, EmbeddingRepository, MessageRepository
from app.infrastructure.db.repo.chat_session_repo import SQLAlchemyChatSessionRepo
from app.infrastructure.db.repo.embedding_repo import SQLAlchemyEmbeddingRepo
from app.infrastructure.db.repo.message_repo import SQLAlchemyMessageRepo
from app.infrastructure.embedding_service import EmbeddingService
from app.infrastructure.jwt_service import JWTService
from app.infrastructure.llm_service import LLMService
from app.infrastructure.product_client import ProductServiceClient


class ChatProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def provide_jwt_config(self, config: Config) -> JWTConfig:
        return config.jwt

    @provide(scope=Scope.APP)
    def provide_jwt_service(self, jwt_config: JWTConfig) -> JWTService:
        return JWTService(jwt_config)

    @provide(scope=Scope.APP)
    def provide_ai_config(self, config: Config) -> AIConfig:
        return config.ai

    @provide(scope=Scope.APP)
    def provide_openai_client(self, ai_config: AIConfig) -> openai.AsyncOpenAI:
        return openai.AsyncOpenAI(api_key=ai_config.openai_api_key.get_secret_value())

    @provide(scope=Scope.APP)
    def provide_anthropic_client(self, ai_config: AIConfig) -> anthropic.AsyncAnthropic:
        return anthropic.AsyncAnthropic(
            api_key=ai_config.anthropic_api_key.get_secret_value()
        )

    @provide(scope=Scope.APP)
    def provide_embedding_service(
        self, client: openai.AsyncOpenAI, ai_config: AIConfig
    ) -> EmbeddingService:
        return EmbeddingService(client, ai_config.embedding_model)

    @provide(scope=Scope.APP)
    def provide_llm_service(
        self, client: anthropic.AsyncAnthropic, ai_config: AIConfig
    ) -> LLMService:
        return LLMService(client, ai_config.llm_model)

    @provide(scope=Scope.APP)
    async def provide_http_client(self, config: Config) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            base_url=config.product_service.url, timeout=10.0
        ) as client:
            yield client

    @provide(scope=Scope.APP)
    def provide_product_client(self, client: httpx.AsyncClient) -> ProductServiceClient:
        return ProductServiceClient(client)

    @provide(scope=Scope.REQUEST)
    def provide_session_repo(self, session: AsyncSession) -> ChatSessionRepository:
        return SQLAlchemyChatSessionRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_message_repo(self, session: AsyncSession) -> MessageRepository:
        return SQLAlchemyMessageRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_embedding_repo(self, session: AsyncSession) -> EmbeddingRepository:
        return SQLAlchemyEmbeddingRepo(session)

    @provide(scope=Scope.REQUEST)
    def provide_rag_service(
        self,
        embedding_repo: EmbeddingRepository,
        embedding_service: EmbeddingService,
        product_client: ProductServiceClient,
    ) -> RAGService:
        return RAGService(embedding_repo, embedding_service, product_client)

    @provide(scope=Scope.REQUEST)
    def provide_chat_service(
        self,
        session_repo: ChatSessionRepository,
        message_repo: MessageRepository,
        rag_service: RAGService,
        llm_service: LLMService,
    ) -> ChatService:
        return ChatService(session_repo, message_repo, rag_service, llm_service)
