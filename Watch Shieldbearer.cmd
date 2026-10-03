@echo off
rem Opens the source build in the test arena and cycles the Shieldbearer through idle, walk, attack, block, hit and defeat.
rem Screenshots of the first pass are saved under support\runtime\hero-review. Needs Unreal Engine 5.8.
start "" "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "%~dp0game\WonderChess.uproject" -game -WCLab -WCHeroReview -WCProfileName=wonder_vnext -windowed -ResX=1600 -ResY=900 -nosplash -WCEvidenceDir="%~dp0support\runtime\hero-review"
