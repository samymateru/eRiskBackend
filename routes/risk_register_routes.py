from fastapi import APIRouter, Depends
from core.utils import exception_response
from models.risk_register_models import add_new_risk_register, get_current_risk_register, get_all_risk_register
from schemas.risk_register_schemas import NewRiskRegister
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/risk_registers")

@router.post("/{module_id}")
async def create_new_risk_register(
        module_id: str,
        register: NewRiskRegister,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        result  = await add_new_risk_register(connection=connection, register=register, module_id=module_id)
        return result

@router.get("/current/{module_id}")
async def fetch_current_risk_register(
        module_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_current_risk_register(connection=connection, module_id=module_id)
        return data


@router.get("/{module_id}")
async def fetch_all_risk_register(
        module_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_all_risk_register(connection=connection, module_id=module_id)
        return data
