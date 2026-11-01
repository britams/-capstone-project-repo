@echo off
rem Step 3: drag a video file or a folder of pictures onto this file. Runs 5 conditions and writes a table.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check_vespai.ps1" "%~1"
echo.
pause
