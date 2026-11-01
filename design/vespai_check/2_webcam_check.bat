@echo off
rem Step 2: live webcam check. Keys: g grid, k chamber only, i size, [ ] frame mm, +/- conf, s save, q quit
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check_vespai.ps1"
echo.
pause
