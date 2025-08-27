from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NewRiskKRI(BaseModel):
    name: str
    type: str
    frequency: str
    description: Optional[str] = None
    very_high: Optional[str] = None
    high: Optional[str] = None
    medium: Optional[str] = None
    low: Optional[str] = None

class CreateRiskKRI(BaseModel):
    risk_kri_id: str
    risk_id: str
    name: str
    type: str
    frequency: str
    description: Optional[str] = None
    very_high: Optional[str] = None
    high: Optional[str] = None
    medium: Optional[str] = None
    low: Optional[str] = None
    next_at: datetime
    created_at: datetime

class ReadRiskKRI(BaseModel):
    risk_kri_id: str
    risk_id: str
    name: str
    type: str
    frequency: str
    description: Optional[str] = None
    very_high: Optional[str] = None
    high: Optional[str] = None
    medium: Optional[str] = None
    low: Optional[str] = None
    next_at: datetime
    created_at: datetime

