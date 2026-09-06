$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$reportRoot = Join-Path $projectRoot 'reports/WC-310/runtime/trait-native'
$outputRoot = Join-Path $reportRoot 'build'
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null
& python (Join-Path $PSScriptRoot 'generate_catalog_fixture.py')
if ($LASTEXITCODE -ne 0) { throw 'Canonical fixture generation failed' }
$vswhere = 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$vsRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vsRoot) { throw 'MSVC x64 compiler not installed' }
$vcvars = Join-Path $vsRoot 'VC/Auxiliary/Build/vcvars64.bat'
$includeRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$fixtureRoot = Join-Path $PSScriptRoot 'build'
$combat = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp'
$testSource = Join-Path $PSScriptRoot 'trait_combat_tests.cpp'
$executable = Join-Path $outputRoot 'trait_combat_tests.exe'
$buildScript = Join-Path $outputRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$includeRoot" /I"$fixtureRoot" "$combat" "$testSource" /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $buildScript -Encoding ascii
$started = [DateTime]::UtcNow.ToString('o')
Push-Location $outputRoot
try {
    & cmd /c $buildScript 2>&1 | Tee-Object -FilePath 'compile.log'
    $compileCode = $LASTEXITCODE
    if ($compileCode -ne 0) { throw "MSVC compilation failed: $compileCode" }
    & $executable 2>&1 | Tee-Object -FilePath 'run.log'
    $runCode = $LASTEXITCODE
    [ordered]@{ started_utc=$started; ended_utc=[DateTime]::UtcNow.ToString('o'); compile_exit=$compileCode; process_exit=$runCode; executable=$executable; executable_sha256=(Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant(); source_sha256=(Get-FileHash -LiteralPath $testSource -Algorithm SHA256).Hash.ToLowerInvariant(); core_sha256=(Get-FileHash -LiteralPath $combat -Algorithm SHA256).Hash.ToLowerInvariant() } | ConvertTo-Json | Set-Content -LiteralPath 'process.json' -Encoding utf8
    if ($runCode -ne 0) { throw "Trait tests failed: $runCode" }
} finally { Pop-Location }

