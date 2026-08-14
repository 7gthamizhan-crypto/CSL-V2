from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.connection import get_db
from app.models.domain import Container, Officer, ExaminationBay, Scanner

router = APIRouter(prefix="/simulator", tags=["Scenario Simulator"])

class ScenarioRequest(BaseModel):
    officer_absent: Optional[bool] = False
    bay_closed: Optional[bool] = False
    scanner_failure: Optional[bool] = False
    increased_workload: Optional[bool] = False

@router.post("/run")
def run_simulation(req: ScenarioRequest, db: Session = Depends(get_db)):
    total_containers = db.query(Container).filter(Container.status.in_(["Ready", "Pending", "Scheduled"])).count()
    if total_containers == 0:
        total_containers = 134

    total_officers = db.query(Officer).filter(Officer.availability == True).count() or 12
    total_bays = db.query(ExaminationBay).filter(ExaminationBay.status == "Available").count() or 10

    # Baseline daily capacity: ~48 containers per day across officers & bays
    base_scheduled = min(total_containers, 48)
    base_wait = 35.0
    base_util = 82.0

    sim_scheduled = base_scheduled
    sim_wait = base_wait
    sim_util = base_util
    impact_notes = []

    if req.officer_absent:
        # 25% staff absence (3 out of 12 officers absent) -> reduces daily capacity by 25%
        absent_count = max(1, int(total_officers * 0.25))
        capacity_loss = int(base_scheduled * 0.25)
        sim_scheduled = max(12, sim_scheduled - capacity_loss)
        sim_wait += 35.0
        sim_util += 12.0
        impact_notes.append(
            f"Staff Shortage ({absent_count} Officers Absent / 25% reduced): "
            f"Daily examination capacity drops by {capacity_loss} containers/day. "
            f"Remaining containers are deferred to Day 2/3, and queue waiting time increases by +35 mins."
        )

    if req.bay_closed:
        capacity_loss = int(base_scheduled * 0.15)
        sim_scheduled = max(10, sim_scheduled - capacity_loss)
        sim_wait += 25.0
        sim_util += 8.0
        impact_notes.append(
            f"Examination Bay Closure (1 Bay Inactive): "
            f"Physical inspection throughput decreases by {capacity_loss} containers/day."
        )

    if req.scanner_failure:
        capacity_loss = int(base_scheduled * 0.10)
        sim_scheduled = max(10, sim_scheduled - capacity_loss)
        sim_wait += 40.0
        impact_notes.append(
            "Scanner Failure / Maintenance: Scanner-designated cargo requires manual unpacking, "
            "adding +40 mins dwell time per container."
        )

    if req.increased_workload:
        sim_wait += 45.0
        sim_util = min(100.0, sim_util + 15.0)
        impact_notes.append(
            "Port Volume Surge (+40 Containers arriving at quay): Overall port backlog increases."
        )

    return {
        "baseline": {
            "containers_scheduled": base_scheduled,
            "avg_waiting_time_mins": base_wait,
            "resource_utilization_pct": base_util
        },
        "simulation": {
            "containers_scheduled": sim_scheduled,
            "avg_waiting_time_mins": sim_wait,
            "resource_utilization_pct": min(100.0, sim_util)
        },
        "impact_notes": impact_notes
    }
