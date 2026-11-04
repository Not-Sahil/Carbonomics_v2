# CARBONOMICS v3 — Intelligent Carbon Intelligence Platform
### AI-Powered Digital Infrastructure Monitoring, Predictive Analytics & Green Computing Optimization

[![Version](https://img.shields.io/badge/version-3.0.0-emerald.svg)](https://github.com/Not-Sahil/Carbonomics_v2)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38BDF8.svg)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-black.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-red.svg)](https://www.sqlalchemy.org/)
[![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-1.3-F7931E.svg)](https://scikit-learn.org/)
[![GSF SCI](https://img.shields.io/badge/Standard-GSF%20SCI%20v2.1-16C784.svg)](https://greensoftware.foundation/)

---

## 1. Project Introduction

**Carbonomics v3** transforms enterprise digital sustainability from static retrospective estimates into a **real-time, physics-grounded, machine-learning-driven carbon intelligence platform**. 

It measures hardware telemetry across endpoints, datacenter servers, and cloud workloads; calculates Software Carbon Intensity (SCI) according to Green Software Foundation standards; detects operational anomalies; projects time-series emissions with 95% confidence intervals; and provides actionable, prioritized carbon abatement recommendations.

---

## 2. Key Capabilities & Platform Modules

1. **Executive Overview Dashboard:** Real-time KPI summary (Total Carbon, Electricity MWh, Fleet Nodes, Efficiency Score, Abatement Potential) with diurnal trend area charts and device distribution.
2. **Live Telemetry Daemon:** 3-second live hardware streaming of CPU load, RAM allocation, storage usage, power draw in Watts, active network rates, and top computing processes.
3. **Fleet Inventory Management:** Persistent device registry with search, category filtering, department tagging, and detailed hardware node drawers.
4. **Multi-Modal Carbon Estimator:** Dedicated physics calculators for physical client hardware, API microservices, cloud virtual machines, and batch CSV drag-and-drop file ingestion.
5. **Machine Learning & SHAP Explainability:** Dual-stage regression ($R^2=0.9788$), calibrated Isolation Forest anomaly detection, K-Means clustering ($k=4$), and local SHAP feature attribution.
6. **Predictive Time-Series Forecasting:** Autoregressive lagged Gradient Boosting projecting 24h, 7d, 30d, 90d, and 6-month trajectories with heteroscedastic confidence envelopes.
7. **Carbon Abatement Center:** Prioritized actionable protocols (Cloud Region Migration, Idle Sleep Policies, CPU Core Right-Sizing, Storage Tiering) with implementation steps.
8. **Interactive What-If Simulator:** Dynamic sliders for CPU duty, fleet size, uptime, and grid zones computing instantaneous CO₂e reductions, dollar OPEX savings, and trees saved.
9. **Green Cloud Intelligence:** Global 11-region comparison matrix across AWS, GCP, and Azure with a Carbon-Aware Batch Scheduler that time-shifts jobs to align with renewable peaks.
10. **ESG Reporting & Scopes:** Verifiable GHG Protocol accounting across Scope 1 (Direct), Scope 2 (Electricity), and Scope 3 (Embodied Manufacturing), with one-click CSV audit export.
11. **AI Carbon Advisor:** Conversational assistant grounded in verified database telemetry that answers footprint queries and cites backend analytical tools.
12. **Platform Governance & Settings:** Organization parameters, regional grid emission factor overrides, and instant device agent onboarding scripts.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts, Framer Motion, Lucide React |
| **Backend API** | Python 3.11, Flask, Flask-CORS, Gunicorn, REST, Server-Sent Events (SSE) |
| **Persistence** | SQLAlchemy 2.0 ORM, SQLite (local zero-config), PostgreSQL (Docker / production) |
| **Machine Learning** | Scikit-learn (GradientBoosting, RandomForest, IsolationForest, KMeans), Pandas, NumPy, Joblib |
| **Telemetry Edge** | Python `psutil`, PyNVML (NVIDIA GPU), cross-platform hardware sampling |
| **Containerization** | Docker, Docker Compose (multi-stage builds) |

---

## 4. Machine Learning Benchmarks

Trained and evaluated on `data/devices_4500.csv` with an 80/20 stratified train-test split:

- **Carbon Regressor:** GradientBoostingRegressor — **$R^2 = 0.9788$**, **$\text{MAE} = 0.0142 \text{ kg CO}_2\text{e}$**
- **Energy Regressor:** Log1p RandomForestRegressor — **$R^2 = 0.9664$** (guaranteed physical non-negativity)
- **Anomaly Scoring:** Calibrated Isolation Forest (5% contamination) with severity classification
- **Fleet Clustering:** K-Means ($k=4$) into *Energy Efficient*, *Moderate*, *High*, and *Optimization Required*

---

## 5. Quick Start & Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.11)
- Node.js 18+ (tested on Node v22.15.0)

### Step 1: Install Backend Dependencies
```powershell
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r backend/requirements.txt
```

### Step 2: Start Backend Server
```powershell
python backend/api/app.py
```
*Backend active at:* `http://localhost:5000` (API & automatic database initialization)

### Step 3: Start Next.js Enterprise Frontend
Open a new terminal:
```powershell
cd frontend
npm install
npm run dev
```
*Frontend Dashboard active at:* [`http://localhost:3000`](http://localhost:3000)

### Step 4 (Optional): Start Device Agent
To stream live telemetry from your local machine to the fleet dashboard:
```powershell
python device_agent/agent.py --server http://localhost:5000 --region ap-south-1 --device-type laptop
```

---

## 6. Docker Deployment

Launch full enterprise stack (PostgreSQL + Flask Backend + Next.js Frontend) in one command:
```bash
docker-compose up --build -d
```

---

## 7. Testing

Execute complete unit and integration test suite:
```powershell
.venv\Scripts\python -m unittest discover -s tests -p "test_*.py"
```
All 12 unit tests across physics equations, ML models, and REST endpoints pass with 100% compliance.

---

## 8. Documentation Index

- [`ARCHITECTURE.md`](ARCHITECTURE.md): System architecture, GSF-SCI mathematical equations, and component topology.
- [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md): Complete REST endpoint reference and JSON schemas.
- [`ML_DOCUMENTATION.md`](ML_DOCUMENTATION.md): Dataset specifications, cross-validation metrics, and explainability.
- [`DEPLOYMENT.md`](DEPLOYMENT.md): Production guidelines, Docker configuration, and cloud deployment.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): Collaboration standards and git branch workflows.

---

## 9. Contributors & License

Maintained collaboratively by the **Carbonomics Core Engineering Team**.  
Licensed under the MIT License.

