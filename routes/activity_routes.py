from fastapi import APIRouter, Depends, HTTPException
from core.utils import exception_response
from models.activity_models import add_new_activity, get_current_activities
from models.rmp_models import get_current_rmp
from schemas.activity_schemas import NewActivity
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/activities")

@router.post("/{module_id}")
async def create_new_activity(
        module_id: str,
        activity: NewActivity,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        current_rmp = await get_current_rmp(
            connection=connection,
            module_id=module_id
        )

        if current_rmp is None:
            raise HTTPException(status_code=400, detail="RMP Not Found")
        data = await add_new_activity(connection=connection, activity=activity, rmp_id=current_rmp.rmp_id)
        return data

@router.get("/{module_id}")
async def fetch_current_rmp_activities(
        module_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        current_rmp = await get_current_rmp(connection=connection, module_id=module_id)
        if current_rmp is None:
            return []
        data = await get_current_activities(connection=connection, rmp_id=current_rmp.rmp_id)
        return data