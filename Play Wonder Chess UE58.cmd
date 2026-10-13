@echo off
powershell -NoProfile -File "%~dp0tools\unreal\launch_milestones.ps1" -Mode Solo -Storybook -Executable "%~dp0builds\WonderChess-UE58-r1\Windows\WonderChess.exe" %*
if errorlevel 1 pause
