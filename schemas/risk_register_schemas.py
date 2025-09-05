from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RiskRegisterStatus(str, Enum):
    CURRENT = "current"
    CLOSED = "closed"
    ARCHIVED = "archived"

class NewRiskRegister(BaseModel):
    name: str
    year: Optional[int] = None

class CreateRiskRegister(BaseModel):
    risk_register_id: str
    module_id: Optional[str] = ""
    name: str
    year: Optional[int] = datetime.now().year
    status: Optional[RiskRegisterStatus] = RiskRegisterStatus.CURRENT
    creator: str
    approver: Optional[str] = None
    approved_at: Optional[datetime] = datetime.now()
    created_at: Optional[datetime] = datetime.now()

class ReadRiskRegister(BaseModel):
    risk_register_id: str
    module_id: Optional[str] = ""
    name: str
    year: Optional[int] = datetime.now().year
    status: Optional[RiskRegisterStatus] = RiskRegisterStatus.CURRENT
    creator: Optional[str] = ""
    approver: Optional[str] = ""
    approved_at: Optional[datetime] = datetime.now()
    created_at: Optional[datetime] = datetime.now()

class DeactivateRiskRegister(BaseModel):
    status: str

