import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.domain import Container, Officer, ExaminationBay, Scanner, Schedule, ReadinessValidation, RiskAssessment, Setting

def parse_hour_from_setting(time_str: str, default_hour: int) -> int:
    try:
        clean_str = time_str.strip().upper()
        match = re.search(r'(\d{1,2}):?(\d{2})?\s*(AM|PM)?', clean_str)
        if match:
            h = int(match.group(1))
            ampm = match.group(3)
            if ampm == "PM" and h < 12:
                h += 12
            elif ampm == "AM" and h == 12:
                h = 0
            return h
        return default_hour
    except Exception:
        return default_hour

def run_schedule_optimization(db: Session, target_date: datetime = None) -> Dict[str, Any]:
    # 0. Load dynamic system settings from DB
    db_settings = db.query(Setting).all()
    settings_dict = {s.setting_name: s.setting_value for s in db_settings}

    exam_durations = {
        "Scanner": int(settings_dict.get("Scanner Exam Duration", "20")),
        "Standard": int(settings_dict.get("Standard Exam Duration", "45")),
        "High Risk": int(settings_dict.get("High Risk Exam Duration", "75")),
        "Hazardous": int(settings_dict.get("Hazardous Exam Duration", "90")),
        "Complex": int(settings_dict.get("Complex Exam Duration", "120"))
    }

    start_hour = parse_hour_from_setting(settings_dict.get("Working Hours Start", "08:00 AM"), 8)
    end_hour = parse_hour_from_setting(settings_dict.get("Working Hours End", "05:00 PM"), 17)

    if end_hour <= start_hour:
        end_hour = start_hour + 9

    total_work_minutes = (end_hour - start_hour) * 60

    if target_date is None:
        target_date = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    else:
        target_date = target_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)

    # 1. Load ready containers sorted by Risk Score descending (highest risk first)
    ready_containers = (
        db.query(Container)
        .join(ReadinessValidation)
        .join(RiskAssessment)
        .filter(
            ReadinessValidation.ready_for_schedule == True,
            Container.status.in_(["Pending", "Ready", "Scheduled"])
        )
        .order_by(RiskAssessment.risk_score.desc())
        .all()
    )

    if not ready_containers:
        return {"status": "NO_DATA", "scheduled_count": 0, "message": "No ready containers eligible for scheduling."}

    # Load available resources
    available_officers = db.query(Officer).filter(Officer.availability == True).all()
    available_bays = db.query(ExaminationBay).filter(ExaminationBay.status == "Available").all()
    available_scanners = db.query(Scanner).filter(Scanner.availability == True).all()

    if not available_officers or not available_bays:
        return {"status": "NO_RESOURCES", "scheduled_count": 0, "message": "Insufficient officers or examination bays available."}

    # Clear current schedules before inserting multi-day optimization results
    db.query(Schedule).delete(synchronize_session=False)

    scheduled_results = []
    
    # We maintain officer, bay, scanner schedules per day index (0, 1, 2, ...)
    day_officer_schedules: Dict[int, Dict[int, List[tuple]]] = {}
    day_bay_schedules: Dict[int, Dict[int, List[tuple]]] = {}
    day_scanner_schedules: Dict[int, Dict[int, List[tuple]]] = {}

    def get_day_resource_schedules(day_idx: int):
        if day_idx not in day_officer_schedules:
            day_officer_schedules[day_idx] = {o.officer_id: [] for o in available_officers}
            day_bay_schedules[day_idx] = {b.bay_id: [] for b in available_bays}
            day_scanner_schedules[day_idx] = {s.scanner_id: [] for s in available_scanners}
        return day_officer_schedules[day_idx], day_bay_schedules[day_idx], day_scanner_schedules[day_idx]

    max_days_limit = 10

    for c in ready_containers:
        duration = exam_durations.get(c.examination_type, 45)
        assigned = False

        # Try scheduling in Day 0, Day 1, Day 2, etc.
        for day_idx in range(max_days_limit):
            off_sched, bay_sched, scan_sched = get_day_resource_schedules(day_idx)
            current_day_date = target_date + timedelta(days=day_idx)

            for start_min in range(0, total_work_minutes - duration + 1, 15):
                end_min = start_min + duration

                # Find matching officer free during [start_min, end_min]
                selected_officer = None
                for o in available_officers:
                    if c.examination_type in ["Hazardous", "Complex"] and o.qualification not in [c.examination_type, "Complex", "Hazardous"]:
                        continue
                    overlap = any(not (end_min <= s_min or start_min >= e_min) for s_min, e_min in off_sched[o.officer_id])
                    if not overlap:
                        selected_officer = o
                        break

                if not selected_officer:
                    continue

                # Find matching bay free during [start_min, end_min]
                selected_bay = None
                for b in available_bays:
                    if c.examination_type == "Hazardous" and b.bay_type != "Hazardous":
                        continue
                    overlap = any(not (end_min <= s_min or start_min >= e_min) for s_min, e_min in bay_sched[b.bay_id])
                    if not overlap:
                        selected_bay = b
                        break

                if not selected_bay:
                    continue

                # Scanner requirement check
                selected_scanner = None
                if c.examination_type == "Scanner" and available_scanners:
                    for s in available_scanners:
                        overlap = any(not (end_min <= s_min or start_min >= e_min) for s_min, e_min in scan_sched[s.scanner_id])
                        if not overlap:
                            selected_scanner = s
                            break
                    if not selected_scanner:
                        selected_scanner = available_scanners[0]

                # Record schedule for this day
                off_sched[selected_officer.officer_id].append((start_min, end_min))
                bay_sched[selected_bay.bay_id].append((start_min, end_min))
                if selected_scanner:
                    scan_sched[selected_scanner.scanner_id].append((start_min, end_min))

                start_dt = current_day_date + timedelta(minutes=start_min)
                end_dt = current_day_date + timedelta(minutes=end_min)

                start_str = start_dt.strftime("%H:%M")
                day_str = current_day_date.strftime("%Y-%m-%d")

                r_score = c.risk_assessment.risk_score if c.risk_assessment else 45
                r_level = c.risk_assessment.risk_level if c.risk_assessment else "Medium"

                explanation = (
                    f"Scheduled on Day {day_idx + 1} ({day_str}) at {start_str} based on Risk Score {r_score} ({r_level}) "
                    f"and configured {c.examination_type} duration ({duration} mins). "
                    f"Assigned Officer: {selected_officer.officer_name} ({selected_officer.qualification}), Bay: {selected_bay.bay_name}."
                )

                sched = Schedule(
                    container_id=c.container_id,
                    officer_id=selected_officer.officer_id,
                    bay_id=selected_bay.bay_id,
                    scanner_id=selected_scanner.scanner_id if selected_scanner else None,
                    start_time=start_dt,
                    end_time=end_dt,
                    status="Scheduled",
                    explanation=explanation
                )
                c.status = "Scheduled"
                db.add(sched)
                scheduled_results.append(sched)
                assigned = True
                break

            if assigned:
                break

    db.commit()

    total_days = max(day_officer_schedules.keys()) + 1 if day_officer_schedules else 1

    return {
        "status": "OPTIMAL",
        "scheduled_count": len(scheduled_results),
        "total_days": total_days,
        "message": f"Successfully generated multi-day schedule for ALL {len(scheduled_results)} containers across {total_days} operational days using configured shift hours ({start_hour:02d}:00 - {end_hour:02d}:00)."
    }
