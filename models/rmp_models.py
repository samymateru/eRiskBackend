from psycopg import AsyncConnection
from core.constants import RMPColumns, Tables
from core.utils import exception_response, get_unique_key, from_enum
from schemas.rmp_schemas import CreateRMP, ReadRMP, DeactivateRMP, RMPStatus, NewRMP
from services.databases.postgres.insert import InsertQueryBuilder
from services.databases.postgres.read import ReadBuilder
from services.databases.postgres.update import UpdateQueryBuilder


async def add_new_rmp(connection: AsyncConnection, rmp: NewRMP, module_id: str):
    with exception_response():
        __register__ = CreateRMP(
            rmp_id=get_unique_key(),
            module_id=module_id,
            name=rmp.name,
            status=RMPStatus.CURRENT
        )
        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.RMP.value)
            .values(__register__)
            .returning(RMPColumns.NAME.value, RMPColumns.RMP_ID.value)
        )

        return await builder.execute()


async def get_all_rmp(connection: AsyncConnection, module_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RMP))
            .where(from_enum(RMPColumns.MODULE_ID), module_id)
            .fetch_all()
        )
        return [ReadRMP(**data) for data in builder]


async def get_current_rmp(connection: AsyncConnection, module_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RMP))
            .where(from_enum(RMPColumns.MODULE_ID), module_id)
            .where(from_enum(RMPColumns.STATUS), RMPStatus.CURRENT)
            .fetch_one()
        )
        if builder is not None:
            return ReadRMP(**builder)
        else:
            return builder


async def get_single_rmp(connection: AsyncConnection, rmp_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RMP))
            .where(from_enum(RMPColumns.RMP_ID), rmp_id)
            .fetch_one()
        )
        if builder is not None:
            return ReadRMP(**builder)
        else:
            return builder


async def deactivate_rmp(connection: AsyncConnection, rmp_id: str):
    with exception_response():
        __rmp__ = DeactivateRMP(
            status=RMPStatus.CLOSED
        )
        builder = (
            UpdateQueryBuilder(connection=connection)
            .into_table(from_enum(Tables.RMP))
            .values(__rmp__)
            .where({RMPColumns.RMP_ID.value: rmp_id})
            .check_exists({RMPColumns.RMP_ID.value: rmp_id})
            .returning(RMPColumns.RMP_ID.value)
        )

        return await builder.execute()



