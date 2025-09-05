from fastapi import APIRouter, Depends, Query, HTTPException

from __schemas__ import CreateResponse
from core.utils import exception_response
from models.user_models import get_entity_user, add_new_entity_user, add_new_organization_user, get_organization_users, \
    add_new_module_user, get_module_users, get_users, get_user
from schemas.users_schemas import NewRiskUser
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/risk_users")

@router.post("/{module_id}", status_code=201, response_model=CreateResponse)
async def create_new_risk_user(
        module_id: str,
        user: NewRiskUser,
        entity_id: str = Query(...),
        organization_id: str = Query(...),
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        entity_user = await get_entity_user(connection=connection, email=user.email)

        if entity_user is None:
            _user_ = await add_new_entity_user(connection=connection, user=user, entity=entity_id)

            await add_new_organization_user(
                connection=connection,
                user_id=_user_.get("id"),
                organization_id=organization_id
            )

            await add_new_module_user(
                connection=connection,
                user=user,
                module_id=module_id,
                user_id=_user_.get("id")
            )

            return CreateResponse(detail="Successfully create user")

        organization_user = await get_organization_users(
            connection=connection,
            user_id=entity_user.id,
            organization_id=organization_id
        )

        module_user = await get_module_users(
            connection=connection,
            user_id=entity_user.id,
            module_id=module_id
        )

        if organization_user.__len__() == 0:
            await add_new_organization_user(
                connection=connection,
                user_id=entity_user.id,
                organization_id=organization_id
            )
        if module_user.__len__() == 0:
            await add_new_module_user(
                connection=connection,
                user=user,
                module_id=module_id,
                user_id=entity_user.id
            )

            return CreateResponse(detail="Successfully create user")
        else:
            raise HTTPException(status_code=400, detail="User Already exists")


@router.get("/{module_id}")
async def fetch_risk_users(
        module_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_users(connection=connection, module_id=module_id)
        return data

@router.get("/user/{module_id}")
async def fetch_risk_user(
        module_id: str,
        user_id: str = Query(...),
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_user(connection=connection, module_id=module_id, user_id=user_id)
        return data