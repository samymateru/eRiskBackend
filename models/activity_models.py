from psycopg import AsyncConnection
from __schemas__ import BaseUser, Creator
from core.constants import Tables, ActivitiesColumns, ActivityOwnerColumns
from core.utils import exception_response, get_unique_key, from_enum
from schemas.activity_schemas import NewActivity, CreateActivity, ReadActivity, JoinReadActivity, NewActivityOwner, \
    CreateActivityOwner
from services.databases.postgres.insert import InsertQueryBuilder
from services.databases.postgres.read import ReadBuilder
from datetime import datetime


async def add_new_activity(connection: AsyncConnection, activity: NewActivity, rmp_id: str, user_id: str):
    with exception_response():

        __activity__ = CreateActivity(
            activity_id=get_unique_key(),
            rmp_id=rmp_id,
            title=activity.title,
            type=activity.type,
            frequency=activity.frequency,
            category=activity.category,
            leads="",
            creator=user_id
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
        builder =  await (
            ReadBuilder(connection=connection)
            .from_table(Tables.ACTIVITIES.value, alias="act")
            .select(ReadActivity)
            .join(
                "LEFT",
                Tables.USERS.value,
                "usr.id = act.creator",
                alias="usr",
                model=BaseUser,
                use_prefix=True
            )
            .select_joins()
            .where("act."+from_enum(ActivitiesColumns.RMP_ID), rmp_id)
            .fetch_all()

        )
        results = []
        for data in builder:
            user = Creator(
                usr_name=data.get("usr_name"),
                usr_email=data.get("usr_email"),
                usr_image=data.get("usr_image"),
                usr_status=data.get("usr_status"),
                usr_id=data.get("usr_id")
            )
            clean_data = {k: v for k, v in data.items() if not k.startswith("usr_")}

            clean_data["user"] = user
            results.append(JoinReadActivity(**clean_data))

        return results


async def get_single_activity(connection: AsyncConnection, activity_id: str):
    with exception_response():
        builder = await (
            ReadBuilder(connection=connection)
            .from_table(Tables.ACTIVITIES.value)
            .where(from_enum(ActivitiesColumns.ACTIVITY_ID), activity_id)
            .fetch_one()
        )
        if builder is not None:
            return ReadActivity(**builder)
        else:
            return builder


async def add_activity_owners(connection: AsyncConnection, owners: NewActivityOwner, activity_id: str):
    with exception_response():
        for owner in owners.owners:
            __owner__ = CreateActivityOwner(
                activity_owner_id=get_unique_key(),
                activity_id=activity_id,
                date_assigned=datetime.now(),
                user_id=owner
            )
            builder = (
                InsertQueryBuilder(connection=connection)
                .into_table(Tables.ACTIVITY_OWNERS.value)
                .values(__owner__)
                .returning(ActivityOwnerColumns.ACTIVITY_ID.value)
            )
            return await builder.execute()
