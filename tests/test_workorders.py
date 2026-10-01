"""
Unit tests for workorders generator and physical plies layer.
"""

import os
import unittest
from costing.data_import.mitek_parser import load_mitek_file
from costing.workorders.generator import generate_production_workorders, WorkorderGenerator
from costing.workorders.exports import export_workorders_csv, export_cutting_plan_csv


class TestWorkorders(unittest.TestCase):
    def setUp(self):
        sample_file = os.path.join("output", "Богородск 21 h1400 t40.xlsm")
        if os.path.exists(sample_file):
            self.data = load_mitek_file(sample_file)
        else:
            self.data = None

    def test_workorder_generation(self):
        if not self.data:
            self.skipTest("Sample data not available")
        wo = generate_production_workorders(self.data, stock_length_mm=6000.0)
        
        self.assertIn("assembly_tasks", wo)
        self.assertIn("cutting_plan", wo)
        self.assertIn("plates_summary", wo)
        self.assertGreater(wo["total_physical_layers"], 0)
        self.assertGreater(wo["total_press_points"], 0)
        self.assertEqual(wo["total_physical_layers"], len(wo["assembly_tasks"]))

        # Test CSV export
        wo_csv = export_workorders_csv(wo)
        self.assertIn("ПРОИЗВОДСТВЕННЫЙ НАРЯД", wo_csv)
        self.assertIn("TSK-001", wo_csv)

        cut_csv = export_cutting_plan_csv(wo["cutting_plan"])
        self.assertIn("КАРТА РАСКРОЯ", cut_csv)

    def test_multi_ply_truss_generation(self):
        """
        Тестирование многослойных пакетов ферм (plies=2, qty=3 -> 6 физических задач).
        """
        synthetic_project = {
            "summary": {"project_name": "Тест многослойности"},
            "frames": [
                {
                    "name": "Ферма 2х-слойная",
                    "qty": 3,
                    "plies": 2,
                    "total_layers": 6,
                    "press_points_ply": 18,
                    "vol_m3_ply": 0.15,
                    "plates_m2_ply": 0.35,
                    "span_mm": 9000,
                    "height_mm": 2100,
                    "pitch_deg": 25.0
                }
            ],
            "timber": [],
            "plates": [
                {"size_str": "100x150", "gauge": "T150", "qty": 12, "area_m2": 0.18}
            ]
        }
        
        wo = generate_production_workorders(synthetic_project)
        self.assertEqual(wo["total_physical_layers"], 6)
        self.assertEqual(len(wo["assembly_tasks"]), 6)
        self.assertEqual(wo["total_press_points"], 6 * 18)
        self.assertAlmostEqual(wo["total_timber_vol_m3"], 6 * 0.15, places=4)

        # Check each task structure
        for idx, task in enumerate(wo["assembly_tasks"], start=1):
            self.assertEqual(task["task_id"], f"TSK-{idx:03d}")
            self.assertEqual(task["layer_num"], idx)
            self.assertEqual(task["total_layers_for_frame"], 6)
            self.assertEqual(task["packet_info"], "3 пак. x 2 сл.")
            self.assertEqual(task["press_points"], 18)


if __name__ == "__main__":
    unittest.main()
