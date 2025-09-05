from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class NewRiskUser(BaseModel):
    name: str
    email: str
    role: str
    type: str

class EntityUser(BaseModel):
    id: str
    entity: str
    name: str
    email: str
    telephone: Optional[str] = None
    administrator: bool
    owner: bool
    created_at: datetime
    image: Optional[str] = None

class ReadOrganizationUser(BaseModel):
    organization_id: str
    user_id: str
    administrator: bool
    owner: bool
    created_at: datetime

class ReadRiskModuleUser(BaseModel):
    module_id: str
    user_id: str
    role: str
    type: str
    created_at: datetime

class CreateEntityUser(BaseModel):
    id: str
    entity: str
    name: str
    email: str
    password_hash: str
    status: str
    telephone: Optional[str] = None
    administrator: bool
    owner: bool
    created_at: Optional[datetime] = datetime.now()
    image: Optional[str] = None


class CreateOrganizationUser(BaseModel):
    organization_id: str
    user_id: str
    administrator: bool
    owner: bool
    created_at: datetime


class CreateModuleUser(BaseModel):
    risk_user_id: str
    module_id: str
    user_id: str
    role: str
    type: str
    created_at: datetime


class ReadUser(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    type: str
    status: Optional[str] = None
    telephone: Optional[str] = None
    image: Optional[str] = None
    created_at: Optional[datetime] = datetime.now()
