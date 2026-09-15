@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\iputu\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\CodexWorktrees\wc\m7\tools\unreal\launch_milestones.ps1" -Mode Lab -ArtSlice
if errorlevel 1 pause
