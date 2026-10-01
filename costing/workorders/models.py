"""
Production Work Orders, Assembly Layer Tasks, and Cutting Models.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CuttingPart:
    truss: str
    label: str
    length_m: float
    length_mm: int


@dataclass
class BarLayout:
    bar_index: int
    section: str
    stock_length_mm: float
    used_length_m: float
    remaining_length_m: float
    waste_pct: float
    parts: List[CuttingPart] = field(default_factory=list)


@dataclass
class AssemblyLayerTask:
    frame_name: str
    layer_index: int
    plies_in_packet: int
    span_mm: int
    height_mm: int
    press_points: int
    plates_area_m2: float
    timber_vol_m3: float


@dataclass
class ProductionWorkOrder:
    order_id: str
    project_name: str
    created_at: str
    total_physical_layers: int
    total_press_points: int
    assembly_tasks: List[AssemblyLayerTask] = field(default_factory=list)
    cutting_layouts: List[BarLayout] = field(default_factory=list)
