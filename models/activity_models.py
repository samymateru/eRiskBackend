from psycopg import AsyncConnection
from core.constants import Tables, ActivitiesColumns
from core.utils import exception_response, get_unique_key, from_enum
from schemas.activity_schemas import NewActivity, CreateActivity, ReadActivity
from services.databases.postgres.insert import InsertQueryBuilder
from services.databases.postgres.read import ReadBuilder


async def add_new_activity(connection: AsyncConnection, activity: NewActivity, rmp_id: str):
    with exception_response():

        __activity__ = CreateActivity(
            activity_id=get_unique_key(),
            rmp_id=rmp_id,
            title=activity.title,
            type=activity.type,
            frequency=activity.frequency,
            category=activity.category,
            leads="",
            creator=""
        )

        builder = (
            InsertQueryBuilder(connection=connection)
            .into_table(Tables.ACTIVITIES)
            .values(__activity__)
            .check_exists({ActivitiesColumns.TITLE.value: activity.title})
            .returning(ActivitiesColumns.ACTIVITY_ID.value, ActivitiesColumns.TITLE.value)
        )

        return await builder.execute()


async def get_current_activities(connection: AsyncConnection, rmp_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(from_enum(Tables.ACTIVITIES))
            .where(from_enum(ActivitiesColumns.RMP_ID), rmp_id)
            .fetch_all()
        )
        return [ReadActivity(**data) for data in builder]