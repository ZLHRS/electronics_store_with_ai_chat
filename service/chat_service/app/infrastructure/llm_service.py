from __future__ import annotations

import openai

from app.domain.entity.chat_entity import MessageEntity
from app.domain.repo.chat_repo import ProductContext

_SYSTEM = """Ты AI-ассистент интернет-магазина Shop.
Твоя задача — помогать пользователям найти подходящие товары.

Правила:
- Предлагай конкретные товары из предоставленного контекста
- Указывай цены
- Объясняй кратко, почему товар подходит под запрос
- Задавай уточняющие вопросы если запрос неясен
- Если подходящих товаров в контексте нет — честно сообщи об этом
- Отвечай на русском языке, кратко и по делу
"""


class LLMService:
    def __init__(self, client: openai.AsyncOpenAI, model: str):
        self._client = client
        self._model = model

    async def chat(
        self,
        history: list[MessageEntity],
        context: list[ProductContext],
        user_message: str,
    ) -> str:
        messages = self._build_messages(history, context, user_message)
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "system", "content": _SYSTEM}] + messages,
        )
        return response.choices[0].message.content or ""

    def _build_messages(
        self,
        history: list[MessageEntity],
        context: list[ProductContext],
        user_message: str,
    ) -> list[dict]:
        messages = []

        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        if context:
            context_text = "Найденные товары в каталоге:\n\n" + "\n\n".join(
                f"[Товар {i + 1}]\n{item.content}\n(Релевантность: {item.similarity:.0%})"
                for i, item in enumerate(context)
            )
            full_message = f"{context_text}\n\n---\nЗапрос пользователя: {user_message}"
        else:
            full_message = user_message

        messages.append({"role": "user", "content": full_message})
        return messages
