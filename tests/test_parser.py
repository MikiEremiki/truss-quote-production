"""
Unit tests for data_import layer (MiTek parser).
"""

import os
import unittest
from costing.data_import.mitek_parser import load_mitek_file, parse_mitek_workbook


class TestMiTekParser(unittest.TestCase):
    def setUp(self):
        self.sample_file = os.path.join("output", "Богородск 21 h1400 t40.xlsm")

    def test_parse_sample_file(self):
        if not os.path.exists(self.sample_file):
            self.skipTest("Sample file not found")
        data = load_mitek_file(self.sample_file)
        
        self.assertIn("summary", data)
        self.assertIn("frames", data)
        self.assertIn("timber", data)
        self.assertIn("plates", data)
        self.assertIn("fasteners", data)
        
        summary = data["summary"]
        self.assertGreater(summary["total_net_timber_m3"], 0.0)
        self.assertGreater(summary["total_timber_surface_m2"], 0.0)
        self.assertGreater(summary["total_plates_area_m2"], 0.0)
        self.assertGreater(summary["total_physical_layers"], 0)
        
    def test_parse_empty_workbook(self):
        """
        Тестирование парсинга пустого Excel-файла без необходимых листов.
        """
        import openpyxl
        wb = openpyxl.Workbook() # only has 'Sheet'
        data = parse_mitek_workbook(wb)
        self.assertIn("summary", data)
        self.assertEqual(data["frames"], [])
        self.assertEqual(data["timber"], [])
        self.assertEqual(data["plates"], [])
        self.assertEqual(data["summary"]["total_net_timber_m3"], 0.0)


if __name__ == "__main__":
    unittest.main()
