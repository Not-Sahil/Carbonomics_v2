"""
Carbonomics v3 — Transparent Carbon Efficiency Scoring Engine
Computes mathematically grounded 0-100 efficiency scores.

Formula:
  Score = 100 * [ w_carbon * S_carbon + w_energy * S_energy + w_util * S_util + w_renewable * S_renewable ]
where:
  - S_carbon = exp(- (emission_per_unit / benchmark_emission))
  - S_energy = exp(- (energy_kwh_per_hour / benchmark_energy))
  - S_util = 1.0 - |utilization - target_optimal_utilization| / 100
  - S_renewable = renewable_grid_percentage / 100
"""

import math
from typing import Dict, Any


def compute_carbon_efficiency_score(
    item: Dict[str, Any],
    target_optimal_util: float = 65.0
) -> Dict[str, Any]:
    """
    Evaluate multidimensional computing efficiency on a scale of 0 to 100.
    """
    total_kg = float(item.get("total_daily_kg", 0.0))
    total_kwh = float(item.get("total_kwh_daily", item.get("total_kwh", 0.0)))
    uptime_h = max(0.5, float(item.get("uptime_hours_per_day", item.get("uptime_hours", 8.0))))
    cpu_util = float(item.get("cpu_util_pct", 40.0))
    renewable_pct = float(item.get("renewable_pct", 20.0))

    # Units of useful work done
    is_service = bool(item.get("daily_requests"))
    if is_service:
        work_units = float(item.get("daily_requests", 1000.0))
        benchmark_emission_per_unit = 0.00005  # kg per request
        benchmark_kwh_per_hour = 0.15
    else:
        work_units = uptime_h
        # Benchmark for standard energy-star certified modern computing device
        benchmark_emission_per_unit = 0.035   # kg per hour
        benchmark_kwh_per_hour = 0.045        # ~45 Watts average

    # 1. Carbon intensity subscore (lower emission per unit is better)
    emission_per_unit = total_kg / max(work_units, 1.0)
    s_carbon = math.exp(- (emission_per_unit / max(benchmark_emission_per_unit, 1e-9)))

    # 2. Energy efficiency subscore (lower wattage per active hour is better)
    kwh_per_hour = total_kwh / max(uptime_h, 0.5)
    s_energy = math.exp(- (kwh_per_hour / max(benchmark_kwh_per_hour, 1e-9)))

    # 3. Workload utilization factor (idle < 15% or over-saturation > 90% penalized)
    util_diff = abs(cpu_util - target_optimal_util)
    s_util = max(0.0, 1.0 - (util_diff / 80.0))

    # 4. Clean energy / renewable adoption factor
    s_renewable = min(1.0, max(0.0, renewable_pct / 100.0))

    # Composite weighted score
    w_carbon = 0.40
    w_energy = 0.30
    w_util = 0.20
    w_renewable = 0.10

    raw_score = (w_carbon * s_carbon + w_energy * s_energy + w_util * s_util + w_renewable * s_renewable) * 100.0
    final_score = round(min(100.0, max(5.0, raw_score)), 1)

    # Grade classification
    if final_score >= 90:
        grade = "A+"
    elif final_score >= 80:
        grade = "A"
    elif final_score >= 70:
        grade = "B+"
    elif final_score >= 60:
        grade = "B"
    elif final_score >= 50:
        grade = "C"
    elif final_score >= 40:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": final_score,
        "grade": grade,
        "subscores": {
            "carbon_intensity": round(s_carbon * 100.0, 1),
            "energy_efficiency": round(s_energy * 100.0, 1),
            "utilization_optimality": round(s_util * 100.0, 1),
            "renewable_grid_factor": round(s_renewable * 100.0, 1),
        },
        "formula": "Score = 100 * [0.40*S_carbon + 0.30*S_energy + 0.20*S_util + 0.10*S_renewable]",
        "emission_per_unit": round(emission_per_unit, 6),
        "kwh_per_hour": round(kwh_per_hour, 4)
    }
