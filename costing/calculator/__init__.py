"""
Calculator Layer - Engineering and Financial Calculations for Trusses, Timber, Plates, and Services.
"""

from costing.calculator.engine import CostCalculator, calculate_cost
from costing.calculator.timber import calculate_timber_surface_area, calculate_sections_breakdown
from costing.calculator.plates import calculate_plate_area_m2, calculate_plates_cost_and_sale
from costing.calculator.services import resolve_default_design_rates, distribute_design_cost

__all__ = [
    "CostCalculator",
    "calculate_cost",
    "calculate_timber_surface_area",
    "calculate_sections_breakdown",
    "calculate_plate_area_m2",
    "calculate_plates_cost_and_sale",
    "resolve_default_design_rates",
    "distribute_design_cost",
]
