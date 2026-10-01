"""
Services Calculation Module - Antiseptic Treatment, Design (Separate vs Distributed), Cutting, Fasteners, Logistics, Overhead.
"""

from typing import Dict, Any, List
from costing.core.pricing_catalog import DK_PRICING_CATALOG


def resolve_default_design_rates(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Определение базовой стоимости проектирования (стандарт vs вальма).
    """
    tot_roof = data.get("summary", {}).get("total_roof_area_m2", 0.0)
    frames = data.get("frames", [])
    has_hip = any("hip" in str(f.get("item_type", "")).lower() or "вальм" in str(f.get("name", "")).lower() for f in frames)
    
    if has_hip and tot_roof > 0:
        price = max(DK_PRICING_CATALOG["design"]["hip_min_price"], round(tot_roof * DK_PRICING_CATALOG["design"]["hip_price_m2"], 2))
        cost = max(DK_PRICING_CATALOG["design"]["hip_min_cost"], round(tot_roof * DK_PRICING_CATALOG["design"]["hip_cost_m2"], 2))
    else:
        price = DK_PRICING_CATALOG["design"]["standard_price"]
        cost = DK_PRICING_CATALOG["design"]["standard_cost"]
        
    return {
        "design_price": price,
        "design_cost": cost,
        "is_hip": has_hip
    }


def distribute_design_cost(
    position_costs: List[Dict[str, Any]],
    design_price: float,
    design_cost: float,
    design_mode: str,
    total_truss_vol: float
) -> Dict[str, float]:
    """
    Распределение или выделение строки проектирования в КП.
    """
    tot_distributed = 0.0
    separate_price = 0.0
    separate_cost = 0.0
    
    if design_mode == "distributed":
        design_pool = design_price
        if total_truss_vol > 0:
            for p in position_costs:
                if p["item_type"] in ["truss", "cut_timber"]:
                    portion = round(design_pool * (p["net_vol_m3"] / total_truss_vol), 2)
                    p["distributed_design_price"] = portion
                    p["final_position_sale"] = round(p["sale_price_base"] + portion, 2)
                    tot_distributed += portion
                else:
                    p["distributed_design_price"] = 0.0
                    p["final_position_sale"] = p["sale_price_base"]
        else:
            for p in position_costs:
                portion = round(design_pool / len(position_costs), 2)
                p["distributed_design_price"] = portion
                p["final_position_sale"] = round(p["sale_price_base"] + portion, 2)
                tot_distributed += portion
        separate_price = 0.0
        separate_cost = 0.0
    else:
        for p in position_costs:
            p["distributed_design_price"] = 0.0
            p["final_position_sale"] = p["sale_price_base"]
        separate_price = design_price
        separate_cost = design_cost

    return {
        "total_distributed_design": tot_distributed,
        "separate_design_price": separate_price,
        "separate_design_cost": separate_cost
    }
