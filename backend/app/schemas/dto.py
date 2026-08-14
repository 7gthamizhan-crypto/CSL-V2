from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Importer DTOs
class ImporterBase(BaseModel):
    importer_code: str
    importer_name: str
    address: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = "Active"

class ImporterCreate(ImporterBase):
    pass

class ImporterResponse(ImporterBase):
    importer_id: int
    class Config:
        from_attributes = True

# Clearing Agent DTOs
class ClearingAgentBase(BaseModel):
    agent_code: str
    agent_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = "Active"

class ClearingAgentCreate(ClearingAgentBase):
    pass

class ClearingAgentResponse(ClearingAgentBase):
    agent_id: int
    class Config:
        from_attributes = True

# Risk Assessment DTOs
class RiskAssessmentResponse(BaseModel):
    risk_id: int
    container_id: int
    risk_score: int
    risk_level: str
    previous_offences: int
    country_score: int
    hs_score: int
    value_score: int
    final_score: int
    class Config:
        from_attributes = True

# Readiness Validation DTOs
class ReadinessValidationResponse(BaseModel):
    validation_id: int
    container_id: int
    payment_completed: bool
    documents_available: bool
    permit_available: bool
    container_arrived: bool
    ready_for_schedule: bool
    anomaly_review_status: Optional[str] = "Passed"
    hs_review_status: Optional[str] = "Passed"
    readiness_status: Optional[str] = "Ready"
    readiness_reason: Optional[str] = None
    class Config:
        from_attributes = True

# Container DTOs
class ContainerBase(BaseModel):
    container_number: str
    cusdec_number: str
    country_of_origin: str
    hs_code: str
    goods_description: Optional[str] = None
    cif_value: float
    duty_amount: float
    examination_type: Optional[str] = "Standard"

class ContainerCreate(ContainerBase):
    importer_id: Optional[int] = None
    agent_id: Optional[int] = None

class ContainerResponse(ContainerBase):
    container_id: int
    importer_id: Optional[int] = None
    agent_id: Optional[int] = None
    arrival_date: datetime
    status: str
    risk_assessment: Optional[RiskAssessmentResponse] = None
    readiness_validation: Optional[ReadinessValidationResponse] = None
    class Config:
        from_attributes = True

# Officer DTOs
class OfficerBase(BaseModel):
    officer_code: str
    officer_name: str
    designation: Optional[str] = "Customs Officer"
    qualification: Optional[str] = "General"
    daily_capacity: Optional[int] = 6
    availability: Optional[bool] = True

class OfficerCreate(OfficerBase):
    pass

class OfficerResponse(OfficerBase):
    officer_id: int
    class Config:
        from_attributes = True

# Bay DTOs
class BayBase(BaseModel):
    bay_name: str
    bay_type: Optional[str] = "Standard"
    capacity: Optional[int] = 1
    status: Optional[str] = "Available"

class BayCreate(BayBase):
    pass

class BayResponse(BayBase):
    bay_id: int
    class Config:
        from_attributes = True

# Scanner DTOs
class ScannerBase(BaseModel):
    scanner_name: str
    location: Optional[str] = None
    capacity: Optional[int] = 20
    availability: Optional[bool] = True

class ScannerCreate(ScannerBase):
    pass

class ScannerResponse(ScannerBase):
    scanner_id: int
    class Config:
        from_attributes = True

# Schedule DTOs
class ScheduleResponse(BaseModel):
    schedule_id: int
    container_id: int
    officer_id: int
    bay_id: int
    scanner_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    status: str
    explanation: Optional[str] = None
    container: Optional[ContainerResponse] = None
    officer: Optional[OfficerResponse] = None
    bay: Optional[BayResponse] = None
    scanner: Optional[ScannerResponse] = None
    class Config:
        from_attributes = True

# Report & Settings DTOs
class ReportResponse(BaseModel):
    report_id: int
    report_name: str
    report_type: str
    generated_date: datetime
    generated_by: str
    file_location: Optional[str] = None
    class Config:
        from_attributes = True

class SettingResponse(BaseModel):
    setting_id: int
    setting_name: str
    setting_value: str
    description: Optional[str] = None
    class Config:
        from_attributes = True

class SettingUpdate(BaseModel):
    setting_value: str
