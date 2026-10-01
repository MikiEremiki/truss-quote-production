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
class AssemblyTask:
    task_id: str
    frame_name: str
    qty: int
    span_mm: int
    height_mm: int
    pitch_deg: float
    press_points: int
    plates_area_m2: float
    timber_vol_m3: float


# Alias for backwards compatibility
AssemblyLayerTask = AssemblyTask


@dataclass
class BoardRequirement:
    section: str
    stock_length_m: float
    stock_length_mm: int
    total_boards: int
    total_length_m: float
    total_volume_m3: float
    net_length_m: float
    net_volume_m3: float
    parts_count: int
    waste_pct: float


@dataclass
class ProductionWorkOrder:
    order_id: str
    project_name: str
    created_at: str
    total_frames_count: int
    total_physical_layers: int
    total_boards_count: int
    total_press_points: int
    total_timber_vol_m3: float
    boards_summary: List[BoardRequirement] = field(default_factory=list)
    assembly_tasks: List[AssemblyTask] = field(default_factory=list)
    cutting_layouts: List[BarLayout] = field(default_factory=list)
