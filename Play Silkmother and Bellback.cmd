@echo off
set "WC_SILK_ROOT=%~dp0"
if not exist "%WC_SILK_ROOT%builds\WonderChess-Silkmother-r2\Windows\WonderChess.exe" (
  echo The Silkmother candidate package is not available. See its production report.
  pause
  exit /b 1
)
start "" "%WC_SILK_ROOT%builds\WonderChess-Silkmother-r2\Windows\WonderChess.exe" -WCSolo -WCProfileName=wonder_vnext -WCStorybook -WCCombatClarityExperiment -WCSilkmotherCandidate -windowed -ForceRes -ResX=1600 -ResY=1000 -nosplash -WCSavePath="%WC_SILK_ROOT%support\saves\silkmother-candidate\solo.json"
