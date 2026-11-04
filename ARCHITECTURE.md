# Carbonomics v3 — System Architecture

**Carbonomics v3** is an enterprise-grade carbon intelligence and green computing infrastructure optimization platform. This document outlines the end-to-end system topology, data pipelines, physics modeling, and deployment architectures.

---

## 1. High-Level Architectural Topology

```
+-----------------------------------------------------------------------------------+
|                            EDGE TELEMETRY & WORKLOADS                             |
|                                                                                   |
|  [ Device Agent (psutil/NVML) ]  [ Microservices (RPC/REST) ]  [ Batch Ingestion] |
|               |                                |                        |         |
|               | (Auth Bearer Token)            | (Payload metrics)      | (CSV)   |
+---------------+--------------------------------+------------------------+---------+
                                 |
                                 v
+-----------------------------------------------------------------------------------+
|                        CENTRAL ENTERPRISE BACKEND (FLASK)                         |
|                                                                                   |
|  +--------------------+  +-----------------------+  +--------------------------+  |
|  | JWT / Auth Control |  | GSF-SCI Carbon Engine |  | What-If & Cloud Sim      |  |
|  +--------------------+  +-----------------------+  +--------------------------+  |
|  | Emission Registry  |  | Persistent Fleet Svc  |  | AI Carbon Advisor Engine |  |
|  +--------------------+  +-----------------------+  +--------------------------+  |
+----------------------------------------+------------------------------------------+
                                         |
               +-------------------------+-------------------------+
               |                                                   |
               v                                                   v
+-----------------------------+               +-------------------------------------+
|   MODULAR MACHINE LEARNING  |               |          DATA PERSISTENCE           |
|                             |               |                                     |
|  - Emission Regressor (GB)  |               |  - SQLAlchemy 2.0 ORM               |
|  - Energy Regressor (RF)    |               |  - SQLite (Local Development)       |
|  - Isolation Forest (Anom)  |               |  - PostgreSQL (Docker / Production) |
|  - K-Means Clustering (k=4) |               |  - Serialized Models (.joblib)      |
|  - Time-Series Forecaster   |               |  - Emission Factor JSON Registry    |
|  - SHAP Explainability Engine|              +-------------------------------------+
+-----------------------------+                                    |
               |                                                   |
               +-------------------------+-------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                  ENTERPRISE DASHBOARD (NEXT.JS 14 / REACT / TS)                   |
|                                                                                   |
|  - Landing Page & Value Proposition       - Interactive What-If Simulator         |
|  - Executive Overview (KPIs, Trends)      - Green Cloud Matrix & Batch Scheduler  |
|  - Real-Time Hardware Telemetry (3s SSE)  - ESG Reporting & Scope 1/2/3 Breakdown |
|  - Fleet Inventory & Device Drawers       - Conversational AI Carbon Advisor      |
|  - Multi-Modal Carbon Estimator (CSV/VM)  - Platform Settings & Agent Onboarding  |
|  - ML Insights & SHAP Feature Importance  - Dark Enterprise Aesthetic (#090D14)   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Architectural Subsystems

### 2.1 Physics-Based Carbon Calculation Engine (`backend/core/carbon_calculator.py`)
Compliant with the **Green Software Foundation (GSF) Software Carbon Intensity (SCI)** specification:
$$\text{SCI} = \frac{(E \times I) + M}{R}$$
Where:
- $E$ is Operational Energy (kWh), modeled using nonlinear active + standby curves for CPU, GPU, RAM, Storage (SSD/HDD), Displays, and Network egress/ingress.
- $I$ is Regional Location Grid Carbon Intensity ($\text{kg CO}_2\text{e/kWh}$), dynamically resolved via `backend/core/emission_factors.py`.
- $M$ is Embodied Manufacturing Carbon amortized over the hardware lifespan (typically 3–5 years).
- $R$ is Functional Workload Unit (hours active, transactions processed, or requests served).

### 2.2 Modular Machine Learning Subsystem (`backend/ml/`)
- **Carbon Regressor:** Evaluates GradientBoosting vs. Random Forest on 4,500 real hardware records. GradientBoosting achieved an $R^2$ of **0.9788** with an MAE of **0.0142 kg $\text{CO}_2\text{e}$**.
- **Energy Regressor:** Predicts pure electricity draw in kWh using log1p transformation to ensure physical non-negativity.
- **Anomaly Engine:** Calibrated Isolation Forest detecting multivariate outliers (parasitic standby leaks, thermal spikes).
- **Time-Series Forecaster:** Autoregressive lagged Gradient Boosting providing 24h, 7d, 30d, 90d, and 6-month trajectories with 95% heteroscedastic confidence envelopes.
- **Device Clustering:** K-Means ($k=4$) categorizing nodes into *Energy Efficient*, *Moderate*, *High Consumption*, and *Optimization Required*.
- **Explainable AI:** Feature attribution explaining variance drivers (Grid Factor, CPU Duty, GPU Power, Memory).

### 2.3 Persistence Layer (`backend/db/`)
- **SQLAlchemy ORM Models:** Entities for `User`, `Organization`, `Department`, `Device`, `DeviceMetric`, `AnomalyEvent`, `OptimizationRecommendation`, `SustainabilityTarget`, and `AuditLog`.
- **Zero-Config Database:** Automatically initializes and seeds SQLite (`data/carbonomics_v3.db`) locally, seamlessly switching to PostgreSQL when `DATABASE_URL` is configured.

### 2.4 Device Telemetry Agent (`device_agent/agent.py`)
- Cross-platform daemon using `psutil` and optional `pynvml`.
- Collects core frequencies, virtual memory, disk usage, active network rates, thermal state, and top active computing processes.
- Communicates via authenticated REST bearer tokens to `/api/fleet/register` and `/api/fleet/heartbeat`.

### 2.5 Enterprise Next.js SaaS Frontend (`frontend/`)
- Built on Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts, Framer Motion, and Lucide React.
- Styled with dark theme palette: Background `#090D14`, Cards `#151D2B`, Primary Emerald `#16C784`, Cyan `#38BDF8`.
- 12 fully functional operational views without placeholders or mock data.

