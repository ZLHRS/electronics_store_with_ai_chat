from app.domain.entity.chat_entity import ChatSessionEntity, MessageEntity
from app.infrastructure.db.model.chat_session_model import ChatSessionModel
from app.infrastructure.db.model.message_model import MessageModel


def session_model_to_entity(model: ChatSessionModel) -> ChatSessionEntity:
    return ChatSessionEntity(
        id=model.id,
        user_id=model.user_id,
        title=model.title,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def message_model_to_entity(model: MessageModel) -> MessageEntity:
    return MessageEntity(
        id=model.id,
        session_id=model.session_id,
        role=model.role,
        content=model.content,
        created_at=model.created_at,
    )
