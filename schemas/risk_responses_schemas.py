from pydantic import BaseModel
from datetime import datetime



class NewRiskResponse(BaseModel):
    control: str
    objective: str
    type: str
    frequency: str
    action_plan: str

class CreateRiskResponse(BaseModel):
    risk_response_id: str
    risk_id: str
    control: str
    objective: str
    type: str
    frequency: str
    action_plan: str
    created_at: datetime = datetime.now()

class ReadRiskResponse(BaseModel):
    risk_response_id: str
    risk_id: str
    control: str
    objective: str
    type: str
    frequency: str
    action_plan: str
    created_at: datetime