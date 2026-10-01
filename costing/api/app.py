"""
FastAPI Application Setup & Startup for MiTek Costing & Production Suite.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from costing.version import __version__, __version_full__
from costing.api.routes import router as api_router

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def create_app() -> FastAPI:
    """
    Фабрика приложения FastAPI.
    """
    application = FastAPI(
        title="MiTek Production & Costing Web Service",
        description="Модульный программный комплекс расчета коммерческих предложений и нарядов производства ферм на МЗП",
        version=__version__
    )

    # Middleware для отключения кэширования статики и HTML при разработке/работе
    @application.middleware("http")
    async def add_no_cache_headers(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static") or request.url.path == "/":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # Подключение API роутера
    application.include_router(api_router)

    # Подключение статических файлов
    static_dir = BASE_DIR / "web" / "static"
    if static_dir.exists():
        application.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @application.get("/", response_class=HTMLResponse)
    def index():
        template_path = BASE_DIR / "web" / "templates" / "index.html"
        if template_path.exists():
            return FileResponse(str(template_path))
        return HTMLResponse("<h1>MiTek Costing Service</h1><p>Frontend template not found.</p>")

    @application.get("/admin")
    def admin():
        return RedirectResponse(url="/?tab=tab-admin", status_code=307)

    return application


app = create_app()


def start(host: str = "127.0.0.1", port: int = 8000):
    """
    Запуск ASGI веб-сервера.
    """
    print("=" * 60)
    print(f"  Запуск Веб-сервиса MiTek Costing & Production Pro ({__version_full__})")
    print("=" * 60)
    print(f"\n  Адрес: http://{host}:{port}")
    print("  Для остановки нажмите Ctrl+C\n")
    uvicorn.run("costing.api.app:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    start()
