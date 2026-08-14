from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.models.domain import Container, RiskAssessment, ReadinessValidation

router = APIRouter(prefix="/risk", tags=["Risk Assessment"])

@router.get("")
def get_all_risk_intelligence(
    risk_level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(RiskAssessment).join(Container)
    if risk_level and risk_level != "All":
        query = query.filter(RiskAssessment.risk_level == risk_level)
        
    risks = query.order_by(RiskAssessment.final_score.desc()).all()
    all_risks = db.query(RiskAssessment).all()
    
    avg_score = round(sum(r.final_score for r in all_risks) / max(len(all_risks), 1), 1)
    
    high_ready = 0
    high_blocked = 0
    for r in all_risks:
        if r.risk_level in ["Critical", "High"]:
            rv = r.container.readiness_validation
            if rv and rv.readiness_status == "Ready":
                high_ready += 1
            elif rv and rv.readiness_status == "Blocked":
                high_blocked += 1
                
    kpis = {
        "critical_count": sum(1 for r in all_risks if r.risk_level == "Critical"),
        "high_count": sum(1 for r in all_risks if r.risk_level == "High"),
        "avg_score": avg_score,
        "high_risk_ready": high_ready,
        "high_risk_blocked": high_blocked
    }
    
    by_level = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for r in all_risks:
        if r.risk_level in by_level:
            by_level[r.risk_level] += 1
            
    factor_stack = []
    for r in risks[:10]:
        factor_stack.append({
            "container": r.container.container_number,
            "hs_pts": r.hs_risk_points,
            "country_pts": r.country_risk_points,
            "value_pts": r.value_risk_points,
            "history_pts": r.history_risk_points
        })
        
    items = []
    for r in risks:
        items.append({
            "container_id": r.container.container_id,
            "container_number": r.container.container_number,
            "cusdec_number": r.container.cusdec_number,
            "importer": r.container.importer.importer_name if r.container.importer else "N/A",
            "hs_code": r.container.hs_code,
            "country": r.container.country_of_origin,
            "cif": r.container.cif_value,
            "hs_pts": r.hs_risk_points,
            "country_pts": r.country_risk_points,
            "value_pts": r.value_risk_points,
            "history_pts": r.history_risk_points,
            "anomaly_adj": r.anomaly_adjustment,
            "doc_adj": r.document_adjustment,
            "final_score": r.final_score,
            "risk_level": r.risk_level,
            "recommended_action": r.recommended_action
        })
        
    return {
        "kpis": kpis,
        "charts": {
            "by_level": [{"name": k, "value": v} for k, v in by_level.items()],
            "factor_contribution": factor_stack
        },
        "items": items
    }

@router.get("/{container_id}")
def get_risk_details(container_id: int, db: Session = Depends(get_db)):
    risk = db.query(RiskAssessment).filter(RiskAssessment.container_id == container_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk assessment not found.")
    
    factors = []
    if risk.previous_offences > 0:
        factors.append(f"Previous Offences ({risk.previous_offences})")
    if risk.value_score > 20:
        factors.append("High CIF Cargo Value")
    if risk.hs_score >= 80:
        factors.append("Sensitive HS Code Category")
    if risk.country_score >= 20:
        factors.append("High Risk Country of Origin")

    return {
        "risk_id": risk.risk_id,
        "container_id": risk.container_id,
        "risk_score": risk.final_score,
        "risk_level": risk.risk_level,
        "factors": factors,
        "breakdown": {
            "previous_offences": risk.history_risk_points,
            "country_score": risk.country_risk_points,
            "hs_score": risk.hs_risk_points,
            "value_score": risk.value_risk_points,
            "anomaly_adjustment": risk.anomaly_adjustment,
            "document_adjustment": risk.document_adjustment
        }
    }
