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
        self.assertIn("boards_summary", wo)
        self.assertIn("cutting_plan", wo)
        self.assertIn("plates_summary", wo)
        self.assertGreater(wo["total_physical_layers"], 0)
        self.assertGreater(wo["total_frames_count"], 0)
        self.assertGreater(wo["total_boards_count"], 0)
        self.assertGreater(wo["total_press_points"], 0)
        self.assertEqual(len(wo["assembly_tasks"]), len(self.data.get("frames", [])))

        # Проверка калькуляции досок по сечениям
        self.assertGreater(len(wo["boards_summary"]), 0)
        for b in wo["boards_summary"]:
            self.assertIn("section", b)
            self.assertGreater(b["total_boards"], 0)
            self.assertGreater(b["total_length_m"], 0.0)
            self.assertGreater(b["total_volume_m3"], 0.0)

        # Test CSV export
        wo_csv = export_workorders_csv(wo)
        self.assertIn("ПРОИЗВОДСТВЕННЫЙ НАРЯД", wo_csv)
        self.assertIn("ПОТРЕБНОСТЬ В ПИЛОМАТЕРИАЛЕ", wo_csv)
        self.assertIn("СБОРОЧНЫЕ ЗАДАНИЯ", wo_csv)
        self.assertIn("TSK-001", wo_csv)

        cut_csv = export_cutting_plan_csv(wo["cutting_plan"])
        self.assertIn("КАРТА РАСКРОЯ", cut_csv)

    def test_multi_ply_truss_generation(self):
        """
        Тестирование многослойных пакетов ферм: 1 сборочное задание на марку фермы с указанием количества.
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
            "timber": [
                {
                    "truss": "Ферма 2х-слойная",
                    "label": "T1",
                    "qty": 6,
                    "length_m": 4.5,
                    "thick_mm": 45,
                    "depth_mm": 145,
                    "section": "45x145",
                    "volume_m3": 0.15
                }
            ],
            "plates": [
                {"size_str": "100x150", "gauge": "T150", "qty": 12, "area_m2": 0.18}
            ]
        }
        
        wo = generate_production_workorders(synthetic_project)
        self.assertEqual(wo["total_physical_layers"], 6)
        self.assertEqual(wo["total_frames_count"], 3)
        self.assertEqual(len(wo["assembly_tasks"]), 1)
        self.assertEqual(wo["total_press_points"], 6 * 18)
        self.assertAlmostEqual(wo["total_timber_vol_m3"], 6 * 0.15, places=4)
        self.assertGreater(wo["total_boards_count"], 0)
        self.assertEqual(len(wo["boards_summary"]), 1)
        self.assertEqual(wo["boards_summary"][0]["section"], "45x145")

        # Check task structure
        task = wo["assembly_tasks"][0]
        self.assertEqual(task["task_id"], "TSK-001")
        self.assertEqual(task["frame_name"], "Ферма 2х-слойная")
        self.assertEqual(task["qty"], 3)
        self.assertEqual(task["span_mm"], 9000)
        self.assertEqual(task["height_mm"], 2100)
        self.assertEqual(task["press_points"], 6 * 18)


if __name__ == "__main__":
    unittest.main()
