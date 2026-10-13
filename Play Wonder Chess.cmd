@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\unreal\launch_milestones.ps1" -Mode Solo -Storybook -CreaturePreview -Visible %*
if errorlevel 1 pause
