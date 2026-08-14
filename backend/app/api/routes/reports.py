import io
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.domain import Report, Setting, Schedule, Container, RiskAssessment, Officer, ExaminationBay
from app.schemas.dto import SettingUpdate

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

router = APIRouter(tags=["Reports & Settings"])

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that draws running header line and 'Page X of Y' + Date footer on every page"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Footer Date & Page Number
        date_str = datetime.now().strftime("%d %b %Y, %H:%M:%S")
        footer_text = f"Report Date: {date_str} | Sri Lanka Customs Optimization System (CEO)"
        page_str = f"Page {self._pageNumber} of {page_count}"

        # Draw footer line & text
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 36, A4[0] - 36, 36)

        self.drawString(36, 22, footer_text)
        self.drawRightString(A4[0] - 36, 22, page_str)

        self.restoreState()


@router.get("/reports/pdf/download")
def download_pdf_report(db: Session = Depends(get_db)):
    containers = db.query(Container).join(RiskAssessment, isouter=True).order_by(Container.container_id.asc()).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceAfter=15
    )

    cell_header_style = ParagraphStyle(
        'CellHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#ffffff'),
        alignment=0
    )

    cell_style = ParagraphStyle(
        'CellText',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b'),
        alignment=0
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("SRI LANKA CUSTOMS DEPARTMENT", title_style))
    story.append(Paragraph("DAILY CONTAINER EXAMINATION ROSTER & OPTIMIZATION REPORT", subtitle_style))

    # Executive Summary Box
    total_cnt = len(containers)
    ready_cnt = sum(1 for c in containers if c.status in ["Ready", "Scheduled"])
    scheduled_cnt = sum(1 for c in containers if c.status == "Scheduled")
    critical_cnt = sum(1 for c in containers if c.risk_assessment and c.risk_assessment.risk_level in ["High", "Critical"])

    summary_data = [
        [
            Paragraph(f"<b>Total Containers:</b> {total_cnt}", cell_style),
            Paragraph(f"<b>Eligible/Ready:</b> {ready_cnt}", cell_style),
            Paragraph(f"<b>Scheduled:</b> {scheduled_cnt}", cell_style),
            Paragraph(f"<b>High/Critical Risk:</b> {critical_cnt}", cell_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Data Table Header
    table_headers = [
        Paragraph("Container No", cell_header_style),
        Paragraph("CusDec No", cell_header_style),
        Paragraph("Origin", cell_header_style),
        Paragraph("HS Code", cell_header_style),
        Paragraph("Exam Category", cell_header_style),
        Paragraph("Risk Level", cell_header_style),
        Paragraph("Assigned Officer", cell_header_style),
        Paragraph("Bay / Time", cell_header_style)
    ]

    table_data = [table_headers]

    for c in containers:
        # Check if container has active schedule
        sched = db.query(Schedule).filter(Schedule.container_id == c.container_id).first()
        officer_name = sched.officer.officer_name if sched and sched.officer else "Unassigned"
        bay_time = f"{sched.bay.bay_name} ({sched.start_time})" if sched and sched.bay else "Pending"
        r_level = c.risk_assessment.risk_level if c.risk_assessment else "Low"

        row = [
            Paragraph(c.container_number, cell_style),
            Paragraph(c.cusdec_number, cell_style),
            Paragraph(c.country_of_origin, cell_style),
            Paragraph(c.hs_code, cell_style),
            Paragraph(c.examination_type, cell_style),
            Paragraph(r_level, cell_style),
            Paragraph(officer_name, cell_style),
            Paragraph(bay_time, cell_style)
        ]
        table_data.append(row)

    # Column Widths total = 520pt (fitting A4 page width)
    col_widths = [75, 75, 55, 45, 75, 50, 75, 70]

    data_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))

    story.append(data_table)

    # Build PDF using custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    filename = f"Customs_Container_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).all()
    if not reports:
        rep1 = Report(report_name="Daily Customs Examination Timetable", report_type="PDF", generated_by="Superintendent Bandara")
        rep2 = Report(report_name="Customs Officer Workload & Performance Audit", report_type="PDF", generated_by="Superintendent Bandara")
        rep3 = Report(report_name="Container Risk Distribution & Dwell Time Analysis", report_type="PDF", generated_by="System Scheduler")
        db.add_all([rep1, rep2, rep3])
        db.commit()
        reports = db.query(Report).all()
    return reports


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return db.query(Setting).all()


@router.post("/reset-demo-data")
def reset_all_demo_data(db: Session = Depends(get_db)):
    from app.sample_data.generator import seed_sample_data
    seed_sample_data(db, force=True)
    return {"status": "success", "message": "All demonstration data, reviews, and schedules have been reset to default state!"}

@router.put("/settings/{setting_id}")
def update_setting(setting_id: int, payload: SettingUpdate, db: Session = Depends(get_db)):
    st = db.query(Setting).filter(Setting.setting_id == setting_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Setting not found.")
    st.setting_value = payload.setting_value
    db.commit()
    db.refresh(st)
    return st
