"""
Tests for Physics-Based Carbon Calculator Engine (GSF SCI Compliance)
"""

import unittest
from backend.core.carbon_calculator import CarbonCalculator
from backend.core.emission_factors import registry


class TestCarbonCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = CarbonCalculator()

    def test_device_estimation_bounds(self):
        res = self.calc.estimate_device(
            device_type="laptop",
            cpu_util_pct=50,
            memory_gb=16,
            storage_gb=512,
            uptime_hours_per_day=8,
            region="ap-south-1"
        )
        self.assertIn("total_daily_kg", res)
        self.assertIn("total_kwh_daily", res)
        self.assertGreater(res["total_daily_kg"], 0.0)
        self.assertGreater(res["total_kwh_daily"], 0.0)
        self.assertLess(res["total_daily_kg"], 1.5)  # A single laptop in 8h shouldn't exceed 1.5 kg

    def test_service_estimation(self):
        res = self.calc.estimate_service(
            cpu_time_ms=100,
            memory_mb=512,
            daily_requests=5000,
            region="us-east-1"
        )
        self.assertIn("total_daily_kg", res)
        self.assertGreater(res["total_daily_kg"], 0.0)

    def test_cloud_vm_estimation(self):
        res = self.calc.estimate_cloud_vm(
            instance_type="cloud_vm_medium",
            vcpus=4,
            memory_gb=16,
            region="us-west-2"
        )
        self.assertIn("total_daily_kg", res)
        self.assertGreater(res["total_daily_kg"], 0.0)

    def test_fleet_summary_aggregation(self):
        sample_devices = [
            {"total_daily_kg": 0.2, "status": "online", "device_type": "laptop"},
            {"total_daily_kg": 0.8, "status": "online", "device_type": "desktop"},
            {"total_daily_kg": 1.5, "status": "offline", "device_type": "server_1u"}
        ]
        summary = self.calc.compute_fleet_summary(sample_devices)
        self.assertEqual(summary["total_devices"], 3)
        self.assertEqual(summary["online_count"], 2)
        self.assertEqual(summary["offline_count"], 1)
        self.assertAlmostEqual(summary["total_daily_kg"], 2.5, places=3)


if __name__ == "__main__":
    unittest.main()

