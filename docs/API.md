# Спецификация REST API (MiTek Costing & Production)

Интерактивная OpenAPI / Swagger документация доступна при запущенном сервере по адресу: `http://127.0.0.1:8000/docs`.

---

### 1. `GET /api/sample`
Загружает и производит полный первичный расчет для демонстрационного объекта *«Богородск 21 дом 110м2»*.

**Ответ (200 OK):**
```json
{
  "status": "success",
  "data": { ... },     // Нормализованные данные MiTek
  "cost": { ... },     // Полный расчет себестоимости и P&L
  "cutting": { ... }   // 1D Bin Packing раскладка заготовок
}
```

---

### 2. `POST /api/upload`
Загружает и парсит пользовательский файл выгрузки MiTek (`.xlsm` или `.xlsx`) через `multipart/form-data`.

**Параметры формы:**
- `file`: бинарный файл книги Excel.

**Ответ (200 OK):**
```json
{
  "status": "success",
  "filename": "МойПроект.xlsm",
  "data": { ... },
  "cost": { ... },
  "cutting": { ... }
}
```

---

### 3. `POST /api/costing/calculate`
Выполняет расчет себестоимости материалов, услуг и базовых наценок (для вкладки «Калькулятор стоимости»).

**Тело запроса (JSON):**
```json
{
  "client_profile": "standard",
  "timber_price_m3": 31900.0,
  "timber_waste_factor": 1.15,
  "plate_price_m2": 4500.0,
  "cutting_price_m3": 2000.0,
  "treatment_price_m2": 65.0,
  "design_mode": "separate",
  "design_price_fixed": 15000.0,
  "fasteners_price_fixed": 5625.0,
  "logistics_price_fixed": 12000.0,
  "overhead_pct": 10.0
}
```

---

### 4. `POST /api/positions/calculate`
Выполняет расчет сложности работ, защитной обработки, прирезки и наценок по маркам ферм (для вкладки «Позиции & Сложность работ»).

**Тело запроса (JSON):**
```json
{
  "custom_items": {
    "Ф1": {
      "type": "truss",
      "subtype": "duopitch",
      "has_treatment": true,
      "has_cutting": true,
      "work_rate_m3": 4400.0,
      "margin_pct": 58.0
    }
  }
}
```

---

### 5. `POST /api/cutting/optimize`
Оптимизирует раскрой пиломатериала (1D Stock Cutting / Bin Packing) под заданную длину хлыста и пропил (для вкладки «Раскрой (мм)»).

**Тело запроса (JSON):**
```json
{
  "stock_length_mm": 6000.0,
  "kerf_mm": 4.0
}
```

---

### 6. `POST /api/financials/calculate`
Выполняет расчет P&L показателей, скидок, агентских комиссий и НДС (для вкладки «P&L Финансы»).

**Тело запроса (JSON):**
```json
{
  "discount_type": "percent",
  "discount_val": 5.0,
  "agent_id": "piletskiy",
  "agent_pct": 10.0,
  "agent_mode": "markup",
  "vat_pct": 20.0
}
```

---

### 7. `POST /api/calculate`
Выполняет комплексный пересчет себестоимости, попозиционных цен и раскроя по переданным параметрам (обратная совместимость).

**Тело запроса (JSON):**
```json
{
  "client_profile": "standard",
  "timber_price_m3": 31900.0,
  "timber_cost_m3": 29000.0,
  "timber_waste_factor": 1.15,
  "plate_price_m2": 4500.0,
  "plate_cost_m2": 4000.0,
  "treatment_price_m2": 65.0,
  "treatment_cost_m2": 50.0,
  "design_price_fixed": 15000.0,
  "design_cost_fixed": 10000.0,
  "design_mode": "separate",
  "fasteners_cost_fixed": 4500.0,
  "fasteners_price_fixed": 5625.0,
  "logistics_fixed": 12000.0,
  "margin_pct": 58.0,
  "overhead_pct": 10.0,
  "discount_type": "percent",
  "discount_val": 5.0,
  "agent_id": "piletskiy",
  "agent_mode": "markup",
  "agent_pct": 12.0,
  "vat_pct": 20.0,
  "stock_length_mm": 6000.0,
  "custom_items": {
    "Т1": {
      "type": "truss",
      "subtype": "duopitch",
      "work_rate_m3": 4400,
      "margin_pct": 58.0,
      "has_treatment": true,
      "has_cutting": true
    }
  }
}
```

---

### 8. `POST /api/quote`
Формирует структурированное коммерческое предложение с разбивкой по товарным позициям, скидкам, агентским надбавкам и НДС.

**Тело запроса (JSON):**
```json
{
  "project_name": "Богородск 21 дом 110м2",
  "client_name": "ООО СтройКомплект",
  "version_comment": "Расчет со скидкой 5%",
  "calc_params": { ... }
}
```

---

### 9. `POST /api/workorders`
Генерирует комплект производственных нарядов для цеха, включая расчет потребности в пиломатериале по сечениям (хлысты 6.0 м), сборочные задания по маркам ферм, карты раскроя хлыстов и сводную ведомость пластин МЗП.

**Тело запроса (JSON):**
```json
{
  "stock_length_mm": 6000.0,
  "kerf_mm": 4.0
}
```

**Ответ (200 OK):**
```json
{
  "status": "success",
  "workorders": {
    "order_id": "WO-261001-2015",
    "project_name": "Богородск 21 дом 110м2",
    "created_at": "01.10.2026 20:15",
    "total_frames_count": 25,
    "total_physical_layers": 32,
    "total_boards_count": 84,
    "total_boards_meters": 504.0,
    "total_press_points": 740,
    "total_timber_vol_m3": 3.8450,
    "boards_summary": [
      {
        "section": "45x145",
        "stock_length_m": 6.0,
        "stock_length_mm": 6000,
        "total_boards": 54,
        "total_length_m": 324.0,
        "net_length_m": 298.5,
        "total_volume_m3": 2.1141,
        "net_volume_m3": 1.9477,
        "parts_count": 142,
        "waste_pct": 7.87
      }
    ],
    "assembly_tasks": [
      {
        "task_id": "TSK-001",
        "frame_name": "Ф1",
        "qty": 8,
        "plies": 1,
        "total_layers": 8,
        "span_mm": 8400,
        "height_mm": 2100,
        "pitch_deg": 25.0,
        "press_points": 240,
        "press_points_per_unit": 30,
        "timber_vol_m3": 0.8420,
        "plates_m2": 3.250
      }
    ],
    "cutting_plan": { ... },
    "plates_summary": [
      {
        "size_str": "100x150",
        "gauge": "T150",
        "total_qty": 64,
        "unit_area_m2": 0.015,
        "total_area_m2": 0.96
      }
    ]
  }
}
```

---

### 10. `GET /api/info`
Возвращает системную информацию о версии программного комплекса.

**Ответ (200 OK):**
```json
{
  "status": "success",
  "app_name": "MiTek Costing & Production Pro",
  "version": "2.0.0",
  "version_suffix": "PRO",
  "version_full": "2.0.0-PRO"
}
```

---

### 11. `GET /api/admin/type-aliases`
Возвращает типы конструкций, присутствующие в текущем проекте MiTek, полный каталог доступных подтипов (`all_options`) и сохраненные пользовательские алиасы (`aliases`).

**Ответ (200 OK):**
```json
{
  "status": "success",
  "types": {
    "duopitch": "Двускатная ферма",
    "cut_timber": "Доска с прирезкой / Стропила"
  },
  "all_options": {
    "duopitch": "Двускатная ферма",
    "monopitch": "Односкатная ферма",
    "scissor": "Ножничная ферма",
    "girder": "Балка на МЗП",
    "gable_ladder": "Фронтонная лестница",
    "hip": "Вальма",
    "cut_timber": "Доска с прирезкой / Стропила",
    "raw_timber": "Просто доска (без распила)",
    "custom": "Другое / Индивидуальная"
  },
  "aliases": {
    "duopitch": "scissor"
  }
}
```

---

### 12. `PUT /api/admin/type-aliases`
Сохраняет сопоставление алиасов типов конструкций в `settings.json`. Пустая строка сбрасывает алиас на значение по умолчанию.

**Тело запроса (JSON):**
```json
{
  "aliases": {
    "duopitch": "scissor",
    "cut_timber": ""
  }
}
```

**Ответ (200 OK):**
```json
{
  "status": "success",
  "aliases": {
    "duopitch": "scissor"
  }
}
```
