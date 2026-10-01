"""
Production Workorders Generator.
Формирует послойные наряды для сборочного стола/пресса МЗП, ведомости раскроя и накладные для цеха.
"""

from typing import Dict, Any, List
from datetime import datetime
from costing.workorders.optimizer import optimize_cutting_stock


class WorkorderGenerator:
    """
    Генератор производственных заданий и карт для цеха.
    """

    def generate_workorders(self, project_data: Dict[str, Any], stock_length_mm: float = 6000.0) -> Dict[str, Any]:
        """
        Формирование полного пакета производственной документации.
        """
        frames = project_data.get("frames", [])
        timber = project_data.get("timber", [])
        plates = project_data.get("plates", [])
        
        assembly_tasks: List[Dict[str, Any]] = []
        
        # 1. Послойные сборочные наряды (каждый физический слой собирается отдельно)
        layer_counter = 1
        for f in frames:
            name = f["name"]
            qty = f.get("qty", 1)
            plies = f.get("plies", 1)
            total_layers = f.get("total_layers", qty * plies)
            press_pts = f.get("press_points_ply", 0)
            vol_ply = f.get("vol_m3_ply", 0.0)
            plates_ply = f.get("plates_m2_ply", 0.0)
            
            for l_idx in range(1, total_layers + 1):
                assembly_tasks.append({
                    "task_id": f"TSK-{layer_counter:03d}",
                    "frame_name": name,
                    "layer_num": l_idx,
                    "total_layers_for_frame": total_layers,
                    "packet_info": f"{qty} пак. x {plies} сл.",
                    "span_mm": f.get("span_mm", 0),
                    "height_mm": f.get("height_mm", 0),
                    "pitch_deg": f.get("pitch_deg", 0.0),
                    "press_points": press_pts,
                    "timber_vol_m3": vol_ply,
                    "plates_m2": plates_ply
                })
                layer_counter += 1

        # 2. Карты раскроя
        cutting_plan = optimize_cutting_stock(timber_items=timber, stock_length_mm=stock_length_mm)
        
        # 3. Ведомость пластин МЗП
        plates_summary: Dict[str, Dict[str, Any]] = {}
        for p in plates:
            size_str = p.get("size_str", "Стандарт")
            gauge = p.get("gauge", "T150")
            key = f"{size_str} ({gauge})"
            if key not in plates_summary:
                plates_summary[key] = {
                    "size_str": size_str,
                    "gauge": gauge,
                    "total_qty": 0,
                    "total_area_m2": 0.0
                }
            plates_summary[key]["total_qty"] += p.get("qty", 0)
            plates_summary[key]["total_area_m2"] += p.get("area_m2", 0.0)
            
        for val in plates_summary.values():
            val["total_area_m2"] = round(val["total_area_m2"], 2)

        return {
            "order_id": f"WO-{datetime.now().strftime('%y%m%d-%H%M')}",
            "project_name": project_data.get("summary", {}).get("project_name", "Проект"),
            "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "total_physical_layers": len(assembly_tasks),
            "total_press_points": sum(t["press_points"] for t in assembly_tasks),
            "total_timber_vol_m3": round(sum(t["timber_vol_m3"] for t in assembly_tasks), 4),
            "assembly_tasks": assembly_tasks,
            "cutting_plan": cutting_plan,
            "plates_summary": list(plates_summary.values())
        }


def generate_production_workorders(project_data: Dict[str, Any], stock_length_mm: float = 6000.0) -> Dict[str, Any]:
    """
    Хелпер генерации производственного задания.
    """
    gen = WorkorderGenerator()
    return gen.generate_workorders(project_data=project_data, stock_length_mm=stock_length_mm)
