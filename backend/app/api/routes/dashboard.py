from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.domain import Container, Schedule, Officer, ExaminationBay, RiskAssessment, Recommendation, ReadinessValidation, AnomalyAlert, Document

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_summary(db: Session = Depends(get_db)):
    all_containers = db.query(Container).all()
    total_containers = len(all_containers)
    
    critical_high = db.query(RiskAssessment).filter(RiskAssessment.risk_level.in_(["Critical", "High"])).count()
    ai_review_req = db.query(Recommendation).filter(Recommendation.status.in_(["Open", "Needs Further Review"])).count()
    ready_for_schedule = db.query(ReadinessValidation).filter(ReadinessValidation.readiness_status == "Ready").count()
    scheduled_today = db.query(Container).filter(Container.status == "Scheduled").count()
    blocked_count = db.query(ReadinessValidation).filter(ReadinessValidation.readiness_status == "Blocked").count()
    
    officers = db.query(Officer).filter(Officer.availability == True).all()
    bays = db.query(ExaminationBay).filter(ExaminationBay.status == "Available").count() or 1
    schedules = db.query(Schedule).all()
    
    total_off_cap = sum(o.daily_capacity for o in officers) or 60
    assigned_slots = len(schedules)
    officer_utilization = min(98, int((assigned_slots / max(total_off_cap, 1)) * 100))
    
    occupied_mins = sum(45 for s in schedules)
    total_bay_mins = bays * 540
    bay_utilization = min(98, int((occupied_mins / max(total_bay_mins, 1)) * 100))
    
    # 8 KPI Cards
    kpis = {
        "total_containers": total_containers,
        "critical_high_risk": critical_high,
        "ai_review_required": ai_review_req,
        "ready_for_scheduling": ready_for_schedule,
        "scheduled_today": scheduled_today,
        "blocked": blocked_count,
        "officer_utilization": f"{officer_utilization}%",
        "bay_utilization": f"{bay_utilization}%"
    }
    
    # Funnel
    funnel = [
        {"stage": "Received", "count": total_containers},
        {"stage": "Risk Screened", "count": db.query(RiskAssessment).count()},
        {"stage": "Ready", "count": ready_for_schedule},
        {"stage": "Scheduled", "count": scheduled_today},
        {"stage": "Completed", "count": db.query(Container).filter(Container.status == "Completed").count()}
    ]
    
    # Risk Distribution Donut
    risk_dist = [
        {"name": lvl, "value": db.query(RiskAssessment).filter(RiskAssessment.risk_level == lvl).count()}
        for lvl in ["Critical", "High", "Medium", "Low"]
    ]
    
    # AI Review Reasons
    reasons_count = {}
    for r in db.query(Recommendation).all():
        reasons_count[r.type] = reasons_count.get(r.type, 0) + 1
    ai_reasons = [{"reason": k, "count": v} for k, v in sorted(reasons_count.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    # Officer Workload
    officer_workload = []
    for o in officers[:8]:
        assigned = db.query(Schedule).filter(Schedule.officer_id == o.officer_id).count()
        officer_workload.append({"officer_name": o.officer_name.split(" ")[0], "assigned_minutes": assigned * 45})
        
    # Bay Utilization
    bay_data = []
    for b in db.query(ExaminationBay).all():
        assigned = db.query(Schedule).filter(Schedule.bay_id == b.bay_id).count()
        util = min(100, int((assigned * 45 / 540) * 100))
        bay_data.append({"bay_name": b.bay_name, "utilization_pct": util})

    # Main Table
    table_items = []
    for c in all_containers[:15]:
        risk = c.risk_assessment
        readiness = c.readiness_validation
        rec = db.query(Recommendation).filter(Recommendation.container_id == c.container_id).first()
        anom = db.query(AnomalyAlert).filter(AnomalyAlert.container_id == c.container_id).first()
        doc = db.query(Document).filter(Document.container_id == c.container_id).first()
        sched = db.query(Schedule).filter(Schedule.container_id == c.container_id).first()
        
        table_items.append({
            "container_id": c.container_id,
            "container_number": c.container_number,
            "cusdec_number": c.cusdec_number,
            "importer": c.importer.importer_name if c.importer else "N/A",
            "risk_level": risk.risk_level if risk else "Low",
            "risk_score": risk.final_score if risk else 0,
            "anomaly_alerts": anom.severity if anom else "None",
            "document_status": doc.status if doc else "Verified",
            "readiness_status": readiness.readiness_status if readiness else "Ready",
            "recommended_action": rec.recommended_action if rec else (risk.recommended_action if risk else "Standard Exam"),
            "scheduled_time": sched.start_time.strftime("%H:%M") if (sched and sched.start_time) else "Not Scheduled"
        })

    return {
        "kpis": kpis,
        "visuals": {
            "pipeline_funnel": funnel,
            "risk_distribution": risk_dist,
            "ai_review_reasons": ai_reasons,
            "officer_workload": officer_workload,
            "bay_utilization": bay_data,
            "daily_capacity": {"used_minutes": occupied_mins, "capacity_minutes": total_bay_mins}
        },
        "main_table": table_items
    }
