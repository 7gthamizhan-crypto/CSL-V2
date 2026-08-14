from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database.connection import get_db
from app.models.domain import Container, Recommendation, RecommendationReview, AuditEvent, ReadinessValidation

router = APIRouter(tags=["AI Recommendations"])

class ReviewRequest(BaseModel):
    reviewer: str = "Senior Customs Officer"
    decision: str  # Accepted, Overridden, Needs Further Review
    override_reason: Optional[str] = None
    note: Optional[str] = None

@router.get("/recommendations")
def get_recommendations(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    source_module: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Recommendation).join(Container)
    
    if status and status != "All":
        query = query.filter(Recommendation.status == status)
    if severity and severity != "All":
        query = query.filter(Recommendation.severity == severity)
    if source_module and source_module != "All":
        query = query.filter(Recommendation.source_module == source_module)
        
    recs = query.order_by(Recommendation.created_at.desc()).all()
    
    # Calculate KPIs
    all_recs = db.query(Recommendation).all()
    kpis = {
        "open_recommendations": sum(1 for r in all_recs if r.status == "Open"),
        "critical_recommendations": sum(1 for r in all_recs if r.severity == "Critical" and r.status == "Open"),
        "awaiting_review": sum(1 for r in all_recs if r.status in ["Open", "Needs Further Review"]),
        "accepted_today": sum(1 for r in all_recs if r.status == "Accepted"),
        "overridden_today": sum(1 for r in all_recs if r.status == "Overridden")
    }
    
    # Charts data
    by_type = {}
    by_severity = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    top_reasons = {}
    
    for r in all_recs:
        by_type[r.source_module] = by_type.get(r.source_module, 0) + 1
        if r.severity in by_severity:
            by_severity[r.severity] += 1
        top_reasons[r.type] = top_reasons.get(r.type, 0) + 1
        
    result_items = []
    for r in recs:
        latest_rev = db.query(RecommendationReview).filter(RecommendationReview.recommendation_id == r.id).order_by(RecommendationReview.reviewed_at.desc()).first()
        result_items.append({
            "id": r.id,
            "recommendation_id": f"REC-{r.id:04d}",
            "time": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "container_number": r.container.container_number,
            "cusdec_number": r.container.cusdec_number,
            "importer": r.container.importer.importer_name if r.container.importer else "N/A",
            "source_module": r.source_module,
            "type": r.type,
            "severity": r.severity,
            "recommended_action": r.recommended_action,
            "primary_reason": r.reason_text,
            "confidence": round(r.confidence * 100, 1),
            "status": r.status,
            "reviewer": latest_rev.reviewer if latest_rev else "Unassigned",
            "override_reason": latest_rev.override_reason if latest_rev else None
        })
        
    return {
        "kpis": kpis,
        "charts": {
            "by_type": [{"name": k, "value": v} for k, v in by_type.items()],
            "by_severity": [{"name": k, "value": v} for k, v in by_severity.items()],
            "top_reasons": [{"name": k, "count": v} for k, v in sorted(top_reasons.items(), key=lambda x: x[1], reverse=True)[:5]]
        },
        "items": result_items
    }

@router.post("/recommendations/{rec_id}/review")
def review_recommendation(
    rec_id: int,
    req: ReviewRequest,
    db: Session = Depends(get_db)
):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    if req.decision == "Overridden" and not req.override_reason:
        raise HTTPException(status_code=400, detail="Mandatory override reason required when overriding system recommendation.")
        
    rec.status = req.decision
    
    # Save review record
    review = RecommendationReview(
        recommendation_id=rec.id,
        reviewer=req.reviewer,
        decision=req.decision,
        override_reason=req.override_reason if req.decision == "Overridden" else None,
        note=req.note,
        reviewed_at=datetime.utcnow()
    )
    db.add(review)
    
    # Update container readiness if accepted
    readiness = db.query(ReadinessValidation).filter(ReadinessValidation.container_id == rec.container_id).first()
    if readiness and req.decision == "Accepted":
        readiness.anomaly_review_status = "Passed"
        if readiness.hs_review_status == "Passed" and readiness.payment_completed and readiness.permit_available:
            readiness.readiness_status = "Ready"
            readiness.readiness_reason = "Human sign-off complete. Container ready for scheduling."
            rec.container.status = "Ready"

    # Log Immutable Audit Event
    audit = AuditEvent(
        container_id=rec.container_id,
        event_type="Recommendation Reviewed",
        source_module="AI Recommendation Center",
        rule_model_version="v2.1.0-governance",
        payload_snapshot=f"Action: {rec.recommended_action}. Decision: {req.decision}.",
        actor=req.reviewer,
        decision=req.decision,
        override_reason=req.override_reason if req.decision == "Overridden" else None
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Recommendation review successfully submitted", "status": rec.status}
