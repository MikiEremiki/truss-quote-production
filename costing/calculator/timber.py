"""
Timber Calculation Module - Volume, Gross/Net Factors, Section Breakdowns, Surface Areas.
"""

from typing import List, Dict, Any


def calculate_timber_surface_area(length_m: float, thick_mm: float, depth_mm: float, qty: int = 1) -> float:
    """
    4-сторонняя площадь поверхности деревянной детали в м2: S = Q * 2 * (T + D) * L
    """
    th_m = thick_mm / 1000.0
    dp_m = depth_mm / 1000.0
    return round(qty * 2.0 * (th_m + dp_m) * length_m, 4)


def calculate_sections_breakdown(
    timber_items: List[Dict[str, Any]],
    timber_price_m3: float,
    waste_factor: float = 1.15
) -> Dict[str, Dict[str, Any]]:
    """
    Группировка и расчет объемов, погонажа и площадей по сечениям пиломатериала.
    """
    sections: Dict[str, Dict[str, Any]] = {}
    
    for t in timber_items:
        sec = t.get("section", "Не указано")
        if sec not in sections:
            sections[sec] = {
                "net_vol": 0.0,
                "total_length_m": 0.0,
                "count": 0,
                "surf_m2": 0.0
            }
        qty = t.get("qty", 1)
        sections[sec]["net_vol"] += t.get("volume_m3", 0.0)
        sections[sec]["total_length_m"] += t.get("length_m", 0.0) * qty
        sections[sec]["count"] += qty
        sections[sec]["surf_m2"] += t.get("surface_area_m2", 0.0)

    for sec, val in sections.items():
        net_v = val["net_vol"]
        gross_v = round(net_v * waste_factor, 4)
        val["net_vol"] = round(net_v, 4)
        val["gross_vol"] = gross_v
        val["cost_rub"] = round(gross_v * timber_price_m3, 2)
        val["total_length_m"] = round(val["total_length_m"], 2)
        val["surf_m2"] = round(val["surf_m2"], 2)

    return sections
