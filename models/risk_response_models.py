from psycopg import AsyncConnection
from core.constants import Tables, RiskResponsesColumns
from core.utils import exception_response, from_enum
from schemas.risk_responses_schemas import ReadRiskResponse
from schemas.risk_schemas import ReadRisk
from services.databases.postgres.read import ReadBuilder

async def get_risk_responses(connection: AsyncConnection, risk_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_RESPONSES))
            .where(from_enum(RiskResponsesColumns.RISK_ID), risk_id)
            .fetch_all()
        )
        return [ReadRiskResponse(**data) for data in builder]


async def get_all_risk_responses(connection: AsyncConnection, register_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table("risks", alias="risk")
            .select(ReadRisk)
            .join(
                "RIGHT",
                from_enum(Tables.RISK_RESPONSES),
                "rs.risk_id = risk.risk_id",
                alias="rs",
                model=ReadRiskResponse,
                use_prefix=False)
            .select_joins()
            .where("risk.register_id", register_id)
            .fetch_all()
        )
        return [ReadRiskResponse(**data) for data in builder]