from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class RiskRatingTypes(str, Enum):
    INHERENT = "inherent"
    RESIDUAL = "residual"


class NewRiskRating(BaseModel):
    impact: int
    likelihood: int
    type: RiskRatingTypes

class UpdateInherentRiskRating(BaseModel):
    inherent_impact: int
    inherent_likelihood: int


class UpdateResidualRiskRating(BaseModel):
    residual_impact: int
    residual_likelihood: int




class CreateRiskRating(BaseModel):
    risk_rating_id: str
    risk_id: str
    inherent_impact: int
    inherent_likelihood: int
    created_at: datetime = datetime.now()


class ReadRiskRating(BaseModel):
    risk_rating_id: str
    risk_id: str
    inherent_impact: int
    inherent_likelihood: int
    inherent_impact: int
    inherent_likelihood: int
    created_at: datetime