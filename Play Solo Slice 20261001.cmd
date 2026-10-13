@echo off
powershell.exe -NoProfile -File "%~dp0support\tools\parallel_slice_20261001\play_solo_slice.ps1"
if errorlevel 1 pause
