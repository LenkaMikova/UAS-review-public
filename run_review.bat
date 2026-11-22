@echo off
setlocal
cd /d "%~dp0"
title Review runner
echo Review runner
echo.

where py >nul 2>&1
if %errorlevel%==0 (
  py -3 "70_scripts\runner\ensure_env.py"
) else (
  python "70_scripts\runner\ensure_env.py"
)
if errorlevel 1 (
  echo.
  echo Review runner skoncil s chybou. Text je vyse.
  pause
)
endlocal
