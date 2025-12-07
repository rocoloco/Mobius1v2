@echo off
echo ========================================
echo Mobius Dashboard Launcher
echo ========================================
echo.
echo Step 1: Deploying updates to Modal...
echo.

REM Deploy to Modal first
python deploy_wrapper.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Modal deployment failed!
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Opening Mobius Dashboard...
echo ========================================
echo.
echo Opening dashboard at: https://rocoloco--mobius-v2-final-fastapi-app.modal.run
echo.
echo No local server needed - dashboard is served from Modal!
echo.

REM Open Chrome directly to Modal URL (no CORS issues!)
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "https://rocoloco--mobius-v2-final-fastapi-app.modal.run"

echo.
echo Dashboard opened in Chrome.
echo Press any key to exit...
pause >nul
