@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Pouziti: original_run.bat backup ^| compare ^| restore
  echo.
  echo   backup   zaloha puvodnich vystupu do 99_backup\original_run
  echo   compare  porovnani ziveho behu s tou zalohou
  echo   restore  vratit zalohu do zivych slozek
  echo.
  pause
  exit /b 1
)
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 "70_scripts\original_run.py" %*
) else (
  python "70_scripts\original_run.py" %*
)
if errorlevel 1 (
  echo.
  echo original_run skoncil s chybou.
  pause
)
endlocal
