@call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"C:\Users\iputu\Documents\Wonder Chess\game\Source\WonderChessRuntime\Public" "C:\Users\iputu\Documents\Wonder Chess\game\Source\WonderChessRuntime\Private\Simulation\WonderSimulation.cpp" "C:\Users\iputu\Documents\Wonder Chess\game\Source\WonderChessRuntime\Private\Simulation\WonderTournament.cpp" "C:\Users\iputu\Documents\Wonder Chess\game\Source\WonderChessRuntime\Private\Simulation\WonderSave.cpp" "C:\Users\iputu\Documents\Wonder Chess\tests\runtime\vnext_timeout_probe.cpp" /Fe:"C:\Users\iputu\Documents\Wonder Chess\reports\vnext\timeout-probe\20260910T153323985Z\timeout_probe.exe"
@exit /b %errorlevel%
