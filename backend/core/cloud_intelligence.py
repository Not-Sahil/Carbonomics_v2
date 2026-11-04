"""
Carbonomics v3 — Green Cloud Intelligence & Carbon-Aware Scheduling Simulator
Analyzes cloud infrastructure emissions across AWS, GCP, and Azure.
Simulates time-shifted and geo-shifted batch job execution to minimize grid carbon intensity.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from .emission_factors import registry


class GreenCloudIntelligence:
    """Cloud carbon comparison and carbon-aware batch scheduler"""

    def __init__(self):
        self.registry = registry

    def compare_regions(self, vcpus: int = 8, memory_gb: float = 32.0, uptime_hours: float = 24.0) -> List[Dict[str, Any]]:
        """
        Compare carbon intensity and estimated daily emissions across global cloud regions.
        """
        # Baseline wattage for 8 vCPU modern server slice (~90W typical active)
        nominal_watts = (vcpus * 12.0) + (memory_gb * 0.35)
        kwh_uncooled = (nominal_watts * uptime_hours) / 1000.0

        comparison = []
        for r_key, r_info in self.registry.regions.items():
            if r_key == "on-premise":
                continue

            pue = r_info.get("pue_typical", 1.2)
            ef = r_info.get("factor", 0.42)
            total_kwh = kwh_uncooled * pue
            daily_kg = total_kwh * ef
            annual_kg = daily_kg * 365.0

            # Green score (0 - 100) based on low emission factor & high renewables
            green_score = round(min(100.0, max(10.0, (1.0 - (ef / 0.85)) * 60.0 + (r_info.get("renewable_pct", 20) * 0.4))), 1)

            comparison.append({
                "region_key": r_key,
                "name": r_info.get("name"),
                "country": r_info.get("country"),
                "emission_factor_kg_kwh": round(ef, 4),
                "renewable_pct": r_info.get("renewable_pct"),
                "typical_pue": round(pue, 2),
                "daily_kwh": round(total_kwh, 3),
                "daily_kg_co2": round(daily_kg, 4),
                "annual_t_co2": round(annual_kg / 1000.0, 4),
                "green_score": green_score,
                "grade": r_info.get("grid_intensity_grade", "Medium")
            })

        comparison.sort(key=lambda x: x["daily_kg_co2"])
        return comparison

    def schedule_carbon_aware_job(
        self,
        job_name: str = "Nightly ML Batch Pipeline",
        duration_hours: float = 4.0,
        vcpus: int = 16,
        memory_gb: float = 64.0,
        preferred_region: str = "ap-south-1"
    ) -> Dict[str, Any]:
        """
        Carbon-Aware Scheduling Simulator.
        Evaluates a 24-hour diurnal solar/wind grid intensity curve to identify the lowest carbon execution window.
        """
        base_region_info = self.registry.get_region(preferred_region)
        base_ef = base_region_info.get("factor", 0.71)

        # Diurnal grid intensity profile (solar noon has highest renewable supply; evening peak has lowest)
        hourly_profiles = []
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        # Energy consumption of the job
        nominal_watts = (vcpus * 14.0) + (memory_gb * 0.35)
        pue = base_region_info.get("pue_typical", 1.25)
        job_kwh = (nominal_watts * duration_hours / 1000.0) * pue

        best_window = None
        min_carbon = float("inf")

        for h in range(24):
            time_slot = now + timedelta(hours=h)
            hour_of_day = time_slot.hour

            # Solar surge between 10:00 and 15:00 UTC, evening fossil peak at 18:00 - 22:00
            if 10 <= hour_of_day <= 15:
                carbon_multiplier = 0.72  # Solar maximum
                clean_status = "Optimal (High Solar/Wind)"
            elif 18 <= hour_of_day <= 22:
                carbon_multiplier = 1.24  # Peaker plants active
                clean_status = "Carbon Intensive (Peak Grid Demand)"
            else:
                carbon_multiplier = 0.95
                clean_status = "Moderate Base Load"

            slot_ef = round(base_ef * carbon_multiplier, 4)
            carbon_emitted = round(job_kwh * slot_ef, 4)

            slot_data = {
                "start_time": time_slot.strftime("%Y-%m-%d %H:00 UTC"),
                "hour": hour_of_day,
                "emission_factor": slot_ef,
                "job_carbon_kg": carbon_emitted,
                "status": clean_status
            }
            hourly_profiles.append(slot_data)

            if carbon_emitted < min_carbon:
                min_carbon = carbon_emitted
                best_window = slot_data

        baseline_carbon = round(job_kwh * base_ef, 4)
        saved_carbon = max(0.0, baseline_carbon - min_carbon)
        saved_pct = round((saved_carbon / max(baseline_carbon, 1e-6)) * 100.0, 1)

        # Alternative: Geo-shifting to greenest region (eu-north-1)
        greenest_ef = self.registry.get_region("eu-north-1")["factor"]
        geo_shifted_carbon = round(job_kwh * greenest_ef, 4)
        geo_saved_pct = round(((baseline_carbon - geo_shifted_carbon) / baseline_carbon) * 100.0, 1)

        return {
            "job_name": job_name,
            "duration_hours": duration_hours,
            "vcpus": vcpus,
            "memory_gb": memory_gb,
            "energy_kwh": round(job_kwh, 3),
            "unoptimized_carbon_kg": baseline_carbon,
            "time_shifted_carbon_kg": min_carbon,
            "time_shift_savings_kg": round(saved_carbon, 4),
            "time_shift_savings_pct": saved_pct,
            "recommended_window": best_window,
            "geo_shift_alternative": {
                "target_region": "eu-north-1",
                "carbon_kg": geo_shifted_carbon,
                "savings_pct": geo_saved_pct
            },
            "hourly_timeline": hourly_profiles
        }
