from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.domain import Container, Schedule, InspectionOutcome, AuditEvent, RiskAssessment, Importer

router = APIRouter(tags=["Examination Outcome"])

class RecordOutcomeRequest(BaseModel):
    container_id: int
    schedule_id: Optional[int] = None
    outcome_type: str  # Violation Found, No Issue Found
    violation_type: Optional[str] = None  # Undeclared Goods, Misclassification, Under-valuation, Permit Deficit, None
    officer_notes: str
    evidence_reference: Optional[str] = None
    officer_name: str = "Senior Customs Inspector"

@router.get("/outcomes")
def get_outcomes(
    outcome_type: Optional[str] = None,
    violation_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(InspectionOutcome).join(Container)
    
    if outcome_type and outcome_type != "All":
        query = query.filter(InspectionOutcome.outcome_type == outcome_type)
    if violation_type and violation_type != "All":
        query = query.filter(InspectionOutcome.violation_type == violation_type)
        
    outcomes = query.all()
    all_outcomes = db.query(InspectionOutcome).all()
    
    # Calculate KPIs
    completed_today = len(all_outcomes)
    violations = sum(1 for o in all_outcomes if o.outcome_type == "Violation Found")
    no_issue = sum(1 for o in all_outcomes if o.outcome_type == "No Issue Found")
    pending = db.query(Schedule).filter(Schedule.status == "Scheduled").count()
    
    # High risk hit rate calculation
    high_risk_completed = 0
    high_risk_hits = 0
    for o in all_outcomes:
        if o.container.risk_assessment and o.container.risk_assessment.risk_level in ["Critical", "High"]:
            high_risk_completed += 1
            if o.outcome_type == "Violation Found":
                high_risk_hits += 1
                
    hit_rate = round((high_risk_hits / max(high_risk_completed, 1)) * 100, 1)
    
    kpis = {
        "completed_today": completed_today,
        "violations_found": violations,
        "no_issue_found": no_issue,
        "pending_outcome": pending,
        "high_risk_hit_rate": f"{hit_rate}%"
    }
    
    by_outcome = {"Violation Found": violations, "No Issue Found": no_issue}
    by_violation = {}
    for o in all_outcomes:
        if o.violation_type and o.violation_type != "None":
            by_violation[o.violation_type] = by_violation.get(o.violation_type, 0) + 1
            
    items = []
    for o in outcomes:
        risk_lvl = o.container.risk_assessment.risk_level if o.container.risk_assessment else "Low"
        items.append({
            "id": o.id,
            "container_number": o.container.container_number,
            "cusdec_number": o.container.cusdec_number,
            "importer": o.container.importer.importer_name if o.container.importer else "N/A",
            "date": o.completed_at.strftime("%Y-%m-%d %H:%M"),
            "officer": o.schedule.officer.officer_name if (o.schedule and o.schedule.officer) else "Assigned Officer",
            "risk_level": risk_lvl,
            "recommended_action": o.container.risk_assessment.recommended_action if o.container.risk_assessment else "Standard Exam",
            "examination_type": o.container.examination_type,
            "outcome_type": o.outcome_type,
            "violation_type": o.violation_type or "None",
            "notes": o.officer_notes,
            "evidence_ref": o.evidence_reference or f"EVID-2026-{o.id:04d}",
            "completed_time": o.completed_at.strftime("%H:%M")
        })
        
    return {
        "kpis": kpis,
        "charts": {
            "by_outcome": [{"name": k, "value": v} for k, v in by_outcome.items()],
            "by_violation": [{"name": k, "count": v} for k, v in by_violation.items()]
        },
        "items": items
    }

@router.post("/outcomes")
def record_outcome(
    req: RecordOutcomeRequest,
    db: Session = Depends(get_db)
):
    cont = db.query(Container).filter(Container.container_id == req.container_id).first()
    if not cont:
        raise HTTPException(status_code=404, detail="Container not found")
        
    outcome = InspectionOutcome(
        schedule_id=req.schedule_id,
        container_id=req.container_id,
        outcome_type=req.outcome_type,
        violation_type=req.violation_type if req.outcome_type == "Violation Found" else None,
        officer_notes=req.officer_notes,
        evidence_reference=req.evidence_reference or f"EVID-2026-{datetime.utcnow().strftime('%M%S')}",
        completed_at=datetime.utcnow()
    )
    db.add(outcome)
    
    # Mark container completed
    cont.status = "Completed"
    if req.schedule_id:
        sched = db.query(Schedule).filter(Schedule.schedule_id == req.schedule_id).first()
        if sched:
            sched.status = "Completed"
            
    # Update importer previous offences if violation found
    if req.outcome_type == "Violation Found" and cont.importer:
        risk = db.query(RiskAssessment).filter(RiskAssessment.container_id == cont.container_id).first()
        if risk:
            risk.previous_offences += 1

    audit = AuditEvent(
        container_id=cont.container_id,
        event_type="Outcome Recorded",
        source_module="Examination Outcome",
        rule_model_version="v1.0.0-exec",
        payload_snapshot=f"Outcome: {req.outcome_type}. Violation: {req.violation_type}.",
        actor=req.officer_name,
        decision=req.outcome_type,
        override_reason=req.officer_notes
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Examination outcome recorded successfully", "outcome_id": outcome.id}
