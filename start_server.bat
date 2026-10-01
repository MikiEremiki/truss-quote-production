@echo off
title MiTek Web Service
uv run app.py
if errorlevel 1 (
    py app.py
    if errorlevel 1 (
        python app.py
        if errorlevel 1 (
            echo.
            echo Error starting Python application. Please check if uv or Python is installed.
            pause
        )
    )
)
