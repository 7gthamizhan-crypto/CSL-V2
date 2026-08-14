import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database.connection import engine, Base, SessionLocal
from app.sample_data.generator import seed_sample_data
from app.api.routes import (
    dashboard, containers, risk, readiness, schedule, resources, simulator, reports,
    recommendations, anomalies, documents, hs_intelligence, outcomes, data_quality, audit
)

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

# Seed synthetic data if empty
db = SessionLocal()
try:
    seed_sample_data(db)
finally:
    db.close()

app = FastAPI(
    title="Sri Lanka Customs Examination Optimizer (CEO)",
    description="Enterprise decision support system for import container scheduling and resource optimization using Google OR-Tools CP-SAT Solver.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(containers.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(readiness.router, prefix="/api/v1")
app.include_router(schedule.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")
app.include_router(simulator.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(anomalies.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(hs_intelligence.router, prefix="/api/v1")
app.include_router(outcomes.router, prefix="/api/v1")
app.include_router(data_quality.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")

# Serve frontend build in production if dist directory exists
dist_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            return None
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "message": "Sri Lanka Customs Examination Optimizer (CEO) API is active.",
            "docs": "/docs",
            "version": "1.0.0"
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
