from psycopg import AsyncConnection
from core.constants import Tables, EntityUserColumns
from core.utils import exception_response, from_enum, get_unique_key
from schemas.users_schemas import EntityUser, CreateEntityUser, NewRiskUser, CreateOrganizationUser, \
    ReadOrganizationUser, ReadRiskModuleUser, CreateModuleUser, ReadUser
from services.databases.postgres.insert import InsertQueryBuilder
from services.databases.postgres.read import ReadBuilder
from datetime import datetime

from services.security.security import generate_hash_password


async def get_entity_user(connection: AsyncConnection, email: str):
    with exception_response():
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.USERS))
            .where("email", email)
            .fetch_one()
        )
        if builder is None:
            return None
        return EntityUser(**builder)

async def get_entity_users(connection: AsyncConnection, entity_id: str):
    with exception_response():
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.USERS))
            .where("entity", entity_id)
            .fetch_all()
        )
        return [EntityUser(**data) for data in builder]


async def get_organization_users(connection: AsyncConnection, user_id: str, organization_id: str):
    with exception_response():
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.ORGANIZATIONS_USERS))
            .where("user_id", user_id)
            .where("organization_id", organization_id)
            .fetch_all()
        )
        return [ReadOrganizationUser(**data) for data in builder]


async def get_module_users(connection: AsyncConnection, user_id: str, module_id: str):
    with exception_response():
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_MODULE_USERS))
            .where("user_id", user_id)
            .where("module_id", module_id)
            .fetch_all()
        )
        return [ReadRiskModuleUser(**data) for data in builder]


async def add_new_entity_user(connection: AsyncConnection, user:NewRiskUser, entity: str):
    with exception_response():
        __entity_user__ = CreateEntityUser(
            id=get_unique_key(),
            entity=entity,
            name=user.name,
            status="Active",
            password_hash=generate_hash_password("123456"),
            email=user.email,
            administrator=False,
            owner=False,
            image="https://github.com/shadcn.png"
        )
        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.USERS)
            .values(__entity_user__)
            .check_exists({"email": user.email})
            .returning(EntityUserColumns.ID)
        )

        return await builder.execute()

async def add_new_organization_user(connection: AsyncConnection, user_id: str, organization_id: str):
    with exception_response():
        __organization_user__ = CreateOrganizationUser(
            organization_id=organization_id,
            user_id=user_id,
            administrator=False,
            owner=False,
            created_at=datetime.now()
        )
        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.ORGANIZATIONS_USERS)
            .values(__organization_user__)
            .returning("user_id", "organization_id")
        )
        return await builder.execute()

async def add_new_module_user(connection: AsyncConnection, user: NewRiskUser, user_id: str, module_id: str):
    with exception_response():
        __module_user__ = CreateModuleUser(
            risk_user_id=get_unique_key(),
            module_id=module_id,
            user_id=user_id,
            role=user.role,
            type=user.type,
            created_at=datetime.now()
        )
        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.RISK_MODULE_USERS)
            .values(__module_user__)
            .returning("user_id", "module_id"))

        return await builder.execute()

async def get_users(connection: AsyncConnection, module_id: str):
    with exception_response():
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_MODULE_USERS), alias="mod_usr")
            .join("LEFT", from_enum(Tables.USERS), "mod_usr.user_id = users.id", alias="users")
            .where("mod_usr.module_id", module_id)
            .fetch_all()
        )
        return [ReadUser(**data) for data in builder]

async def get_user(connection: AsyncConnection, module_id: str, user_id: str):
    with exception_response():
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_MODULE_USERS), alias="mod_usr")
            .join("LEFT", from_enum(Tables.USERS), "mod_usr.user_id = users.id", alias="users")
            .where("mod_usr.module_id", module_id)
            .where("mod_usr.user_id", user_id)
            .fetch_one()
        )
        if builder is None:
            return builder
        return ReadUser(**builder)

