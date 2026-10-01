"""
Unit tests for quote layer (Commercial Proposals, discounts, agent modes, VAT, HTML export).
"""

import os
import unittest
from costing.data_import.mitek_parser import load_mitek_file
from costing.calculator.engine import calculate_cost
from costing.quote.engine import generate_quote, QuoteEngine
from costing.quote.pdf_export import render_quote_html
from costing.quote.exports import export_quote_csv


class TestQuote(unittest.TestCase):
    def setUp(self):
        sample_file = os.path.join("output", "Богородск 21 h1400 t40.xlsm")
        if os.path.exists(sample_file):
            self.data = load_mitek_file(sample_file)
        else:
            self.data = None

    def test_quote_generation(self):
        if not self.data:
            self.skipTest("Sample data not available")
        calc = calculate_cost(self.data, {"discount_val": 5000, "discount_type": "amount", "vat_pct": 20})
        quote = generate_quote(calc, project_name="Богородск 21", client_name="Иванов И.И.")
        
        self.assertEqual(quote["project_name"], "Богородск 21")
        self.assertEqual(quote["client_name"], "Иванов И.И.")
        self.assertGreater(len(quote["items"]), 0)
        self.assertGreater(quote["financials"]["final_price_with_vat"], 0)
        
        # Test HTML rendering
        html = render_quote_html(quote)
        self.assertIn("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", html)
        self.assertIn("Богородск 21", html)
        self.assertIn("Специальная скидка", html)
        self.assertIn("НДС (20", html)

        # Test CSV export
        csv_out = export_quote_csv(quote)
        self.assertIn("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", csv_out)
        self.assertIn("Иванов И.И.", csv_out)
        self.assertIn("ИТОГО К ОПЛАТЕ", csv_out)

    def test_agent_modes(self):
        if not self.data:
            self.skipTest("Sample data not available")
            
        # Markup mode (+10% on price)
        c_markup = calculate_cost(self.data, {"agent_pct": 10.0, "agent_mode": "markup"})
        # Margin mode (10% from DK margin, price unchanged)
        c_margin = calculate_cost(self.data, {"agent_pct": 10.0, "agent_mode": "margin"})
        # None
        c_base = calculate_cost(self.data, {"agent_pct": 0.0})
        
        base_price = c_base["financial_summary"]["client_net_price"]
        markup_price = c_markup["financial_summary"]["client_net_price"]
        margin_price = c_margin["financial_summary"]["client_net_price"]
        
        self.assertGreater(markup_price, base_price)
        self.assertAlmostEqual(margin_price, base_price, places=2)
        self.assertLess(c_margin["financial_summary"]["dk_net_profit"], c_base["financial_summary"]["dk_net_profit"])


if __name__ == "__main__":
    unittest.main()
