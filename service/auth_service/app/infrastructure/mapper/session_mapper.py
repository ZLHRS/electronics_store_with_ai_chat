from app.domain.entity.session_entity import SessionEntity
from app.infrastructure.db.model.user_session_model import UserSessionModel


def session_model_to_entity(model: UserSessionModel) -> SessionEntity:
    return SessionEntity(
        id=model.id,
        user_id=model.user_id,
        refresh_token_hash=model.refresh_token_hash,
        device_id=model.device_id,
        ip_address=model.ip_address,
        user_agent=model.user_agent,
        created_at=model.created_at,
        expires_at=model.expires_at,
        last_used_at=model.last_used_at,
        revoked=model.revoked,
    )
