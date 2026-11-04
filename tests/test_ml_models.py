"""
Tests for Modular Machine Learning Subsystem
"""

import unittest
from backend.ml.inference import get_ml_engine
from backend.ml.scoring import compute_carbon_efficiency_score
from backend.ml.explainability import explain_prediction
from backend.ml.preprocessing import DEVICE_FEATURE_COLUMNS


class TestMLModels(unittest.TestCase):
    def setUp(self):
        self.engine = get_ml_engine()

    def test_carbon_and_energy_prediction(self):
        sample = {
            "device_type": "laptop",
            "cpu_util_pct": 45.0,
            "memory_gb": 16.0,
            "storage_gb": 512.0,
            "uptime_hours_per_day": 8.0,
            "region": "ap-south-1"
        }
        carbon_pred = self.engine.predict_device_carbon(sample)
        energy_pred = self.engine.predict_device_energy(sample)

        self.assertGreater(carbon_pred, 0.0)
        self.assertGreater(energy_pred, 0.0)

    def test_carbon_efficiency_score(self):
        score_data = compute_carbon_efficiency_score({
            "total_daily_kg": 0.15,
            "total_kwh_daily": 0.35,
            "uptime_hours_per_day": 8.0,
            "cpu_util_pct": 55.0,
            "renewable_pct": 30.0
        })
        self.assertIn("score", score_data)
        self.assertIn("grade", score_data)
        self.assertGreaterEqual(score_data["score"], 0.0)
        self.assertLessEqual(score_data["score"], 100.0)

    def test_clustering(self):
        devices = [
            {"device_id": "1", "device_type": "laptop", "cpu_util_pct": 20.0, "total_daily_kg": 0.1},
            {"device_id": "2", "device_type": "server_2u", "cpu_util_pct": 90.0, "total_daily_kg": 2.5}
        ]
        clustered = self.engine.cluster_devices(devices)
        self.assertEqual(len(clustered), 2)
        self.assertIn("cluster_label", clustered[0])

    def test_explainability(self):
        features = [45.0, 16.0, 512.0, 8.0, 0.0, 1.0, 1.0, 45.0, 8.0, 0.0, 0.71]
        exp = explain_prediction(features, DEVICE_FEATURE_COLUMNS, 0.18)
        self.assertIn("contributions", exp)
        self.assertIn("narrative", exp)
        self.assertGreater(len(exp["contributions"]), 0)


if __name__ == "__main__":
    unittest.main()
