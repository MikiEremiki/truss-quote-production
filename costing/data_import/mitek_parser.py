"""
Парсер инженерных выгрузок MiTek Pamir (.xlsm / .xlsx).
Извлекает геометрию, спецификации пиломатериалов, пластин МЗП, метизов и сводные параметры.
"""

import io
import os
import re
from typing import Dict, Any, Union, BinaryIO, Optional
from pathlib import Path
import openpyxl

from costing.data_import.base import BaseProjectImporter


def parse_mitek_workbook(wb: openpyxl.Workbook) -> Dict[str, Any]:
    """
    Основная функция парсинга открытой книги openpyxl выгрузки MiTek Pamir.
    """
    data: Dict[str, Any] = {
        "general": {},
        "frames": [],
        "timber": [],
        "plates": [],
        "fasteners": [],
        "surfaces": [],
        "roofing": [],
        "summary": {}
    }
    
    # 1. General Data
    if "General Data" in wb.sheetnames:
        ws = wb["General Data"]
        for r in range(1, ws.max_row + 1):
            row_vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
            non_empty = [v for v in row_vals if v is not None and str(v).strip() != ""]
            if len(non_empty) >= 2:
                k = str(non_empty[0]).strip()
                v = non_empty[-1]
                data["general"][k] = v
            elif len(non_empty) == 1 and isinstance(non_empty[0], str):
                data["general"][non_empty[0].strip()] = True

    # 2. Manufacture frames
    if "Manufacture frames" in wb.sheetnames:
        ws = wb["Manufacture frames"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) > 1:
            for r in rows[1:]:
                if r[0] is not None:
                    name = str(r[0])
                    qty = int(r[1]) if r[1] is not None else 1
                    plies = int(r[2]) if r[2] is not None else 1
                    span = round(float(r[3])) if r[3] is not None else 0
                    height = round(float(r[4])) if r[4] is not None else 0
                    pitch = float(r[5]) if r[5] is not None else 0.0
                    vol_ply = round(float(r[6]), 4) if r[6] is not None else 0.0
                    plates_dm2 = float(r[7]) if r[7] is not None else 0.0
                    press_pts = int(r[8]) if r[8] is not None else 0
                    
                    # Физическое число слоев на сборку (каждый слой изготавливается отдельно на прессе)
                    total_layers = qty * plies
                    total_vol = round(vol_ply * total_layers, 4)
                    plates_m2_total = round((plates_dm2 * total_layers) / 100.0, 2)
                    
                    # Определение типа изделия по умолчанию
                    item_type = "truss" if plates_dm2 > 0 else "cut_timber"

                    data["frames"].append({
                        "name": name,
                        "qty": qty,
                        "plies": plies,
                        "total_layers": total_layers,
                        "span_mm": int(span),
                        "height_mm": int(height),
                        "pitch_deg": pitch,
                        "vol_m3_ply": vol_ply,
                        "total_vol_m3": total_vol,
                        "plates_m2_ply": round(plates_dm2 / 100.0, 2),
                        "total_plates_m2": plates_m2_total,
                        "press_points_ply": press_pts,
                        "total_press_points": press_pts * total_layers,
                        "item_type": item_type
                    })

    # 3. Timber (Заготовки)
    if "Timber" in wb.sheetnames:
        ws = wb["Timber"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) > 1:
            for r in rows[1:]:
                if r[0] is not None:
                    qty = int(r[2]) if r[2] is not None else 1
                    len_m = float(r[5]) if r[5] is not None else 0.0
                    th_mm = round(float(r[6])) if r[6] is not None else 0
                    dp_mm = round(float(r[7])) if r[7] is not None else 0
                    
                    th_m = th_mm / 1000.0
                    dp_m = dp_mm / 1000.0
                    vol = qty * len_m * th_m * dp_m
                    # Площадь боковой поверхности для защитной обработки (м2)
                    surf_area = qty * 2.0 * (th_m + dp_m) * len_m
                    
                    sec_str = f"{int(th_mm)}x{int(dp_mm)}" if th_mm and dp_mm else "Не указано"
                    data["timber"].append({
                        "truss": str(r[0]),
                        "label": str(r[1]) if r[1] is not None else "",
                        "qty": qty,
                        "ply": int(r[3]) if r[3] is not None else 1,
                        "type": str(r[4]) if r[4] is not None else "",
                        "length_m": round(len_m, 4),
                        "length_mm": int(round(len_m * 1000.0)),
                        "thick_mm": int(th_mm),
                        "depth_mm": int(dp_mm),
                        "section": sec_str,
                        "grade": str(r[8]) if r[8] is not None else "C24",
                        "volume_m3": round(vol, 4),
                        "surface_area_m2": round(surf_area, 2)
                    })

    # 4. Connector Plates (МЗП)
    if "Connector Plates" in wb.sheetnames:
        ws = wb["Connector Plates"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) > 1:
            for r in rows[1:]:
                if r[0] is not None:
                    qty = int(r[1]) if r[1] is not None else 0
                    d_mm = round(float(r[3])) if r[3] is not None else 0
                    l_mm = round(float(r[4])) if r[4] is not None else 0
                    area_m2 = (d_mm * l_mm / 1_000_000.0) * qty
                    area_dm2 = area_m2 * 100.0
                    data["plates"].append({
                        "truss": str(r[0]),
                        "qty": qty,
                        "depth_mm": int(d_mm),
                        "length_mm": int(l_mm),
                        "size_str": f"{int(d_mm)}x{int(l_mm)}",
                        "gauge": str(r[5]) if r[5] is not None else "T150",
                        "area_m2": round(area_m2, 2),
                        "area_dm2": round(area_dm2, 2)
                    })

    # 5. Fasteners (Метизы)
    if "Fasteners" in wb.sheetnames:
        ws = wb["Fasteners"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) > 1:
            for r in rows[1:]:
                if r[0] is not None:
                    desc = str(r[0])
                    obj = str(r[1]) if len(r) > 1 and r[1] is not None else ""
                    qty = int(r[2]) if len(r) > 2 and r[2] is not None else (int(r[1]) if len(r) > 1 and str(r[1]).isdigit() else 0)
                    data["fasteners"].append({
                        "desc": desc,
                        "object": obj,
                        "qty": qty
                    })

    # 6. Surfaces (Скаты)
    if "Surfaces" in wb.sheetnames:
        ws = wb["Surfaces"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) > 1:
            for r in rows[1:]:
                if len(r) > 4 and r[1] is not None:
                    name = str(r[1])
                    pitch = float(r[3]) if r[3] is not None and str(r[3]).replace('.', '', 1).isdigit() else 0.0
                    area = float(r[4]) if r[4] is not None and str(r[4]).replace('.', '', 1).isdigit() else 0.0
                    if area > 0:
                        data["surfaces"].append({
                            "name": name,
                            "pitch": pitch,
                            "area_m2": round(area, 2)
                        })

    # 7. Roofing Data (Погонаж кровли)
    if "Roofing Data" in wb.sheetnames:
        ws = wb["Roofing Data"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) > 1:
            for r in rows[1:]:
                if r[0] is not None:
                    data["roofing"].append({
                        "name": str(r[0]),
                        "length_m": float(r[1]) if r[1] is not None else 0.0
                    })

    # Сводные показатели
    tot_vol = sum(t["volume_m3"] for t in data["timber"])
    tot_surf_area = sum(t["surface_area_m2"] for t in data["timber"])
    tot_plates_m2 = sum(p["area_m2"] for p in data["plates"])
    tot_layers = sum(f["total_layers"] for f in data["frames"])
    tot_press_points = sum(f["total_press_points"] for f in data["frames"])
    tot_roof_area = sum(s["area_m2"] for s in data["surfaces"])

    # Расчет точной площади поверхности для каждой марки конструкций
    for f in data["frames"]:
        f_name = f["name"]
        frame_surf = 0.0
        for t in data["timber"]:
            t_name = t["truss"]
            clean_f = re.sub(r'^\d+x', '', f_name)
            if t_name == f_name or t_name in f_name or clean_f.startswith(t_name) or t_name.startswith(clean_f):
                frame_surf += t["surface_area_m2"]
        if frame_surf == 0.0 and f["total_vol_m3"] > 0:
            frame_surf = round(f["total_vol_m3"] * 50.0, 2)
        f["surface_area_m2"] = round(frame_surf, 2)

    raw_spacing = data["general"].get("Frame spacing", 640)
    try:
        spacing_int = int(round(float(raw_spacing)))
    except (ValueError, TypeError):
        spacing_int = 640

    data["summary"] = {
        "total_net_timber_m3": round(tot_vol, 4),
        "total_timber_surface_m2": round(tot_surf_area, 2),
        "total_plates_area_m2": round(tot_plates_m2, 2),
        "total_plates_area_dm2": round(tot_plates_m2 * 100.0, 2),
        "total_plates_count": sum(p["qty"] for p in data["plates"]),
        "total_physical_layers": tot_layers,
        "total_press_points": tot_press_points,
        "total_roof_area_m2": round(tot_roof_area, 2),
        "project_name": data["general"].get("Project name") or data["general"].get("Project Name") or data["general"].get("Site") or "Богородск 21 дом 110м2",
        "pitch_deg": data["general"].get("Pitch", 35.0),
        "spacing_mm": spacing_int
    }

    return data


def load_mitek_file(source: Union[str, Path, bytes, BinaryIO]) -> Dict[str, Any]:
    """
    Загрузка файла по пути или из байтов и парсинг.
    """
    if isinstance(source, (str, Path)):
        wb = openpyxl.load_workbook(str(source), data_only=True)
    elif isinstance(source, bytes):
        wb = openpyxl.load_workbook(io.BytesIO(source), data_only=True)
    else:
        wb = openpyxl.load_workbook(source, data_only=True)
    return parse_mitek_workbook(wb)


class MiTekProjectImporter(BaseProjectImporter):
    """
    Реализация импортера для файлов MiTek Pamir.
    """
    def parse(self, source: Union[str, Path, BinaryIO, bytes]) -> Dict[str, Any]:
        return load_mitek_file(source)
