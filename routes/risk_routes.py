from fastapi import APIRouter, Depends, HTTPException
from core.constants import RisksColumns
from core.utils import  exception_response
from models.risk_models import get_general_risk_details, get_all_risk_approved, add_new_risk
from models.risk_rating_models import initialize_risk_rating
from models.risk_register_models import get_current_risk_register
from schemas.risk_schemas import NewRisk
from services.databases.postgres.connections import AsyncDBPoolSingleton


router = APIRouter(prefix="/risks")

@router.get("/{module_id}")
async def fetch_risks(
        module_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        current_risk_register = await get_current_risk_register(connection=connection, module_id=module_id)
        if current_risk_register is None:
            return []
        risks = await get_all_risk_approved(connection=connection, risk_register_id=current_risk_register.risk_register_id)
        return risks


@router.get("/risk/{risk_id}")
async def fetch_risk_details(
        risk_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        risk = await get_general_risk_details(connection=connection, risk_id=risk_id)
        return risk


@router.post("/{module_id}")
async def create_risk(
        module_id: str,
        risk: NewRisk,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        current_risk_register = await get_current_risk_register(
            connection=connection,
            module_id=module_id
        )

        if current_risk_register is None:
            raise HTTPException(status_code=400, detail="Register Not Found")

        result = await add_new_risk(
            connection=connection,
            risk=risk,
            risk_register_id=current_risk_register.risk_register_id
        )

        await initialize_risk_rating(
            connection=connection,
            risk=risk,
            risk_id=result.get(RisksColumns.RISK_ID.value)
        )

        return result



