from datetime import datetime

from psycopg import AsyncConnection

from core.constants import Tables, RiskRatingsColumns
from core.utils import from_enum, exception_response, get_unique_key
from schemas.risk_ratings_schemas import ReadRiskRating, CreateRiskRating, UpdateResidualRiskRating
from schemas.risk_schemas import NewRisk
from services.databases.postgres.insert import InsertQueryBuilder
from services.databases.postgres.read import ReadBuilder
from services.databases.postgres.update import UpdateQueryBuilder


async def get_risk_ratings(connection: AsyncConnection, risk_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.RISK_RATINGS))
            .where(from_enum(RiskRatingsColumns.RISK_ID), risk_id)
            .fetch_all()
        )
        return [ReadRiskRating(**data) for data in builder]

async def initialize_risk_rating(connection: AsyncConnection, risk: NewRisk, risk_id: str):
    __risk_ratings__ = CreateRiskRating(
        risk_rating_id=get_unique_key(),
        risk_id=risk_id,
        inherent_impact=risk.impact,
        inherent_likelihood=risk.likelihood,
        created_at=datetime.now()
    )

    builder = (
        InsertQueryBuilder(connection=connection)
        .into_table(Tables.RISK_RATINGS)
        .values(__risk_ratings__)
        .returning(RiskRatingsColumns.RISK_ID.value)
    )

    result = await builder.execute()
    return result

async def edit_residual_risk_rating(connection: AsyncConnection, risk: UpdateResidualRiskRating, risk_id: str):
    with exception_response():
         builder = (
             UpdateQueryBuilder(connection=connection)
             .into_table(Tables.RISK_RATINGS)
             .values(risk)
             .where({RiskRatingsColumns.RISK_ID.value: risk_id})
             .check_exists({RiskRatingsColumns.RISK_ID.value: risk_id})
         )

         result = await builder.execute()
         return result

