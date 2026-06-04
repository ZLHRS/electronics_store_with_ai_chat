import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import setup_config
from app.domain.permissions import P
from app.infrastructure.db.model.permission_model import PermissionModel
from app.infrastructure.db.model.role_model import RoleModel
from app.infrastructure.db.model.role_permission_model import RolePermissionModel
from app.infrastructure.db.model.user_model import UserModel
from app.infrastructure.db.model.user_role_model import UserRoleModel
from app.infrastructure.security import SecurityService

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [v for v in vars(P).values() if isinstance(v, str) and "." in v],
    "manager": [
        P.PRODUCTS_READ, P.PRODUCTS_CREATE, P.PRODUCTS_UPDATE,
        P.ORDERS_READ_OWN, P.ORDERS_READ_ALL,
        P.ORDERS_UPDATE_OWN, P.ORDERS_UPDATE_ALL,
    ],
    "user": [
        P.USERS_READ,
        P.PRODUCTS_READ,
        P.ORDERS_READ_OWN,
        P.ORDERS_UPDATE_OWN,
    ],
}

PERMISSION_DESCRIPTIONS: dict[str, str] = {
    P.USERS_READ:        "Read users",
    P.USERS_CREATE:      "Create users",
    P.USERS_UPDATE:      "Update users",
    P.USERS_DELETE:      "Delete users",
    P.ROLES_READ:        "Read roles",
    P.ROLES_ASSIGN:      "Assign roles to users",
    P.PRODUCTS_READ:     "Read products",
    P.PRODUCTS_CREATE:   "Create products",
    P.PRODUCTS_UPDATE:   "Update products",
    P.PRODUCTS_DELETE:   "Delete products",
    P.ORDERS_READ_OWN:   "Read own orders",
    P.ORDERS_READ_ALL:   "Read all orders",
    P.ORDERS_UPDATE_OWN: "Update own orders",
    P.ORDERS_UPDATE_ALL: "Update all orders",
}


def _make_session() -> async_sessionmaker[AsyncSession]:
    config = setup_config()
    engine = create_async_engine(config.postgres.get_url())
    return async_sessionmaker(engine, expire_on_commit=False)


async def _get_or_create_permission(session: AsyncSession, code: str) -> PermissionModel:
    obj = await session.scalar(select(PermissionModel).where(PermissionModel.code == code))
    if obj:
        return obj
    obj = PermissionModel(code=code, description=PERMISSION_DESCRIPTIONS.get(code, ""))
    session.add(obj)
    await session.flush()
    return obj


async def _get_or_create_role(session: AsyncSession, name: str) -> RoleModel:
    obj = await session.scalar(select(RoleModel).where(RoleModel.name == name))
    if obj:
        return obj
    obj = RoleModel(name=name, description=name.capitalize())
    session.add(obj)
    await session.flush()
    return obj


async def seed_rbac() -> None:
    session_factory = _make_session()
    async with session_factory() as session:
        perm_objects: dict[str, PermissionModel] = {}
        all_codes = set(v for v in vars(P).values() if isinstance(v, str) and "." in v)
        for code in all_codes:
            perm_objects[code] = await _get_or_create_permission(session, code)

        for role_name, perm_codes in ROLE_PERMISSIONS.items():
            role = await _get_or_create_role(session, role_name)
            for code in perm_codes:
                if code not in perm_objects:
                    continue
                await session.execute(
                    insert(RolePermissionModel)
                    .values(role_id=role.id, permission_id=perm_objects[code].id)
                    .on_conflict_do_nothing()
                )

        await session.commit()
    print("✓ Roles and permissions seeded")


async def create_admin(email: str, password: str) -> None:
    config = setup_config()
    security = SecurityService(config.auth)
    session_factory = _make_session()

    async with session_factory() as session:
        existing = await session.scalar(select(UserModel).where(UserModel.email == email))
        if existing:
            user = existing
            print(f"  User '{email}' already exists — assigning admin role")
        else:
            user = UserModel(email=email, password=security.hash_password(password))
            session.add(user)
            await session.flush()
            print(f"  Created user '{email}'")

        admin_role = await session.scalar(select(RoleModel).where(RoleModel.name == "admin"))
        if admin_role is None:
            print("  ERROR: run seed first (roles not found)")
            return

        await session.execute(
            insert(UserRoleModel)
            .values(user_id=user.id, role_id=admin_role.id)
            .on_conflict_do_nothing()
        )
        await session.commit()
    print(f"✓ Admin '{email}' ready — login to activate permissions")


def _prompt(label: str, secret: bool = False) -> str:
    import getpass
    return getpass.getpass(f"{label}: ") if secret else input(f"{label}: ")


async def main() -> None:
    want_admin = "--admin" in sys.argv

    await seed_rbac()

    if want_admin:
        email = os.getenv("ADMIN_EMAIL") or _prompt("Admin email")
        password = os.getenv("ADMIN_PASSWORD") or _prompt("Admin password", secret=True)
        await create_admin(email, password)


if __name__ == "__main__":
    asyncio.run(main())
