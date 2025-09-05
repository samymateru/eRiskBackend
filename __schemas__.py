from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class CurrentUser(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    entity_id: Optional[str] = None
    organization_id: Optional[str] = None
    module_id: Optional[str] = None
    module_name: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None

class Frequency(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Bi weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUALLY = "Annually"
    SEMI_ANNUALLY = "Semi Annually"
    SPECIFIC_DATE = "Specific Date"

class CreateResponse(BaseModel):
    detail: str

class BaseUser(BaseModel):
    id: str
    name: str
    email: str
    image: Optional[str] = None
    telephone: Optional[str] = None
    status: Optional[str] =None
    created_at : Optional[datetime] = datetime.now()

class Creator(BaseModel):
    usr_id: str
    usr_name: str
    usr_email: str
    user_telephone: Optional[str] = None
    usr_image: Optional[str] = None
    usr_status: Optional[str] = None
