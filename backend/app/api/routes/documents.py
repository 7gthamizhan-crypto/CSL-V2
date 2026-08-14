from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.domain import Container, Document, DocumentFieldCheck, AuditEvent, ReadinessValidation

router = APIRouter(tags=["Document Intelligence"])

class DocumentStatusRequest(BaseModel):
    status: str  # Verified, Review, Missing
    reviewer: str = "Document Control Officer"
    note: Optional[str] = None

@router.get("/documents")
def get_documents(
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document).join(Container)
    
    if status and status != "All":
        query = query.filter(Document.status == status)
    if document_type and document_type != "All":
        query = query.filter(Document.document_type == document_type)
        
    docs = query.all()
    all_docs = db.query(Document).all()
    
    kpis = {
        "checked": len(all_docs),
        "verified": sum(1 for d in all_docs if d.status == "Verified"),
        "needs_review": sum(1 for d in all_docs if d.status == "Review"),
        "missing": sum(1 for d in all_docs if d.status == "Missing"),
        "avg_confidence": round((sum(d.confidence_score for d in all_docs) / max(len(all_docs), 1)) * 100, 1)
    }
    
    by_status = {"Verified": 0, "Review": 0, "Missing": 0}
    by_issue = {}
    
    for d in all_docs:
        if d.status in by_status:
            by_status[d.status] += 1
        for fc in d.field_checks:
            if fc.issue_type:
                by_issue[fc.issue_type] = by_issue.get(fc.issue_type, 0) + 1
                
    items = []
    for d in docs:
        checks_passed = sum(1 for fc in d.field_checks if fc.match_status == "Match")
        total_checks = len(d.field_checks)
        issues_list = [fc.issue_type for fc in d.field_checks if fc.issue_type]
        
        items.append({
            "id": d.id,
            "container_number": d.container.container_number,
            "cusdec_number": d.container.cusdec_number,
            "importer": d.container.importer.importer_name if d.container.importer else "N/A",
            "document_type": d.document_type,
            "document_ref": d.document_ref,
            "extraction_status": d.extraction_status,
            "confidence": round(d.confidence_score * 100, 1),
            "checks_passed": f"{checks_passed}/{max(total_checks, 1)}",
            "issues": ", ".join(issues_list) if issues_list else "None",
            "status": d.status,
            "reviewer": "AI OCR Engine"
        })
        
    return {
        "kpis": kpis,
        "charts": {
            "by_status": [{"name": k, "value": v} for k, v in by_status.items()],
            "by_issue": [{"name": k, "count": v} for k, v in by_issue.items()]
        },
        "items": items
    }

@router.get("/documents/{container_id}/checks")
def get_container_document_checks(container_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.container_id == container_id).all()
    results = []
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
        results.append({
            "document_id": d.id,
            "document_type": d.document_type,
            "document_ref": d.document_ref,
            "status": d.status,
            "confidence": round(d.confidence_score * 100, 1),
            "fields": fields
        })
    return {"documents": results}

@router.post("/documents/{doc_id}/status")
def update_document_status(
    doc_id: int,
    req: DocumentStatusRequest,
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    doc.status = req.status
    
    # If missing/rejected mandatory document, update readiness gate
    if req.status in ["Missing", "Review"]:
        readiness = db.query(ReadinessValidation).filter(ReadinessValidation.container_id == doc.container_id).first()
        if readiness:
            readiness.documents_available = (req.status != "Missing")
            if req.status == "Missing":
                readiness.readiness_status = "Blocked"
                readiness.readiness_reason = f"Mandatory document ({doc.document_type}) missing or rejected."

    audit = AuditEvent(
        container_id=doc.container_id,
        event_type="Document Status Updated",
        source_module="Document Intelligence",
        rule_model_version="v1.4.0-ocr",
        payload_snapshot=f"Document {doc.document_type} status set to {req.status}.",
        actor=req.reviewer,
        decision=req.status,
        override_reason=req.note
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Document status updated", "status": doc.status}
