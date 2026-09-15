@call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /W4 /I"C:\Users\iputu\AppData\Local\CodexWorktrees\wc\m7\game\Source\WonderChessRuntime\Public" /I"C:\Users\iputu\AppData\Local\CodexWorktrees\wc\m7\data\vnext\generated" "C:\Users\iputu\AppData\Local\CodexWorktrees\wc\m7\game\Source\WonderChessRuntime\Private\Simulation\WonderSimulation.cpp" "C:\Users\iputu\AppData\Local\CodexWorktrees\wc\m7\tests\runtime\vnext_combat_tests.cpp" /Fe:"C:\Users\iputu\AppData\Local\CodexWorktrees\wc\m7\reports\vnext\milestones\mana-20260913\native-contract-r7\vnext_combat_tests.exe"
@exit /b %errorlevel%
