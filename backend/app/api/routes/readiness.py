from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.domain import Container, ReadinessValidation

router = APIRouter(prefix="/readiness", tags=["Readiness Validation"])

@router.get("/{container_id}")
def get_readiness_status(container_id: int, db: Session = Depends(get_db)):
    r = db.query(ReadinessValidation).filter(ReadinessValidation.container_id == container_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Readiness validation record not found.")
    return r

@router.post("/validate/{container_id}")
def validate_container_readiness(container_id: int, db: Session = Depends(get_db)):
    c = db.query(Container).filter(Container.container_id == container_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Container not found.")

    r = db.query(ReadinessValidation).filter(ReadinessValidation.container_id == container_id).first()
    if not r:
        r = ReadinessValidation(container_id=container_id)
        db.add(r)

    is_ready = r.payment_completed and r.documents_available and r.permit_available and r.container_arrived
    r.ready_for_schedule = is_ready
    c.status = "Ready" if is_ready else "Pending"

    db.commit()
    return {"container_id": container_id, "ready_for_schedule": is_ready, "status": c.status}
