"""
Production Workorders Generator.
Формирует наряды для сборочного стола/пресса МЗП, ведомости раскроя, расчет потребности в досках и накладные для цеха.
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
        
        # 1. Сборочные задания для стола / пресса по маркам ферм
        task_counter = 1
        for f in frames:
            name = f["name"]
            qty = f.get("qty", 1)
            plies = f.get("plies", 1)
            total_layers = f.get("total_layers", qty * plies)
            press_pts_ply = f.get("press_points_ply", 0)
            vol_ply = f.get("vol_m3_ply", 0.0)
            plates_ply = f.get("plates_m2_ply", 0.0)
            
            # Общие показатели на данную марку
            tot_press_points = f.get("total_press_points", press_pts_ply * total_layers)
            tot_vol_m3 = f.get("total_vol_m3", round(vol_ply * total_layers, 4))
            tot_plates_m2 = f.get("plates_m2", round(plates_ply * total_layers, 3))
            
            assembly_tasks.append({
                "task_id": f"TSK-{task_counter:03d}",
                "frame_name": name,
                "qty": qty,
                "plies": plies,
                "total_layers": total_layers,
                "span_mm": f.get("span_mm", 0),
                "height_mm": f.get("height_mm", 0),
                "pitch_deg": f.get("pitch_deg", 0.0),
                "press_points": tot_press_points,
                "press_points_per_unit": press_pts_ply,
                "timber_vol_m3": tot_vol_m3,
                "plates_m2": tot_plates_m2
            })
            task_counter += 1

        # 2. Карты раскроя
        cutting_plan = optimize_cutting_stock(timber_items=timber, stock_length_mm=stock_length_mm)
        
        # 3. Расчет потребности в досках и сечениях для заказа
        boards_summary: List[Dict[str, Any]] = []
        for sec_name, sec_info in cutting_plan.get("by_section", {}).items():
            th_mm, dp_mm = 0.0, 0.0
            clean_sec = sec_name.replace("х", "x").replace("Х", "x").replace("X", "x")
            if "x" in clean_sec:
                parts = clean_sec.split("x")
                try:
                    th_mm = float(parts[0].strip())
                    dp_mm = float(parts[1].strip())
                except (ValueError, IndexError):
                    pass

            stock_len_m = sec_info.get("stock_length_m", stock_length_mm / 1000.0)
            stock_bars = sec_info.get("total_bars", 0)
            tot_stock_len_m = sec_info.get("total_stock_length_m", stock_bars * stock_len_m)
            net_len_m = sec_info.get("net_length_m", 0.0)
            parts_cnt = sec_info.get("total_parts_count", 0)
            waste_pct = sec_info.get("waste_pct", 0.0)

            if th_mm > 0 and dp_mm > 0:
                sec_vol_m3 = round(tot_stock_len_m * (th_mm / 1000.0) * (dp_mm / 1000.0), 4)
                net_vol_m3 = round(net_len_m * (th_mm / 1000.0) * (dp_mm / 1000.0), 4)
            else:
                net_vol_m3 = round(sum(t.get("volume_m3", 0.0) for t in timber if t.get("section") == sec_name), 4)
                sec_vol_m3 = round(net_vol_m3 * (tot_stock_len_m / net_len_m), 4) if net_len_m > 0 else net_vol_m3

            boards_summary.append({
                "section": sec_name,
                "stock_length_m": round(stock_len_m, 2),
                "stock_length_mm": int(round(stock_len_m * 1000)),
                "total_boards": stock_bars,
                "total_length_m": round(tot_stock_len_m, 2),
                "net_length_m": round(net_len_m, 2),
                "total_volume_m3": sec_vol_m3,
                "net_volume_m3": net_vol_m3,
                "parts_count": parts_cnt,
                "waste_pct": waste_pct
            })

        # 4. Ведомость пластин МЗП
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

        tot_frames_count = sum(f.get("qty", 1) for f in frames)
        tot_physical_layers = sum(f.get("total_layers", f.get("qty", 1) * f.get("plies", 1)) for f in frames)

        return {
            "order_id": f"WO-{datetime.now().strftime('%y%m%d-%H%M')}",
            "project_name": project_data.get("summary", {}).get("project_name", "Проект"),
            "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "total_frames_count": tot_frames_count,
            "total_physical_layers": tot_physical_layers,
            "total_press_points": sum(t["press_points"] for t in assembly_tasks),
            "total_timber_vol_m3": round(sum(t["timber_vol_m3"] for t in assembly_tasks), 4),
            "total_boards_count": cutting_plan.get("summary", {}).get("total_bars_count", 0),
            "total_boards_meters": cutting_plan.get("summary", {}).get("total_stock_meters", 0.0),
            "boards_summary": boards_summary,
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
