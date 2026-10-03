@echo off
rem Opens a small window to store the Meshy API key, encrypted for this Windows user. No generation is submitted.
"%~dp0.venv\Scripts\pythonw.exe" "%~dp0tools\production\set_meshy_key.py"
