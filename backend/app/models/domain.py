from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Importer(Base):
    __tablename__ = "importers"

    importer_id = Column(Integer, primary_key=True, index=True)
    importer_code = Column(String, unique=True, index=True, nullable=False)
    importer_name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, default="Active")

    containers = relationship("Container", back_populates="importer")

class ClearingAgent(Base):
    __tablename__ = "clearing_agents"

    agent_id = Column(Integer, primary_key=True, index=True)
    agent_code = Column(String, unique=True, index=True, nullable=False)
    agent_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, default="Active")

    containers = relationship("Container", back_populates="agent")

class Container(Base):
    __tablename__ = "containers"

    container_id = Column(Integer, primary_key=True, index=True)
    container_number = Column(String, unique=True, index=True, nullable=False)
    cusdec_number = Column(String, unique=True, index=True, nullable=False)
    importer_id = Column(Integer, ForeignKey("importers.importer_id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("clearing_agents.agent_id"), nullable=True)
    country_of_origin = Column(String, nullable=False)
    hs_code = Column(String, nullable=False)
    goods_description = Column(Text, nullable=True)
    cif_value = Column(Float, nullable=False)
    duty_amount = Column(Float, nullable=False)
    examination_type = Column(String, default="Standard")  # Scanner, Standard, High Risk, Hazardous, Complex
    arrival_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Pending")  # Pending, Ready, Scheduled, Completed

    importer = relationship("Importer", back_populates="containers")
    agent = relationship("ClearingAgent", back_populates="containers")
    risk_assessment = relationship("RiskAssessment", back_populates="container", uselist=False, cascade="all, delete-orphan")
    readiness_validation = relationship("ReadinessValidation", back_populates="container", uselist=False, cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="container", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="container", cascade="all, delete-orphan")
    anomaly_alerts = relationship("AnomalyAlert", back_populates="container", cascade="all, delete-orphan")
    hs_reviews = relationship("HSReview", back_populates="container", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="container", cascade="all, delete-orphan")
    outcomes = relationship("InspectionOutcome", back_populates="container", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="container", cascade="all, delete-orphan")

class Officer(Base):
    __tablename__ = "officers"

    officer_id = Column(Integer, primary_key=True, index=True)
    officer_code = Column(String, unique=True, index=True, nullable=False)
    officer_name = Column(String, nullable=False)
    designation = Column(String, default="Customs Officer")
    qualification = Column(String, default="General")  # General, Hazardous, Scanner, Complex
    daily_capacity = Column(Integer, default=6)
    availability = Column(Boolean, default=True)

    schedules = relationship("Schedule", back_populates="officer")

class ExaminationBay(Base):
    __tablename__ = "examination_bays"

    bay_id = Column(Integer, primary_key=True, index=True)
    bay_name = Column(String, unique=True, index=True, nullable=False)
    bay_type = Column(String, default="Standard")  # Standard, Hazardous
    capacity = Column(Integer, default=1)
    status = Column(String, default="Available")  # Available, Maintenance, Closed

    schedules = relationship("Schedule", back_populates="bay")

class Scanner(Base):
    __tablename__ = "scanners"

    scanner_id = Column(Integer, primary_key=True, index=True)
    scanner_name = Column(String, unique=True, index=True, nullable=False)
    location = Column(String, nullable=True)
    capacity = Column(Integer, default=20)
    availability = Column(Boolean, default=True)

    schedules = relationship("Schedule", back_populates="scanner")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    risk_id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False, unique=True)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String, default="Low")  # Low, Medium, High, Critical
    previous_offences = Column(Integer, default=0)
    country_score = Column(Integer, default=0)
    hs_score = Column(Integer, default=0)
    value_score = Column(Integer, default=0)
    final_score = Column(Integer, default=0)

    # Expanded intelligence breakdown & adjustments
    hs_risk_points = Column(Integer, default=0)
    country_risk_points = Column(Integer, default=0)
    value_risk_points = Column(Integer, default=0)
    history_risk_points = Column(Integer, default=0)
    anomaly_adjustment = Column(Integer, default=0)
    document_adjustment = Column(Integer, default=0)
    recommended_action = Column(String, default="Standard Automated Inspection")

    container = relationship("Container", back_populates="risk_assessment")

class ReadinessValidation(Base):
    __tablename__ = "readiness_validations"

    validation_id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False, unique=True)
    payment_completed = Column(Boolean, default=True)
    documents_available = Column(Boolean, default=True)
    permit_available = Column(Boolean, default=True)
    container_arrived = Column(Boolean, default=True)
    ready_for_schedule = Column(Boolean, default=True)

    # Expanded gate fields
    anomaly_review_status = Column(String, default="Passed")  # Passed, Review Required, Blocked
    hs_review_status = Column(String, default="Passed")       # Passed, Review Required, Blocked
    readiness_status = Column(String, default="Ready")        # Ready, Ready - Review Required, Blocked
    readiness_reason = Column(Text, nullable=True)

    container = relationship("Container", back_populates="readiness_validation")

class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("officers.officer_id"), nullable=False)
    bay_id = Column(Integer, ForeignKey("examination_bays.bay_id"), nullable=False)
    scanner_id = Column(Integer, ForeignKey("scanners.scanner_id"), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="Scheduled")  # Scheduled, Completed, Cancelled
    explanation = Column(Text, nullable=True)

    container = relationship("Container", back_populates="schedules")
    officer = relationship("Officer", back_populates="schedules")
    bay = relationship("ExaminationBay", back_populates="schedules")
    scanner = relationship("Scanner", back_populates="schedules")
    outcomes = relationship("InspectionOutcome", back_populates="schedule", cascade="all, delete-orphan")

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    generated_date = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String, default="System Administrator")
    file_location = Column(String, nullable=True)

class Setting(Base):
    __tablename__ = "settings"

    setting_id = Column(Integer, primary_key=True, index=True)
    setting_name = Column(String, unique=True, nullable=False)
    setting_value = Column(String, nullable=False)
    description = Column(String, nullable=True)

# --- NEW INTELLIGENCE & GOVERNANCE MODELS ---

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False)
    document_type = Column(String, nullable=False)  # Invoice, Packing List, Bill of Lading, Import Permit
    document_ref = Column(String, nullable=False)
    extraction_status = Column(String, default="Extracted")  # Extracted, Manual Review
    status = Column(String, default="Verified")  # Verified, Review, Missing
    confidence_score = Column(Float, default=0.95)
    created_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("Container", back_populates="documents")
    field_checks = relationship("DocumentFieldCheck", back_populates="document", cascade="all, delete-orphan")

class DocumentFieldCheck(Base):
    __tablename__ = "document_field_checks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    field_name = Column(String, nullable=False)
    document_value = Column(String, nullable=True)
    declaration_value = Column(String, nullable=True)
    match_status = Column(String, default="Match")  # Match, Mismatch
    issue_type = Column(String, nullable=True)      # Value Mismatch, Quantity Mismatch, HS Mismatch, Expired Permit

    document = relationship("Document", back_populates="field_checks")

class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False)
    anomaly_type = Column(String, nullable=False)  # CIF Outlier, Importer Frequency, HS-Country Anomaly, Quantity Discrepancy
    observed_value = Column(String, nullable=True)
    reference_value = Column(String, nullable=True)
    variance_pct = Column(Float, default=0.0)
    severity = Column(String, default="Medium")  # Critical, High, Medium, Low
    rule_code = Column(String, nullable=False)
    reason_text = Column(Text, nullable=False)
    disposition = Column(String, default="Unresolved")  # Unresolved, False Positive, Valid Concern, Needs Review

    container = relationship("Container", back_populates="anomaly_alerts")

class HSReview(Base):
    __tablename__ = "hs_reviews"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False)
    goods_description = Column(Text, nullable=True)
    declared_hs_code = Column(String, nullable=False)
    suggested_hs_code = Column(String, nullable=False)
    suggested_description = Column(Text, nullable=True)
    confidence = Column(Float, default=0.90)
    match_status = Column(String, default="Match")  # Match, Mismatch
    review_decision = Column(String, default="Pending")  # Pending, Accept Declared, Accept Suggested, Escalate
    review_note = Column(Text, nullable=True)

    container = relationship("Container", back_populates="hs_reviews")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False)
    source_module = Column(String, nullable=False)  # Risk, Fraud, Document, HS, Capacity
    type = Column(String, nullable=False)            # Physical Examination, Document Verification, HS Audit, Value Audit
    severity = Column(String, default="Medium")      # Critical, High, Medium, Low
    recommended_action = Column(Text, nullable=False)
    reason_text = Column(Text, nullable=False)
    confidence = Column(Float, default=0.88)
    status = Column(String, default="Open")          # Open, Accepted, Overridden, Needs Further Review
    created_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("Container", back_populates="recommendations")
    reviews = relationship("RecommendationReview", back_populates="recommendation", cascade="all, delete-orphan")

class RecommendationReview(Base):
    __tablename__ = "recommendation_reviews"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    reviewer = Column(String, nullable=False)
    decision = Column(String, nullable=False)  # Accepted, Overridden, Needs Further Review
    override_reason = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="reviews")

class InspectionOutcome(Base):
    __tablename__ = "inspection_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id"), nullable=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=False)
    outcome_type = Column(String, default="Pending")  # Violation Found, No Issue Found, Pending
    violation_type = Column(String, nullable=True)     # Undeclared Goods, Misclassification, Under-valuation, Permit Deficit, None
    officer_notes = Column(Text, nullable=True)
    evidence_reference = Column(String, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("Container", back_populates="outcomes")
    schedule = relationship("Schedule", back_populates="outcomes")

class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    id = Column(Integer, primary_key=True, index=True)
    source_entity = Column(String, nullable=False)  # Container, Document, Importer, Resource
    record_id = Column(String, nullable=False)
    field_name = Column(String, nullable=False)
    issue_type = Column(String, nullable=False)      # Missing Field, Format Error, Duplicate, Out of Range
    current_value = Column(String, nullable=True)
    expected_rule = Column(String, nullable=False)
    severity = Column(String, default="Medium")      # Critical, High, Medium, Low
    validation_rule = Column(Text, nullable=False)
    status = Column(String, default="Open")          # Open, Resolved, Ignored
    ai_ready_flag = Column(Boolean, default=False)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.container_id"), nullable=True)
    event_type = Column(String, nullable=False)     # Recommendation Generated, Recommendation Reviewed, Readiness Updated, Schedule Optimized, Outcome Recorded
    source_module = Column(String, nullable=False)
    rule_model_version = Column(String, default="v1.0.0-demo")
    payload_snapshot = Column(Text, nullable=True)
    actor = Column(String, default="System / Officer")
    decision = Column(String, nullable=True)
    override_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("Container", back_populates="audit_events")
