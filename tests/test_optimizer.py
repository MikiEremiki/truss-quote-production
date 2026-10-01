"""
Unit tests for workorders optimizer (1D Bin Packing stock cutting).
"""

import unittest
from costing.workorders.optimizer import optimize_cutting_stock


class TestCuttingOptimizer(unittest.TestCase):
    def test_cutting_single_section(self):
        timber_items = [
            {"truss": "T1", "label": "B1", "section": "45x145", "length_m": 2.5, "qty": 4},
            {"truss": "T1", "label": "T1", "section": "45x145", "length_m": 1.2, "qty": 2},
            {"truss": "T1", "label": "W1", "section": "45x95", "length_m": 0.8, "qty": 6},
        ]
        
        result = optimize_cutting_stock(timber_items, stock_length_mm=6000.0, kerf_mm=4.0)
        
        self.assertIn("summary", result)
        self.assertIn("by_section", result)
        
        sec_145 = result["by_section"]["45x145"]
        # 4 * 2.5 = 10m, 2 * 1.2 = 2.4m -> total net = 12.4m -> at least 3 bars of 6m
        self.assertGreaterEqual(sec_145["total_bars"], 3)
        self.assertEqual(sec_145["total_parts_count"], 6)

    def test_oversize_part(self):
        timber_items = [
            {"truss": "T1", "label": "B1", "section": "45x145", "length_m": 7.5, "qty": 1},
        ]
        result = optimize_cutting_stock(timber_items, stock_length_mm=6000.0)
        sec = result["by_section"]["45x145"]
        self.assertEqual(sec["total_bars"], 1)
        self.assertTrue(sec["bars"][0]["oversize"])


if __name__ == "__main__":
    unittest.main()
