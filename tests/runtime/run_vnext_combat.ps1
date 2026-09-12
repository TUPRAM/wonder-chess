param([string]$OutputDirectory = "")
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$buildRoot = if ($OutputDirectory) { [IO.Path]::GetFullPath($OutputDirectory) } else { Join-Path $projectRoot 'reports/vnext/native-combat' }
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
& python (Join-Path $projectRoot 'tools/vnext/catalog.py') --check
if ($LASTEXITCODE -ne 0) { throw 'Canonical vNext generation parity failed' }
$vswhere = 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$vsRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vsRoot) { throw 'MSVC x64 compiler unavailable' }
$vcvars = Join-Path $vsRoot 'VC/Auxiliary/Build/vcvars64.bat'
$includeRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$generated = Join-Path $projectRoot 'data/vnext/generated'
$combat = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp'
$testSource = Join-Path $PSScriptRoot 'vnext_combat_tests.cpp'
$executable = Join-Path $buildRoot 'vnext_combat_tests.exe'
$script = Join-Path $buildRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /W4 /I"$includeRoot" /I"$generated" "$combat" "$testSource" /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $script -Encoding ascii
$record = [ordered]@{ started_utc=[DateTime]::UtcNow.ToString('o'); compile_exit=$null; test_exit=$null; boundary='Native deterministic synthetic combat, not Unreal or human acceptance'; source_hashes=[ordered]@{} }
foreach ($source in @($combat,$testSource,(Join-Path $includeRoot 'Simulation/WonderSimulation.h'),(Join-Path $generated 'WonderVNextCatalog.h'))) {
    $record.source_hashes[$source]=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
}
Push-Location $buildRoot
try {
    & cmd /c $script 2>&1 | Tee-Object -FilePath 'compile.log'
    $record.compile_exit=$LASTEXITCODE
    if ($record.compile_exit -ne 0) { throw 'Native combat compilation failed' }
    & $executable 2>&1 | Tee-Object -FilePath 'tests.log'
    $record.test_exit=$LASTEXITCODE
    $record.executable_sha256=(Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($record.test_exit -ne 0) { throw 'Native combat tests failed' }
} finally {
    $record.ended_utc=[DateTime]::UtcNow.ToString('o')
    $record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath 'process.json' -Encoding utf8
    Pop-Location
}
