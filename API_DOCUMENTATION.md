# Carbonomics v3 — API Documentation

Central REST and Server-Sent Events (SSE) API specification.  
Default Base URL: `http://localhost:5000`

---

## 1. System & Authentication

### `GET /api/health`
Returns system status, active database nodes, version, and ML readiness.
```json
{
  "status": "ok",
  "version": "3.0.0",
  "platform": "Carbonomics v3 Enterprise",
  "ml_ready": true,
  "psutil": true,
  "database": "connected",
  "fleet_total": 35,
  "fleet_online": 26
}
```

### `POST /api/auth/register`
Create user account.
```json
{
  "username": "analyst_1",
  "email": "analyst@carbonomics.io",
  "password": "SecurePassword123"
}
```

### `POST /api/auth/login`
Authenticate and obtain JWT bearer token.
```json
{
  "username": "admin",
  "password": "admin123"
}
```

---

## 2. Fleet & Device Telemetry

### `GET /api/fleet/devices`
List all persistent fleet nodes with real-time operational states and health scores.

### `POST /api/fleet/register`
Register a hardware node.
```json
{
  "device_id": "DEV-DA59010F",
  "device_name": "Lab-Workstation-1",
  "device_type": "workstation",
  "region": "ap-south-1",
  "cpu_util_pct": 35.4,
  "memory_total_gb": 32.0,
  "auth_token": "tok_sec_123"
}
```

### `POST /api/fleet/heartbeat`
Periodic telemetry ping sent every 15s by device agents.

### `GET /api/fleet/clusters`
Returns fleet devices categorized by K-Means into 4 efficiency clusters.

---

## 3. Carbon Estimation

### `POST /api/estimate/device`
Estimate physical hardware emissions.
```json
{
  "device_type": "laptop",
  "cpu_util_pct": 45.0,
  "memory_gb": 16.0,
  "storage_gb": 512.0,
  "uptime_hours_per_day": 8.0,
  "region": "ap-south-1",
  "cooling_pue": 1.0
}
```

### `POST /api/estimate/service`
Estimate emissions for API microservices or cloud functions.
```json
{
  "service_name": "auth-api",
  "cpu_time_ms": 120,
  "memory_mb": 1024,
  "daily_requests": 25000,
  "region": "us-east-1"
}
```

### `POST /api/estimate/cloud-vm`
Estimate emissions for cloud virtual machines across AWS, GCP, and Azure.
```json
{
  "provider": "aws",
  "vcpus": 8,
  "memory_gb": 32.0,
  "region": "us-west-2",
  "avg_cpu_util_pct": 50.0
}
```

### `POST /api/estimate/csv`
Upload a `.csv` batch file with automatic schema detection.

---

## 4. Machine Learning & Forecasting

### `POST /api/forecast`
Generate 6-month predictive trajectories with confidence intervals.
```json
{
  "horizon_months": 6,
  "growth_rate": 0.05,
  "scenario": "baseline"
}
```

### `GET /api/anomalies`
Returns flagged anomalies identified by the calibrated Isolation Forest.

### `POST /api/explain`
Returns SHAP feature importance attributions for a given hardware state.

---

## 5. What-If Simulation & Cloud Intelligence

### `POST /api/simulate`
Run physics-based simulation evaluating before-and-after operational policies.
```json
{
  "device_count": 50,
  "current_cpu_util": 50.0,
  "target_cpu_util": 30.0,
  "current_uptime_hours": 12.0,
  "target_uptime_hours": 8.0,
  "current_region": "ap-south-1",
  "target_region": "eu-north-1",
  "target_pue": 1.12
}
```

### `GET /api/cloud/compare`
Compares 11 global regions across AWS, GCP, and Azure.

### `POST /api/cloud/schedule`
Carbon-aware batch scheduler simulating diurnal solar/wind alignment.

---

## 6. AI Carbon Advisor

### `POST /api/advisor/chat`
Ask natural language questions to the data-grounded assistant.
```json
{
  "query": "What is our current fleet carbon footprint?"
}
```
Response includes verified tool outputs and suggested follow-up questions.

