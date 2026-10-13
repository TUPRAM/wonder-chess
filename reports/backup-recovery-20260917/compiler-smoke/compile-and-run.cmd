@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64 10.0.22621.0 -vcvars_ver=14.44
if errorlevel 1 exit /b %errorlevel%
cd /d "C:\Users\USER\Documents\Wonder Chess\reports\backup-recovery-20260917\compiler-smoke"
cl /nologo /W4 /WX /EHsc /std:c++20 smoke.cpp /Fe:smoke.exe /link kernel32.lib
if errorlevel 1 exit /b %errorlevel%
smoke.exe
exit /b %errorlevel%
