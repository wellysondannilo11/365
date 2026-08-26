@echo off
setlocal
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Python virtual environment not found. Use: py -m venv .venv
  exit /b 2
)
call .venv\Scripts\activate.bat
python scripts\global\data_acquisition_worker.py --config config\data_acquisition_local.json
endlocal
