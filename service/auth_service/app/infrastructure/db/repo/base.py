from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyBaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
