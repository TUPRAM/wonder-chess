@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0support\tools\development_20260930\play_development.ps1"
if errorlevel 1 pause
