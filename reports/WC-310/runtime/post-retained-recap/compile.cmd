@call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"C:\Users\iputu\Documents\Wonder Chess\game\Source\WonderChessRuntime\Public" /I"C:\Users\iputu\Documents\Wonder Chess\tests\runtime\build" "C:\Users\iputu\Documents\Wonder Chess\game\Source\WonderChessRuntime\Private\Simulation\WonderSimulation.cpp" "C:\Users\iputu\Documents\Wonder Chess\game\Source\WonderChessRuntime\Private\Simulation\WonderTournament.cpp" "C:\Users\iputu\Documents\Wonder Chess\tests\runtime\runtime_tests.cpp" /Fe:"C:\Users\iputu\Documents\Wonder Chess\tests\runtime\build\wonder_runtime_tests.exe"
@exit /b %errorlevel%
