from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.domain import Container, DataQualityIssue, AuditEvent

router = APIRouter(tags=["Data Quality & AI Readiness"])

class ResolveIssueRequest(BaseModel):
    status: str  # Resolved, Ignored
    actor: str = "Data Governance Officer"
    note: Optional[str] = None

@router.get("/data-quality")
def get_data_quality(
    source_entity: Optional[str] = None,
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DataQualityIssue)
    
    if source_entity and source_entity != "All":
        query = query.filter(DataQualityIssue.source_entity == source_entity)
    if issue_type and issue_type != "All":
        query = query.filter(DataQualityIssue.issue_type == issue_type)
    if status and status != "All":
        query = query.filter(DataQualityIssue.status == status)
        
    issues = query.all()
    all_issues = db.query(DataQualityIssue).all()
    total_containers = db.query(Container).count()
    
    kpis = {
        "completeness_score": 96.4,
        "valid_records": total_containers - sum(1 for i in all_issues if i.status == "Open"),
        "duplicates": 0,
        "missing_hs_codes": 0,
        "ai_ready_records": sum(1 for i in all_issues if i.ai_ready_flag) + (total_containers - len(all_issues))
    }
    
    scorecard = [
        {"dimension": "Completeness", "score": 96.4, "status": "Excellent"},
        {"dimension": "Validity", "score": 94.8, "status": "Good"},
        {"dimension": "Consistency", "score": 92.1, "status": "Good"},
        {"dimension": "Timeliness", "score": 98.0, "status": "Excellent"}
    ]
    
    by_type = {}
    for i in all_issues:
        by_type[i.issue_type] = by_type.get(i.issue_type, 0) + 1
        
    items = []
    for i in issues:
        items.append({
            "id": i.id,
            "issue_id": f"DQ-{i.id:04d}",
            "source_entity": i.source_entity,
            "record_id": i.record_id,
            "field_name": i.field_name,
            "issue_type": i.issue_type,
            "current_value": i.current_value,
            "expected_rule": i.expected_rule,
            "severity": i.severity,
            "validation_rule": i.validation_rule,
            "status": i.status,
            "ai_ready": i.ai_ready_flag,
            "owner": "Data Governance Team"
        })
        
    return {
        "kpis": kpis,
        "scorecard": scorecard,
        "charts": {
            "by_type": [{"name": k, "count": v} for k, v in by_type.items()]
        },
        "items": items
    }

@router.post("/data-quality/{issue_id}/resolve")
def resolve_issue(
    issue_id: int,
    req: ResolveIssueRequest,
    db: Session = Depends(get_db)
):
    issue = db.query(DataQualityIssue).filter(DataQualityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Data quality issue not found")
        
    issue.status = req.status
    if req.status == "Resolved":
        issue.ai_ready_flag = True
        
    audit = AuditEvent(
        container_id=None,
        event_type="Data Quality Issue Resolved",
        source_module="Data Quality & AI Readiness",
        rule_model_version="v1.0.0-dq",
        payload_snapshot=f"Issue {issue.field_name} set to {req.status}.",
        actor=req.actor,
        decision=req.status,
        override_reason=req.note
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Issue updated", "status": issue.status}
