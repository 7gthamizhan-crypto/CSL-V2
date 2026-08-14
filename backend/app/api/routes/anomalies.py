from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.domain import Container, AnomalyAlert, AuditEvent

router = APIRouter(tags=["Fraud & Anomaly Detection"])

class DispositionRequest(BaseModel):
    disposition: str  # False Positive, Valid Concern, Needs Review
    reviewer: str = "Customs Risk Analyst"
    note: Optional[str] = None

@router.get("/anomalies")
def get_anomalies(
    disposition: Optional[str] = None,
    severity: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnomalyAlert).join(Container)
    
    if disposition and disposition != "All":
        query = query.filter(AnomalyAlert.disposition == disposition)
    if severity and severity != "All":
        query = query.filter(AnomalyAlert.severity == severity)
    if anomaly_type and anomaly_type != "All":
        query = query.filter(AnomalyAlert.anomaly_type == anomaly_type)
        
    alerts = query.all()
    all_alerts = db.query(AnomalyAlert).all()
    
    kpis = {
        "screened": db.query(Container).count(),
        "alerts_detected": len(all_alerts),
        "high_severity": sum(1 for a in all_alerts if a.severity in ["Critical", "High"]),
        "cif_anomalies": sum(1 for a in all_alerts if a.anomaly_type == "CIF Outlier"),
        "importer_pattern_alerts": sum(1 for a in all_alerts if a.anomaly_type == "Importer Frequency")
    }
    
    by_type = {}
    by_severity = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    scatter_data = []
    
    for a in all_alerts:
        by_type[a.anomaly_type] = by_type.get(a.anomaly_type, 0) + 1
        if a.severity in by_severity:
            by_severity[a.severity] += 1
            
        try:
            obs = float(a.observed_value.replace("$", "").replace(",", "")) if a.observed_value else 0
            ref = float(a.reference_value.split(" ")[0].replace("$", "").replace(",", "")) if a.reference_value else 0
            scatter_data.append({
                "container_number": a.container.container_number,
                "declared_cif": obs,
                "reference_cif": ref,
                "severity": a.severity
            })
        except Exception:
            pass

    items = []
    for a in alerts:
        items.append({
            "id": a.id,
            "alert_id": f"ALT-{a.id:04d}",
            "container_number": a.container.container_number,
            "cusdec_number": a.container.cusdec_number,
            "importer": a.container.importer.importer_name if a.container.importer else "N/A",
            "alert_type": a.anomaly_type,
            "severity": a.severity,
            "observed_value": a.observed_value,
            "reference_value": a.reference_value,
            "variance_pct": a.variance_pct,
            "reason": a.reason_text,
            "rule_code": a.rule_code,
            "disposition": a.disposition,
            "recommended_action": "Flag for Valuation Review" if a.anomaly_type == "CIF Outlier" else "Impose Physical Audit"
        })
        
    return {
        "kpis": kpis,
        "charts": {
            "by_type": [{"name": k, "value": v} for k, v in by_type.items()],
            "by_severity": [{"name": k, "value": v} for k, v in by_severity.items()],
            "scatter": scatter_data[:40]
        },
        "items": items
    }

@router.post("/anomalies/{alert_id}/disposition")
def update_disposition(
    alert_id: int,
    req: DispositionRequest,
    db: Session = Depends(get_db)
):
    alert = db.query(AnomalyAlert).filter(AnomalyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.disposition = req.disposition
    
    audit = AuditEvent(
        container_id=alert.container_id,
        event_type="Anomaly Alert Reviewed",
        source_module="Fraud & Anomaly Detection",
        rule_model_version="v2.1.0-rules",
        payload_snapshot=f"Alert {alert.rule_code} set to {req.disposition}.",
        actor=req.reviewer,
        decision=req.disposition,
        override_reason=req.note
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Disposition updated successfully", "disposition": alert.disposition}
