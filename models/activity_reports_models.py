from psycopg import AsyncConnection
from __schemas__ import BaseUser, Creator
from core.constants import Tables, ActivityReportsColumns
from core.utils import exception_response, get_unique_key
from schemas.activity_reports_schemas import NewActivityReport, CreateActivityReport, ReadActivityReport, \
    JoinReadActivityReport
from services.databases.postgres.insert import InsertQueryBuilder
from datetime import datetime
from services.databases.postgres.read import ReadBuilder


async def add_new_activity_report(connection: AsyncConnection, report: NewActivityReport, activity_id: str, user_id: str):
    with exception_response():
        __activity_report_ = CreateActivityReport(
            activity_report_id=get_unique_key(),
            activity_id=activity_id,
            description=report.description,
            conclusion=report.conclusion,
            attachment=report.attachment,
            created_by=user_id,
            created_at=datetime.now()
        )
        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.ACTIVITY_REPORTS.value)
            .values(__activity_report_)
            .returning(
            ActivityReportsColumns.ACTIVITY_ID.value, ActivityReportsColumns.ACTIVITY_REPORT_ID.value
            )
        )
        return await builder.execute()

async def get_activity_reports(connection: AsyncConnection, activity_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(Tables.ACTIVITY_REPORTS.value, alias="act_rep")
            .select(ReadActivityReport)
            .join(
                "LEFT",Tables.USERS.value,
                "usr.id = act_rep.created_by",
                alias="usr",
                model=BaseUser,
                use_prefix=True
            )
            .select_joins()
            .where("act_rep."+ActivityReportsColumns.ACTIVITY_ID.value, activity_id)
            .fetch_all()
        )

        results = []
        for data in builder:
            creator = Creator(
                usr_name=data.get("usr_name"),
                usr_email=data.get("usr_email"),
                usr_image=data.get("usr_image"),
                usr_status=data.get("usr_status"),
                usr_id=data.get("usr_id")
            )
            clean_data = {k: v for k, v in data.items() if not k.startswith("usr_")}
            clean_data["creator"] = creator
            results.append(JoinReadActivityReport(**clean_data))
        return results

async def get_activity_report(connection: AsyncConnection, activity_report_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(Tables.ACTIVITY_REPORTS.value)
            .join(
                "LEFT", Tables.USERS.value,
                "usr.id = act_rep.created_by",
                alias="usr",
                model=BaseUser,
                use_prefix=True
            )
            .where(ActivityReportsColumns.ACTIVITY_REPORT_ID.value, activity_report_id)
            .fetch_one()
        )
        if builder is None:
            return builder
        return JoinReadActivityReport(**builder)
