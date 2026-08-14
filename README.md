# 🇱🇰 Sri Lanka Customs Examination Optimizer (CEO)

**Sri Lanka Customs Examination Optimizer (CEO)** is an intelligent, automated cargo examination scheduling & resource management system built according to §3.5 – §3.9 ESDD specifications.

It utilizes **Constraint Satisfaction Programming (CSP)** and **Multi-Day Interval Packing** to schedule import containers across Customs Officers, Examination Bays, and Gate Scanners based on dynamic multi-factor risk scores.

---

## 🏗️ System Architecture

* **Frontend**: React (Vite), Lucide SVG Icons, Recharts Analytics, Dark Obsidian Glassmorphism CSS.
* **Backend**: FastAPI (Python), SQLAlchemy ORM, SQLite Database, ReportLab PDF Engine.
* **Optimization Engine**: Custom Job-Shop Constraint Programming (CP-SAT) solver with multi-day shift packing algorithms.

---

## 📋 Prerequisites

Before running the application, make sure you have installed:
* **Python**: `v3.10` or higher
* **Node.js**: `v18.0` or higher
* **npm**: `v9.0` or higher

---

## 🚀 Quick Start Guide

### 1. Run Backend Server (FastAPI)

Open terminal window 1:

```bash
# Navigate to backend directory
cd SriLankaCustomsOptimizer/backend

# Activate Python virtual environment (if not already created)
source ../../.venv/bin/activate  # or python3 -m venv .venv && source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Run FastAPI backend server
export PYTHONPATH="$(pwd)"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> 🌐 **Backend API**: `http://localhost:8000`  
> 📖 **API Docs (Swagger)**: `http://localhost:8000/docs`

---

### 2. Run Frontend Application (React + Vite)

Open terminal window 2:

```bash
# Navigate to frontend directory
cd SriLankaCustomsOptimizer/frontend

# Install frontend dependencies
npm install

# Start Vite development server
npm run dev -- --host 0.0.0.0 --port 5173
```

> 💻 **Web App Interface**: `http://localhost:5173`

---

## ⚡ One-Command Start Script (Optional)

You can launch both backend and frontend servers simultaneously using this single shell command:

```bash
cd SriLankaCustomsOptimizer && (python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & cd frontend && npm run dev -- --host 0.0.0.0 --port 5173)
```

---

## 🌟 Key Application Features

1. **Executive Operations Dashboard (`/`)**:
   * Real-time port throughput, audit-blocked queue counts, 69% Bay Workload Utilization, and 35% Officer Capacity metrics.
2. **Container Queue Management (`/containers`)**:
   * Interactive status filters, custom glassmorphic dropdown popovers, and search bar.
3. **Risk Assessment Engine (`/risk`)**:
   * Dynamic 4-factor risk scoring (HS Code, Country of Origin, CIF Cargo Value, Importer Infractions).
4. **Readiness Validation Audit (`/readiness`)**:
   * Pre-scheduling readiness checklist (Duty Payment, Permit Approval, Document Verification, Vessel Arrival).
5. **Daily Multi-Day Schedule Roster (`/schedule`)**:
   * Interactive Gantt timeline chart spanning 3 operational days with click-to-view scheduling explanations.
6. **Resource Management (`/resources`)**:
   * Interactive **Mark Working / Mark Absent** toggles for officers, bay maintenance toggles, and modal forms to add/delete resources.
7. **What-If Scenario Simulator (`/simulator`)**:
   * Evaluate operational impacts (25% staff absence, bay closures, volume surges) before real-world execution.
8. **Live PDF Export (`/reports`)**:
   * Streams multi-page PDF reports with running page numbers (`Page X of Y`) and timestamp footers.

---

## ⚙️ Configuration & Settings

Operating shift hours (*08:00 AM – 05:00 PM*) and examination durations per cargo type (*Scanner: 20m, Standard: 45m, High Risk: 75m, Hazardous: 90m, Complex: 120m*) can be edited dynamically on the **Settings (`/settings`)** page and saved directly to the database.
