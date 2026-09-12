@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\unreal\launch_vnext_lab.ps1"
if errorlevel 1 pause
