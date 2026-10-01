"""
Пользовательские настройки приложения (админка). Хранятся в JSON-файле settings.json в корне проекта.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

from costing.core.pricing_catalog import DK_PRICING_CATALOG

SETTINGS_PATH = Path(os.environ.get(
    "COSTING_SETTINGS_PATH",
    str(Path(__file__).resolve().parent.parent.parent / "settings.json")
))


def _load_raw() -> Dict[str, Any]:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def get_truss_types() -> Dict[str, str]:
    """Типы конструкций: ключ -> стандартное название."""
    return {k: v["label"] for k, v in DK_PRICING_CATALOG["truss_types"].items()}


def get_type_aliases() -> Dict[str, str]:
    """Сохраненные alias типов конструкций (только непустые и известные ключи)."""
    raw = _load_raw().get("type_aliases", {})
    known = get_truss_types()
    if not isinstance(raw, dict):
        return {}
    return {k: str(v).strip() for k, v in raw.items() if k in known and str(v).strip()}


def save_type_aliases(aliases: Dict[str, str]) -> Dict[str, str]:
    known = get_truss_types()
    data = _load_raw()
    clean = get_type_aliases()
    for k, v in aliases.items():
        if k not in known:
            continue
        v_str = str(v).strip()
        if v_str and (v_str in known or v_str in known.values()):
            clean[k] = v_str
        else:
            clean.pop(k, None)
    data["type_aliases"] = clean
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return clean
