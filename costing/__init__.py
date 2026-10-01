"""
Costing & Production Suite - Монорепозиторий и основной пакет для расчета ферм MiTek на МЗП.
"""

from costing.core.pricing_catalog import DK_PRICING_CATALOG, CLIENT_PROFILES, AGENTS_CATALOG
from costing.data_import.mitek_parser import parse_mitek_workbook, load_mitek_file
from costing.calculator.engine import CostCalculator, calculate_cost
from costing.quote.engine import QuoteEngine, generate_quote
from costing.workorders.optimizer import optimize_cutting_stock
from costing.workorders.generator import WorkorderGenerator, generate_production_workorders
from costing.api.app import app

# Alias for data_import layer
import costing.data_import as importers

from costing.version import __version__, __version_suffix__, __version_full__

__all__ = [
    "DK_PRICING_CATALOG",
    "CLIENT_PROFILES",
    "AGENTS_CATALOG",
    "parse_mitek_workbook",
    "load_mitek_file",
    "CostCalculator",
    "calculate_cost",
    "QuoteEngine",
    "generate_quote",
    "optimize_cutting_stock",
    "WorkorderGenerator",
    "generate_production_workorders",
    "importers",
    "app",
    "__version__",
    "__version_suffix__",
    "__version_full__",
]
