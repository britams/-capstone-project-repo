@echo off
rem VespAI live webcam launcher (CAP-AI-SJ-09). Double-click. Runs the .ps1 with the same name.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dpn0.ps1" %*
echo.
pause
