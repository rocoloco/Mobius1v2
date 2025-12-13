@echo off
echo Starting Mobius Development Environment...
echo.

REM Note: Backend runs on Modal, not locally
echo Backend is running on Modal: https://rocoloco--mobius-v2-final-fastapi-app.modal.run
echo Your logo preservation fix is deployed and active!

REM No need to wait - Modal backend is already running

REM Start frontend in a new window
echo Starting Frontend (Vite)...
start "Mobius Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both services are starting...
echo.
echo Backend: https://rocoloco--mobius-v2-final-fastapi-app.modal.run
echo Frontend: http://localhost:5173
echo API Docs: https://rocoloco--mobius-v2-final-fastapi-app.modal.run/docs
echo.
echo Press any key to close this window (services will keep running)
pause >nul