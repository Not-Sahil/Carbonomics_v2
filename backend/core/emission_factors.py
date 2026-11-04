"""
Carbonomics v3 — Emission Factor Registry & Hardware Profile Manager
Provides centralized, hot-reloadable emission factors and hardware coefficients.
Compliant with Green Software Foundation (GSF) Software Carbon Intensity (SCI).
"""

import json
import os
import threading
from typing import Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "emission_factors.json")

# Built-in robust defaults
DEFAULT_REGIONS = {
    "ap-south-1": {"name": "Asia Pacific (Mumbai)", "country": "IN", "factor": 0.71, "renewable_pct": 18, "grid_intensity_grade": "High", "pue_typical": 1.35},
    "ap-southeast-1": {"name": "Asia Pacific (Singapore)", "country": "SG", "factor": 0.49, "renewable_pct": 20, "grid_intensity_grade": "Medium-High", "pue_typical": 1.32},
    "ap-northeast-1": {"name": "Asia Pacific (Tokyo)", "country": "JP", "factor": 0.47, "renewable_pct": 24, "grid_intensity_grade": "Medium", "pue_typical": 1.28},
    "us-east-1": {"name": "US East (N. Virginia)", "country": "US", "factor": 0.42, "renewable_pct": 28, "grid_intensity_grade": "Medium", "pue_typical": 1.22},
    "us-west-1": {"name": "US West (N. California)", "country": "US", "factor": 0.21, "renewable_pct": 58, "grid_intensity_grade": "Low-Medium", "pue_typical": 1.18},
    "us-west-2": {"name": "US West (Oregon)", "country": "US", "factor": 0.15, "renewable_pct": 74, "grid_intensity_grade": "Low", "pue_typical": 1.15},
    "eu-west-1": {"name": "Europe West (Ireland)", "country": "IE", "factor": 0.28, "renewable_pct": 52, "grid_intensity_grade": "Medium-Low", "pue_typical": 1.16},
    "eu-central-1": {"name": "Europe Central (Frankfurt)", "country": "DE", "factor": 0.35, "renewable_pct": 46, "grid_intensity_grade": "Medium", "pue_typical": 1.20},
    "eu-north-1": {"name": "Europe North (Stockholm)", "country": "SE", "factor": 0.08, "renewable_pct": 95, "grid_intensity_grade": "Ultra-Low", "pue_typical": 1.12},
    "sa-east-1": {"name": "South America (São Paulo)", "country": "BR", "factor": 0.18, "renewable_pct": 78, "grid_intensity_grade": "Low-Medium", "pue_typical": 1.25},
    "ca-central-1": {"name": "Canada Central (Montreal)", "country": "CA", "factor": 0.13, "renewable_pct": 82, "grid_intensity_grade": "Low", "pue_typical": 1.15},
    "on-premise": {"name": "On-Premise / Corporate Lab", "country": "Global", "factor": 0.42, "renewable_pct": 20, "grid_intensity_grade": "Medium", "pue_typical": 1.45},
}

DEFAULT_PROFILES = {
    "laptop": {"cpu_tdp": 45, "idle_w": 8, "typical_w": 25, "memory_watt_gb": 0.3, "display_w": 5, "embodied_kg_co2": 180, "lifespan_years": 4},
    "desktop": {"cpu_tdp": 125, "idle_w": 40, "typical_w": 80, "memory_watt_gb": 0.4, "display_w": 30, "embodied_kg_co2": 320, "lifespan_years": 5},
    "workstation": {"cpu_tdp": 250, "idle_w": 80, "typical_w": 200, "memory_watt_gb": 0.5, "display_w": 40, "embodied_kg_co2": 520, "lifespan_years": 5},
    "server_1u": {"cpu_tdp": 200, "idle_w": 80, "typical_w": 150, "memory_watt_gb": 0.4, "display_w": 0, "embodied_kg_co2": 950, "lifespan_years": 4},
    "server_2u": {"cpu_tdp": 400, "idle_w": 120, "typical_w": 280, "memory_watt_gb": 0.4, "display_w": 0, "embodied_kg_co2": 1400, "lifespan_years": 4},
    "server_blade": {"cpu_tdp": 300, "idle_w": 100, "typical_w": 220, "memory_watt_gb": 0.4, "display_w": 0, "embodied_kg_co2": 1100, "lifespan_years": 4},
    "raspberry_pi": {"cpu_tdp": 5, "idle_w": 2, "typical_w": 4, "memory_watt_gb": 0.1, "display_w": 0, "embodied_kg_co2": 15, "lifespan_years": 5},
    "mini_pc": {"cpu_tdp": 35, "idle_w": 5, "typical_w": 15, "memory_watt_gb": 0.3, "display_w": 0, "embodied_kg_co2": 120, "lifespan_years": 5},
    "network_switch": {"cpu_tdp": 0, "idle_w": 20, "typical_w": 30, "memory_watt_gb": 0, "display_w": 0, "embodied_kg_co2": 150, "lifespan_years": 6},
    "router": {"cpu_tdp": 0, "idle_w": 8, "typical_w": 12, "memory_watt_gb": 0, "display_w": 0, "embodied_kg_co2": 60, "lifespan_years": 5},
    "cloud_vm_small": {"cpu_tdp": 30, "idle_w": 6, "typical_w": 18, "memory_watt_gb": 0.35, "display_w": 0, "embodied_kg_co2": 80, "lifespan_years": 3},
    "cloud_vm_medium": {"cpu_tdp": 70, "idle_w": 15, "typical_w": 45, "memory_watt_gb": 0.35, "display_w": 0, "embodied_kg_co2": 160, "lifespan_years": 3},
    "cloud_vm_large": {"cpu_tdp": 150, "idle_w": 35, "typical_w": 110, "memory_watt_gb": 0.35, "display_w": 0, "embodied_kg_co2": 320, "lifespan_years": 3},
    "cloud_vm_gpu": {"cpu_tdp": 180, "idle_w": 50, "typical_w": 350, "memory_watt_gb": 0.45, "display_w": 0, "embodied_kg_co2": 750, "lifespan_years": 3},
}

DEFAULT_ALIASES = {
    "india": "ap-south-1", "in": "ap-south-1", "asia": "ap-southeast-1",
    "us": "us-east-1", "usa": "us-east-1", "united states": "us-east-1",
    "europe": "eu-central-1", "germany": "eu-central-1", "de": "eu-central-1",
    "ireland": "eu-west-1", "sweden": "eu-north-1", "australia": "ap-southeast-1",
    "au": "ap-southeast-1", "japan": "ap-northeast-1", "jp": "ap-northeast-1",
    "singapore": "ap-southeast-1", "sg": "ap-southeast-1", "canada": "ca-central-1",
    "ca": "ca-central-1", "brazil": "sa-east-1", "br": "sa-east-1",
}


class EmissionFactorRegistry:
    """Thread-safe, reloadable emission factor registry"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmissionFactorRegistry, cls).__new__(cls)
                cls._instance._init_registry()
            return cls._instance

    def _init_registry(self):
        self.regions = dict(DEFAULT_REGIONS)
        self.device_profiles = dict(DEFAULT_PROFILES)
        self.aliases = dict(DEFAULT_ALIASES)
        self.cloud_providers = {}
        self.hardware_constants = {
            "memory_ddr4_watt_per_gb": 0.3725,
            "memory_ddr5_watt_per_gb": 0.2800,
            "storage_ssd_active_watt_per_gb": 0.0018,
            "storage_hdd_active_watt_per_gb": 0.0055,
            "network_kwh_per_gb_lan": 0.0001,
            "network_kwh_per_gb_wan": 0.0012,
            "gpu_tdp_workstation": 300,
            "gpu_tdp_desktop": 220,
            "gpu_tdp_laptop": 80,
            "gpu_tdp_datacenter_a100": 400,
            "gpu_idle_fraction": 0.12,
        }
        self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(DATA_PATH):
            try:
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "regions" in data:
                        self.regions.update(data["regions"])
                    if "device_profiles" in data:
                        self.device_profiles.update(data["device_profiles"])
                    if "country_aliases" in data:
                        self.aliases.update(data["country_aliases"])
                    if "cloud_providers" in data:
                        self.cloud_providers.update(data["cloud_providers"])
                    if "hardware_coefficients" in data:
                        self.hardware_constants.update(data["hardware_coefficients"])
            except Exception as e:
                print(f"Warning: could not load emission factors from {DATA_PATH}: {e}")

    def save_to_disk(self):
        try:
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            payload = {
                "version": "3.0.0",
                "regions": self.regions,
                "device_profiles": self.device_profiles,
                "country_aliases": self.aliases,
                "cloud_providers": self.cloud_providers,
                "hardware_coefficients": self.hardware_constants,
            }
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            return True
        except Exception as e:
            print(f"Warning: could not save emission factors: {e}")
            return False

    def resolve_region_key(self, region_name: str) -> str:
        if not region_name:
            return "ap-south-1"
        cleaned = str(region_name).strip().lower()
        if cleaned in self.regions:
            return cleaned
        if cleaned in self.aliases:
            return self.aliases[cleaned]
        for key in self.regions:
            if key in cleaned:
                return key
        return "ap-south-1"

    def get_region(self, region_name: str) -> Dict[str, Any]:
        key = self.resolve_region_key(region_name)
        data = dict(self.regions.get(key, self.regions["ap-south-1"]))
        data["region_key"] = key
        return data

    def get_factor(self, region_name: str) -> float:
        return self.get_region(region_name).get("factor", 0.42)

    def get_profile(self, device_type: str) -> Dict[str, Any]:
        key = str(device_type).strip().lower() if device_type else "laptop"
        if key not in self.device_profiles:
            # Map common variations
            if "server" in key:
                key = "server_1u"
            elif "desk" in key or "pc" in key:
                key = "desktop"
            elif "workstation" in key or "rig" in key:
                key = "workstation"
            elif "pi" in key:
                key = "raspberry_pi"
            elif "cloud" in key or "vm" in key:
                key = "cloud_vm_medium"
            else:
                key = "laptop"
        return dict(self.device_profiles.get(key, self.device_profiles["laptop"]))

    def get_hardware_constant(self, key: str, default: float = 0.0) -> float:
        return float(self.hardware_constants.get(key, default))

    def update_region(self, region_key: str, data: Dict[str, Any]) -> bool:
        with self._lock:
            if region_key in self.regions:
                self.regions[region_key].update(data)
            else:
                self.regions[region_key] = data
            return self.save_to_disk()


# Singleton instance
registry = EmissionFactorRegistry()

# Backwards compatibility exports for existing code
REGION_FACTORS = registry.regions
DEVICE_PROFILES = registry.device_profiles
DEVICE_TDP_PROFILES = registry.device_profiles

