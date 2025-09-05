from fastapi import APIRouter, Depends, Query, Form
from __schemas__ import CreateResponse
from core.utils import exception_response
from models.activity_reports_models import add_new_activity_report, get_activity_reports, get_activity_report
from schemas.activity_reports_schemas import NewActivityReport
from services.databases.postgres.connections import AsyncDBPoolSingleton

router = APIRouter(prefix="/activity_reports")

@router.post("/{activity_id}", status_code=201, response_model=CreateResponse)
async def create_new_activity_reports(
        activity_id: str,
        description: str = Form(...),
        conclusion: str = Form(...),
        user_id: str = Query(...),
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():

        report = NewActivityReport(
            description=description,
            conclusion=conclusion
        )

        await add_new_activity_report(
            connection=connection,
            report=report,
            activity_id=activity_id,
            user_id=user_id
        )
        return CreateResponse(detail="Report Submitted Successfully")


@router.get("/{activity_id}")
async def fetch_activity_reports(
        activity_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_activity_reports(connection=connection, activity_id=activity_id)
        return data


@router.get("/report/{activity_report_id}")
async def fetch_activity_report(
        activity_report_id: str,
        connection = Depends(AsyncDBPoolSingleton.get_db_connection),
        #user: CurrentUser  = Depends(get_current_user),
):
    with exception_response():
        data = await get_activity_report(connection=connection, activity_report_id=activity_report_id)
        return data
