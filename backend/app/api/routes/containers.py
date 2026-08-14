from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.domain import Container, RiskAssessment, ReadinessValidation, Schedule, Importer, ClearingAgent
from app.schemas.dto import ContainerCreate, ContainerResponse

router = APIRouter(prefix="/containers", tags=["Containers"])

@router.get("", response_model=List[ContainerResponse])
def get_containers(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Container).join(RiskAssessment, isouter=True).join(ReadinessValidation, isouter=True)

    if search:
        s_pattern = f"%{search}%"
        query = query.filter(
            (Container.container_number.ilike(s_pattern)) |
            (Container.cusdec_number.ilike(s_pattern)) |
            (Container.goods_description.ilike(s_pattern))
        )

    if status:
        query = query.filter(Container.status == status)

    if exam_type:
        query = query.filter(Container.examination_type == exam_type)

    if risk_level:
        query = query.filter(RiskAssessment.risk_level == risk_level)

    return query.order_by(Container.container_id.desc()).all()

@router.get("/{container_id}", response_model=ContainerResponse)
def get_container_by_id(container_id: int, db: Session = Depends(get_db)):
    c = db.query(Container).filter(Container.container_id == container_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Container not found.")
    return c

@router.post("", response_model=ContainerResponse)
def create_container(payload: ContainerCreate, db: Session = Depends(get_db)):
    # Check if container_number already exists
    existing = db.query(Container).filter(Container.container_number == payload.container_number).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Container number '{payload.container_number}' already exists in system.")

    # Find default importer and agent if not specified
    imp_id = payload.importer_id
    if not imp_id:
        imp = db.query(Importer).first()
        imp_id = imp.importer_id if imp else None

    agt_id = payload.agent_id
    if not agt_id:
        agt = db.query(ClearingAgent).first()
        agt_id = agt.agent_id if agt else None

    c = Container(
        container_number=payload.container_number.strip().upper(),
        cusdec_number=payload.cusdec_number.strip().upper(),
        country_of_origin=payload.country_of_origin,
        hs_code=payload.hs_code or "870323",
        goods_description=payload.goods_description or "General Commercial Cargo",
        cif_value=float(payload.cif_value or 0.0),
        duty_amount=float(payload.duty_amount or 0.0),
        examination_type=payload.examination_type or "Standard",
        importer_id=imp_id,
        agent_id=agt_id,
        status="Ready"
    )
    db.add(c)
    db.flush()

    # Calculate dynamic risk score based on examination type & value
    base_score = 45
    if payload.examination_type == "High Risk":
        base_score = 75
    elif payload.examination_type == "Hazardous":
        base_score = 90
    elif payload.examination_type == "Complex":
        base_score = 95
    elif payload.examination_type == "Scanner":
        base_score = 25

    if payload.cif_value and payload.cif_value > 100000:
        base_score = min(100, base_score + 10)

    risk_lvl = "Low"
    if base_score >= 85:
        risk_lvl = "Critical"
    elif base_score >= 60:
        risk_lvl = "High"
    elif base_score >= 35:
        risk_lvl = "Medium"

    risk = RiskAssessment(
        container_id=c.container_id,
        risk_score=base_score,
        risk_level=risk_lvl,
        hs_score=base_score,
        final_score=base_score
    )
    readiness = ReadinessValidation(
        container_id=c.container_id,
        payment_completed=True,
        documents_available=True,
        permit_available=True,
        container_arrived=True,
        ready_for_schedule=True
    )
    db.add(risk)
    db.add(readiness)
    db.commit()
    db.refresh(c)
    return c

@router.get("/{container_id}/full-intelligence")
@router.get("/{container_id}/intelligence-360")
def get_container_full_intelligence(container_id: int, db: Session = Depends(get_db)):
    c = db.query(Container).filter(Container.container_id == container_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Container not found.")

    risk = c.risk_assessment
    readiness = c.readiness_validation
    schedules = c.schedules
    docs = c.documents
    alerts = c.anomaly_alerts
    hs_revs = c.hs_reviews
    recs = c.recommendations
    outcomes = c.outcomes
    audits = c.audit_events

    doc_list = []
    for d in docs:
        fields = []
        for fc in d.field_checks:
            fields.append({
                "field_name": fc.field_name,
                "document_value": fc.document_value,
                "declaration_value": fc.declaration_value,
                "match_status": fc.match_status,
                "issue_type": fc.issue_type
            })
        doc_list.append({
            "id": d.id,
            "document_type": d.document_type,
            "document_ref": d.document_ref,
            "extraction_status": d.extraction_status,
            "status": d.status,
            "confidence": round(d.confidence_score * 100, 1),
            "fields": fields
        })

    return {
        "overview": {
            "container_id": c.container_id,
            "container_number": c.container_number,
            "cusdec_number": c.cusdec_number,
            "importer_name": c.importer.importer_name if c.importer else "N/A",
            "agent_name": c.agent.agent_name if c.agent else "N/A",
            "country_of_origin": c.country_of_origin,
            "hs_code": c.hs_code,
            "goods_description": c.goods_description,
            "cif_value": c.cif_value,
            "duty_amount": c.duty_amount,
            "examination_type": c.examination_type,
            "arrival_date": c.arrival_date.strftime("%Y-%m-%d %H:%M"),
            "status": c.status
        },
        "risk": {
            "risk_score": risk.final_score if risk else 0,
            "risk_level": risk.risk_level if risk else "Low",
            "hs_risk_points": risk.hs_risk_points if risk else 0,
            "country_risk_points": risk.country_risk_points if risk else 0,
            "value_risk_points": risk.value_risk_points if risk else 0,
            "history_risk_points": risk.history_risk_points if risk else 0,
            "anomaly_adjustment": risk.anomaly_adjustment if risk else 0,
            "document_adjustment": risk.document_adjustment if risk else 0,
            "recommended_action": risk.recommended_action if risk else "Standard Exam"
        },
        "anomalies": [{
            "id": a.id,
            "anomaly_type": a.anomaly_type,
            "observed_value": a.observed_value,
            "reference_value": a.reference_value,
            "variance_pct": a.variance_pct,
            "severity": a.severity,
            "reason": a.reason_text,
            "disposition": a.disposition
        } for a in alerts],
        "documents": doc_list,
        "hs_review": {
            "declared_hs_code": hs_revs[0].declared_hs_code if hs_revs else c.hs_code,
            "suggested_hs_code": hs_revs[0].suggested_hs_code if hs_revs else c.hs_code,
            "suggested_description": hs_revs[0].suggested_description if hs_revs else c.goods_description,
            "confidence": round(hs_revs[0].confidence * 100, 1) if hs_revs else 95.0,
            "match_status": hs_revs[0].match_status if hs_revs else "Match",
            "review_decision": hs_revs[0].review_decision if hs_revs else "Pending"
        } if hs_revs else None,
        "readiness": {
            "payment_completed": readiness.payment_completed if readiness else True,
            "documents_available": readiness.documents_available if readiness else True,
            "permit_available": readiness.permit_available if readiness else True,
            "container_arrived": readiness.container_arrived if readiness else True,
            "anomaly_review_status": readiness.anomaly_review_status if readiness else "Passed",
            "hs_review_status": readiness.hs_review_status if readiness else "Passed",
            "readiness_status": readiness.readiness_status if readiness else "Ready",
            "readiness_reason": readiness.readiness_reason if readiness else None
        },
        "schedule": [{
            "schedule_id": s.schedule_id,
            "officer_name": s.officer.officer_name if s.officer else "Officer",
            "bay_name": s.bay.bay_name if s.bay else "Bay",
            "scanner_name": s.scanner.scanner_name if s.scanner else "N/A",
            "start_time": s.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "status": s.status,
            "explanation": s.explanation
        } for s in schedules],
        "outcome": {
            "outcome_type": outcomes[0].outcome_type,
            "violation_type": outcomes[0].violation_type or "None",
            "officer_notes": outcomes[0].officer_notes,
            "evidence_reference": outcomes[0].evidence_reference,
            "completed_at": outcomes[0].completed_at.strftime("%Y-%m-%d %H:%M")
        } if outcomes else None,
        "recommendations": [{
            "id": r.id,
            "source_module": r.source_module,
            "type": r.type,
            "severity": r.severity,
            "action": r.recommended_action,
            "reason": r.reason_text,
            "status": r.status
        } for r in recs],
        "audit": [{
            "id": a.id,
            "timestamp": a.created_at.strftime("%Y-%m-%d %H:%M"),
            "event_type": a.event_type,
            "source_module": a.source_module,
            "actor": a.actor,
            "decision": a.decision,
            "override_reason": a.override_reason
        } for a in audits]
    }

@router.delete("/{container_id}")
def delete_container(container_id: int, db: Session = Depends(get_db)):
    c = db.query(Container).filter(Container.container_id == container_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Container not found.")

    # Delete related risk assessment, readiness validation, and schedules
    db.query(RiskAssessment).filter(RiskAssessment.container_id == container_id).delete()
    db.query(ReadinessValidation).filter(ReadinessValidation.container_id == container_id).delete()
    db.query(Schedule).filter(Schedule.container_id == container_id).delete()

    db.delete(c)
    db.commit()
    return {"message": f"Container {c.container_number} removed successfully."}

