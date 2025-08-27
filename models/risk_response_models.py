from psycopg import AsyncConnection
from core.constants import Tables, RiskResponsesColumns
from core.utils import exception_response, from_enum
from schemas.risk_responses_schemas import ReadRiskResponse
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