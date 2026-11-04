"""
Carbonomics v3 — ML Preprocessing & Feature Engineering Pipeline
Handles normalization, categorical mappings, physical feature augmentation, and lag generation.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from backend.core.emission_factors import registry

DEVICE_FEATURE_COLUMNS = [
    "cpu_util_pct",
    "memory_gb",
    "storage_gb",
    "uptime_hours",
    "gpu_util_pct",
    "display_count",
    "cooling_pue",
    "cpu_tdp",
    "idle_w",
    "storage_is_hdd",
    "emission_factor"
]

SERVICE_FEATURE_COLUMNS = [
    "cpu_time_ms",
    "memory_mb",
    "daily_requests",
    "network_latency_ms",
    "storage_gb",
    "gpu_time_ms",
    "idle_cpu_percent",
    "cooling_pue",
    "emission_factor"
]


def extract_device_features(d: Dict[str, Any]) -> List[float]:
    """Convert raw device dict into engineered numerical feature vector"""
    device_type = str(d.get("device_type", "laptop")).lower()
    profile = registry.get_profile(device_type)
    region = str(d.get("region", "ap-south-1"))
    ef = float(d.get("emission_factor") or registry.get_factor(region))

    storage_type = str(d.get("storage_type", "ssd")).lower()
    is_hdd = 1.0 if storage_type == "hdd" else 0.0

    return [
        float(d.get("cpu_util_pct", 40.0)),
        float(d.get("memory_gb", 16.0)),
        float(d.get("storage_gb", 512.0)),
        float(d.get("uptime_hours_per_day", d.get("uptime_hours", 8.0))),
        float(d.get("gpu_util_pct", 0.0)),
        float(d.get("display_count", 1)),
        float(d.get("cooling_pue", 1.0)),
        float(profile.get("cpu_tdp", 45.0)),
        float(profile.get("idle_w", 8.0)),
        is_hdd,
        ef
    ]


def extract_service_features(s: Dict[str, Any]) -> List[float]:
    """Convert raw microservice/endpoint dict into numerical feature vector"""
    region = str(s.get("cloud_region", s.get("region", "ap-south-1")))
    ef = float(s.get("emission_factor") or registry.get_factor(region))

    return [
        float(s.get("cpu_time_ms", 100.0)),
        float(s.get("memory_mb", 512.0)),
        float(s.get("daily_requests", 1000.0)),
        float(s.get("network_latency_ms", 50.0)),
        float(s.get("storage_gb", 0.0)),
        float(s.get("gpu_time_ms", 0.0)),
        float(s.get("idle_cpu_percent", 20.0)),
        float(s.get("cooling_pue", 1.4)),
        ef
    ]


def create_time_series_lags(
    series: np.ndarray,
    n_lags: int = 7
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate supervised autoregressive lag matrices for time-series forecasting.
    X: [t-n_lags, ..., t-1, rolling_mean, rolling_std] -> y: [t]
    """
    X, y = [], []
    for i in range(n_lags, len(series)):
        window = series[i - n_lags:i]
        rolling_mean = np.mean(window)
        rolling_std = np.std(window)
        features = list(window) + [rolling_mean, rolling_std]
        X.append(features)
        y.append(series[i])
    return np.array(X), np.array(y)

