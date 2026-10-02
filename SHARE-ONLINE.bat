@echo off
REM ===================================================================
REM  Angel Studios - share a public link with anyone, anywhere.
REM
REM  Double-click this file to run the site AND create a public
REM  web address you can send to your manager or students.
REM
REM  Requirements: the computer must stay on, and this window
REM  must stay open, for the link to keep working.
REM
REM  The address is printed on screen and saved to the Desktop as
REM  "Angel-Studios-LINK.txt".
REM ===================================================================

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py
) else (
    set PY=python
)

echo.
echo   Starting Angel Studios and creating a public link...
echo   This can take up to a minute. Please wait.
echo.

%PY% tools\keep_online.py --hours 24

echo.
pause
