from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NewRisk(BaseModel):
    name: str
    process: str
    sub_process: str
    description: Optional[str] = None
    impact: int
    likelihood: int
    department: str
    category: str
    owners: Optional[List[str]] = None

class NewRiskOwner(BaseModel):
    owners: List[str]

class CreateRisk(BaseModel):
    risk_id: str
    register_id: str
    name: str
    process: str
    sub_process: str
    description: Optional[str] = None
    department: str
    category: str
    created_at: datetime
    creator: Optional[str] = None
    year: int

class CreateRiskOwner(BaseModel):
    risk_owner_id: str
    user_id: str
    risk_id: str
    date_assigned: datetime

class ReadRisk(BaseModel):
    risk_id: str
    register_id: str
    name: str
    process: str
    sub_process: str
    description: Optional[str] = None
    department: str
    category: str
    created_at: datetime
    creator: Optional[str] = None
    year: int

class RiskRatingJoin(BaseModel):
    inherent_impact: Optional[int] = None
    inherent_likelihood: Optional[int] = None
    residual_impact: Optional[int] = None
    residual_likelihood: Optional[int] = None

class JoinRisk(BaseModel):
    risk_id: str
    name: str
    process: str
    sub_process: str
    description: Optional[str] = None
    department: str
    category: str
    created_at: datetime
    creator: Optional[str] = None
    register_id: str
    year: int
    inherent_impact: Optional[int] = None
    inherent_likelihood: Optional[int] = None
    residual_impact: Optional[int] = None
    residual_likelihood: Optional[int] = None
    process_name: Optional[str] = None

