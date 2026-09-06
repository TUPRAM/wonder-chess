param([int]$Tournaments = 1)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$buildRoot = Join-Path $PSScriptRoot 'build'
& python (Join-Path $PSScriptRoot 'generate_catalog_fixture.py')
if ($LASTEXITCODE -ne 0) { throw 'Canonical fixture generation failed' }
$vswhere = 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$vsRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vsRoot) { throw 'MSVC x64 compiler not installed' }
$vcvars = Join-Path $vsRoot 'VC/Auxiliary/Build/vcvars64.bat'
$includeRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$combat = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp'
$tournament = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderTournament.cpp'
if (-not (Test-Path -LiteralPath $tournament)) { $tournament = Join-Path $PSScriptRoot 'WonderTournament.pending.cpp' }
$testSource = Join-Path $PSScriptRoot 'runtime_tests.cpp'
$executable = Join-Path $buildRoot 'wonder_runtime_tests.exe'
$buildScript = Join-Path $buildRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$includeRoot" /I"$buildRoot" "$combat" "$tournament" "$testSource" /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $buildScript -Encoding ascii
Push-Location $buildRoot
try {
    & cmd /c $buildScript 2>&1 | Tee-Object -FilePath 'compile.log'
    if ($LASTEXITCODE -ne 0) { throw "MSVC compilation failed: $LASTEXITCODE" }
    & $executable $Tournaments 2>&1 | Tee-Object -FilePath 'runtime-tests.log'
    if ($LASTEXITCODE -ne 0) { throw "Runtime tests failed: $LASTEXITCODE" }
} finally { Pop-Location }
