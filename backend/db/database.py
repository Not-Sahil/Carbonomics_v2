"""
Carbonomics v3 — Database Session & Seeding Manager
Supports zero-configuration SQLite for development and PostgreSQL for production.
"""

import os
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import (
    Base, User, Organization, Department, Device, DeviceMetric,
    AnomalyEvent, OptimizationRecommendation, SustainabilityTarget,
    EmissionRecord
)

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "carbonomics_v3.db")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables and seed default users, targets, and initial fleet devices"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Organization
        org = db.query(Organization).first()
        if not org:
            org = Organization(name="GreenTech Enterprise")
            db.add(org)
            db.commit()
            db.refresh(org)

            # Seed Departments
            dept_eng = Department(name="Engineering & Infrastructure", organization_id=org.id)
            dept_ai = Department(name="Data Science & AI Lab", organization_id=org.id)
            dept_ops = Department(name="Cloud Operations", organization_id=org.id)
            db.add_all([dept_eng, dept_ai, dept_ops])
            db.commit()

        # 2. Seed Default Admin User
        admin_user = db.query(User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@carbonomics.io",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                organization_id=org.id,
                is_active=True
            )
            viewer_user = User(
                username="analyst",
                email="analyst@carbonomics.io",
                password_hash=generate_password_hash("analyst123"),
                role="analyst",
                organization_id=org.id,
                is_active=True
            )
            db.add_all([admin_user, viewer_user])
            db.commit()

        # 3. Seed Sustainability Targets
        if db.query(SustainabilityTarget).count() == 0:
            targets = [
                SustainabilityTarget(
                    title="15% Fleet Energy Consumption Reduction",
                    target_type="energy_reduction",
                    target_value=15.0,
                    current_value=9.4,
                    unit="%",
                    deadline="Q4 2026",
                    status="on_track"
                ),
                SustainabilityTarget(
                    title="Scope-2 Location Emission Abatement",
                    target_type="emission_reduction",
                    target_value=25.0,
                    current_value=18.2,
                    unit="%",
                    deadline="Q1 2027",
                    status="on_track"
                ),
                SustainabilityTarget(
                    title="Average Fleet Carbon Efficiency > 85",
                    target_type="efficiency_improvement",
                    target_value=85.0,
                    current_value=82.6,
                    unit="score",
                    deadline="Q3 2026",
                    status="on_track"
                ),
                SustainabilityTarget(
                    title="Idle Machine Sleep Policy Compliance",
                    target_type="idle_reduction",
                    target_value=90.0,
                    current_value=74.0,
                    unit="%",
                    deadline="Q2 2026",
                    status="at_risk"
                ),
            ]
            db.add_all(targets)
            db.commit()

        # 4. Seed Initial Devices from CSV if empty
        if db.query(Device).count() == 0:
            csv_path = os.path.join(DB_DIR, "devices_4500.csv")
            sample_csv = os.path.join(DB_DIR, "sample_devices.csv")
            target_csv = csv_path if os.path.exists(csv_path) else sample_csv

            if os.path.exists(target_csv):
                import pandas as pd
                try:
                    from core.carbon_calculator import CarbonCalculator
                except (ImportError, ModuleNotFoundError):
                    from backend.core.carbon_calculator import CarbonCalculator
                calc = CarbonCalculator()

                df = pd.read_csv(target_csv)
                # Seed first 35 devices for rich dashboard demonstration
                subset = df.head(35)
                for idx, row in subset.iterrows():
                    d_type = str(row.get("device_type", "laptop"))
                    d_region = str(row.get("region", "ap-south-1"))
                    cpu_u = float(row.get("cpu_util_pct", 40.0))
                    mem_g = float(row.get("memory_gb", 16.0))
                    stor_g = float(row.get("storage_gb", 512.0))
                    uptime = float(row.get("uptime_hours_per_day", 8.0))
                    d_name = str(row.get("device_name", f"Hardware-Node-{idx+1}"))

                    res = calc.estimate_device(
                        device_type=d_type,
                        cpu_util_pct=cpu_u,
                        memory_gb=mem_g,
                        storage_gb=stor_g,
                        uptime_hours_per_day=uptime,
                        region=d_region,
                        device_name=d_name
                    )

                    is_online = (idx % 4 != 0)  # ~75% online
                    last_seen_time = datetime.utcnow() if is_online else (datetime.utcnow() - timedelta(hours=idx * 2))

                    device = Device(
                        device_uuid=f"DEV-{1000 + idx}",
                        name=d_name,
                        device_type=d_type,
                        region=res["region"],
                        organization_id=org.id,
                        status="online" if is_online else "offline",
                        last_seen=last_seen_time,
                        latest_cpu_util=cpu_u,
                        latest_memory_util=float(row.get("gpu_util_pct", 35.0)),
                        latest_storage_util=48.5,
                        latest_power_watts=res["power_breakdown_watts"]["total_active_watts"],
                        latest_daily_kg=res["total_daily_kg"],
                        health_score=round(max(60.0, 100.0 - (cpu_u * 0.3)), 1),
                        tags=json.dumps(["production", d_type, res["region"]]),
                        os_name="Linux" if "server" in d_type else "macOS" if "laptop" in d_type else "Windows",
                        os_version="6.5.0-generic" if "server" in d_type else "14.4.1",
                        processor="Intel Xeon Platinum" if "server" in d_type else "Apple M3 Pro" if "laptop" in d_type else "AMD Ryzen 9"
                    )
                    db.add(device)
                    db.flush()

                    # Add historical metrics for device
                    metric = DeviceMetric(
                        device_id=device.id,
                        cpu_util_pct=cpu_u,
                        memory_util_pct=52.0,
                        storage_util_pct=48.0,
                        power_watts=res["power_breakdown_watts"]["total_active_watts"],
                        energy_kwh_daily=res["total_kwh_daily"],
                        carbon_kg_daily=res["total_daily_kg"],
                        uptime_hours=uptime,
                        timestamp=last_seen_time
                    )
                    db.add(metric)

                db.commit()

        # 5. Seed Default Recommendations
        if db.query(OptimizationRecommendation).count() == 0:
            recs = [
                OptimizationRecommendation(
                    category="Cloud Region",
                    title="Migrate compute workloads to EU-North (Stockholm)",
                    description="Transfer scheduled batch data transformation tasks from ap-south-1 to eu-north-1. Stockholm runs on 95% hydro and wind generation.",
                    affected_entity="Fleet Region ap-south-1",
                    potential_savings_kwh=142.5,
                    potential_savings_kg=78.2,
                    effort="medium",
                    priority="high",
                    confidence_pct=94.0,
                    status="pending"
                ),
                OptimizationRecommendation(
                    category="Idle Policy",
                    title="Activate 10-minute automated sleep policy on idle workstations",
                    description="Telemetric audit identified 14 workstations with <12% CPU activity remaining fully powered during off-peak night cycles.",
                    affected_entity="Workstations Lab B",
                    potential_savings_kwh=68.4,
                    potential_savings_kg=35.1,
                    effort="low",
                    priority="high",
                    confidence_pct=91.0,
                    status="in_progress"
                ),
                OptimizationRecommendation(
                    category="CPU Right-Sizing",
                    title="Right-size over-allocated vCPU capacity on server_2u nodes",
                    description="Average server cluster utilization remains at 31%. Down-scaling 4 nodes to 1U architecture avoids standing thermal baseline.",
                    affected_entity="Datacenter Rack 3",
                    potential_savings_kwh=195.0,
                    potential_savings_kg=112.4,
                    effort="high",
                    priority="medium",
                    confidence_pct=88.5,
                    status="pending"
                ),
                OptimizationRecommendation(
                    category="Storage Tiering",
                    title="Migrate archival datasets to cold storage",
                    description="Move 18TB of inactive log analytics from warm SSD pools to tape/glacier tiering to cut static parasitic wattage.",
                    affected_entity="Analytics Cluster",
                    potential_savings_kwh=28.0,
                    potential_savings_kg=14.6,
                    effort="low",
                    priority="medium",
                    confidence_pct=96.0,
                    status="pending"
                )
            ]
            db.add_all(recs)
            db.commit()

        # 6. Seed Sample Anomaly Events
        if db.query(AnomalyEvent).count() == 0:
            sample_device = db.query(Device).first()
            anomalies = [
                AnomalyEvent(
                    device_id=sample_device.id if sample_device else None,
                    entity_name=sample_device.name if sample_device else "Hardware-Node-1",
                    anomaly_score=-0.78,
                    metric_name="CPU Thermal Spike",
                    metric_value=96.4,
                    expected_value=42.0,
                    severity="high",
                    explanation="Unscheduled persistent core saturation outside standard deployment hours.",
                    suggested_action="Inspect runaway batch daemon or background cryptocurrency miner.",
                    is_resolved=False
                ),
                AnomalyEvent(
                    device_id=None,
                    entity_name="Workstation-Cluster-4",
                    anomaly_score=-0.64,
                    metric_name="Parasitic Idle Power",
                    metric_value=245.0,
                    expected_value=85.0,
                    severity="medium",
                    explanation="Device drawing full dual-GPU active power despite zero active user sessions.",
                    suggested_action="Enforce display driver power-state D3 sleep policy.",
                    is_resolved=False
                )
            ]
            db.add_all(anomalies)
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error during database initialization: {e}")
    finally:
        db.close()

