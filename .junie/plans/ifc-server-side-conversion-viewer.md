---
sessionId: session-261001-181956-5xm0
---

# Requirements

### Overview & Goals
Перевести просмотр IFC на серверную конвертацию IFC -> glTF/GLB (подход OpenConstructionERP), чтобы убрать зависимость от CDN, wasm и web-ifc в браузере и исправить нестабильность версий библиотек.

### Scope
**In scope**
- Эндпоинт загрузки IFC и конвертации в GLB на сервере.
- Браузерный просмотрщик на three.js + GLTFLoader + OrbitControls (локальные файлы в `web/static`).
- Сохранение текущего UI: блок «3D-просмотр модели (IFC)» на вкладке «Обзор и Конструктив».

**Out of scope**
- Тайлинг/стриминг, измерения, сечения, привязка к данным BIM.
- Реализация сейчас: план только сохранён, к реализации не приступаем.

### Functional Requirements
- Пользователь выбирает .ifc, сервер возвращает GLB, модель отображается и центрируется камерой.
- Ошибки конвертации показываются в `#ifc-status`.
- Работа без доступа к интернету.

# Technical Design

### Current Implementation
- `web/static/js/modules/ifc-viewer.js`: клиентский web-ifc-three с CDN (хрупко по версиям).
- `web/templates/index.html`: блок `#ifc-canvas-container`, `#ifc-file-input`, `#ifc-status`.
- `web/static/js/app.js`: `window.handleIfcUpload`.
- Бэкенд: `app.py` (+ пакет web).

### Key Decisions
- Серверная конвертация через `ifcopenshell` (`ifcopenshell.geom` iterator) + `trimesh`/свой экспорт в GLB. Рационально: нет wasm и CDN в браузере.
- Three.js, `GLTFLoader`, `OrbitControls` кладутся локально в `web/static/vendor`.
- Кэш GLB во временной папке `output/ifc_cache` по хэшу файла.

### Proposed Changes
- Новый модуль `web/ifc_convert.py`: `convert_ifc_to_glb(path) -> bytes`.
- Новый эндпоинт `POST /api/ifc/convert` (multipart) -> `model/gltf-binary`.
- Переписать `ifc-viewer.js`: upload на эндпоинт, `GLTFLoader.parse`, OrbitControls, автоцентровка.
- Добавить `ifcopenshell` (и `trimesh`/`numpy`) в `pyproject.toml`.

### Risks
- Большие IFC: долгая конвертация -> индикатор прогресса, лимит размера, фоновая задача при необходимости.
- Ось Z-up (IFC) vs Y-up (glTF): поворот модели.
- Сборка `ifcopenshell` под Windows/Python версии проекта.

# Testing

- Юнит-тест `convert_ifc_to_glb` на `output/Богородск 21 h1400 t40.ifc`: результат начинается с `glTF`.
- Тест эндпоинта: корректный файл -> 200, не-IFC -> 4xx.
- Ручная проверка в браузере: загрузка, вращение, центровка, офлайн-режим.

# Delivery Steps

###   Step 1: Серверная конвертация IFC в GLB
Сервер конвертирует IFC в GLB через эндпоинт.

- Добавить зависимости `ifcopenshell`, `trimesh` в `pyproject.toml`.
- Создать `web/ifc_convert.py` с `convert_ifc_to_glb` (геометрия, цвета, Z-up -> Y-up).
- Добавить `POST /api/ifc/convert` с проверкой типа/размера и кэшем.
- Написать тесты на реальном IFC из `output/`.

###   Step 2: Переписать клиентский просмотрщик на GLTFLoader
Браузер показывает GLB без CDN.

- Положить three.js, GLTFLoader, OrbitControls в `web/static/vendor`.
- Переписать `web/static/js/modules/ifc-viewer.js`: отправка файла, загрузка GLB, OrbitControls, автоцентровка, статусы и ошибки.
- Оставить разметку в `index.html` и `window.handleIfcUpload` в `app.js`.
- Обновить документацию (ADR/README) о новой схеме.