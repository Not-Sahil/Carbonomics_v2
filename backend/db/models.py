"""
Carbonomics v3 — SQLAlchemy Database Models
Provides enterprise persistence for users, organizations, devices, telemetry metrics,
emission records, anomalies, recommendations, and sustainability targets.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="organization")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)

    organization = relationship("Organization", back_populates="departments")
    devices = relationship("Device", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="analyst")  # admin, analyst, viewer, device_agent
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_uuid = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    device_type = Column(String(50), default="laptop", index=True)
    region = Column(String(50), default="ap-south-1", index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(30), nullable=True)
    os_name = Column(String(50), nullable=True)
    os_version = Column(String(100), nullable=True)
    processor = Column(String(150), nullable=True)

    auth_token = Column(String(128), nullable=True)
    status = Column(String(20), default="offline")  # online, offline, idle, warning
    last_seen = Column(DateTime, default=datetime.utcnow, index=True)
    tags = Column(Text, nullable=True)  # JSON-serialized tags
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Latest cached metrics for fast querying
    latest_cpu_util = Column(Float, default=0.0)
    latest_memory_util = Column(Float, default=0.0)
    latest_storage_util = Column(Float, default=0.0)
    latest_power_watts = Column(Float, default=0.0)
    latest_daily_kg = Column(Float, default=0.0)
    health_score = Column(Float, default=95.0)

    department = relationship("Department", back_populates="devices")
    organization = relationship("Organization", back_populates="devices")
    metrics = relationship("DeviceMetric", back_populates="device", cascade="all, delete-orphan")
    anomalies = relationship("AnomalyEvent", back_populates="device", cascade="all, delete-orphan")


class DeviceMetric(Base):
    __tablename__ = "device_metrics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    cpu_util_pct = Column(Float, default=0.0)
    memory_util_pct = Column(Float, default=0.0)
    memory_used_gb = Column(Float, default=0.0)
    storage_util_pct = Column(Float, default=0.0)
    gpu_util_pct = Column(Float, default=0.0)
    uptime_hours = Column(Float, default=8.0)
    net_bytes_sent_mb = Column(Float, default=0.0)
    net_bytes_recv_mb = Column(Float, default=0.0)

    power_watts = Column(Float, default=0.0)
    energy_kwh_daily = Column(Float, default=0.0)
    carbon_kg_daily = Column(Float, default=0.0)

    device = relationship("Device", back_populates="metrics")


class EmissionRecord(Base):
    __tablename__ = "emission_records"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), default="device", index=True)  # device, service, cloud_vm
    entity_name = Column(String(120), nullable=False)
    region = Column(String(50), default="ap-south-1")
    energy_kwh = Column(Float, default=0.0)
    carbon_kg = Column(Float, default=0.0)
    calculation_type = Column(String(20), default="estimated")  # estimated, measured
    breakdown_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True, index=True)
    entity_name = Column(String(120), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    anomaly_score = Column(Float, default=-0.5)
    metric_name = Column(String(50), default="energy_spike")
    metric_value = Column(Float, default=0.0)
    expected_value = Column(Float, default=0.0)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    explanation = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)

    device = relationship("Device", back_populates="anomalies")


class OptimizationRecommendation(Base):
    __tablename__ = "optimization_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # CPU, GPU, Memory, Storage, Cloud, Sleep
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    affected_entity = Column(String(120), nullable=False)
    potential_savings_kwh = Column(Float, default=0.0)
    potential_savings_kg = Column(Float, default=0.0)
    effort = Column(String(20), default="medium")  # low, medium, high
    priority = Column(String(20), default="high")  # low, medium, high
    confidence_pct = Column(Float, default=85.0)
    status = Column(String(20), default="pending")  # pending, reviewed, accepted, dismissed, completed
    created_at = Column(DateTime, default=datetime.utcnow)


class SustainabilityTarget(Base):
    __tablename__ = "sustainability_targets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    target_type = Column(String(50), default="emission_reduction")
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    unit = Column(String(20), default="%")
    deadline = Column(String(50), default="2026-12-31")
    status = Column(String(30), default="on_track")  # on_track, at_risk, achieved


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
