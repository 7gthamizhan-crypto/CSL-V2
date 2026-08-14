import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.domain import (
    Importer, ClearingAgent, Container, Officer, ExaminationBay, Scanner,
    RiskAssessment, ReadinessValidation, Setting, Document, DocumentFieldCheck,
    AnomalyAlert, HSReview, Recommendation, RecommendationReview,
    InspectionOutcome, DataQualityIssue, AuditEvent
)

SRI_LANKAN_COMPANIES = [
    "Lanka Trade Holdings", "Ceylon Logistics Ltd", "Colombo Maritime Imports",
    "Serendib Freight Lines", "Lankan Spice Exports & Imports", "Elephant Brand Traders",
    "Highland Distributing Co", "Apex Lanka Shipping", "Oceanic Cargo Lanka", "Sunstar Global"
]

CLEARING_AGENTS = [
    "TransLanka Clearing Agency", "Island Freight Services", "Ceylon Port Forwarders",
    "Greenlight Logistics", "Customs Express Lanka", "Maritime Clearing Services"
]

HS_CODES = [
    ("870323", "Motor Vehicles passenger 1500cc-3000cc", 85, "High", "870332", "Diesel Passenger Vehicles >2500cc"),
    ("847130", "Laptops and Portable Digital Computers", 25, "Low", "847130", "Laptops and Portable Digital Computers"),
    ("300490", "Medicaments & Pharmaceutical Formulations", 45, "Medium", "300490", "Medicaments & Pharmaceutical Formulations"),
    ("220830", "Whiskies and Distilled Spirits", 95, "Critical", "220890", "Other Spirits & Liqueurs"),
    ("620342", "Cotton Trousers & Men Garments", 15, "Low", "620342", "Cotton Trousers & Men Garments"),
    ("851712", "Mobile Cellular Telephones & Smartphones", 65, "Medium", "851762", "Network Switching & Routing Apparatus"),
    ("271019", "Petroleum & Lubricating Mineral Oils", 90, "Critical", "271019", "Petroleum & Lubricating Mineral Oils"),
    ("070310", "Onions & Agricultural Edible Produce", 35, "Low", "070310", "Onions & Agricultural Edible Produce")
]

COUNTRIES = [
    "China", "India", "Singapore", "Japan", "United Arab Emirates",
    "Germany", "United States", "Malaysia", "United Kingdom", "Vietnam"
]

OFFICER_NAMES = [
    "Bandara K.M.", "Perera W.A.", "Silva S.D.", "Fernando T.M.", "Jayawardena P.K.",
    "Ratnayake R.M.", "Dissanayake D.M.", "Wickramasinghe A.K.", "Gunawardena H.P.",
    "Herath H.M.", "Karunaratne K.L.", "Fonseka G.S.", "Senanayake C.P.", "Rajapaksha N.S.",
    "Mendis D.A.", "Peiris M.R.", "Amarasinghe A.T.", "Dias K.V.", "Cooray C.J.",
    "Liyanage L.P.", "Samaraweera S.B.", "Abeysekara A.H.", "Ranasinghe R.P.",
    "Jayasinghe J.M.", "Pathirana P.K."
]

def seed_sample_data(db: Session, force: bool = False):
    # If force or DB has old schema count < 100, clear & re-seed
    if not force and db.query(Container).count() >= 100 and db.query(Recommendation).count() > 0:
        return

    # Delete existing records cleanly if re-seeding
    db.query(AuditEvent).delete()
    db.query(DataQualityIssue).delete()
    db.query(InspectionOutcome).delete()
    db.query(RecommendationReview).delete()
    db.query(Recommendation).delete()
    db.query(HSReview).delete()
    db.query(AnomalyAlert).delete()
    db.query(DocumentFieldCheck).delete()
    db.query(Document).delete()
    db.query(ReadinessValidation).delete()
    db.query(RiskAssessment).delete()
    db.query(Container).delete()
    db.query(Officer).delete()
    db.query(ExaminationBay).delete()
    db.query(Scanner).delete()
    db.query(Importer).delete()
    db.query(ClearingAgent).delete()
    db.commit()

    # 1. Seed Importers (30)
    importers = []
    for i in range(1, 31):
        name = f"{SRI_LANKAN_COMPANIES[(i-1) % len(SRI_LANKAN_COMPANIES)]} {i}"
        code = f"IMP{i:04d}"
        imp = Importer(
            importer_code=code,
            importer_name=name,
            address=f"No. {i*12}, Galle Road, Colombo {(i%15)+1}",
            contact_person=f"Managing Director {i}",
            phone=f"+94 11 2{i:06d}",
            email=f"compliance@{code.lower()}.lk"
        )
        db.add(imp)
        importers.append(imp)
    db.commit()

    # 2. Seed Clearing Agents (15)
    agents = []
    for i in range(1, 16):
        name = f"{CLEARING_AGENTS[(i-1) % len(CLEARING_AGENTS)]} {i}"
        code = f"AGT{i:04d}"
        agt = ClearingAgent(
            agent_code=code,
            agent_name=name,
            phone=f"+94 11 4{i:06d}",
            email=f"operations@{code.lower()}.lk"
        )
        db.add(agt)
        agents.append(agt)
    db.commit()

    # 3. Seed Officers (15)
    officers = []
    qualifications = ["General", "Scanner", "Hazardous", "Complex"]
    for i, name in enumerate(OFFICER_NAMES[:15], 1):
        qual = qualifications[(i - 1) % len(qualifications)]
        off = Officer(
            officer_code=f"OF{i:03d}",
            officer_name=name,
            designation="Senior Inspector" if i % 3 == 0 else "Customs Officer",
            qualification=qual,
            daily_capacity=6,
            availability=True
        )
        db.add(off)
        officers.append(off)
    db.commit()

    # 4. Seed Examination Bays (6)
    bays = []
    for i in range(1, 7):
        b_type = "Hazardous" if i in [5, 6] else "Standard"
        bay = ExaminationBay(
            bay_name=f"Bay {i:02d}",
            bay_type=b_type,
            capacity=1,
            status="Available"
        )
        db.add(bay)
        bays.append(bay)
    db.commit()

    # 5. Seed Scanners (2)
    scanners = [
        Scanner(scanner_name="Scanner Alpha (Gate 01)", location="Port Gate 1", capacity=25, availability=True),
        Scanner(scanner_name="Scanner Beta (Gate 04)", location="Port Gate 4", capacity=25, availability=True)
    ]
    for s in scanners:
        db.add(s)
    db.commit()

    # 6. Seed Settings
    settings = [
        Setting(setting_name="Working Hours Start", setting_value="08:00 AM", description="Shift start time"),
        Setting(setting_name="Working Hours End", setting_value="05:00 PM", description="Shift end time"),
        Setting(setting_name="Scanner Exam Duration", setting_value="20", description="Duration in minutes"),
        Setting(setting_name="Standard Exam Duration", setting_value="45", description="Duration in minutes"),
        Setting(setting_name="High Risk Exam Duration", setting_value="75", description="Duration in minutes"),
        Setting(setting_name="Hazardous Exam Duration", setting_value="90", description="Duration in minutes"),
        Setting(setting_name="Complex Exam Duration", setting_value="120", description="Duration in minutes"),
        Setting(setting_name="Critical Risk Threshold", setting_value="80", description="Minimum score for Critical"),
        Setting(setting_name="High Risk Threshold", setting_value="60", description="Minimum score for High"),
        Setting(setting_name="Medium Risk Threshold", setting_value="35", description="Minimum score for Medium"),
    ]
    for st in settings:
        if not db.query(Setting).filter(Setting.setting_name == st.setting_name).first():
            db.add(st)
    db.commit()

    # 7. Seed Hero Container (MSCU4000001) - Complete Cross-Module Life Cycle
    hero_imp = importers[0]
    hero_agent = agents[0]
    hero_cont = Container(
        container_number="MSCU4000001",
        cusdec_number="CUS2026/COL/10001",
        importer_id=hero_imp.importer_id,
        agent_id=hero_agent.agent_id,
        country_of_origin="Japan",
        hs_code="870323",
        goods_description="Motor Vehicles passenger 1500cc-3000cc (Used SUV Spec)",
        cif_value=18500.00,
        duty_amount=12950.00,
        examination_type="High Risk",
        arrival_date=datetime.utcnow() - timedelta(hours=14),
        status="Ready"
    )
    db.add(hero_cont)
    db.flush()

    # Hero Risk Assessment
    hero_risk = RiskAssessment(
        container_id=hero_cont.container_id,
        risk_score=88,
        risk_level="Critical",
        previous_offences=2,
        country_score=20,
        hs_score=45,
        value_score=23,
        final_score=88,
        hs_risk_points=45,
        country_risk_points=20,
        value_risk_points=10,
        history_risk_points=13,
        anomaly_adjustment=15,
        document_adjustment=10,
        recommended_action="Full Physical Inspection & Valuation Audit"
    )
    db.add(hero_risk)

    # Hero Readiness Validation
    hero_readiness = ReadinessValidation(
        container_id=hero_cont.container_id,
        payment_completed=True,
        documents_available=True,
        permit_available=True,
        container_arrived=True,
        ready_for_schedule=True,
        anomaly_review_status="Review Required",
        hs_review_status="Review Required",
        readiness_status="Ready - Review Required",
        readiness_reason="Unresolved CIF Anomaly and HS Classification Mismatch require officer sign-off before physical examination."
    )
    db.add(hero_readiness)

    # Hero Documents & Field Checks
    hero_doc1 = Document(
        container_id=hero_cont.container_id,
        document_type="Commercial Invoice",
        document_ref="INV-2026-JP-9912",
        extraction_status="Extracted",
        status="Review",
        confidence_score=0.94
    )
    db.add(hero_doc1)
    db.flush()
    db.add(DocumentFieldCheck(document_id=hero_doc1.id, field_name="CIF Value", document_value="$42,500.00", declaration_value="$18,500.00", match_status="Mismatch", issue_type="Value Mismatch"))
    db.add(DocumentFieldCheck(document_id=hero_doc1.id, field_name="Importer Name", document_value="Lanka Trade Holdings 1", declaration_value="Lanka Trade Holdings 1", match_status="Match", issue_type=None))

    hero_doc2 = Document(
        container_id=hero_cont.container_id,
        document_type="Bill of Lading",
        document_ref="BL-MSCU-4000001",
        extraction_status="Extracted",
        status="Verified",
        confidence_score=0.98
    )
    db.add(hero_doc2)
    db.flush()
    db.add(DocumentFieldCheck(document_id=hero_doc2.id, field_name="Port of Loading", document_value="Yokohama, JP", declaration_value="Yokohama, JP", match_status="Match", issue_type=None))

    hero_doc3 = Document(
        container_id=hero_cont.container_id,
        document_type="Import Permit",
        document_ref="PERMIT-MOT-2026-081",
        extraction_status="Extracted",
        status="Review",
        confidence_score=0.89
    )
    db.add(hero_doc3)
    db.flush()
    db.add(DocumentFieldCheck(document_id=hero_doc3.id, field_name="Engine Capacity", document_value="3450 cc", declaration_value="2400 cc", match_status="Mismatch", issue_type="HS Mismatch"))

    # Hero Anomaly Alert
    hero_alert = AnomalyAlert(
        container_id=hero_cont.container_id,
        anomaly_type="CIF Outlier",
        observed_value="$18,500.00",
        reference_value="$45,000.00 (Peer Median)",
        variance_pct=58.88,
        severity="Critical",
        rule_code="RULE_CIF_UNDERVALUATION",
        reason_text="Declared CIF value is 58.8% lower than median reference value ($45,000) for Japanese vehicle imports of similar spec.",
        disposition="Valid Concern"
    )
    db.add(hero_alert)

    # Hero HS Review
    hero_hs = HSReview(
        container_id=hero_cont.container_id,
        goods_description="Motor Vehicles passenger 1500cc-3000cc (Used SUV Spec)",
        declared_hs_code="870323",
        suggested_hs_code="870332",
        suggested_description="Diesel Passenger Vehicles >2500cc",
        confidence=0.92,
        match_status="Mismatch",
        review_decision="Pending",
        review_note="Permit specifies 3450cc engine capacity, which reclassifies vehicle to HS 870332."
    )
    db.add(hero_hs)

    # Hero Recommendation
    hero_rec = Recommendation(
        container_id=hero_cont.container_id,
        source_module="Fraud",
        type="Valuation & Classification Audit",
        severity="Critical",
        recommended_action="Escalate to High-Risk Bay 05 with Hazardous/Complex qualified Officer. Require duty re-assessment.",
        reason_text="CIF under-valuation by 58.8% coupled with engine capacity discrepancy on permit.",
        confidence=0.95,
        status="Open"
    )
    db.add(hero_rec)

    # Hero Data Quality Issue
    hero_dq = DataQualityIssue(
        source_entity="Document",
        record_id=hero_cont.container_number,
        field_name="Engine Capacity",
        issue_type="Inconsistent Value",
        current_value="2400 cc (CusDec) vs 3450 cc (Permit)",
        expected_rule="CusDec declaration must match Ministry of Transport Permit specification",
        severity="Critical",
        validation_rule="VAL_RULE_DOC_CONSISTENCY_04",
        status="Open",
        ai_ready_flag=False
    )
    db.add(hero_dq)

    # Hero Audit Event
    db.add(AuditEvent(
        container_id=hero_cont.container_id,
        event_type="Recommendation Generated",
        source_module="Fraud & Anomaly Engine",
        rule_model_version="v2.1.0-rules",
        payload_snapshot="Declared CIF: $18,500 vs Ref: $45,000. Suggested HS: 870332.",
        actor="AI Fraud Engine",
        decision="Recommendation Pushed to Center",
        override_reason=None
    ))

    # 8. Seed Additional 110 Containers across diverse statuses
    exam_types = ["Scanner", "Standard", "High Risk", "Hazardous", "Complex"]
    statuses = ["Pending", "Ready", "Scheduled", "Completed"]

    for i in range(2, 115):
        c_number = f"MSCU{4000000 + i}"
        cusdec = f"CUS2026/COL/{10000 + i}"
        hs_info = HS_CODES[(i - 1) % len(HS_CODES)]
        cif = round(random.uniform(12000, 280000), 2)
        duty = round(cif * random.uniform(0.12, 0.40), 2)
        exam_type = exam_types[(i - 1) % len(exam_types)]
        imp = random.choice(importers)
        agt = random.choice(agents)
        origin_country = random.choice(COUNTRIES)

        # Status mix
        if i % 5 == 0:
            c_status = "Completed"
        elif i % 3 == 0:
            c_status = "Scheduled"
        elif i % 2 == 0:
            c_status = "Ready"
        else:
            c_status = "Pending"

        cont = Container(
            container_number=c_number,
            cusdec_number=cusdec,
            importer_id=imp.importer_id,
            agent_id=agt.agent_id,
            country_of_origin=origin_country,
            hs_code=hs_info[0],
            goods_description=f"{hs_info[1]} Grade-{(i%3)+1}",
            cif_value=cif,
            duty_amount=duty,
            examination_type=exam_type,
            arrival_date=datetime.utcnow() - timedelta(hours=random.randint(4, 96)),
            status=c_status
        )
        db.add(cont)
        db.flush()

        # Risk Assessment
        base_score = hs_info[2]
        prev_off = 2 if i % 8 == 0 else (1 if i % 4 == 0 else 0)
        country_score = random.randint(5, 30)
        value_score = 30 if cif > 120000 else 10
        final_risk = min(100, base_score + prev_off * 10 + country_score // 2)

        if final_risk >= 80:
            r_level = "Critical"
        elif final_risk >= 60:
            r_level = "High"
        elif final_risk >= 35:
            r_level = "Medium"
        else:
            r_level = "Low"

        risk = RiskAssessment(
            container_id=cont.container_id,
            risk_score=final_risk,
            risk_level=r_level,
            previous_offences=prev_off,
            country_score=country_score,
            hs_score=base_score,
            value_score=value_score,
            final_score=final_risk,
            hs_risk_points=base_score,
            country_risk_points=country_score,
            value_risk_points=value_score,
            history_risk_points=prev_off * 10,
            anomaly_adjustment=10 if r_level in ["Critical", "High"] else 0,
            document_adjustment=5 if r_level == "Critical" else 0,
            recommended_action="Physical Inspection" if final_risk > 60 else "Automated Scanner Pass"
        )
        db.add(risk)

        # Readiness
        is_blocked = (i % 9 == 0)
        needs_review = (r_level in ["Critical", "High"] and not is_blocked)

        if is_blocked:
            r_status = "Blocked"
            r_reason = "Duty Payment Pending & Missing Ministry of Environment Permit."
        elif needs_review:
            r_status = "Ready - Review Required"
            r_reason = "Unresolved AI Recommendation requires supervisory officer review."
        else:
            r_status = "Ready"
            r_reason = "All mandatory payment, permit, and document checks passed."

        ready_val = ReadinessValidation(
            container_id=cont.container_id,
            payment_completed=not is_blocked,
            documents_available=True,
            permit_available=not is_blocked,
            container_arrived=True,
            ready_for_schedule=not is_blocked,
            anomaly_review_status="Review Required" if needs_review else "Passed",
            hs_review_status="Review Required" if (i % 6 == 0) else "Passed",
            readiness_status=r_status,
            readiness_reason=r_reason
        )
        db.add(ready_val)

        # Seed Documents
        doc1 = Document(
            container_id=cont.container_id,
            document_type="Commercial Invoice",
            document_ref=f"INV-2026-COL-{1000+i}",
            extraction_status="Extracted",
            status="Review" if (i % 5 == 0) else "Verified",
            confidence_score=round(random.uniform(0.85, 0.99), 2)
        )
        db.add(doc1)
        db.flush()
        db.add(DocumentFieldCheck(
            document_id=doc1.id,
            field_name="CIF Value",
            document_value=f"${cif:,.2f}",
            declaration_value=f"${cif:,.2f}",
            match_status="Match",
            issue_type=None
        ))

        # Anomaly Alerts for high/critical risk
        if r_level in ["Critical", "High"] or i % 7 == 0:
            anom_type = random.choice(["CIF Outlier", "Importer Frequency", "HS-Country Anomaly", "Quantity Discrepancy"])
            variance = round(random.uniform(25.0, 70.0), 1)
            ref_val = cif * (1 + variance/100)
            alert = AnomalyAlert(
                container_id=cont.container_id,
                anomaly_type=anom_type,
                observed_value=f"${cif:,.2f}",
                reference_value=f"${ref_val:,.2f} (Peer Benchmark)",
                variance_pct=variance,
                severity=r_level,
                rule_code=f"RULE_{anom_type.replace(' ', '_').upper()}",
                reason_text=f"Observed {anom_type} shows {variance}% deviation from standard regional threshold.",
                disposition="Needs Review" if i % 2 == 0 else "Valid Concern"
            )
            db.add(alert)

        # HS Reviews
        is_hsmatch = (hs_info[0] == hs_info[4])
        hs_rev = HSReview(
            container_id=cont.container_id,
            goods_description=cont.goods_description,
            declared_hs_code=hs_info[0],
            suggested_hs_code=hs_info[4],
            suggested_description=hs_info[5],
            confidence=round(random.uniform(0.82, 0.97), 2),
            match_status="Match" if is_hsmatch else "Mismatch",
            review_decision="Accept Declared" if is_hsmatch else "Pending",
            review_note="System verified description alignment." if is_hsmatch else "Possible sub-heading misclassification detected."
        )
        db.add(hs_rev)

        # Recommendations
        if r_level in ["Critical", "High"] or not is_hsmatch:
            rec_status = "Open" if (i % 3 != 0) else "Accepted"
            rec = Recommendation(
                container_id=cont.container_id,
                source_module="Risk" if r_level in ["Critical", "High"] else "HS Intelligence",
                type="Physical Examination" if r_level in ["Critical", "High"] else "Classification Audit",
                severity=r_level,
                recommended_action=f"Assign to {exam_type} Bay for targeted physical inspection and document verification.",
                reason_text=f"High risk score ({final_risk}/100) combined with {r_level} priority indicators.",
                confidence=round(random.uniform(0.85, 0.96), 2),
                status=rec_status
            )
            db.add(rec)
            db.flush()

            if rec_status == "Accepted":
                db.add(RecommendationReview(
                    recommendation_id=rec.id,
                    reviewer="Senior Officer Bandara K.M.",
                    decision="Accepted",
                    override_reason=None,
                    note="Accepted system recommendation for physical examination.",
                    reviewed_at=datetime.utcnow() - timedelta(hours=2)
                ))

        # Data Quality Issues
        if i % 11 == 0:
            db.add(DataQualityIssue(
                source_entity="Container",
                record_id=cont.container_number,
                field_name="Goods Description",
                issue_type="Ambiguous Text",
                current_value=cont.goods_description,
                expected_rule="Description must include specific material composition and commercial brand.",
                severity="Medium",
                validation_rule="VAL_RULE_TEXT_SPECIFICITY",
                status="Open",
                ai_ready_flag=False
            ))

        # Audit Event
        db.add(AuditEvent(
            container_id=cont.container_id,
            event_type="Container Registered",
            source_module="CORE Pipeline",
            rule_model_version="v1.0.0",
            payload_snapshot=f"Container {c_number} arrived from {origin_country}.",
            actor="Port Terminal API",
            decision=None,
            override_reason=None
        ))

    db.commit()
    print("Database successfully seeded with comprehensive Sri Lanka Customs AI Expansion dataset!")

if __name__ == "__main__":
    from app.database.connection import SessionLocal
    db = SessionLocal()
    seed_sample_data(db, force=True)
    db.close()
