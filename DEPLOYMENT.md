# Carbonomics v3 — Deployment & Operations Guide

This guide covers running **Carbonomics v3** locally, via Docker Compose, and deploying to cloud platforms (Render, AWS, DigitalOcean).

---

## 1. Local Development (Dual Process)

### Prerequisites
- Python 3.10+ (tested on Python 3.11)
- Node.js 18+ (tested on Node v22.15.0 with npm 11)

### Terminal 1 — Backend API
```powershell
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run backend (port 5000)
python backend/api/app.py
```
Backend API will be active at: `http://localhost:5000`

### Terminal 2 — Next.js Enterprise Frontend
```powershell
cd frontend
npm run dev
```
Frontend Dashboard will be active at: `http://localhost:3000`

---

## 2. Docker Compose Deployment

Run the full stack with a single command:
```bash
docker-compose up --build -d
```
This launches:
- **`carbonomics-db`:** PostgreSQL 15 on port 5432
- **`carbonomics-backend`:** Gunicorn Flask API on port 5000
- **`carbonomics-frontend`:** Next.js Production Server on port 3000

---

## 3. Render Cloud Deployment

Carbonomics v3 preserves full backward compatibility with the existing `render.yaml`:
```yaml
services:
  - type: web
    name: carbonomics
    env: python
    plan: free
    buildCommand: pip install --upgrade pip && pip install -r backend/requirements.txt
    startCommand: gunicorn backend.api.app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.12
```

---

## 4. Hardware Telemetry Agent Deployment

On any monitored machine (laptop, server, lab workstation):
```bash
python device_agent/agent.py --server http://YOUR_SERVER_IP:5000 --region ap-south-1 --device-type laptop
```
To run a one-time non-daemon inspection:
```bash
python device_agent/agent.py --once
```
