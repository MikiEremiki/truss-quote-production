"""
Основной расчетный модуль (Calculation Engine).
Выполняет попозиционную калькуляцию прямых затрат, надбавок, себестоимости и интеграцию со справочниками цен.
"""

from typing import Dict, Any, List, Optional
from costing.core.pricing_catalog import DK_PRICING_CATALOG, CLIENT_PROFILES, AGENTS_CATALOG
from costing.calculator.timber import calculate_sections_breakdown
from costing.calculator.services import resolve_default_design_rates, distribute_design_cost


class CostCalculator:
    """
    Класс калькулятора себестоимости и попозиционного ценообразования.
    """

    def __init__(self, pricing_catalog: Optional[Dict[str, Any]] = None):
        self.catalog = pricing_catalog or DK_PRICING_CATALOG

    def calculate(self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Полный расчет себестоимости, попозиционных цен и сводных финансовых показателей.
        """
        if params is None:
            params = {}

        # 1. Профиль клиента и глобальные ставки по умолчанию (все редактируемы)
        profile_key = params.get("client_profile", "standard")
        profile = CLIENT_PROFILES.get(profile_key, CLIENT_PROFILES["standard"])
        
        timber_price_m3 = float(params.get("timber_price_m3", profile.get("timber_price_m3", self.catalog["timber_default_sale_m3"])))
        timber_cost_m3 = float(params.get("timber_cost_m3", self.catalog["timber_base_cost_m3"]))
        timber_waste_factor = float(params.get("timber_waste_factor", 1.15))
        
        plate_price_m2 = float(params.get("plate_price_m2", self.catalog["plates_base_price_m2"]))
        plate_cost_m2 = float(params.get("plate_cost_m2", self.catalog["plates_base_cost_m2"]))
        
        cutting_cost_m3 = float(params.get("cutting_cost_m3", self.catalog["cutting"]["cost_m3"]))
        cutting_price_m3 = float(params.get("cutting_price_m3", self.catalog["cutting"]["price_m3"]))
        
        treatment_price_m2 = float(params.get("treatment_price_m2", profile.get("treatment_price_m2", self.catalog["treatment"]["standard_price_m2"])))
        treatment_cost_m2 = float(params.get("treatment_cost_m2", self.catalog["treatment"]["cost_m2"]))
        
        # Проектирование: автоопределение ставки (стандарт vs вальма)
        design_rates = resolve_default_design_rates(data)
        design_price_fixed = float(params.get("design_price_fixed", design_rates["design_price"]))
        design_cost_fixed = float(params.get("design_cost_fixed", design_rates["design_cost"]))
        design_mode = params.get("design_mode", "separate") # "separate" или "distributed"
        
        fasteners_cost_fixed = float(params.get("fasteners_cost_fixed", 4500.0))
        fasteners_price_fixed = float(params.get("fasteners_price_fixed", fasteners_cost_fixed * 1.25))
        
        logistics_fixed = float(params.get("logistics_fixed", 12000.0))
        logistics_price_fixed = float(params.get("logistics_price_fixed", logistics_fixed))
        
        default_margin_pct = float(params.get("margin_pct", profile.get("margin_pct", self.catalog["default_order_margin_pct"])))
        overhead_pct = float(params.get("overhead_pct", 10.0)) / 100.0
        
        # Скидка на заказ
        discount_type = params.get("discount_type", "percent") # "percent" или "amount"
        discount_val = max(0.0, float(params.get("discount_val", 0.0)))
        
        # Агентские вознаграждения
        agent_id = params.get("agent_id", "none")
        preset_agent = AGENTS_CATALOG.get(agent_id, AGENTS_CATALOG["none"])
        agent_name = params.get("agent_name", preset_agent["name"])
        agent_pct = max(0.0, float(params.get("agent_pct", preset_agent["pct"])))
        agent_mode = params.get("agent_mode", "markup") # "markup", "margin", "discount"
        
        # НДС
        vat_pct = max(0.0, float(params.get("vat_pct", 0.0)))
        
        # Позиционная настройка цен и флагов
        custom_items = params.get("custom_items", {})

        # Шаг 1. Расчет прямых затрат и базовых цен по позициям
        position_costs: List[Dict[str, Any]] = []
        tot_timber_cost = 0.0
        tot_plates_cost = 0.0
        tot_cutting_cost = 0.0
        tot_work_cost = 0.0
        tot_treatment_area_calc = 0.0
        
        tot_structures_cost = 0.0
        tot_structures_sale_base = 0.0
        total_truss_vol_for_design = 0.0

        for f in data.get("frames", []):
            name = f["name"]
            item_cfg = custom_items.get(name, {})
            
            # Тип позиции
            p_type = item_cfg.get("type", f.get("item_type", "truss")) # 'truss', 'cut_timber', 'raw_timber'
            
            # Подтип фермы / работы
            p_subtype = item_cfg.get("subtype", "duopitch" if p_type == "truss" else ("cut_timber" if p_type == "cut_timber" else "raw_timber"))
            subtype_info = self.catalog["truss_types"].get(p_subtype, self.catalog["truss_types"]["duopitch"])
            
            # Попозиционные флаги: обработка и прирезка
            has_treatment = bool(item_cfg.get("has_treatment", True))
            has_cutting = bool(item_cfg.get("has_cutting", True if p_type in ["truss", "cut_timber"] else False))
            
            # Объемы
            vol_net = f["total_vol_m3"]
            vol_gross = round(vol_net * timber_waste_factor, 4)
            
            # Надбавка за длину > 12м
            span_is_over_12m = f.get("span_mm", 0) > self.catalog["span_over_12m"]["threshold_mm"]
            span_cost_add = self.catalog["span_over_12m"]["cost_add_m3"] if span_is_over_12m else 0.0
            span_price_add = self.catalog["span_over_12m"]["price_add_m3"] if span_is_over_12m else 0.0
            
            # Ставка работы
            default_work_cost_rate = (subtype_info["cost_m3"] + span_cost_add) if p_type == "truss" else 0.0
            p_work_cost_rate = float(item_cfg.get("work_rate_m3", default_work_cost_rate))
            
            # Стоимость пиломатериала
            p_timber_price = float(item_cfg.get("timber_price_m3", timber_price_m3))
            pos_timber_cost = round(vol_gross * timber_cost_m3, 2)
            pos_timber_sale = round(vol_gross * p_timber_price, 2)
            
            # Стоимость пластин МЗП
            pos_plates_cost = round(f["total_plates_m2"] * plate_cost_m2, 2) if p_type == "truss" else 0.0
            pos_plates_sale = round(f["total_plates_m2"] * plate_price_m2, 2) if p_type == "truss" else 0.0
            
            # Прирезка
            pos_cutting_cost = round(vol_net * cutting_cost_m3, 2) if has_cutting else 0.0
            pos_cutting_sale = round(vol_net * cutting_price_m3, 2) if has_cutting else 0.0
            
            # Работа по сборке (с возможностью ручного оверрайда)
            if "override_work_cost" in item_cfg and item_cfg["override_work_cost"] is not None and str(item_cfg["override_work_cost"]).strip() != "":
                pos_work_cost = round(float(item_cfg["override_work_cost"]), 2)
            else:
                pos_work_cost = round(vol_net * p_work_cost_rate, 2) if p_type == "truss" else 0.0
                
            # Защитная обработка для позиции
            pos_surf_m2 = f.get("surface_area_m2", 0.0)
            if has_treatment:
                pos_treatment_cost = round(pos_surf_m2 * treatment_cost_m2, 2)
                pos_treatment_sale = round(pos_surf_m2 * treatment_price_m2, 2)
                tot_treatment_area_calc += pos_surf_m2
            else:
                pos_treatment_cost = 0.0
                pos_treatment_sale = 0.0
                
            # Себестоимость чисто конструкции (пиломатериал + МЗП + прирезка + сборка)
            pos_prime_cost = round(pos_timber_cost + pos_plates_cost + pos_cutting_cost + pos_work_cost, 2)
            if "override_prime_cost" in item_cfg and item_cfg["override_prime_cost"] is not None and str(item_cfg["override_prime_cost"]).strip() != "":
                pos_prime_cost = round(float(item_cfg["override_prime_cost"]), 2)
                
            p_margin_pct = float(item_cfg.get("margin_pct", default_margin_pct))
            
            # Базовая цена продажи позиции (до распределения проектирования)
            if "override_sale_price" in item_cfg and item_cfg["override_sale_price"] is not None and str(item_cfg["override_sale_price"]).strip() != "":
                pos_sale_price_base = round(float(item_cfg["override_sale_price"]), 2)
            else:
                pos_sale_price_base = round(pos_prime_cost * (1.0 + p_margin_pct / 100.0), 2)
                
            tot_timber_cost += pos_timber_cost
            tot_plates_cost += pos_plates_cost
            tot_cutting_cost += pos_cutting_cost
            tot_work_cost += pos_work_cost
            tot_structures_cost += pos_prime_cost
            tot_structures_sale_base += pos_sale_price_base
            
            if p_type in ["truss", "cut_timber"]:
                total_truss_vol_for_design += vol_net

            position_costs.append({
                "name": name,
                "qty_packets": f["qty"],
                "plies": f["plies"],
                "total_layers": f["total_layers"],
                "span_mm": f.get("span_mm", 0),
                "height_mm": f.get("height_mm", 0),
                "span_is_over_12m": span_is_over_12m,
                "item_type": p_type,
                "truss_subtype": p_subtype,
                "subtype_label": subtype_info["label"],
                "has_treatment": has_treatment,
                "has_cutting": has_cutting,
                "net_vol_m3": round(vol_net, 4),
                "gross_vol_m3": round(vol_gross, 4),
                "surface_area_m2": round(pos_surf_m2, 2),
                "plates_m2": round(f["total_plates_m2"], 2),
                "timber_price_m3": p_timber_price,
                "work_rate_m3": p_work_cost_rate,
                "margin_pct": round(p_margin_pct, 1),
                "timber_cost": pos_timber_cost,
                "plates_cost": pos_plates_cost,
                "cutting_cost": pos_cutting_cost,
                "work_cost": pos_work_cost,
                "prime_cost": pos_prime_cost,
                "treatment_cost": pos_treatment_cost,
                "treatment_sale": pos_treatment_sale,
                "sale_price_base": pos_sale_price_base,
                "distributed_design_price": 0.0,
                "final_position_sale": pos_sale_price_base
            })

        # Шаг 2. Распределение проектирования
        design_dist = distribute_design_cost(
            position_costs=position_costs,
            design_price=design_price_fixed,
            design_cost=design_cost_fixed,
            design_mode=design_mode,
            total_truss_vol=total_truss_vol_for_design
        )
        separate_design_price = design_dist["separate_design_price"]
        separate_design_cost = design_dist["separate_design_cost"]

        # Шаг 3. Финансовые показатели чисто от конструкций
        tot_structures_sale = round(sum(p["final_position_sale"] for p in position_costs), 2)
        profit_structures_only = round(tot_structures_sale - tot_structures_cost, 2)
        margin_structures_only_pct = round((profit_structures_only / tot_structures_sale * 100.0), 2) if tot_structures_sale > 0 else 0.0

        # Шаг 4. Дополнительные услуги (Допы)
        total_treatment_sale = round(tot_treatment_area_calc * treatment_price_m2, 2)
        total_treatment_cost = round(tot_treatment_area_calc * treatment_cost_m2, 2)
        
        tot_extras_cost = round(total_treatment_cost + separate_design_cost + fasteners_cost_fixed + logistics_fixed, 2)
        tot_extras_sale = round(total_treatment_sale + separate_design_price + fasteners_price_fixed + logistics_price_fixed, 2)
        profit_extras = round(tot_extras_sale - tot_extras_cost, 2)

        # Накладные расходы (от прямых затрат)
        direct_total = tot_structures_cost + tot_extras_cost
        overhead_cost = round(direct_total * overhead_pct, 2)
        
        # Шаг 5. Промежуточный итог и применение общей скидки
        subtotal_before_discount = round(tot_structures_sale + tot_extras_sale + overhead_cost, 2)
        
        if discount_type == "percent":
            discount_amount = round(subtotal_before_discount * (discount_val / 100.0), 2)
        else:
            discount_amount = round(min(subtotal_before_discount, discount_val), 2)
            
        price_after_discount = round(subtotal_before_discount - discount_amount, 2)

        # Шаг 6. Модуль агентских вознаграждений
        agent_fee = 0.0
        agent_discount = 0.0
        client_net_price = price_after_discount
        
        if agent_pct > 0:
            if agent_mode == "markup": # «В плюс» (Надбавка на КП)
                agent_fee = round(price_after_discount * (agent_pct / 100.0), 2)
                client_net_price = round(price_after_discount + agent_fee, 2)
                dk_net_profit = round(profit_structures_only + profit_extras - overhead_cost - discount_amount, 2)
            elif agent_mode == "margin": # «Из маржи / Не влияет на цену»
                agent_fee = round(price_after_discount * (agent_pct / 100.0), 2)
                client_net_price = price_after_discount
                dk_net_profit = round(profit_structures_only + profit_extras - overhead_cost - discount_amount - agent_fee, 2)
            elif agent_mode == "discount": # «В минус» (Скидка заказчику от агента)
                agent_discount = round(price_after_discount * (agent_pct / 100.0), 2)
                agent_fee = 0.0
                client_net_price = round(price_after_discount - agent_discount, 2)
                dk_net_profit = round(profit_structures_only + profit_extras - overhead_cost - discount_amount - agent_discount, 2)
        else:
            dk_net_profit = round(profit_structures_only + profit_extras - overhead_cost - discount_amount, 2)

        # Шаг 7. Расчет НДС (прямой ввод любого %)
        if vat_pct > 0:
            vat_amount = round(client_net_price * (vat_pct / 100.0), 2)
            final_price_with_vat = round(client_net_price + vat_amount, 2)
        else:
            vat_amount = 0.0
            final_price_with_vat = client_net_price

        # Распределение по сечениям
        sections_breakdown = calculate_sections_breakdown(
            timber_items=data.get("timber", []),
            timber_price_m3=timber_price_m3,
            waste_factor=timber_waste_factor
        )

        tot_net_timber = data.get("summary", {}).get("total_net_timber_m3", 0.0)
        tot_gross_timber = data.get("summary", {}).get("total_gross_timber_m3", round(tot_net_timber * timber_waste_factor, 4))
        tot_plates_m2 = data.get("summary", {}).get("total_plates_area_m2", 0.0)
        tot_press_points = data.get("summary", {}).get("total_press_points", 0)
        tot_roof_area = data.get("summary", {}).get("total_roof_area_m2", 0.0)

        return {
            "parameters": params,
            "catalogs": {
                "truss_types": self.catalog["truss_types"],
                "client_profiles": CLIENT_PROFILES,
                "agents_catalog": AGENTS_CATALOG
            },
            "net_timber_vol_m3": round(tot_net_timber, 4),
            "gross_timber_vol_m3": round(tot_net_timber * timber_waste_factor, 4),
            "total_timber_surface_m2": round(data.get("summary", {}).get("total_timber_surface_m2", 0.0), 2),
            "treated_timber_surface_m2": round(tot_treatment_area_calc, 2),
            "total_plates_area_m2": round(data.get("summary", {}).get("total_plates_area_m2", 0.0), 2),
            "sections_breakdown": sections_breakdown,
            "positions": position_costs,
            
            # Раздельный срез: конструкции vs допы
            "structures_financials": {
                "total_timber_vol_m3": round(tot_net_timber, 4),
                "total_timber_gross_m3": round(tot_gross_timber, 4),
                "total_plates_m2": round(tot_plates_m2, 2),
                "total_press_points": tot_press_points,
                "total_cost": round(tot_structures_cost, 2),
                "total_sale": round(tot_structures_sale, 2),
                "profit_pure_structures": profit_structures_only,
                "margin_pure_structures_pct": margin_structures_only_pct
            },
            "extras_financials": {
                "total_cost": round(tot_extras_cost, 2),
                "total_sale": round(tot_extras_sale, 2),
                "profit_extras": profit_extras,
                "treatment_sale": total_treatment_sale,
                "treatment_cost": total_treatment_cost,
                "design_sale": separate_design_price,
                "design_cost": separate_design_cost,
                "design_mode": design_mode,
                "fasteners_sale": fasteners_price_fixed,
                "fasteners_cost": fasteners_cost_fixed,
                "logistics_sale": logistics_price_fixed,
                "logistics_cost": logistics_fixed
            },
            
            # Сводный P&L отчет
            "financial_summary": {
                "direct_structures_cost": round(tot_structures_cost, 2),
                "direct_extras_cost": round(tot_extras_cost, 2),
                "overhead_cost": overhead_cost,
                "total_cost": round(direct_total + overhead_cost, 2),
                
                "structures_sale": round(tot_structures_sale, 2),
                "extras_sale": round(tot_extras_sale, 2),
                "subtotal_before_discount": subtotal_before_discount,
                
                "discount_type": discount_type,
                "discount_val": discount_val,
                "discount_amount": discount_amount,
                "price_after_discount": price_after_discount,
                
                "agent_id": agent_id,
                "agent_name": agent_name,
                "agent_pct": agent_pct,
                "agent_mode": agent_mode,
                "agent_fee": agent_fee,
                "agent_discount": agent_discount,
                
                "client_net_price": client_net_price,
                
                "vat_pct": vat_pct,
                "vat_amount": vat_amount,
                "final_price_with_vat": final_price_with_vat,
                
                "dk_net_profit": dk_net_profit,
                "dk_profit_margin_pct": round((dk_net_profit / client_net_price * 100.0), 2) if client_net_price > 0 else 0.0
            },
            
            # Совместимость со стандартными полями
            "cost_items": {
                "timber_cost": round(tot_timber_cost, 2),
                "plates_cost": round(tot_plates_cost, 2),
                "treatment_cost": total_treatment_sale,
                "cutting_cost": round(tot_cutting_cost, 2),
                "assembly_work_cost": round(tot_work_cost, 2),
                "design_cost": separate_design_price,
                "fasteners_cost": fasteners_price_fixed,
                "logistics_cost": logistics_price_fixed,
                "overhead_cost": overhead_cost,
                "prime_cost_total": round(direct_total + overhead_cost, 2),
                "margin_cost": dk_net_profit,
                "final_sale_price": final_price_with_vat
            },
            "indicators": {
                "price_per_m2_roof": round(final_price_with_vat / tot_roof_area, 2) if tot_roof_area > 0 else 0,
                "prime_per_m3_timber": round((direct_total + overhead_cost) / tot_net_timber, 2) if tot_net_timber > 0 else 0,
                "sale_per_m3_timber": round(final_price_with_vat / tot_net_timber, 2) if tot_net_timber > 0 else 0,
                "total_physical_layers": data.get("summary", {}).get("total_physical_layers", 0),
                "total_press_points": data.get("summary", {}).get("total_press_points", 0)
            }
        }


def calculate_cost(data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Универсальная функция расчета стоимости (совместимость со всеми вызовами).
    """
    calc = CostCalculator()
    return calc.calculate(data, params or {})
