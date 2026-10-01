"""
FastAPI Routes for MiTek Processing, Costing Calculations, Quotes, and Production Workorders.
"""

import os
import io
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import HTMLResponse

from costing.version import __version__, __version_suffix__, __version_full__
from costing.data_import.mitek_parser import parse_mitek_workbook, load_mitek_file
from costing.calculator.engine import calculate_cost
from costing.workorders.optimizer import optimize_cutting_stock
from costing.workorders.generator import generate_production_workorders
from costing.workorders.exports import export_cutting_plan_csv, export_workorders_csv
from costing.quote.engine import generate_quote
from costing.quote.pdf_export import render_quote_html
from costing.quote.exports import export_quote_csv
from costing.core.settings import get_truss_types, get_type_aliases, save_type_aliases
from costing.api.schemas import CalculateRequest, CuttingOptimizeRequest, QuoteRequest, WorkorderRequest

router = APIRouter(prefix="/api", tags=["Costing & Production API"])


@router.get("/info", tags=["System"])
def get_app_info():
    """
    Информация о версии и программном комплексе.
    """
    return {
        "status": "success",
        "app_name": "MiTek Costing & Production Pro",
        "version": __version__,
        "version_suffix": __version_suffix__,
        "version_full": __version_full__,
    }

@router.get("/admin/type-aliases", tags=["Admin"])
def get_admin_type_aliases():
    """
    Типы конструкций из файла, доступные варианты из каталога и заданные для них alias.
    """
    all_types = get_truss_types()
    try:
        frames = get_current_project_data().get("frames", [])
    except HTTPException:
        frames = []
    default_key = {"truss": "duopitch", "cut_timber": "cut_timber", "raw_timber": "raw_timber"}
    present = {default_key.get(f.get("item_type"), "duopitch") for f in frames}
    types = {k: v for k, v in all_types.items() if k in present}
    return {
        "status": "success",
        "types": types,
        "all_options": all_types,
        "aliases": get_type_aliases(),
    }


@router.put("/admin/type-aliases", tags=["Admin"])
def put_admin_type_aliases(payload: Dict[str, Any]):
    """
    Сохранение alias типов конструкций. Пустое значение сбрасывает alias.
    """
    aliases = payload.get("aliases", {})
    if not isinstance(aliases, dict):
        raise HTTPException(status_code=400, detail="aliases должен быть объектом")
    return {"status": "success", "aliases": save_type_aliases(aliases)}


# Global session cache for active project data
CURRENT_PROJECT_DATA: Optional[Dict[str, Any]] = None


def find_sample_file() -> Optional[str]:
    """
    Поиск демонстрационного файла выгрузки MiTek в корне или в output/.
    """
    candidates = [
        "Богородск 21 h1400 t40.xlsm",
        os.path.join("output", "Богородск 21 h1400 t40.xlsm"),
        os.path.join("..", "output", "Богородск 21 h1400 t40.xlsm")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def get_current_project_data() -> Dict[str, Any]:
    """
    Получение активных данных проекта или загрузка эталонного файла при отсутствии.
    """
    global CURRENT_PROJECT_DATA
    if not CURRENT_PROJECT_DATA:
        file_path = find_sample_file()
        if file_path:
            CURRENT_PROJECT_DATA = load_mitek_file(file_path)
        else:
            raise HTTPException(status_code=400, detail="Сначала загрузите файл MiTek")
    return CURRENT_PROJECT_DATA


@router.get("/sample", tags=["Projects"])
def get_sample_data():
    """
    Загрузка и расчет эталонного проекта (Богородск 21).
    """
    global CURRENT_PROJECT_DATA
    file_path = find_sample_file()
    if file_path:
        CURRENT_PROJECT_DATA = load_mitek_file(file_path)
        calc = calculate_cost(CURRENT_PROJECT_DATA, {})
        cutting = optimize_cutting_stock(CURRENT_PROJECT_DATA["timber"], stock_length_mm=6000.0)
        return {
            "status": "success",
            "data": CURRENT_PROJECT_DATA,
            "cost": calc,
            "cutting": cutting
        }
    raise HTTPException(status_code=404, detail="Тестовый файл не найден")


@router.post("/upload", tags=["Projects"])
async def upload_file(file: UploadFile = File(...)):
    """
    Загрузка и парсинг нового файла выгрузки MiTek (.xlsm / .xlsx).
    """
    global CURRENT_PROJECT_DATA
    try:
        contents = await file.read()
        CURRENT_PROJECT_DATA = load_mitek_file(contents)
        calc = calculate_cost(CURRENT_PROJECT_DATA, {})
        cutting = optimize_cutting_stock(CURRENT_PROJECT_DATA["timber"], stock_length_mm=6000.0)
        return {
            "status": "success",
            "filename": file.filename,
            "data": CURRENT_PROJECT_DATA,
            "cost": calc,
            "cutting": cutting
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обработки файла: {str(e)}")


@router.post("/costing/calculate", tags=["Costing"])
def calculate_costing_endpoint(payload: Dict[str, Any]):
    """
    Расчет себестоимости и цен на материалы/услуги (вкладка Калькулятор стоимости).
    """
    project_data = get_current_project_data()
    calc = calculate_cost(project_data, payload)
    return {
        "status": "success",
        "data": project_data,
        "cost": calc
    }


@router.post("/positions/calculate", tags=["Positions"])
def calculate_positions_endpoint(payload: Dict[str, Any]):
    """
    Пересчет сложности работ, антисептирования, прирезки и наценок по маркам (вкладка Позиции).
    """
    project_data = get_current_project_data()
    calc = calculate_cost(project_data, payload)
    return {
        "status": "success",
        "data": project_data,
        "cost": calc
    }


@router.post("/cutting/optimize", tags=["Cutting"])
def optimize_cutting_endpoint(payload: Dict[str, Any]):
    """
    Оптимизация 1D раскроя пиломатериала на стандартные хлысты (вкладка Раскрой).
    """
    project_data = get_current_project_data()
    stock_len_mm = float(payload.get("stock_length_mm", 6000.0))
    kerf_mm = float(payload.get("kerf_mm", 4.0))
    cutting = optimize_cutting_stock(project_data["timber"], stock_length_mm=stock_len_mm, kerf_mm=kerf_mm)
    return {
        "status": "success",
        "cutting": cutting
    }


@router.post("/financials/calculate", tags=["Financials"])
def calculate_financials_endpoint(payload: Dict[str, Any]):
    """
    Пересчет P&L, скидок, агентских вознаграждений и НДС (вкладка P&L Финансы).
    """
    project_data = get_current_project_data()
    calc = calculate_cost(project_data, payload)
    return {
        "status": "success",
        "cost": calc
    }


@router.post("/calculate", tags=["Comprehensive"])
def recalculate(payload: Dict[str, Any]):
    """
    Комплексный пересчет себестоимости, попозиционных цен и раскроя (обратная совместимость).
    """
    project_data = get_current_project_data()
    stock_len_mm = float(payload.get("stock_length_mm", 6000.0))
    calc = calculate_cost(project_data, payload)
    cutting = optimize_cutting_stock(project_data["timber"], stock_length_mm=stock_len_mm)
    return {
        "status": "success",
        "data": project_data,
        "cost": calc,
        "cutting": cutting
    }


@router.post("/quote", tags=["Quotes"])
def create_quote_endpoint(payload: QuoteRequest):
    """
    Формирование коммерческого предложения.
    """
    project_data = get_current_project_data()
    calc_params = payload.calc_params.dict() if payload.calc_params else {}
    calc = calculate_cost(project_data, calc_params)
    project_name = payload.project_name or project_data.get("summary", {}).get("project_name", "Проект")
    quote = generate_quote(cost_result=calc, project_name=project_name, client_name=payload.client_name or "Заказчик")
    return {
        "status": "success",
        "quote": quote
    }


@router.post("/workorders", tags=["Workorders"])
def get_workorders_endpoint(payload: WorkorderRequest):
    """
    Генерация производственных нарядов и карт раскроя для цеха.
    """
    project_data = get_current_project_data()
    workorders = generate_production_workorders(
        project_data=project_data,
        stock_length_mm=payload.stock_length_mm or 6000.0
    )
    return {
        "status": "success",
        "workorders": workorders
    }


# ==========================================================
# EXPORT / DOWNLOAD ENDPOINTS
# ==========================================================

@router.get("/quote/download/html", tags=["Exports"])
def download_quote_html(client_name: str = "Заказчик"):
    """
    Скачивание готового HTML файла коммерческого предложения.
    """
    project_data = get_current_project_data()
    calc = calculate_cost(project_data)
    project_name = project_data.get("summary", {}).get("project_name", "Проект")
    quote = generate_quote(cost_result=calc, project_name=project_name, client_name=client_name)
    html_content = render_quote_html(quote)
    filename = f"KP_{quote.get('quote_id', 'doc')}.html"
    return Response(
        content=html_content.encode("utf-8"),
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/quote/download/csv", tags=["Exports"])
def download_quote_csv(client_name: str = "Заказчик"):
    """
    Скачивание коммерческого предложения в формате CSV (Excel-совместимый UTF-8 с BOM).
    """
    project_data = get_current_project_data()
    calc = calculate_cost(project_data)
    project_name = project_data.get("summary", {}).get("project_name", "Проект")
    quote = generate_quote(cost_result=calc, project_name=project_name, client_name=client_name)
    csv_text = export_quote_csv(quote)
    filename = f"KP_{quote.get('quote_id', 'doc')}.csv"
    # BOM for Excel utf-8
    bom_content = b'\xef\xbb\xbf' + csv_text.encode("utf-8")
    return Response(
        content=bom_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/cutting/download/csv", tags=["Exports"])
def download_cutting_csv(stock_length_mm: float = 6000.0):
    """
    Скачивание карты раскроя хлыстов в формате CSV (Excel-совместимый UTF-8 с BOM).
    """
    project_data = get_current_project_data()
    timber = project_data.get("timber", [])
    cutting = optimize_cutting_stock(timber_items=timber, stock_length_mm=stock_length_mm)
    csv_text = export_cutting_plan_csv(cutting)
    filename = "Cutting_Plan.csv"
    bom_content = b'\xef\xbb\xbf' + csv_text.encode("utf-8")
    return Response(
        content=bom_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/workorders/download/csv", tags=["Exports"])
def download_workorders_csv(stock_length_mm: float = 6000.0):
    """
    Скачивание производственных нарядов цеха сборки в формате CSV (Excel-совместимый UTF-8 с BOM).
    """
    project_data = get_current_project_data()
    workorders = generate_production_workorders(project_data=project_data, stock_length_mm=stock_length_mm)
    csv_text = export_workorders_csv(workorders)
    filename = f"Workorders_{workorders.get('order_id', 'batch')}.csv"
    bom_content = b'\xef\xbb\xbf' + csv_text.encode("utf-8")
    return Response(
        content=bom_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
