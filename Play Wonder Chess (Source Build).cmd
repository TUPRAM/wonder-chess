@echo off
rem Runs the current source build of the solo game, including imported hero models. Needs Unreal Engine 5.8.
start "" "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "%~dp0game\WonderChess.uproject" -game -WCSolo -WCStorybook -WCProfileName=wonder_vnext -windowed -ResX=1600 -ResY=900 -nosplash -WCSavePath="%~dp0support\runtime\source-build\preparation.wcsave"
