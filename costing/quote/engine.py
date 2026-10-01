"""
Commercial Quote Engine - Generates Client Proposals, Internal Manager Estimates, and Version Snapshots.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from costing.quote.models import CommercialQuote, QuoteVersion, QuoteItem, ApprovalStatus


class QuoteEngine:
    """
    Генератор и контроллер версий коммерческих предложений.
    """

    def build_client_quote_items(self, cost_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Формирование товарных позиций для клиентского КП.
        """
        items: List[Dict[str, Any]] = []
        idx = 1
        
        # 1. Конструкции
        for pos in cost_result.get("positions", []):
            qty = pos.get("qty_packets", 1)
            plies = pos.get("plies", 1)
            plies_str = f" ({plies} сл.)" if plies > 1 else ""
            desc = f"{pos['subtype_label']} / пролет {round(pos['span_mm'] / 1000.0, 2)}м{plies_str}"
            
            items.append({
                "item_no": idx,
                "name": f"Деревянная конструкция марка {pos['name']}",
                "description": desc,
                "qty": qty,
                "unit": "компл." if plies > 1 else "шт.",
                "unit_price": round(pos["final_position_sale"] / qty, 2) if qty > 0 else pos["final_position_sale"],
                "total_price": pos["final_position_sale"],
                "category": "structure"
            })
            idx += 1

        ext = cost_result.get("extras_financials", {})
        
        # 2. Защитная обработка
        if ext.get("treatment_sale", 0) > 0:
            surf_m2 = cost_result.get("treated_timber_surface_m2", 0)
            items.append({
                "item_no": idx,
                "name": "Защитная огнебиозащитная обработка (СенежОгнеБио)",
                "description": f"Антисептирование 4-х сторон заготовок методом распыления/погружения ({surf_m2} м²)",
                "qty": 1,
                "unit": "компл.",
                "unit_price": ext["treatment_sale"],
                "total_price": ext["treatment_sale"],
                "category": "service"
            })
            idx += 1

        # 3. Проектирование (если отдельной строкой)
        if ext.get("design_sale", 0) > 0 and ext.get("design_mode") == "separate":
            items.append({
                "item_no": idx,
                "name": "Разработка конструкторской документации (раздел КР / КДД)",
                "description": "Рабочие чертежи стропильной системы, сборочные схемы и монтажный план узлов",
                "qty": 1,
                "unit": "компл.",
                "unit_price": ext["design_sale"],
                "total_price": ext["design_sale"],
                "category": "service"
            })
            idx += 1

        # 4. Крепеж и метизы
        if ext.get("fasteners_sale", 0) > 0:
            items.append({
                "item_no": idx,
                "name": "Комплект монтажного крепежа и метизов",
                "description": "Анкерные пластины, усиленные уголки, конструкционные саморезы, шпильки",
                "qty": 1,
                "unit": "компл.",
                "unit_price": ext["fasteners_sale"],
                "total_price": ext["fasteners_sale"],
                "category": "extra"
            })
            idx += 1

        # 5. Доставка
        if ext.get("logistics_sale", 0) > 0:
            items.append({
                "item_no": idx,
                "name": "Транспортировка и доставка на объект",
                "description": "Специализированный автотранспорт (шаланда/еврофура)",
                "qty": 1,
                "unit": "рейс",
                "unit_price": ext["logistics_sale"],
                "total_price": ext["logistics_sale"],
                "category": "extra"
            })
            idx += 1

        return items

    def create_quote(
        self,
        project_name: str,
        cost_result: Dict[str, Any],
        client_name: str = "Заказчик",
        version_comment: str = "Первоначальный расчет"
    ) -> Dict[str, Any]:
        """
        Создание структурированного объекта коммерческого предложения.
        """
        fin = cost_result.get("financial_summary", {})
        quote_items = self.build_client_quote_items(cost_result)
        date_str = datetime.now().strftime("%d.%m.%Y")
        
        quote = {
            "quote_id": f"KP-{datetime.now().strftime('%y%m%d-%H%M')}",
            "project_name": project_name,
            "client_name": client_name,
            "date": date_str,
            "current_version": 1,
            "status": ApprovalStatus.DRAFT.value,
            "version_comment": version_comment,
            "items": quote_items,
            "financials": {
                "subtotal": fin.get("subtotal_before_discount", 0.0),
                "discount_type": fin.get("discount_type", "percent"),
                "discount_val": fin.get("discount_val", 0.0),
                "discount_amount": fin.get("discount_amount", 0.0),
                "price_after_discount": fin.get("price_after_discount", 0.0),
                "agent_fee": fin.get("agent_fee", 0.0),
                "agent_discount": fin.get("agent_discount", 0.0),
                "client_net_price": fin.get("client_net_price", 0.0),
                "vat_pct": fin.get("vat_pct", 0.0),
                "vat_amount": fin.get("vat_amount", 0.0),
                "final_price_with_vat": fin.get("final_price_with_vat", 0.0),
                "dk_net_profit": fin.get("dk_net_profit", 0.0),
                "profit_margin_pct": fin.get("dk_profit_margin_pct", 0.0)
            }
        }
        return quote


def generate_quote(cost_result: Dict[str, Any], project_name: str = "Проект", client_name: str = "Заказчик") -> Dict[str, Any]:
    """
    Хелпер для быстрого формирования КП.
    """
    engine = QuoteEngine()
    return engine.create_quote(project_name=project_name, cost_result=cost_result, client_name=client_name)
