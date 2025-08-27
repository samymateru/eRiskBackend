from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from __schemas__ import Frequency


class ActivityStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class NewActivity(BaseModel):
    title: str
    type: str
    category: str
    frequency: Frequency

class CreateActivity(BaseModel):
    activity_id: str
    rmp_id: str
    title: str
    type: str
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    leads: str
    category: str
    frequency: Frequency
    creator: str
    next_at: datetime = datetime.now()
    created_at: datetime = datetime.now()

class ReadActivity(BaseModel):
    activity_id: str
    rmp_id: str
    title: str
    type: str
    status: ActivityStatus
    leads: str
    category: str
    frequency: Frequency
    creator: str
    next_at: datetime
    created_at: datetime