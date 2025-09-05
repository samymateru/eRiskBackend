from psycopg import AsyncConnection
from core.constants import Tables, RiskRegisterColumns
from core.utils import exception_response, get_unique_key, from_enum
from schemas.risk_register_schemas import CreateRiskRegister, ReadRiskRegister, DeactivateRiskRegister, \
    RiskRegisterStatus, NewRiskRegister
from services.databases.postgres.insert import InsertQueryBuilder
from services.databases.postgres.read import ReadBuilder
from services.databases.postgres.update import UpdateQueryBuilder


async def add_new_risk_register(connection: AsyncConnection, register: NewRiskRegister, module_id: str, user_id: str):
    with exception_response():
        __register__ = CreateRiskRegister(
            risk_register_id=get_unique_key(),
            module_id=module_id,
            name=register.name,
            status=RiskRegisterStatus.CURRENT,
            creator=user_id
        )
        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.RISK_REGISTERS.value)
            .values(__register__)
            .returning(RiskRegisterColumns.NAME.value, RiskRegisterColumns.RISK_REGISTER_ID.value)
        )

        return await builder.execute()


async def get_all_risk_register(connection: AsyncConnection, module_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_REGISTERS))
            .where(from_enum(RiskRegisterColumns.MODULE_ID), module_id)
            .fetch_all()
        )
        return [ReadRiskRegister(**data) for data in builder]


async def get_current_risk_register(connection: AsyncConnection, module_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_REGISTERS))
            .where(from_enum(RiskRegisterColumns.MODULE_ID), module_id)
            .where(from_enum(RiskRegisterColumns.STATUS), RiskRegisterStatus.CURRENT)
            .fetch_one()
        )
        if builder is not None:
            return ReadRiskRegister(**builder)
        else:
            return builder

async def get_single_risk_register(connection: AsyncConnection, risk_register_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_REGISTERS))
            .where(from_enum(RiskRegisterColumns.RISK_REGISTER_ID), risk_register_id)
            .fetch_one()
        )
        if builder is not None:
            return ReadRiskRegister(**builder)
        else:
            return builder


async def deactivate_risk_register(connection: AsyncConnection, risk_register_id: str):
    with exception_response():
        __register__ = DeactivateRiskRegister(
            status=RiskRegisterStatus.CLOSED
        )
        builder = (
            UpdateQueryBuilder(connection=connection)
            .into_table(from_enum(Tables.RISK_REGISTERS))
            .values(__register__)
            .where({RiskRegisterColumns.RISK_REGISTER_ID.value: risk_register_id})
            .check_exists({RiskRegisterColumns.RISK_REGISTER_ID.value: risk_register_id})
            .returning(RiskRegisterColumns.RISK_REGISTER_ID.value)
        )

        return await builder.execute()

