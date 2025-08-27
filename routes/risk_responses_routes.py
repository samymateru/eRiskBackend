from fastapi import APIRouter, Depends
from core.constants import Tables, RiskResponsesColumns, RisksColumns
from core.utils import exception_response, get_unique_key
from models.risk_response_models import get_risk_responses
from schemas.risk_responses_schemas import NewRiskResponse, CreateRiskResponse
from services.databases.postgres.connections import AsyncDBPoolSingleton
from services.databases.postgres.insert import InsertQueryBuilder

router = APIRouter(prefix="/risk_responses")
@router.post("/{risk_id}")
async def create_risk_response(
        risk_id: str,
        response: NewRiskResponse,
        conn = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        __risk_response__ = CreateRiskResponse(
            risk_response_id=get_unique_key(),
            risk_id=risk_id,
            control=response.control,
            objective=response.objective,
            type=response.type,
            frequency=response.frequency,
            action_plan=response.action_plan,
        )
        builder = (
            InsertQueryBuilder(connection=conn)
            .into_table(Tables.RISK_RESPONSES)
            .values(__risk_response__)
            .check_exists({RiskResponsesColumns.CONTROL.value: __risk_response__.control})
            .returning(RiskResponsesColumns.CONTROL.value)
        )
        result = await builder.execute()
        return result

@router.get("/{risk_id}")
async def fetch_risk_responses(
        risk_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        responses = await get_risk_responses(connection=connection, risk_id=risk_id)
        return responses
