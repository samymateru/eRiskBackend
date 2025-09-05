from fastapi import Depends, APIRouter

from __schemas__ import CreateResponse
from core.utils import exception_response
from models.kri_models import add_new_risk_kri, get_risk_kri
from schemas.risk_kri_schemas import NewRiskKRI
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/risk_kri")
@router.post("/{risk_id}", status_code=201, response_model=CreateResponse)
async def create_risk_kri(
        risk_id: str,
        kri: NewRiskKRI,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        await add_new_risk_kri(connection=connection, kri=kri, risk_id=risk_id)
        return CreateResponse(detail="Successfully create KRI")

@router.get("/{risk_id}")
async def fetch_risk_kri(
        risk_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_risk_kri(connection=connection, risk_id=risk_id)
        return data
