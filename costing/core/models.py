"""
Domain Data Models for MiTek Truss Projects, Components, and Pricing.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TrussFrame:
    name: str
    qty: int = 1
    plies: int = 1
    total_layers: int = 1
    span_mm: int = 0
    height_mm: int = 0
    pitch_deg: float = 0.0
    vol_m3_ply: float = 0.0
    total_vol_m3: float = 0.0
    plates_m2_ply: float = 0.0
    total_plates_m2: float = 0.0
    press_points_ply: int = 0
    total_press_points: int = 0
    surface_area_m2: float = 0.0
    item_type: str = "truss"  # 'truss', 'cut_timber', 'raw_timber'


@dataclass
class TimberItem:
    truss: str
    label: str
    qty: int
    ply: int
    type: str
    length_m: float
    length_mm: int
    thick_mm: int
    depth_mm: int
    section: str
    grade: str
    volume_m3: float
    surface_area_m2: float


@dataclass
class PlateItem:
    truss: str
    qty: int
    depth_mm: int
    length_mm: int
    size_str: str
    gauge: str
    area_m2: float
    area_dm2: float


@dataclass
class FastenerItem:
    desc: str
    object: str
    qty: int


@dataclass
class ProjectSummary:
    total_net_timber_m3: float
    total_timber_surface_m2: float
    total_plates_area_m2: float
    total_plates_area_dm2: float
    total_plates_count: int
    total_physical_layers: int
    total_press_points: int
    total_roof_area_m2: float
    project_name: str
    pitch_deg: float
    spacing_mm: int


@dataclass
class ProjectData:
    general: Dict[str, Any] = field(default_factory=dict)
    frames: List[Dict[str, Any]] = field(default_factory=list)
    timber: List[Dict[str, Any]] = field(default_factory=list)
    plates: List[Dict[str, Any]] = field(default_factory=list)
    fasteners: List[Dict[str, Any]] = field(default_factory=list)
    surfaces: List[Dict[str, Any]] = field(default_factory=list)
    roofing: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
