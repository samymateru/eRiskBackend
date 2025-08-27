from enum import Enum

from schemas.risk_schemas import CreateRisk


class Tables(str, Enum):
    RISKS = "risks"
    RISK_RATINGS = "risk_ratings"
    RISK_RESPONSES = "risk_responses"
    RISK_KRI = "risk_kri"
    ACTIVITIES = "activities"
    RMP = "rmp"
    RISK_REGISTERS = "risk_registers"

class RisksColumns(str, Enum):
    RISK_ID = "risk_id"
    RISK_REGISTER_ID = "register_id"
    NAME = "name"
    PROCESS = "process"
    SUB_PROCESS = "sub_process"
    DESCRIPTION = "description"
    IMPACT = "impact"
    LIKELIHOOD = "likelihood"
    DEPARTMENT = "department"
    CATEGORY = "category"
    CREATOR = "creator"
    APPROVE = "approve"
    OWNERS = "owners"
    CREATED_AT = "created_at"

class RiskRatingsColumns(str, Enum):
    RISK_RATING_ID = "risk_rating_id"
    RISK_ID = "risk_id"
    IMPACT = "impact"
    LIKELIHOOD = "likelihood"
    TYPE = "type"
    CREATED_AT = "created_at"

class RiskResponsesColumns(str, Enum):
    RISK_RESPONSE_ID = "risk_response_id"
    RISK_ID = "risk_id"
    CONTROL = "control"
    OBJECTIVE = "objective"
    TYPE = "type"
    FREQUENCY = "frequency"
    ACTION_PLAN = "action_plan"
    CREATED_AT = "created_at"

class RiskKRIColumns(str, Enum):
    RISK_KRI_ID = "risk_kri_id"
    RISK_ID = "risk_id"
    NAME = "name"
    TYPE = "type"
    DESCRIPTION = "description"
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEXT_AT = "next_at"
    CREATED_AT = "created_at"

class ActivitiesColumns(str, Enum):
    ACTIVITY_ID = "activity_id"
    RMP_ID = "rmp_id"
    TITLE = "title"
    TYPE = "type"
    CATEGORY = "category"
    FREQUENCY = "frequency"
    STATUS = "status"
    CREATOR = "creator"
    LEADS = "leads"
    NEXT_AT = "next_at"
    CREATED_AT = "created_at"

class RMPColumns(str, Enum):
    RMP_ID = "rmp_id"
    MODULE_ID = "module_id"
    NAME = "name"
    YEAR = "year"
    STATUS = "status"
    CREATOR = "creator"
    APPROVER = "approver"
    APPROVED_AT = "approved_at"
    CREATED_AT = "created_at"

class RiskRegisterColumns(str, Enum):
    RISK_REGISTER_ID = "risk_register_id"
    MODULE_ID = "module_id"
    NAME = "name"
    YEAR = "year"
    STATUS = "status"
    CREATOR = "creator"
    APPROVER = "approver"
    APPROVED_AT = "approved_at"
    CREATED_AT = "created_at"

