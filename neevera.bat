@echo off
title Neevera Assistant

:: 1. Cek apakah sudah punya akses Admin (Jenderal)
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :MulaiNeevera
) else (
    echo Minta izin Admin dulu ya, Neev... klik YES di layar!
    :: Jalankan ulang file .bat ini dengan akses Admin
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit
)

:MulaiNeevera
:: 2. GPS otomatis: Balik ke folder tempat file .bat ini berada
cd /d "%~dp0"

:: 3. Nyalain Virtual Environment milikmu
call venv\Scripts\activate.bat

:: 4. Bangunin Neevera!
python neevera.py

pause