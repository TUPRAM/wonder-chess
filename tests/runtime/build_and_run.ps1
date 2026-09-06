param([int]$Tournaments = 1, [string]$OutputDirectory = "")
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$buildRoot = if ($OutputDirectory) { [IO.Path]::GetFullPath($OutputDirectory) } else { Join-Path $PSScriptRoot 'build' }
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
& python (Join-Path $PSScriptRoot 'generate_catalog_fixture.py') --output-dir $buildRoot
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
$started = [DateTime]::UtcNow.ToString('o')
Push-Location $buildRoot
try {
    & cmd /c $buildScript 2>&1 | Tee-Object -FilePath 'compile.log'
    $compileCode = $LASTEXITCODE
    if ($compileCode -ne 0) { throw "MSVC compilation failed: $compileCode" }
    & $executable $Tournaments 2>&1 | Tee-Object -FilePath 'runtime-tests.log'
    $runCode = $LASTEXITCODE
    $sourceHashes = [ordered]@{}
    foreach ($source in @($combat, $tournament, $testSource, (Join-Path $includeRoot 'Simulation/WonderSimulation.h'), (Join-Path $PSScriptRoot 'update_contract_tests.h'), (Join-Path $buildRoot 'CatalogFixture.h'))) {
        $sourceHashes[$source] = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    [ordered]@{ started_utc=$started; ended_utc=[DateTime]::UtcNow.ToString('o'); compile_exit=$compileCode; process_exit=$runCode; requested_tournaments=$Tournaments; executable=$executable; executable_sha256=(Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant(); source_hashes=$sourceHashes } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'process.json' -Encoding utf8
    if ($runCode -ne 0) { throw "Runtime tests failed: $runCode" }
} finally { Pop-Location }
