import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import DatabaseError
from app.infrastructure.db.model.permission_model import PermissionModel
from app.infrastructure.db.model.role_model import RoleModel
from app.infrastructure.db.model.role_permission_model import RolePermissionModel
from app.infrastructure.db.model.user_role_model import UserRoleModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo


class SQLAlchemyPermissionRepo(SQLAlchemyBaseRepo):
    async def get_user_permissions(self, user_id: uuid.UUID) -> frozenset[str]:
        stmt = (
            select(PermissionModel.code)
            .join(RolePermissionModel, PermissionModel.id == RolePermissionModel.permission_id)
            .join(UserRoleModel, UserRoleModel.role_id == RolePermissionModel.role_id)
            .where(UserRoleModel.user_id == user_id)
        )
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get user permissions") from e
        return frozenset(row[0] for row in result)

    async def get_user_roles(self, user_id: uuid.UUID) -> list[str]:
        stmt = (
            select(RoleModel.name)
            .join(UserRoleModel, RoleModel.id == UserRoleModel.role_id)
            .where(UserRoleModel.user_id == user_id)
            .order_by(RoleModel.name)
        )
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get user roles") from e
        return [row[0] for row in result]

    async def assign_role(self, user_id: uuid.UUID, role_name: str) -> None:
        role_stmt = select(RoleModel.id).where(RoleModel.name == role_name)
        try:
            role_id = (await self.session.execute(role_stmt)).scalar_one_or_none()
            if role_id is None:
                raise DatabaseError(f"Role '{role_name}' not found")
            await self.session.execute(
                insert(UserRoleModel)
                .values(user_id=user_id, role_id=role_id)
                .on_conflict_do_nothing()
            )
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to assign role") from e
