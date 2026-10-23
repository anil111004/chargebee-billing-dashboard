import unittest
from unittest.mock import patch

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_health_check(self):
        response = self.app.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")

    def test_cors_allows_configured_render_host(self):
        with patch("app.ALLOWED_ORIGINS", ["chargebee-billing-dashboard.onrender.com"]):
            response = self.app.get(
                "/api/health",
                headers={"Origin": "https://chargebee-billing-dashboard.onrender.com"},
            )
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "https://chargebee-billing-dashboard.onrender.com",
        )

    def test_dashboard_route(self):
        response = self.app.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("metrics", data)
        self.assertIn("recent_subscriptions", data)


if __name__ == "__main__":
    unittest.main()
