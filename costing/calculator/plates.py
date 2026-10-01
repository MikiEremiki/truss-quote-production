"""
Connector Plates (МЗП) calculation module.
"""

from typing import List, Dict, Any


def calculate_plate_area_m2(depth_mm: float, length_mm: float, qty: int = 1) -> float:
    """
    Расчет площади пластин МЗП в квадратных метрах (м2).
    """
    return round((depth_mm * length_mm / 1_000_000.0) * qty, 4)


def calculate_plates_cost_and_sale(
    total_plates_m2: float,
    plate_cost_m2: float,
    plate_price_m2: float
) -> Dict[str, float]:
    """
    Расчет себестоимости и продажной стоимости пластин МЗП.
    """
    cost = round(total_plates_m2 * plate_cost_m2, 2)
    sale = round(total_plates_m2 * plate_price_m2, 2)
    profit = round(sale - cost, 2)
    return {
        "plates_cost": cost,
        "plates_sale": sale,
        "plates_profit": profit
    }
