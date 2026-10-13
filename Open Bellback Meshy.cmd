@echo off
powershell.exe -NoProfile -File "%~dp0support\tools\meshy\Start-Bellback.ps1"
if errorlevel 1 pause
