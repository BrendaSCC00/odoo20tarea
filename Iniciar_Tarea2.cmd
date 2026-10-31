@echo off
cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
python preparar_tarea2.py
pause
