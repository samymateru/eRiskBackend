from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RMPStatus(str, Enum):
    CURRENT = "current"
    CLOSED = "closed"
    ARCHIVED = "archived"

class NewRMP(BaseModel):
    name: str
    year: Optional[int] = None

class CreateRMP(BaseModel):
    rmp_id: str
    module_id: Optional[str]
    name: str
    year: Optional[int] = datetime.now().year
    status: Optional[RMPStatus] = RMPStatus.CURRENT
    creator: str
    approver: Optional[str] = None
    approved_at: Optional[datetime] = datetime.now()
    created_at: Optional[datetime] = datetime.now()

class ReadRMP(BaseModel):
    rmp_id: str
    module_id: Optional[str] = ""
    name: str
    year: Optional[int] = datetime.now().year
    status: Optional[RMPStatus] = RMPStatus.CURRENT
    creator: Optional[str] = ""
    approver: Optional[str] = ""
    approved_at: Optional[datetime] = datetime.now()
    created_at: Optional[datetime] = datetime.now()

class DeactivateRMP(BaseModel):
    status: RMPStatus

