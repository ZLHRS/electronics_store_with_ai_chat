import pytest

from app.domain.entity.user_entity import RegisterApplication
from app.exceptions import DuplicateEntryError
from app.infrastructure.db.repo.user_repo import SQLAlchemyUserRepo


@pytest.fixture
def user_repo(db_session):
    return SQLAlchemyUserRepo(db_session)


async def test_register_user(user_repo):
    result = await user_repo.register(
        RegisterApplication(email="integration@example.com", password="hashed_password")
    )
    assert result.id is not None
    assert result.email == "integration@example.com"


async def test_get_by_email_found(user_repo):
    await user_repo.register(RegisterApplication(email="findme@example.com", password="hashed"))
    result = await user_repo.get_by_email("findme@example.com")
    assert result is not None
    assert result.email == "findme@example.com"


async def test_get_by_email_not_found(user_repo):
    result = await user_repo.get_by_email("ghost@example.com")
    assert result is None


async def test_register_duplicate_email_raises(user_repo):
    data = RegisterApplication(email="dup@example.com", password="hashed")
    await user_repo.register(data)
    with pytest.raises(DuplicateEntryError):
        await user_repo.register(data)
