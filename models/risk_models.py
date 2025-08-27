from datetime import datetime
from typing import Optional
from psycopg import AsyncConnection
from pydantic import BaseModel
from core.constants import Tables, RisksColumns
from core.utils import from_enum, exception_response, get_unique_key
from schemas.risk_schemas import ReadRisk, CreateRisk, NewRisk, RiskRatingJoin, JoinRisk
from services.databases.postgres.insert import InsertQueryBuilder
from services.databases.postgres.read import ReadBuilder


async def get_all_risk_in_register():
    pass

class BusinessProcess(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

async def get_general_risk_details(connection: AsyncConnection, risk_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table("risks", alias="risk")
            .select(ReadRisk)
            .join(
                "LEFT",
                from_enum(Tables.RISK_RATINGS),
                "rt.risk_id = risk.risk_id",
                alias="rt",
                model=RiskRatingJoin,
                use_prefix=False)
            .join(
                "LEFT",
                "business_process",
                "process.id = risk.process",
                alias="process",
                model=BusinessProcess)
            .select_joins()
            .where("risk.risk_id", risk_id)
            .fetch_one()
        )
        print(builder)
        return JoinRisk(**builder)



async def get_all_risk_approved(connection: AsyncConnection, risk_register_id: str):
    with exception_response():
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISKS), alias="risk")
            .join("LEFT", from_enum(Tables.RISK_RATINGS), "risk_rating.risk_id = risk.risk_id", alias="risk_rating")
            .where("risk"+"."+from_enum(RisksColumns.RISK_REGISTER_ID), risk_register_id)
            .fetch_all()
        )
        print(builder)
        return [ReadRisk(**data) for data in builder]


async def add_new_risk(connection: AsyncConnection, risk: NewRisk, risk_register_id: str):
    __risk__ = CreateRisk(
        risk_id=get_unique_key(),
        name=risk.name,
        process=risk.process,
        sub_process=risk.sub_process,
        description=risk.description,
        department=risk.department,
        category=risk.category,
        creator=None,
        created_at=datetime.now(),
        year=datetime.now().year,
        register_id=risk_register_id
    )

    builder = (
        InsertQueryBuilder(connection=connection)
        .into_table(Tables.RISKS)
        .values(__risk__)
        .check_exists({RisksColumns.NAME.value: __risk__.name})
        .returning(RisksColumns.NAME, RisksColumns.RISK_ID)
    )

    return await builder.execute()
