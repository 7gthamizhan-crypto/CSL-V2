from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.domain import Officer, ExaminationBay, Scanner, Schedule
from app.schemas.dto import (
    OfficerCreate, OfficerResponse, BayCreate, BayResponse, ScannerCreate, ScannerResponse
)

router = APIRouter(prefix="", tags=["Resource Management"])

# Officers CRUD
@router.get("/officers", response_model=List[OfficerResponse])
def get_officers(db: Session = Depends(get_db)):
    return db.query(Officer).all()

@router.post("/officers", response_model=OfficerResponse)
def create_officer(payload: OfficerCreate, db: Session = Depends(get_db)):
    off = Officer(**payload.model_dump())
    db.add(off)
    db.commit()
    db.refresh(off)
    return off

@router.patch("/officers/{officer_id}/toggle-availability")
def toggle_officer_availability(officer_id: int, db: Session = Depends(get_db)):
    off = db.query(Officer).filter(Officer.officer_id == officer_id).first()
    if not off:
        raise HTTPException(status_code=404, detail="Officer not found.")
    off.availability = not off.availability
    db.commit()
    db.refresh(off)
    return {"officer_id": off.officer_id, "availability": off.availability}

@router.delete("/officers/{officer_id}")
def delete_officer(officer_id: int, db: Session = Depends(get_db)):
    off = db.query(Officer).filter(Officer.officer_id == officer_id).first()
    if not off:
        raise HTTPException(status_code=404, detail="Officer not found.")
    db.query(Schedule).filter(Schedule.officer_id == officer_id).delete(synchronize_session=False)
    db.delete(off)
    db.commit()
    return {"message": "Officer deleted successfully."}

# Bays CRUD
@router.get("/bays", response_model=List[BayResponse])
def get_bays(db: Session = Depends(get_db)):
    return db.query(ExaminationBay).all()

@router.post("/bays", response_model=BayResponse)
def create_bay(payload: BayCreate, db: Session = Depends(get_db)):
    bay = ExaminationBay(**payload.model_dump())
    db.add(bay)
    db.commit()
    db.refresh(bay)
    return bay

@router.patch("/bays/{bay_id}/toggle-status")
def toggle_bay_status(bay_id: int, db: Session = Depends(get_db)):
    bay = bay = db.query(ExaminationBay).filter(ExaminationBay.bay_id == bay_id).first()
    if not bay:
        raise HTTPException(status_code=404, detail="Bay not found.")
    bay.status = "Maintenance" if bay.status == "Available" else "Available"
    db.commit()
    db.refresh(bay)
    return {"bay_id": bay.bay_id, "status": bay.status}

@router.delete("/bays/{bay_id}")
def delete_bay(bay_id: int, db: Session = Depends(get_db)):
    bay = db.query(ExaminationBay).filter(ExaminationBay.bay_id == bay_id).first()
    if not bay:
        raise HTTPException(status_code=404, detail="Bay not found.")
    db.query(Schedule).filter(Schedule.bay_id == bay_id).delete(synchronize_session=False)
    db.delete(bay)
    db.commit()
    return {"message": "Bay deleted successfully."}

# Scanners CRUD
@router.get("/scanners", response_model=List[ScannerResponse])
def get_scanners(db: Session = Depends(get_db)):
    return db.query(Scanner).all()

@router.post("/scanners", response_model=ScannerResponse)
def create_scanner(payload: ScannerCreate, db: Session = Depends(get_db)):
    sc = Scanner(**payload.model_dump())
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc

@router.delete("/scanners/{scanner_id}")
def delete_scanner(scanner_id: int, db: Session = Depends(get_db)):
    sc = db.query(Scanner).filter(Scanner.scanner_id == scanner_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scanner not found.")
    db.query(Schedule).filter(Schedule.scanner_id == scanner_id).update({Schedule.scanner_id: None}, synchronize_session=False)
    db.delete(sc)
    db.commit()
    return {"message": "Scanner deleted successfully."}
