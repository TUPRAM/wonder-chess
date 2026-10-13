@echo off
set "WC_SILK_ROOT=%~dp0"
set "WC_SILK_EDITOR=C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
if not exist "%WC_SILK_EDITOR%" (
  echo Open game\WonderChess.uproject in Unreal, then see the Silkmother delivery document for rig paths.
  pause
  exit /b 1
)
start "" "%WC_SILK_EDITOR%" "%WC_SILK_ROOT%game\WonderChess.uproject" -ExecutePythonScript="%WC_SILK_ROOT%art-source\asset-studio\wc_vn_silkmother\stages\production_r001\recipes\open_rig.py" -nosplash
