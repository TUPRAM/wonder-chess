@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\unreal\launch_milestones.ps1" -Mode Solo -Storybook -CragstoatPreview -Visible -Executable "%~dp0builds\WonderChess-Visual-r29\Windows\WonderChess\Binaries\Win64\WonderChess.exe" %*
if errorlevel 1 pause
