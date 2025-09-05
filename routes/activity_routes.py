from fastapi import APIRouter, Depends, HTTPException, Query
from __schemas__ import CreateResponse
from core.utils import exception_response
from models.activity_models import add_new_activity, get_current_activities, get_single_activity, add_activity_owners
from models.rmp_models import get_current_rmp
from schemas.activity_schemas import NewActivity, NewActivityOwner
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/activities")

@router.post("/{module_id}", status_code=201, response_model=CreateResponse)
async def create_new_activity(
        module_id: str,
        activity: NewActivity,
        user_id: str = Query(...),
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
        await add_new_activity(
            connection=connection,
            activity=activity,
            rmp_id=current_rmp.rmp_id,
            user_id=user_id
        )
        return CreateResponse(detail="Successfully create activity")

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

@router.get("/activity/{activity_id}")
async def fetch_single_rmp_activities(
        activity_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_single_activity(connection=connection, activity_id=activity_id)
        return data

@router.post("/owners/{activity_id}", status_code=201, response_model=CreateResponse)
async def assign_activity_owners(
        activity_id: str,
        owners: NewActivityOwner,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        await add_activity_owners(connection=connection, owners=owners, activity_id=activity_id)
        return CreateResponse(detail="Activity Owners Added Successfully")