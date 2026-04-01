@echo off
title Neevera Assistant
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :MulaiNeevera
) else (
    echo Give a permissinion first
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit
)

:MulaiNeevera
cd /d "%~dp0"
call venv\Scripts\activate.bat
python neevera.py
