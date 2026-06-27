@echo off
chcp 65001 > nul
title TVJP - Executive Automated Test Suite
cls
echo =======================================================================
echo            TVJP AUTOMATED METHODOLOGY TESTING SUITE (LAYERS 1 - 9)
echo   Pilar 1 (Structural) - Pilar 2 (Continuous) - Pilar 3 (Non-Deterministic)
echo =======================================================================
echo.

if not exist ".\venv-backend\Scripts\activate.bat" (
    echo [ERROR] Virtual environment backend tidak ditemukan di .\venv-backend
    echo Harap pastikan venv telah terinstall.
    echo.
    pause
    exit /b 1
)

echo [1/2] Mengaktifkan Virtual Environment (venv-backend)...
call .\venv-backend\Scripts\activate.bat

echo.
echo [2/2] Menjalankan Suite Pengujian Otomatis (backend/tests/layers)...
echo -----------------------------------------------------------------------
python -m pytest backend/tests/layers/ -v -s --tb=short

echo.
echo =======================================================================
echo  [Laporan Word Ter-update]    : .\test_reports\laporan.docx
echo  [Laporan Markdown Ter-update]: .\test_reports\laporan.md
echo =======================================================================
echo.
pause
