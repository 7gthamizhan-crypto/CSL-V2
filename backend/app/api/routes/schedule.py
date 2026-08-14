from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.domain import Schedule, Container, Officer, ExaminationBay, Scanner
from app.optimizer.engine import run_schedule_optimization

router = APIRouter(prefix="/schedule", tags=["Scheduling Engine"])

@router.post("/generate")
def generate_schedule(db: Session = Depends(get_db)):
    result = run_schedule_optimization(db)
    if result["status"] in ["NO_DATA", "NO_RESOURCES", "INFEASIBLE"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("")
def get_schedules(db: Session = Depends(get_db)):
    schedules = db.query(Schedule).all()
    results = []
    for s in schedules:
        c = db.query(Container).filter(Container.container_id == s.container_id).first()
        o = db.query(Officer).filter(Officer.officer_id == s.officer_id).first()
        b = db.query(ExaminationBay).filter(ExaminationBay.bay_id == s.bay_id).first()
        sc = db.query(Scanner).filter(Scanner.scanner_id == s.scanner_id).first() if s.scanner_id else None

        results.append({
            "schedule_id": s.schedule_id,
            "container_id": s.container_id,
            "container_number": c.container_number if c else "N/A",
            "cusdec_number": c.cusdec_number if c else "N/A",
            "examination_type": c.examination_type if c else "N/A",
            "risk_level": c.risk_assessment.risk_level if c and c.risk_assessment else "Low",
            "officer_name": o.officer_name if o else "N/A",
            "bay_name": b.bay_name if b else "N/A",
            "scanner_name": sc.scanner_name if sc else "None",
            "start_time": s.start_time.isoformat() if s.start_time else "2026-07-30T08:00:00",
            "end_time": s.end_time.isoformat() if s.end_time else "2026-07-30T08:45:00",
            "status": s.status,
            "explanation": s.explanation
        })
    return results

@router.get("/today")
def get_today_schedule(db: Session = Depends(get_db)):
    return get_schedules(db)

@router.post("/reset")
def reset_schedule_demo(db: Session = Depends(get_db)):
    # Clear all schedules
    db.query(Schedule).delete(synchronize_session=False)
    
    # Set all ready/scheduled containers back to Ready
    db.query(Container).filter(Container.status.in_(["Scheduled", "Completed", "Pending"])).update(
        {Container.status: "Ready"}, synchronize_session=False
    )
    
    db.commit()
    return {"message": "Demonstration data reset successfully. All containers are now ready for scheduling!"}
