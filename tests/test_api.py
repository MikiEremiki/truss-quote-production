"""
Unit tests for API layer.
"""

import unittest
from costing import __version__, __version_suffix__, __version_full__
from costing.api.app import app
from costing.api.routes import (
    get_sample_data,
    recalculate,
    calculate_costing_endpoint,
    calculate_positions_endpoint,
    optimize_cutting_endpoint,
    calculate_financials_endpoint,
    create_quote_endpoint,
    get_workorders_endpoint,
    get_app_info
)
from costing.api.schemas import CalculateRequest, QuoteRequest, WorkorderRequest


class TestAPIEndpoints(unittest.TestCase):
    def test_version_info(self):
        self.assertEqual(__version__, "0.1.0")
        self.assertEqual(__version_suffix__, "")
        self.assertEqual(__version_full__, "v0.1.0")
        self.assertEqual(app.version, "0.1.0")

        res = get_app_info()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["version"], "0.1.0")
        self.assertEqual(res["version_suffix"], "")
        self.assertEqual(res["version_full"], "v0.1.0")

    def test_sample_endpoint(self):
        res = get_sample_data()
        self.assertEqual(res["status"], "success")
        self.assertIn("data", res)
        self.assertIn("cost", res)
        self.assertIn("cutting", res)

    def test_costing_calculate_endpoint(self):
        payload = {"timber_price_m3": 35000.0, "treatment_price_m2": 70.0}
        res = calculate_costing_endpoint(payload)
        self.assertEqual(res["status"], "success")
        self.assertIn("cost", res)
        self.assertEqual(res["cost"]["parameters"]["timber_price_m3"], 35000.0)

    def test_positions_calculate_endpoint(self):
        payload = {"custom_items": {"Ф1": {"type": "truss", "work_rate_m3": 5000}}}
        res = calculate_positions_endpoint(payload)
        self.assertEqual(res["status"], "success")
        self.assertIn("cost", res)

    def test_cutting_optimize_endpoint(self):
        payload = {"stock_length_mm": 6200.0}
        res = optimize_cutting_endpoint(payload)
        self.assertEqual(res["status"], "success")
        self.assertIn("cutting", res)
        self.assertIn("summary", res["cutting"])

    def test_financials_calculate_endpoint(self):
        payload = {"agent_pct": 10.0, "discount_val": 5.0}
        res = calculate_financials_endpoint(payload)
        self.assertEqual(res["status"], "success")
        self.assertIn("cost", res)
        self.assertEqual(res["cost"]["financial_summary"]["agent_pct"], 10.0)

    def test_calculate_endpoint(self):
        payload = {"margin_pct": 50.0, "stock_length_mm": 6500.0}
        res = recalculate(payload)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["cost"]["parameters"]["margin_pct"], 50.0)

    def test_quote_endpoint(self):
        req = QuoteRequest(project_name="Тестовый проект", client_name="Тест")
        res = create_quote_endpoint(req)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["quote"]["project_name"], "Тестовый проект")

    def test_workorders_endpoint(self):
        req = WorkorderRequest(stock_length_mm=6000.0)
        res = get_workorders_endpoint(req)
        self.assertEqual(res["status"], "success")
        self.assertIn("workorders", res)

    def test_download_endpoints_via_testclient(self):
        """
        Тестирование эндпоинтов скачивания файлов через FastAPI TestClient.
        """
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
        except (ImportError, RuntimeError) as e:
            self.skipTest(f"TestClient requires httpx: {e}")
            return

        # 1. Root index.html
        resp_root = client.get("/")
        self.assertEqual(resp_root.status_code, 200)
        self.assertIn("MiTek Engine & Costing Pro", resp_root.text)

        # 2. Quote HTML download
        resp_html = client.get("/api/quote/download/html?client_name=ТестовыйЗаказчик")
        self.assertEqual(resp_html.status_code, 200)
        self.assertEqual(resp_html.headers.get("content-type"), "text/html; charset=utf-8")
        self.assertIn("attachment; filename=", resp_html.headers.get("content-disposition", ""))
        self.assertIn("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", resp_html.text)

        # 3. Quote CSV download
        resp_q_csv = client.get("/api/quote/download/csv?client_name=ТестовыйЗаказчик")
        self.assertEqual(resp_q_csv.status_code, 200)
        self.assertEqual(resp_q_csv.headers.get("content-type"), "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=", resp_q_csv.headers.get("content-disposition", ""))

        # 4. Cutting CSV download
        resp_cut_csv = client.get("/api/cutting/download/csv?stock_length_mm=6000")
        self.assertEqual(resp_cut_csv.status_code, 200)
        self.assertEqual(resp_cut_csv.headers.get("content-type"), "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=", resp_cut_csv.headers.get("content-disposition", ""))

        # 5. Workorders CSV download
        resp_wo_csv = client.get("/api/workorders/download/csv?stock_length_mm=6000")
        self.assertEqual(resp_wo_csv.status_code, 200)
        self.assertEqual(resp_wo_csv.headers.get("content-type"), "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=", resp_wo_csv.headers.get("content-disposition", ""))


if __name__ == "__main__":
    unittest.main()
