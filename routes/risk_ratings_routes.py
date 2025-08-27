from fastapi import APIRouter, Depends
from core.utils import exception_response
from models.risk_rating_models import get_risk_ratings, edit_residual_risk_rating
from schemas.risk_ratings_schemas import NewRiskRating, UpdateResidualRiskRating
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/risk_ratings")
@router.post("/{risk_id}")
async def create_risk_rating(
        risk_id: str,
        rating: NewRiskRating,
        conn = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        pass


@router.get("/{risk_id}")
async def fetch_risk_rating(
        risk_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        rating = await get_risk_ratings(connection=connection, risk_id=risk_id)
        return rating


@router.put("/residual/{risk_id}")
async def update_residual_risk_rating(
        risk_id: str,
        risk: UpdateResidualRiskRating,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        result = await edit_residual_risk_rating(connection=connection, risk=risk, risk_id=risk_id)
        return result