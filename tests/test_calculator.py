"""
Unit tests for calculator layer.
"""

import os
import unittest
from costing.data_import.mitek_parser import load_mitek_file
from costing.calculator.engine import CostCalculator, calculate_cost
from costing.core.pricing_catalog import CLIENT_PROFILES


class TestCalculator(unittest.TestCase):
    def setUp(self):
        sample_file = os.path.join("output", "Богородск 21 h1400 t40.xlsm")
        if os.path.exists(sample_file):
            self.data = load_mitek_file(sample_file)
        else:
            self.data = None

    def test_basic_calculation(self):
        if not self.data:
            self.skipTest("Sample data not available")
        calc = calculate_cost(self.data, {})
        
        self.assertIn("financial_summary", calc)
        self.assertIn("structures_financials", calc)
        self.assertIn("extras_financials", calc)
        self.assertIn("positions", calc)
        
        fin = calc["financial_summary"]
        self.assertGreater(fin["total_cost"], 0.0)
        self.assertGreater(fin["client_net_price"], 0.0)
        self.assertGreater(fin["dk_net_profit"], 0.0)

    def test_client_profiles(self):
        if not self.data:
            self.skipTest("Sample data not available")
            
        calc_std = calculate_cost(self.data, {"client_profile": "standard"})
        calc_evd = calculate_cost(self.data, {"client_profile": "evdokimov"})
        calc_dk = calculate_cost(self.data, {"client_profile": "dk_group"})
        
        # Standard margin (58%) should yield higher price than evdokimov (30%) and dk_group (3%)
        p_std = calc_std["financial_summary"]["client_net_price"]
        p_evd = calc_evd["financial_summary"]["client_net_price"]
        p_dk = calc_dk["financial_summary"]["client_net_price"]
        
        self.assertGreater(p_std, p_evd)
        self.assertGreater(p_evd, p_dk)

    def test_design_modes(self):
        if not self.data:
            self.skipTest("Sample data not available")

        # Separate mode
        calc_sep = calculate_cost(self.data, {"design_mode": "separate", "design_price_fixed": 12000, "overhead_pct": 0})
        # Distributed mode
        calc_dist = calculate_cost(self.data, {"design_mode": "distributed", "design_price_fixed": 12000, "overhead_pct": 0})

        self.assertEqual(calc_sep["extras_financials"]["design_mode"], "separate")
        self.assertEqual(calc_dist["extras_financials"]["design_mode"], "distributed")
        self.assertAlmostEqual(
            calc_sep["financial_summary"]["client_net_price"],
            calc_dist["financial_summary"]["client_net_price"],
            places=2
        )

    def test_empty_and_zero_inputs(self):
        """
        Тестирование граничных случаев (пустой проект, нулевые объемы).
        """
        empty_data = {"summary": {}, "frames": [], "timber": [], "plates": []}
        calc = calculate_cost(empty_data, {})
        self.assertIn("financial_summary", calc)
        self.assertEqual(calc["structures_financials"]["total_timber_vol_m3"], 0.0)
        self.assertEqual(len(calc["positions"]), 0)

    def test_negative_discount_sanitization(self):
        """
        Тестирование защиты от отрицательных скидок.
        """
        if not self.data:
            self.skipTest("Sample data not available")
        calc = calculate_cost(self.data, {"discount_val": -10000})
        # Negative discount should not inflate the price
        self.assertEqual(calc["financial_summary"]["discount_amount"], 0.0)


if __name__ == "__main__":
    unittest.main()
