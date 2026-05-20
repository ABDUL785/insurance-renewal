@echo off
echo ============================================================
echo Insurance Renewal Agent - Setup & Run
echo ============================================================
echo.

echo [1/2] Activating virtual environment and installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

echo.
echo [2/2] Running agent (batch mode)...
echo.
python agent\renewal_agent.py --batch

echo.
echo ============================================================
echo Demo complete! Press any key to exit.
echo ============================================================
pause > nul