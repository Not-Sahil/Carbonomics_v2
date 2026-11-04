"""
Carbonomics v3 — Enterprise Backend Application
Intelligent Carbon Intelligence, Sustainability Analytics & Green Infrastructure Optimization Platform.
Provides REST APIs, SSE real-time streaming, persistent database telemetry, and ML inference.
"""

import os
import sys
import io
import json
import threading
import time
import uuid
from datetime import datetime, timedelta

if sys.platform == "win32":
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

# Add both project root and backend directory to sys.path so all imports resolve seamlessly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in [PROJECT_ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from core.emission_factors import registry, REGION_FACTORS, DEVICE_PROFILES
from core.carbon_calculator import CarbonCalculator
from core.device_monitor import (
    get_live_metrics, get_top_processes, get_network_interfaces,
    compute_device_emission, PSUTIL_AVAILABLE
)
from core.simulator import WhatIfSimulator
from core.cloud_intelligence import GreenCloudIntelligence
from core.ai_advisor import AICarbonAdvisor
from ml.inference import get_ml_engine
from ml.scoring import compute_carbon_efficiency_score
from ml.explainability import explain_prediction
from ml.preprocessing import DEVICE_FEATURE_COLUMNS

from db.database import init_db, SessionLocal, engine
from db.models import (
    User, Device, DeviceMetric, AnomalyEvent, OptimizationRecommendation,
    SustainabilityTarget, Organization, Department, EmissionRecord
)
from api.auth import create_token, get_current_user_payload, login_required

# Initialize database schema and initial data
init_db()

# Singletons
calculator = CarbonCalculator()
ml_engine = get_ml_engine()
simulator = WhatIfSimulator()
cloud_intel = GreenCloudIntelligence()
ai_advisor = AICarbonAdvisor()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Frontend directory configuration
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../../frontend")

# In-memory SSE subscriber registry for real-time live streaming
_sse_clients = []
_sse_lock = threading.Lock()


def _push_event(event_type: str, data: dict):
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _sse_lock:
        for q in list(_sse_clients):
            try:
                q.append(payload)
            except Exception:
                pass


@app.route("/")
def serve_frontend():
    # If a static Next.js export or build exists in frontend/out, serve that, else serve index.html
    out_dir = os.path.join(FRONTEND_DIR, "out")
    if os.path.exists(os.path.join(out_dir, "index.html")):
        return send_from_directory(out_dir, "index.html")
    if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIR, "index.html")
    return jsonify({"message": "Carbonomics v3 Backend API running. Frontend available on port 3000."})


# ═══════════════════════════════════════════════════════════════
# SYSTEM HEALTH & METADATA
# ═══════════════════════════════════════════════════════════════
@app.route("/api/health")
def health():
    db = SessionLocal()
    try:
        device_count = db.query(Device).count()
        online_count = db.query(Device).filter_by(status="online").count()
    except Exception:
        device_count, online_count = 0, 0
    finally:
        db.close()

    return jsonify({
        "status": "ok",
        "version": "3.0.0",
        "platform": "Carbonomics v3 Enterprise",
        "ml_ready": ml_engine.is_trained,
        "psutil": PSUTIL_AVAILABLE,
        "database": "connected",
        "fleet_total": device_count,
        "fleet_online": online_count,
        "timestamp": datetime.utcnow().isoformat()
    })


# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION & USERS
# ═══════════════════════════════════════════════════════════════
@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.json or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password required"}), 400

    db = SessionLocal()
    try:
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            return jsonify({"error": "User with this username or email already exists"}), 409

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role="analyst"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_token(user.id, user.username, user.role)
        return jsonify({
            "token": token,
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}
        }), 201
    finally:
        db.close()


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    db = SessionLocal()
    try:
        user = db.query(User).filter((User.username == username) | (User.email == username)).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid username or password"}), 401

        token = create_token(user.id, user.username, user.role)
        return jsonify({
            "token": token,
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}
        })
    finally:
        db.close()


@app.route("/api/auth/me")
def auth_me():
    payload = get_current_user_payload()
    if not payload:
        # Default anonymous analyst profile for friction-free dashboard exploration
        return jsonify({
            "authenticated": False,
            "user": {"username": "guest_analyst", "role": "viewer"}
        })
    return jsonify({
        "authenticated": True,
        "user": {"id": payload.get("user_id"), "username": payload.get("username"), "role": payload.get("role")}
    })


# ═══════════════════════════════════════════════════════════════
# REFERENCE DATA & REGISTRIES
# ═══════════════════════════════════════════════════════════════
@app.route("/api/regions")
def api_regions():
    return jsonify(registry.regions)


@app.route("/api/device-profiles")
def api_device_profiles():
    return jsonify(registry.device_profiles)


@app.route("/api/regions/update", methods=["POST"])
def api_regions_update():
    data = request.json or {}
    key = data.get("region_key")
    if not key:
        return jsonify({"error": "Missing region_key"}), 400
    success = registry.update_region(key, data.get("factor_data", {}))
    return jsonify({"success": success, "region": registry.get_region(key)})


# ═══════════════════════════════════════════════════════════════
# LIVE LOCAL HARDWARE METRICS
# ═══════════════════════════════════════════════════════════════
@app.route("/api/device/live")
def device_live():
    region = request.args.get("region", "ap-south-1")
    device_type = request.args.get("device_type", "laptop")
    metrics = get_live_metrics()
    emission = calculator.estimate_device(
        device_type=device_type,
        cpu_util_pct=metrics.get("cpu_util_pct", 30),
        memory_gb=metrics.get("memory_total_gb", 16),
        region=region,
        uptime_hours_per_day=min(metrics.get("uptime_hours", 8), 24)
    )
    return jsonify({**metrics, **emission})


@app.route("/api/device/processes")
def device_processes():
    return jsonify({"processes": get_top_processes(15)})


@app.route("/api/device/interfaces")
def device_interfaces():
    return jsonify({"interfaces": get_network_interfaces()})


@app.route("/api/device/stream")
def device_stream():
    region = request.args.get("region", "ap-south-1")
    device_type = request.args.get("device_type", "laptop")
    client_queue = []
    with _sse_lock:
        _sse_clients.append(client_queue)

    def generate():
        try:
            while True:
                metrics = get_live_metrics()
                emission = calculator.estimate_device(
                    device_type=device_type,
                    cpu_util_pct=metrics.get("cpu_util_pct", 30),
                    memory_gb=metrics.get("memory_total_gb", 16),
                    region=region,
                    uptime_hours_per_day=min(metrics.get("uptime_hours", 8), 24)
                )
                payload = json.dumps({
                    **metrics,
                    "total_daily_kg": emission["total_daily_kg"],
                    "total_kwh_daily": emission["total_kwh_daily"],
                    "power_watts": emission["power_breakdown_watts"]["total_active_watts"],
                    "ts": datetime.utcnow().isoformat()
                })
                yield f"data: {payload}\n\n"
                time.sleep(3)
        except GeneratorExit:
            pass
        finally:
            with _sse_lock:
                try:
                    _sse_clients.remove(client_queue)
                except ValueError:
                    pass

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Access-Control-Allow-Origin": "*"}
    )


# ═══════════════════════════════════════════════════════════════
# PERSISTENT FLEET MANAGEMENT
# ═══════════════════════════════════════════════════════════════
@app.route("/api/fleet/register", methods=["POST"])
def fleet_register():
    data = request.json or {}
    dev_uuid = data.get("device_id") or f"DEV-{str(uuid.uuid4())[:8].upper()}"
    name = data.get("device_name") or f"Hardware-Node-{dev_uuid}"
    d_type = data.get("device_type", "laptop")
    region = data.get("region", "ap-south-1")

    # Compute emission metrics
    res = calculator.estimate_device(
        device_type=d_type,
        cpu_util_pct=float(data.get("cpu_util_pct", 30.0)),
        memory_gb=float(data.get("memory_total_gb", data.get("memory_gb", 16.0))),
        region=region,
        device_name=name
    )

    db = SessionLocal()
    try:
        device = db.query(Device).filter_by(device_uuid=dev_uuid).first()
        if not device:
            device = Device(
                device_uuid=dev_uuid,
                name=name,
                device_type=d_type,
                region=region,
                status="online",
                last_seen=datetime.utcnow(),
                auth_token=data.get("auth_token"),
                os_name=data.get("os_name", data.get("os")),
                os_version=data.get("os_version"),
                processor=data.get("processor"),
                latest_cpu_util=float(data.get("cpu_util_pct", 30.0)),
                latest_power_watts=res["power_breakdown_watts"]["total_active_watts"],
                latest_daily_kg=res["total_daily_kg"],
                health_score=round(max(60.0, 100.0 - (float(data.get("cpu_util_pct", 30)) * 0.3)), 1),
                tags=json.dumps([d_type, region, data.get("department", "Engineering")])
            )
            db.add(device)
        else:
            device.status = "online"
            device.last_seen = datetime.utcnow()
            device.latest_cpu_util = float(data.get("cpu_util_pct", 30.0))
            device.latest_power_watts = res["power_breakdown_watts"]["total_active_watts"]
            device.latest_daily_kg = res["total_daily_kg"]

        db.commit()
        db.refresh(device)
        _push_event("fleet_update", {"device_id": dev_uuid, "action": "register"})

        return jsonify({
            "device_id": dev_uuid,
            "registered": True,
            "status": "online",
            "daily_kg": res["total_daily_kg"]
        }), 201
    finally:
        db.close()


@app.route("/api/fleet/heartbeat", methods=["POST"])
def fleet_heartbeat():
    data = request.json or {}
    dev_uuid = data.get("device_id")
    if not dev_uuid:
        return jsonify({"error": "Missing device_id"}), 400

    db = SessionLocal()
    try:
        device = db.query(Device).filter_by(device_uuid=dev_uuid).first()
        if not device:
            return jsonify({"error": "Device not registered"}), 404

        res = calculator.estimate_device(
            device_type=device.device_type,
            cpu_util_pct=float(data.get("cpu_util_pct", device.latest_cpu_util)),
            memory_gb=float(data.get("memory_total_gb", 16.0)),
            region=device.region,
            device_name=device.name
        )

        device.status = "online"
        device.last_seen = datetime.utcnow()
        device.latest_cpu_util = float(data.get("cpu_util_pct", device.latest_cpu_util))
        device.latest_power_watts = res["power_breakdown_watts"]["total_active_watts"]
        device.latest_daily_kg = res["total_daily_kg"]
        device.health_score = round(max(50.0, 100.0 - (device.latest_cpu_util * 0.35)), 1)

        # Record metric historical point
        metric = DeviceMetric(
            device_id=device.id,
            cpu_util_pct=device.latest_cpu_util,
            memory_util_pct=float(data.get("memory_util_pct", 50.0)),
            power_watts=device.latest_power_watts,
            energy_kwh_daily=res["total_kwh_daily"],
            carbon_kg_daily=res["total_daily_kg"],
            timestamp=datetime.utcnow()
        )
        db.add(metric)
        db.commit()

        _push_event("fleet_update", {"device_id": dev_uuid, "action": "heartbeat"})
        return jsonify({
            "ok": True,
            "power_watts": device.latest_power_watts,
            "latest_daily_kg": device.latest_daily_kg
        })
    finally:
        db.close()


@app.route("/api/fleet/devices")
def fleet_devices():
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    db = SessionLocal()
    try:
        devices_query = db.query(Device).filter_by(is_active=True).all()
        dev_list = []
        for d in devices_query:
            is_online = d.last_seen > cutoff if d.last_seen else False
            dev_list.append({
                "id": d.id,
                "device_id": d.device_uuid,
                "device_name": d.name,
                "device_type": d.device_type,
                "region": d.region,
                "status": "online" if is_online else "offline",
                "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                "cpu_util_pct": d.latest_cpu_util,
                "power_watts": d.latest_power_watts,
                "total_daily_kg": d.latest_daily_kg,
                "total_kwh_daily": round(d.latest_power_watts * 8.0 / 1000.0, 4),
                "health_score": d.health_score,
                "os": d.os_name,
                "processor": d.processor,
                "tags": json.loads(d.tags) if d.tags else []
            })
        summary = calculator.compute_fleet_summary(dev_list)
        return jsonify({"devices": dev_list, "summary": summary})
    finally:
        db.close()


@app.route("/api/fleet/summary")
def fleet_summary():
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    db = SessionLocal()
    try:
        devices_query = db.query(Device).filter_by(is_active=True).all()
        dev_list = [{
            "device_name": d.name,
            "device_type": d.device_type,
            "status": "online" if (d.last_seen and d.last_seen > cutoff) else "offline",
            "total_daily_kg": d.latest_daily_kg,
            "total_kwh_daily": d.latest_power_watts * 8.0 / 1000.0
        } for d in devices_query]
        return jsonify(calculator.compute_fleet_summary(dev_list))
    finally:
        db.close()


@app.route("/api/fleet/clusters")
def fleet_clusters():
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    db = SessionLocal()
    try:
        devices = db.query(Device).filter_by(is_active=True).all()
        dev_list = [{
            "device_id": d.device_uuid,
            "device_name": d.name,
            "device_type": d.device_type,
            "region": d.region,
            "cpu_util_pct": d.latest_cpu_util,
            "memory_gb": 16.0,
            "storage_gb": 512.0,
            "uptime_hours_per_day": 8.0,
            "total_daily_kg": d.latest_daily_kg,
            "total_kwh_daily": d.latest_power_watts * 8.0 / 1000.0,
            "status": "online" if (d.last_seen and d.last_seen > cutoff) else "offline"
        } for d in devices]
        clustered = ml_engine.cluster_devices(dev_list)
        return jsonify({"devices": clustered, "count": len(clustered)})
    finally:
        db.close()


@app.route("/api/fleet/remove/<device_id>", methods=["DELETE"])
def fleet_remove(device_id):
    db = SessionLocal()
    try:
        device = db.query(Device).filter((Device.device_uuid == device_id) | (Device.id == device_id)).first()
        if device:
            device.is_active = False
            db.commit()
            return jsonify({"removed": True})
        return jsonify({"error": "Device not found"}), 404
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════
# CARBON ESTIMATION — PHYSICAL HARDWARE, SERVICES, CLOUD VMS
# ═══════════════════════════════════════════════════════════════
@app.route("/api/estimate/device", methods=["POST"])
def estimate_device():
    d = request.json or {}
    res = calculator.estimate_device(
        device_type=d.get("device_type", "laptop"),
        cpu_util_pct=float(d.get("cpu_util_pct", 40)),
        memory_gb=float(d.get("memory_gb", 16)),
        storage_gb=float(d.get("storage_gb", 512)),
        storage_type=str(d.get("storage_type", "ssd")),
        uptime_hours_per_day=float(d.get("uptime_hours_per_day", 8)),
        region=str(d.get("region", "ap-south-1")),
        gpu_util_pct=float(d.get("gpu_util_pct", 0)),
        display_count=int(d.get("display_count", 1)),
        cooling_pue=float(d.get("cooling_pue", 1.0)),
        device_name=str(d.get("device_name", "Hardware Node")),
    )
    # ML predicted validation
    res["ml_prediction"] = ml_engine.predict_device_carbon(res)
    res["ml_energy_kwh"] = ml_engine.predict_device_energy(res)
    res["efficiency"] = compute_carbon_efficiency_score(res)
    return jsonify(res)


@app.route("/api/estimate/service", methods=["POST"])
def estimate_service():
    d = request.json or {}
    res = calculator.estimate_service(
        cpu_time_ms=float(d.get("cpu_time_ms", 100)),
        memory_mb=float(d.get("memory_mb", 512)),
        daily_requests=float(d.get("daily_requests", 1000)),
        region=str(d.get("region", "ap-south-1")),
        network_latency_ms=float(d.get("network_latency_ms", 50)),
        storage_gb=float(d.get("storage_gb", 0)),
        gpu_time_ms=float(d.get("gpu_time_ms", 0)),
        idle_cpu_percent=float(d.get("idle_cpu_percent", 20)),
        cooling_pue=float(d.get("cooling_pue", 1.4)),
        service_name=str(d.get("service_name", "Service Endpoint")),
    )
    res["ml_prediction"] = ml_engine.predict_service(res)
    res["efficiency"] = compute_carbon_efficiency_score(res)
    return jsonify(res)


@app.route("/api/estimate/cloud-vm", methods=["POST"])
def estimate_cloud_vm():
    d = request.json or {}
    res = calculator.estimate_cloud_vm(
        instance_type=d.get("instance_type", "cloud_vm_medium"),
        vcpus=int(d.get("vcpus", 4)),
        memory_gb=float(d.get("memory_gb", 16.0)),
        provider=d.get("provider", "aws"),
        region=d.get("region", "us-east-1"),
        avg_cpu_util_pct=float(d.get("avg_cpu_util_pct", 45.0)),
        uptime_hours=float(d.get("uptime_hours", 24.0)),
        vm_name=d.get("vm_name", "Compute Instance")
    )
    return jsonify(res)


@app.route("/api/estimate/csv", methods=["POST"])
def estimate_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files accepted"}), 400
    try:
        df = pd.read_csv(f)
        result = calculator.estimate_bulk_csv(df)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# ADVANCED ANALYTICS, ANOMALIES & EXPLAINABLE AI (SHAP)
# ═══════════════════════════════════════════════════════════════
@app.route("/api/attribution", methods=["POST"])
def attribution():
    items = (request.json or {}).get("items", [])
    if not items:
        # Pull from persistent database
        db = SessionLocal()
        try:
            devs = db.query(Device).filter_by(is_active=True).all()
            items = [{
                "name": d.name, "device_name": d.name,
                "device_type": d.device_type, "total_daily_kg": d.latest_daily_kg
            } for d in devs]
        finally:
            db.close()

    total = sum(s.get("total_daily_kg", 0) for s in items)
    result = []
    for s in items:
        name = s.get("service_name") or s.get("device_name") or s.get("name") or "unknown"
        daily_kg = float(s.get("total_daily_kg", 0))
        result.append({
            **s,
            "name": name,
            "percentage": round(daily_kg / max(total, 1e-9) * 100, 2),
            "weekly_kg": round(daily_kg * 7, 4),
            "annual_kg": round(daily_kg * 365, 2)
        })
    result.sort(key=lambda x: x["percentage"], reverse=True)
    return jsonify({"items": result, "total_daily_kg": total, "count": len(result)})


@app.route("/api/anomalies", methods=["GET", "POST"])
def anomalies():
    if request.method == "POST":
        items = (request.json or {}).get("items", [])
    else:
        db = SessionLocal()
        try:
            devs = db.query(Device).filter_by(is_active=True).all()
            items = [{
                "device_id": d.device_uuid, "device_name": d.name,
                "device_type": d.device_type, "cpu_util_pct": d.latest_cpu_util,
                "region": d.region, "total_daily_kg": d.latest_daily_kg
            } for d in devs]
        finally:
            db.close()

    detected = ml_engine.detect_anomalies(items)
    return jsonify({"anomalies": detected, "count": len(detected)})


@app.route("/api/forecast", methods=["POST"])
def forecast():
    d = request.json or {}
    items = d.get("items", [])
    if not items:
        db = SessionLocal()
        try:
            devs = db.query(Device).filter_by(is_active=True).all()
            items = [{"total_daily_kg": d.latest_daily_kg} for d in devs]
        finally:
            db.close()

    return jsonify(ml_engine.forecast(
        items,
        horizon_months=int(d.get("horizon_months", 6)),
        growth_rate=float(d.get("growth_rate", 0.05)),
        scenario=str(d.get("scenario", "baseline"))
    ))


@app.route("/api/explain", methods=["POST"])
def api_explain():
    d = request.json or {}
    # Convert item to feature vector
    from ml.preprocessing import extract_device_features
    features = extract_device_features(d)
    pred_c = ml_engine.predict_device_carbon(d)
    explanation = explain_prediction(features, DEVICE_FEATURE_COLUMNS, pred_c)
    return jsonify(explanation)


# ═══════════════════════════════════════════════════════════════
# OPTIMIZATION & WHAT-IF SIMULATION
# ═══════════════════════════════════════════════════════════════
@app.route("/api/optimize", methods=["GET", "POST"])
def optimize():
    if request.method == "POST":
        items = (request.json or {}).get("items", [])
    else:
        db = SessionLocal()
        try:
            devs = db.query(Device).filter_by(is_active=True).all()
            items = [{
                "device_id": d.device_uuid, "device_name": d.name,
                "device_type": d.device_type, "region": d.region,
                "cpu_util_pct": d.latest_cpu_util, "total_daily_kg": d.latest_daily_kg,
                "total_kwh_daily": d.latest_power_watts * 8.0 / 1000.0,
                "row_type": "device"
            } for d in devs]
        finally:
            db.close()

    return jsonify(ml_engine.get_recommendations(items))


@app.route("/api/recommendations/<int:rec_id>/status", methods=["PATCH"])
def update_recommendation_status(rec_id):
    data = request.json or {}
    new_status = data.get("status", "reviewed")
    db = SessionLocal()
    try:
        rec = db.query(OptimizationRecommendation).get(rec_id)
        if not rec:
            return jsonify({"error": "Recommendation not found"}), 404
        rec.status = new_status
        db.commit()
        return jsonify({"success": True, "id": rec.id, "status": rec.status})
    finally:
        db.close()


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    d = request.json or {}
    res = simulator.simulate(
        base_device_type=d.get("device_type", "laptop"),
        device_count=int(d.get("device_count", 50)),
        current_cpu_util=float(d.get("current_cpu_util", 45.0)),
        target_cpu_util=float(d.get("target_cpu_util", 30.0)),
        current_uptime_hours=float(d.get("current_uptime_hours", 12.0)),
        target_uptime_hours=float(d.get("target_uptime_hours", 8.0)),
        current_region=d.get("current_region", "ap-south-1"),
        target_region=d.get("target_region", "eu-north-1"),
        current_pue=float(d.get("current_pue", 1.4)),
        target_pue=float(d.get("target_pue", 1.15)),
        memory_gb=float(d.get("memory_gb", 16.0)),
        storage_gb=float(d.get("storage_gb", 512.0)),
        gpu_util_pct=float(d.get("gpu_util_pct", 10.0)),
        scenario_name=d.get("scenario_name", "Enterprise Optimization")
    )
    return jsonify(res)


@app.route("/api/simulate/presets")
def api_simulate_presets():
    return jsonify(simulator.get_presets())


# ═══════════════════════════════════════════════════════════════
# GREEN CLOUD INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
@app.route("/api/cloud/compare")
def cloud_compare():
    vcpus = int(request.args.get("vcpus", 8))
    mem = float(request.args.get("memory_gb", 32.0))
    uptime = float(request.args.get("uptime_hours", 24.0))
    return jsonify({"regions": cloud_intel.compare_regions(vcpus, mem, uptime)})


@app.route("/api/cloud/schedule", methods=["POST"])
def cloud_schedule():
    d = request.json or {}
    return jsonify(cloud_intel.schedule_carbon_aware_job(
        job_name=d.get("job_name", "Nightly Analytics Pipeline"),
        duration_hours=float(d.get("duration_hours", 4.0)),
        vcpus=int(d.get("vcpus", 16)),
        memory_gb=float(d.get("memory_gb", 64.0)),
        preferred_region=d.get("preferred_region", "ap-south-1")
    ))


# ═══════════════════════════════════════════════════════════════
# REPORTING & SUSTAINABILITY TARGETS
# ═══════════════════════════════════════════════════════════════
@app.route("/api/report", methods=["POST"])
def report():
    d = request.json or {}
    items = d.get("items", [])
    if not items:
        db = SessionLocal()
        try:
            devs = db.query(Device).filter_by(is_active=True).all()
            items = [{
                "total_daily_kg": d.latest_daily_kg,
                "total_kwh_daily": d.latest_power_watts * 8.0 / 1000.0
            } for d in devs]
        finally:
            db.close()

    return jsonify(calculator.generate_report(items, d.get("period", "H1 2026")))


@app.route("/api/targets", methods=["GET", "POST"])
def targets():
    db = SessionLocal()
    try:
        if request.method == "POST":
            d = request.json or {}
            target = SustainabilityTarget(
                title=d.get("title", "Emissions Abatement"),
                target_type=d.get("target_type", "emission_reduction"),
                target_value=float(d.get("target_value", 10.0)),
                current_value=float(d.get("current_value", 0.0)),
                unit=d.get("unit", "%"),
                deadline=d.get("deadline", "2026-12-31"),
                status=d.get("status", "on_track")
            )
            db.add(target)
            db.commit()
            db.refresh(target)
            return jsonify({"id": target.id, "created": True}), 201

        all_targets = db.query(SustainabilityTarget).all()
        return jsonify([{
            "id": t.id,
            "title": t.title,
            "target_type": t.target_type,
            "target_value": t.target_value,
            "current_value": t.current_value,
            "unit": t.unit,
            "deadline": t.deadline,
            "status": t.status
        } for t in all_targets])
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════
# AI CARBON ADVISOR CHATBOT
# ═══════════════════════════════════════════════════════════════
@app.route("/api/advisor/chat", methods=["POST"])
def advisor_chat():
    d = request.json or {}
    query = d.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty prompt"}), 400
    res = ai_advisor.process_query(query)
    return jsonify(res)


# ═══════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════
@app.route("/api/carbon-score", methods=["POST"])
def carbon_score():
    items = (request.json or {}).get("items", [])
    if not items:
        return jsonify({"score": 85.0, "grade": "A", "total_daily_kg": 0.0})
    total = sum(s.get("total_daily_kg", 0) for s in items)
    score_data = compute_carbon_efficiency_score({"total_daily_kg": total, "items_count": len(items)})
    return jsonify({**score_data, "total_daily_kg": total})


if __name__ == "__main__":
    print("Carbonomics v3 Backend API starting on http://0.0.0.0:5000")
    print(f"   psutil available: {PSUTIL_AVAILABLE}")
    print(f"   ML engine trained: {ml_engine.is_trained}")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
