@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\tools\unreal\launch_milestones.ps1" -Mode Solo -Storybook %*
if errorlevel 1 pause
