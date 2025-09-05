from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from schemas.activity_schemas import Creator


class NewActivityReport(BaseModel):
    description: str
    conclusion: str
    attachment: Optional[str] = None

class CreateActivityReport(BaseModel):
    activity_report_id: str
    activity_id: str
    description: str
    conclusion: str
    attachment: Optional[str]
    created_by: str
    created_at: datetime

class ReadActivityReport(BaseModel):
    activity_report_id: str
    activity_id: str
    description: str
    conclusion: str
    attachment: Optional[str]
    created_at: datetime

class JoinReadActivityReport(ReadActivityReport):
    creator: Creator
