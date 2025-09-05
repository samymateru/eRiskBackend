from fastapi import APIRouter, Depends, Query

from __schemas__ import CreateResponse
from core.utils import exception_response
from models.rmp_models import add_new_rmp, get_current_rmp, get_all_rmp
from schemas.rmp_schemas import NewRMP
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/rmp")

@router.post("/{module_id}", status_code=201, response_model=CreateResponse)
async def create_new_rmp(
        module_id: str,
        rmp: NewRMP,
        user_id: str = Query(...),
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        await add_new_rmp(connection=connection, rmp=rmp, module_id=module_id, user_id=user_id)
        return CreateResponse(detail="Successfully create RMP")

@router.get("/current/{module_id}")
async def fetch_current_module_rmp(
        module_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_current_rmp(connection=connection, module_id=module_id)
        return data



@router.get("/{module_id}")
async def fetch_all_module_rmp(
        module_id: str,
        connection=Depends(AsyncDBPoolSingleton.get_db_connection),
        # user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_all_rmp(connection=connection, module_id=module_id)
        return data

