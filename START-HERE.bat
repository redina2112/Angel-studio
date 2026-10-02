@echo off
REM ===================================================================
REM  Angel Studios - one-click launcher
REM
REM  Double-click this file (or START-HERE.bat) to run the website.
REM  Your browser opens automatically at http://127.0.0.1:8000
REM
REM  Keep the window open while you use the site.
REM  Close the window (or press Ctrl+C) to stop.
REM ===================================================================

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PY=python
    ) else (
        echo.
        echo   Python was not found on this computer.
        echo.
        echo   Install it free from:  https://www.python.org/downloads/
        echo   During install, tick "Add Python to PATH".
        echo.
        pause
        exit /b 1
    )
)

echo.
echo   Starting Angel Studios...
echo.

%PY% server.py --open

echo.
echo   The website has stopped.
pause
