"""
Pydantic Schemas for REST API Endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CalculateRequest(BaseModel):
    client_profile: Optional[str] = "standard"
    timber_price_m3: Optional[float] = None
    timber_cost_m3: Optional[float] = None
    timber_waste_factor: Optional[float] = 1.15
    plate_price_m2: Optional[float] = None
    plate_cost_m2: Optional[float] = None
    cutting_cost_m3: Optional[float] = None
    cutting_price_m3: Optional[float] = None
    treatment_price_m2: Optional[float] = None
    treatment_cost_m2: Optional[float] = None
    design_price_fixed: Optional[float] = None
    design_cost_fixed: Optional[float] = None
    design_mode: Optional[str] = "separate"
    fasteners_cost_fixed: Optional[float] = 4500.0
    fasteners_price_fixed: Optional[float] = None
    logistics_fixed: Optional[float] = 12000.0
    logistics_price_fixed: Optional[float] = None
    margin_pct: Optional[float] = None
    overhead_pct: Optional[float] = 10.0
    discount_type: Optional[str] = "percent"
    discount_val: Optional[float] = 0.0
    agent_id: Optional[str] = "none"
    agent_name: Optional[str] = None
    agent_pct: Optional[float] = 0.0
    agent_mode: Optional[str] = "markup"
    vat_pct: Optional[float] = 0.0
    stock_length_mm: Optional[float] = 6000.0
    custom_items: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CuttingOptimizeRequest(BaseModel):
    stock_length_mm: Optional[float] = 6000.0
    kerf_mm: Optional[float] = 4.0


class QuoteRequest(BaseModel):
    project_name: Optional[str] = "Проект"
    client_name: Optional[str] = "Заказчик"
    version_comment: Optional[str] = "Первоначальный расчет"
    calc_params: Optional[CalculateRequest] = None


class WorkorderRequest(BaseModel):
    stock_length_mm: Optional[float] = 6000.0
    kerf_mm: Optional[float] = 4.0
