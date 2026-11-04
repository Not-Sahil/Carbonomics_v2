"""
Tests for Flask REST Endpoints and AI Advisor
"""

import unittest
from backend.api.app import app


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "3.0.0")

    def test_fleet_devices(self):
        res = self.client.get("/api/fleet/devices")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("devices", data)
        self.assertIn("summary", data)

    def test_cloud_compare(self):
        res = self.client.get("/api/cloud/compare")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("regions", data)
        self.assertGreater(len(data["regions"]), 0)

    def test_ai_advisor(self):
        res = self.client.post("/api/advisor/chat", json={"query": "What is our carbon footprint?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("answer", data)
        self.assertIn("tool_used", data)


if __name__ == "__main__":
    unittest.main()

