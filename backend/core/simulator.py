"""
Carbonomics v3 — Interactive What-If Carbon Reduction Simulator
Runs physics-based simulations to evaluate infrastructure transformations,
fleet right-sizing, clean grid migrations, and operational sleep policies.
"""

from typing import Dict, Any, List, Optional
from .carbon_calculator import CarbonCalculator
from .emission_factors import registry


class WhatIfSimulator:
    """Physics-based scenario simulation engine"""

    def __init__(self):
        self.calc = CarbonCalculator()

    def simulate(
        self,
        base_device_type: str = "laptop",
        device_count: int = 50,
        current_cpu_util: float = 45.0,
        target_cpu_util: float = 30.0,
        current_uptime_hours: float = 12.0,
        target_uptime_hours: float = 8.0,
        current_region: str = "ap-south-1",
        target_region: str = "eu-north-1",
        current_pue: float = 1.4,
        target_pue: float = 1.15,
        memory_gb: float = 16.0,
        storage_gb: float = 512.0,
        gpu_util_pct: float = 10.0,
        scenario_name: str = "Custom Transformation"
    ) -> Dict[str, Any]:
        """
        Evaluate before-and-after operational impacts on carbon and energy.
        """
        device_count = max(1, int(device_count))

        # 1. Baseline Evaluation
        baseline_single = self.calc.estimate_device(
            device_type=base_device_type,
            cpu_util_pct=current_cpu_util,
            memory_gb=memory_gb,
            storage_gb=storage_gb,
            uptime_hours_per_day=current_uptime_hours,
            region=current_region,
            gpu_util_pct=gpu_util_pct,
            cooling_pue=current_pue
        )

        baseline_daily_kwh = baseline_single["total_kwh_daily"] * device_count
        baseline_daily_kg = baseline_single["total_daily_kg"] * device_count
        baseline_annual_kg = baseline_daily_kg * 365.0
        baseline_annual_t = baseline_annual_kg / 1000.0

        # 2. Simulated Target Evaluation
        simulated_single = self.calc.estimate_device(
            device_type=base_device_type,
            cpu_util_pct=target_cpu_util,
            memory_gb=memory_gb,
            storage_gb=storage_gb,
            uptime_hours_per_day=target_uptime_hours,
            region=target_region,
            gpu_util_pct=max(0.0, gpu_util_pct * 0.7),
            cooling_pue=target_pue
        )

        simulated_daily_kwh = simulated_single["total_kwh_daily"] * device_count
        simulated_daily_kg = simulated_single["total_daily_kg"] * device_count
        simulated_annual_kg = simulated_daily_kg * 365.0
        simulated_annual_t = simulated_annual_kg / 1000.0

        # 3. Deltas & Reductions
        savings_daily_kg = max(0.0, baseline_daily_kg - simulated_daily_kg)
        savings_annual_kg = savings_daily_kg * 365.0
        savings_annual_t = savings_annual_kg / 1000.0
        savings_daily_kwh = max(0.0, baseline_daily_kwh - simulated_daily_kwh)
        savings_annual_kwh = savings_daily_kwh * 365.0

        pct_reduction = round((savings_daily_kg / max(baseline_daily_kg, 1e-6)) * 100.0, 1)

        # Trees offset equivalent
        trees_saved = round(savings_annual_kg / 21.77, 1)
        cars_off_road_km = round(savings_daily_kg / 0.21, 1)

        # Cost savings estimate (average enterprise electricity ~$0.15/kWh)
        cost_savings_annual_usd = round(savings_annual_kwh * 0.15, 2)

        return {
            "scenario_name": scenario_name,
            "device_count": device_count,
            "baseline": {
                "daily_kwh": round(baseline_daily_kwh, 2),
                "daily_kg": round(baseline_daily_kg, 4),
                "annual_kg": round(baseline_annual_kg, 2),
                "annual_t": round(baseline_annual_t, 3),
                "region": current_region,
                "region_name": registry.get_region(current_region)["name"],
                "pue": current_pue,
                "uptime_hours": current_uptime_hours,
            },
            "simulated": {
                "daily_kwh": round(simulated_daily_kwh, 2),
                "daily_kg": round(simulated_daily_kg, 4),
                "annual_kg": round(simulated_annual_kg, 2),
                "annual_t": round(simulated_annual_t, 3),
                "region": target_region,
                "region_name": registry.get_region(target_region)["name"],
                "pue": target_pue,
                "uptime_hours": target_uptime_hours,
            },
            "savings": {
                "daily_kg": round(savings_daily_kg, 4),
                "annual_kg": round(savings_annual_kg, 2),
                "annual_t": round(savings_annual_t, 3),
                "daily_kwh": round(savings_daily_kwh, 2),
                "annual_kwh": round(savings_annual_kwh, 2),
                "pct_reduction": pct_reduction,
                "trees_equivalent": trees_saved,
                "car_km_daily": cars_off_road_km,
                "estimated_cost_savings_usd": cost_savings_annual_usd
            }
        }

    def get_presets(self) -> Dict[str, Dict[str, Any]]:
        """Pre-configured enterprise scenario archetypes"""
        return {
            "energy_efficient": {
                "name": "Aggressive Green Policy",
                "target_cpu_util": 25.0,
                "target_uptime_hours": 7.5,
                "target_region": "eu-north-1",
                "target_pue": 1.12,
                "description": "Enforces 10-minute automated sleep and routes batch pipelines to Scandinavian hydro grids."
            },
            "renewable_transition": {
                "name": "100% Renewable Grid Transition",
                "target_cpu_util": 40.0,
                "target_uptime_hours": 8.0,
                "target_region": "eu-north-1",
                "target_pue": 1.15,
                "description": "Migrates deployment zones directly to regional grids with >90% renewable generation."
            },
            "datacenter_consolidation": {
                "name": "Modernized High-Density Datacenter",
                "target_cpu_util": 65.0,
                "target_uptime_hours": 24.0,
                "target_region": "us-west-2",
                "target_pue": 1.14,
                "description": "Consolidates low-utilization rack servers into high-density virtualized nodes with liquid cooling."
            }
        }

