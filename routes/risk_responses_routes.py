from fastapi import APIRouter, Depends, HTTPException

from __schemas__ import CreateResponse
from core.constants import Tables, RiskResponsesColumns
from core.utils import exception_response, get_unique_key
from models.risk_register_models import get_current_risk_register
from models.risk_response_models import get_risk_responses, get_all_risk_responses
from schemas.risk_responses_schemas import NewRiskResponse, CreateRiskResponse
from services.databases.postgres.connections import AsyncDBPoolSingleton
from services.databases.postgres.insert import InsertQueryBuilder

router = APIRouter(prefix="/risk_responses")
@router.post("/{risk_id}", status_code=201, response_model=CreateResponse)
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
        await builder.execute()
        return CreateResponse(detail="Successfully create Response")

@router.get("/{risk_id}")
async def fetch_risk_risk_responses(
        risk_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        responses = await get_risk_responses(connection=connection, risk_id=risk_id)
        return responses

@router.get("/all/{module_id}")
async def fetch_all_risk_responses(
        module_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        current_risk_register = await get_current_risk_register(
            connection=connection,
            module_id=module_id
        )

        if current_risk_register is None:
            raise HTTPException(status_code=400, detail="Risk Register Not Found")

        responses = await get_all_risk_responses(
            connection=connection,
            register_id=current_risk_register.risk_register_id
        )
        return responses