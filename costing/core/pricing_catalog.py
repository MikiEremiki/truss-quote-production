"""
Справочники ценовых политик, профилей клиентов и ставок ДревКаркас (DK).
"""

from typing import Dict, Any

DK_PRICING_CATALOG: Dict[str, Any] = {
    "timber_base_cost_m3": 29000.0,
    "timber_default_margin_pct": 10.0,
    "timber_default_sale_m3": 31900.0,
    "plates_base_price_m2": 4500.0,
    "plates_base_cost_m2": 4000.0,
    "plates_default_margin_pct": 5.0,
    
    # Расценки работ по типам конструкций (руб/м3)
    "truss_types": {
        "duopitch": {"label": "Двускатная ферма", "cost_m3": 4400.0, "price_m3": 7500.0, "margin_pct": 70.45},
        "monopitch": {"label": "Односкатная ферма", "cost_m3": 4400.0, "price_m3": 7500.0, "margin_pct": 70.45},
        "scissor": {"label": "Ножничная ферма", "cost_m3": 4400.0, "price_m3": 8500.0, "margin_pct": 93.18},
        "girder": {"label": "Балка на МЗП", "cost_m3": 3500.0, "price_m3": 6000.0, "margin_pct": 71.43},
        "gable_ladder": {"label": "Фронтонная лестница", "cost_m3": 3850.0, "price_m3": 6600.0, "margin_pct": 71.43},
        "hip": {"label": "Вальма", "cost_m3": 4950.0, "price_m3": 10000.0, "margin_pct": 102.02},
        "cut_timber": {"label": "Доска с прирезкой / Стропила", "cost_m3": 1300.0, "price_m3": 2000.0, "margin_pct": 53.85},
        "raw_timber": {"label": "Просто доска (без распила)", "cost_m3": 0.0, "price_m3": 0.0, "margin_pct": 0.0},
        "custom": {"label": "Другое / Индивидуальная", "cost_m3": 4400.0, "price_m3": 7500.0, "margin_pct": 70.45}
    },
    
    # Надбавка за длину фермы свыше 12 метров
    "span_over_12m": {
        "threshold_mm": 12000,
        "cost_add_m3": 600.0,
        "price_add_m3": 1000.0
    },
    
    # Прирезка пиломатериалов
    "cutting": {
        "cost_m3": 1300.0,
        "price_m3": 2000.0,
        "margin_pct": 53.85
    },
    
    # Защитная обработка СенежОгнеБио 300 г/м2
    "treatment": {
        "standard_price_m2": 65.0,
        "evdokimov_price_m2": 50.0,
        "cost_m2": 50.0
    },
    
    # Проектирование КР/КДД
    "design": {
        "standard_price": 15000.0,
        "standard_cost": 10000.0,
        "hip_price_m2": 100.0,
        "hip_cost_m2": 50.0,
        "hip_min_price": 20000.0,
        "hip_min_cost": 10000.0
    },
    
    # Ступенчатые наценки от объема заказа (по сумме конструкций)
    "volume_tiers": [
        {"max_sum": 50000.0, "extra_margin_pct": 30.0},
        {"max_sum": 100000.0, "extra_margin_pct": 15.0},
        {"max_sum": 200000.0, "extra_margin_pct": 5.0}
    ],
    "default_order_margin_pct": 58.0
}

CLIENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "standard": {
        "name": "Стандартный заказчик",
        "margin_pct": 58.0,
        "treatment_price_m2": 65.0,
        "timber_price_m3": 31900.0,
        "description": "Базовые розничные расценки ДК (+58% маржа, обработка 65 ₽/м²)"
    },
    "evdokimov": {
        "name": "Домокомплекты Евдокимов",
        "margin_pct": 30.0,
        "treatment_price_m2": 50.0,
        "timber_price_m3": 31900.0,
        "description": "Спец. наценка 30%, обработка 50 ₽/м²"
    },
    "dk_group": {
        "name": "Модульное производство ДК Групп",
        "margin_pct": 3.0,
        "treatment_price_m2": 50.0,
        "timber_price_m3": 31900.0,
        "description": "Внутренняя наценка 3%, обработка 50 ₽/м²"
    },
    "tiny": {
        "name": "Домокомплекты Тини",
        "margin_pct": 25.0,
        "treatment_price_m2": 65.0,
        "timber_price_m3": 31900.0,
        "description": "Наценка 25%, обработка 65 ₽/м²"
    },
    "reznikov": {
        "name": "Домокомплекты Резников",
        "margin_pct": 30.0,
        "treatment_price_m2": 65.0,
        "timber_price_m3": 31900.0,
        "description": "Наценка 30%, обработка 65 ₽/м²"
    },
    "partners": {
        "name": "Партнеры (скидка 3%)",
        "margin_pct": 55.0,
        "treatment_price_m2": 65.0,
        "timber_price_m3": 31900.0,
        "description": "Партнерский дисконт (-3% от базовой маржи)"
    },
    "custom": {
        "name": "Индивидуальный расчет",
        "margin_pct": 58.0,
        "treatment_price_m2": 65.0,
        "timber_price_m3": 31900.0,
        "description": "Произвольные параметры пользователя"
    }
}

AGENTS_CATALOG: Dict[str, Dict[str, Any]] = {
    "none": {
        "name": "Без агента (0%)",
        "pct": 0.0
    },
    "piletskiy": {
        "name": "Пилецкий Станислав (12%)",
        "pct": 12.0
    },
    "yarikov": {
        "name": "ИП Яриков (5%)",
        "pct": 5.0
    },
    "belov": {
        "name": "Белов Александр Витальевич (5%)",
        "pct": 5.0
    },
    "custom": {
        "name": "Произвольный агент",
        "pct": 0.0
    }
}
