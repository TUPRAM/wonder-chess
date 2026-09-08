@call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
@if errorlevel 1 exit /b 1
@where cl > compiler-location.txt
cl /nologo /Bv /std:c++20 /EHsc /O2 /W4 /I"C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260906T143320Z\equal-investment-counters\source" /I"C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260906T143320Z\equal-investment-counters" "C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260906T143320Z\equal-investment-counters\source/WonderSimulation.cpp" "C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260906T143320Z\equal-investment-counters\source/measure_update_counters.cpp" /Fe:"C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260906T143320Z\equal-investment-counters\measure_update_counters.exe"
@exit /b %errorlevel%
