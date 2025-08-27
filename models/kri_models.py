from psycopg import AsyncConnection
from core.constants import Tables, RiskKRIColumns
from core.utils import get_unique_key, exception_response, from_enum
from schemas.risk_kri_schemas import NewRiskKRI, CreateRiskKRI, ReadRiskKRI
from services.databases.postgres.insert import InsertQueryBuilder
from datetime import datetime

from services.databases.postgres.read import ReadBuilder


async def add_new_risk_kri(connection: AsyncConnection, kri: NewRiskKRI, risk_id: str):
    with exception_response():
        __kri__ = CreateRiskKRI(
            risk_kri_id=get_unique_key(),
            risk_id=risk_id,
            name=kri.name,
            type=kri.type,
            frequency=kri.frequency,
            very_high=kri.very_high,
            high=kri.high,
            medium=kri.medium,
            low=kri.low,
            description=kri.description,
            next_at=datetime.now(),
            created_at=datetime.now()
        )

        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.RISK_KRI.value)
            .values(__kri__)
            .returning(RiskKRIColumns.NAME.value)
        )

        return await builder.execute()

async def get_risk_kri(connection: AsyncConnection, risk_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_KRI))
            .where(from_enum(RiskKRIColumns.RISK_ID), risk_id)
            .fetch_all()
        )
        return [ReadRiskKRI(**data) for data in builder]


