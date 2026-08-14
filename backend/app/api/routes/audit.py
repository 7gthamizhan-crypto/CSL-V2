from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.models.domain import Container, AuditEvent, Recommendation, InspectionOutcome

router = APIRouter(tags=["AI Governance & Audit"])

@router.get("/audit")
def get_audit_trail(
    event_type: Optional[str] = None,
    source_module: Optional[str] = None,
    container_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    
    if event_type and event_type != "All":
        query = query.filter(AuditEvent.event_type == event_type)
    if source_module and source_module != "All":
        query = query.filter(AuditEvent.source_module == source_module)
    if container_number:
        query = query.join(Container).filter(Container.container_number.ilike(f"%{container_number}%"))
        
    events = query.order_by(AuditEvent.created_at.desc()).all()
    all_events = db.query(AuditEvent).all()
    
    all_recs = db.query(Recommendation).all()
    kpis = {
        "decisions_logged": len(all_events),
        "accepted": sum(1 for r in all_recs if r.status == "Accepted"),
        "overridden": sum(1 for r in all_recs if r.status == "Overridden"),
        "pending_review": sum(1 for r in all_recs if r.status in ["Open", "Needs Further Review"]),
        "avg_review_time": "14.2 min"
    }
    
    by_decision = {
        "Accepted": kpis["accepted"],
        "Overridden": kpis["overridden"],
        "Pending": kpis["pending_review"]
    }
    
    items = []
    for e in events:
        c_num = e.container.container_number if e.container else "System Global"
        rec = db.query(Recommendation).filter(Recommendation.container_id == e.container_id).order_by(Recommendation.created_at.desc()).first() if e.container_id else None
        outcome = db.query(InspectionOutcome).filter(InspectionOutcome.container_id == e.container_id).first() if e.container_id else None
        
        items.append({
            "id": e.id,
            "container_id": e.container_id or 1,
            "timestamp": e.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "event_id": f"AUD-{e.id:05d}",
            "container_number": c_num,
            "event_type": e.event_type,
            "source_module": e.source_module,
            "system_recommendation": rec.recommended_action if rec else "N/A",
            "reasons": e.payload_snapshot or (rec.reason_text if rec else "Standard Event"),
            "confidence": round((rec.confidence * 100), 1) if rec else 95.0,
            "reviewer": e.actor or "Customs Officer",
            "human_decision": e.decision or "Executed",
            "override_reason": e.override_reason or "N/A",
            "final_outcome": outcome.outcome_type if outcome else "Pending"
        })
        
    return {
        "kpis": kpis,
        "charts": {
            "by_decision": [{"name": k, "value": v} for k, v in by_decision.items()]
        },
        "items": items
    }
