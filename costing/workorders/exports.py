"""
Export utilities for Production Workorders and Cutting Stock Plans in CSV formats.
"""

import csv
import io
from typing import Dict, Any


def export_cutting_plan_csv(cutting_data: Dict[str, Any]) -> str:
    """
    Экспорт карты раскроя хлыстов в формат CSV (с разделителем ; для Excel).
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', lineterminator='\n')

    writer.writerow(["КАРТА РАСКРОЯ ПИЛОМАТЕРИАЛА"])
    writer.writerow(["Стандартная длина хлыста (мм)", cutting_data.get("stock_length_mm", 6000)])
    writer.writerow(["Всего стандартных хлыстов (шт)", cutting_data.get("total_stock_timbers", 0)])
    writer.writerow(["Общий полезный выход (%)", f"{cutting_data.get('overall_efficiency_pct', 0):.2f}%"])
    writer.writerow(["Общий процент отходов (%)", f"{cutting_data.get('overall_waste_pct', 0):.2f}%"])
    writer.writerow([])

    # Таблица заготовок на хлыстах
    writer.writerow([
        "Сечение",
        "Хлыст №",
        "Длина хлыста (мм)",
        "Использовано (мм)",
        "Остаток/Обрез (мм)",
        "Выход (%)",
        "Кол-во деталей",
        "Список заготовок (Имя: длина мм [ферма])"
    ])

    sections = cutting_data.get("sections", [])
    for sec in sections:
        sec_name = sec.get("section", "")
        for idx, bar in enumerate(sec.get("bars", []), start=1):
            cuts_str = ", ".join([
                f"{c.get('name', 'дет')}: {c.get('length_mm', 0)}мм ({c.get('frame_name', '')})"
                for c in bar.get("cuts", [])
            ])
            writer.writerow([
                sec_name,
                idx,
                bar.get("total_length_mm", 6000),
                bar.get("used_length_mm", 0),
                bar.get("waste_length_mm", 0),
                f"{bar.get('efficiency_pct', 0):.1f}%",
                len(bar.get("cuts", [])),
                cuts_str
            ])

    return output.getvalue()


def export_workorders_csv(workorders_data: Dict[str, Any]) -> str:
    """
    Экспорт производственных нарядов цеха сборки в формат CSV (с разделителем ; для Excel).
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', lineterminator='\n')

    writer.writerow(["ПРОИЗВОДСТВЕННЫЙ НАРЯД ЦЕХА СБОРКИ МЗП", workorders_data.get("order_id", "")])
    writer.writerow(["Объект / Проект", workorders_data.get("project_name", "")])
    writer.writerow(["Дата формирования", workorders_data.get("created_at", "")])
    writer.writerow(["Всего физических слоев / сборочных задач", workorders_data.get("total_physical_layers", 0)])
    writer.writerow(["Всего точек запрессовки", workorders_data.get("total_press_points", 0)])
    writer.writerow(["Общий объем древесины на сборку (м³)", workorders_data.get("total_timber_vol_m3", 0)])
    writer.writerow([])

    # Таблица сборочных задач
    writer.writerow([
        "Код задачи",
        "Марка фермы",
        "Слой пакета",
        "Всего слоев фермы",
        "Комплектация пакета",
        "Пролет (мм)",
        "Высота (мм)",
        "Уклон (град)",
        "Точек МЗП",
        "Объем древесины на слой (м³)",
        "Площадь МЗП на слой (м²)"
    ])

    for task in workorders_data.get("assembly_tasks", []):
        writer.writerow([
            task.get("task_id", ""),
            task.get("frame_name", ""),
            task.get("layer_num", 1),
            task.get("total_layers_for_frame", 1),
            task.get("packet_info", ""),
            task.get("span_mm", 0),
            task.get("height_mm", 0),
            task.get("pitch_deg", 0),
            task.get("press_points", 0),
            f"{task.get('timber_vol_m3', 0):.4f}",
            f"{task.get('plates_m2', 0):.3f}"
        ])

    writer.writerow([])
    writer.writerow(["СВОДНАЯ ВЕДОМОСТЬ ПЛАСТИН МЗП ДЛЯ ПРЕССА"])
    writer.writerow(["Типоразмер МЗП", "Калибр/Тип", "Количество (шт)", "Общая площадь (м²)"])
    for plate in workorders_data.get("plates_summary", []):
        writer.writerow([
            plate.get("size_str", ""),
            plate.get("gauge", ""),
            plate.get("total_qty", 0),
            f"{plate.get('total_area_m2', 0):.2f}"
        ])

    return output.getvalue()
