@echo off
rem Saves a picture of the Auto Chess window every 2 seconds while it is in front, for up to 40 minutes.
rem Pictures go to support\runs\reference-play. Close this window to stop.
"%~dp0.venv\Scripts\python.exe" "%~dp0tools\production\record_reference_play.py" --title "ACPhoenix" --every 2 --minutes 40
pause
