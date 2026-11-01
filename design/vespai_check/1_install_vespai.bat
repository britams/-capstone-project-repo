@echo off
rem Step 1: install VespAI (Seungjun j1 script, into Documents\capstone_vespai). Needs Python 3.12 (python.org, tick "Add python.exe to PATH").
set "PS1=%~dp0j1_vespai_windows.ps1"
if not exist "%PS1%" set "PS1=%~dp0..\..\vision\scripts\j1_vespai_windows.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
echo.
pause
