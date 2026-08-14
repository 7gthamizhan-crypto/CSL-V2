from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.domain import Container, HSReview, AuditEvent, ReadinessValidation

router = APIRouter(tags=["HS Code Intelligence"])

class DecisionRequest(BaseModel):
    decision: str  # Accept Declared, Accept Suggested, Escalate
    reviewer: str = "HS Classification Specialist"
    note: Optional[str] = None

@router.get("/hs-intelligence")
def get_hs_intelligence(
    match_status: Optional[str] = None,
    review_decision: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(HSReview).join(Container)
    
    if match_status and match_status != "All":
        query = query.filter(HSReview.match_status == match_status)
    if review_decision and review_decision != "All":
        query = query.filter(HSReview.review_decision == review_decision)
        
    reviews = query.all()
    all_reviews = db.query(HSReview).all()
    
    kpis = {
        "checked": len(all_reviews),
        "hs_matches": sum(1 for r in all_reviews if r.match_status == "Match"),
        "mismatches": sum(1 for r in all_reviews if r.match_status == "Mismatch"),
        "low_confidence": sum(1 for r in all_reviews if r.confidence < 0.85),
        "review_pending": sum(1 for r in all_reviews if r.review_decision == "Pending")
    }
    
    by_match = {"Match": 0, "Mismatch": 0}
    for r in all_reviews:
        if r.match_status in by_match:
            by_match[r.match_status] += 1
            
    items = []
    for r in reviews:
        items.append({
            "id": r.id,
            "container_number": r.container.container_number,
            "cusdec_number": r.container.cusdec_number,
            "importer": r.container.importer.importer_name if r.container.importer else "N/A",
            "goods_description": r.goods_description,
            "declared_hs_code": r.declared_hs_code,
            "suggested_hs_code": r.suggested_hs_code,
            "suggested_description": r.suggested_description,
            "confidence": round(r.confidence * 100, 1),
            "match_status": r.match_status,
            "risk_impact": "High Duty Discrepancy Risk" if r.match_status == "Mismatch" else "Low Risk",
            "review_decision": r.review_decision,
            "review_note": r.review_note
        })
        
    return {
        "kpis": kpis,
        "charts": {
            "by_match": [{"name": k, "value": v} for k, v in by_match.items()]
        },
        "items": items
    }

@router.post("/hs-intelligence/{review_id}/decision")
def submit_hs_decision(
    review_id: int,
    req: DecisionRequest,
    db: Session = Depends(get_db)
):
    rev = db.query(HSReview).filter(HSReview.id == review_id).first()
    if not rev:
        raise HTTPException(status_code=404, detail="HS Review not found")
        
    rev.review_decision = req.decision
    rev.review_note = req.note
    
    # If accepted suggested code, update container HS code
    if req.decision == "Accept Suggested":
        rev.container.hs_code = rev.suggested_hs_code
        rev.match_status = "Match"
        
    # Update readiness gate if decision made
    readiness = db.query(ReadinessValidation).filter(ReadinessValidation.container_id == rev.container_id).first()
    if readiness and req.decision in ["Accept Declared", "Accept Suggested"]:
        readiness.hs_review_status = "Passed"
        if readiness.anomaly_review_status == "Passed" and readiness.payment_completed:
            readiness.readiness_status = "Ready"

    audit = AuditEvent(
        container_id=rev.container_id,
        event_type="HS Decision Submitted",
        source_module="HS Code Intelligence",
        rule_model_version="v1.8.0-classifier",
        payload_snapshot=f"Decision: {req.decision}. Declared: {rev.declared_hs_code} -> Suggested: {rev.suggested_hs_code}.",
        actor=req.reviewer,
        decision=req.decision,
        override_reason=req.note
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Classification decision saved", "decision": rev.review_decision}
