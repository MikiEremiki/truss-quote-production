"""
Главная точка входа для запуска веб-сервиса MiTek Costing & Production Suite.
Предоставляет обратную совместимость для прямого импорта и запуска uvicorn.
"""

from costing.version import __version__, __version_suffix__, __version_full__
from costing.api.app import app, start, create_app
from costing.core.pricing_catalog import DK_PRICING_CATALOG, CLIENT_PROFILES, AGENTS_CATALOG
from costing.data_import.mitek_parser import parse_mitek_workbook, load_mitek_file
from costing.calculator.engine import CostCalculator, calculate_cost
from costing.workorders.optimizer import optimize_cutting_stock
from costing.workorders.generator import generate_production_workorders
from costing.quote.engine import generate_quote

__all__ = [
    "app",
    "start",
    "create_app",
    "__version__",
    "__version_suffix__",
    "__version_full__",
    "DK_PRICING_CATALOG",
    "CLIENT_PROFILES",
    "AGENTS_CATALOG",
    "parse_mitek_workbook",
    "load_mitek_file",
    "CostCalculator",
    "calculate_cost",
    "optimize_cutting_stock",
    "generate_production_workorders",
    "generate_quote",
]

if __name__ == "__main__":
    start()
