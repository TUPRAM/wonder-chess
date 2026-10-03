param(
    [ValidateRange(1,50)][int]$Tournaments = 25,
    [ValidateRange(1,10000)][int]$FirstSeed = 7001,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
if ($FirstSeed + $Tournaments - 1 -gt 10000) { throw 'Development seed interval must end at or before 10000; reserved confirmation seeds are excluded.' }
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runRoot = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $runRoot) { throw 'Use a fresh output directory to preserve every candidate and failure.' }
$python = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Verified project Python virtual environment unavailable.' }
& $python (Join-Path $projectRoot 'tools/vnext/catalog.py') --check --stage
if ($LASTEXITCODE -ne 0) { throw 'Canonical/generated/staged successor parity failed.' }
$vswhere = 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$compilerRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $compilerRoot) { throw 'Installed MSVC x64 compiler unavailable.' }
$vcvars = Join-Path $compilerRoot 'VC/Auxiliary/Build/vcvars64.bat'
$publicRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$privateRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation'
$sources = @('WonderSimulation.cpp','WonderTournament.cpp','WonderSave.cpp') | ForEach-Object { Join-Path $privateRoot $_ }
$sources += Join-Path $PSScriptRoot 'development_20260930_diagnostics.cpp'
$inputs = $sources + @((Join-Path $publicRoot 'Simulation/WonderSimulation.h'),(Join-Path $publicRoot 'VNext/WonderVNextCatalog.generated.h'),(Join-Path $projectRoot 'data/vnext/catalog.json'))
New-Item -ItemType Directory -Path $runRoot | Out-Null
$executable = Join-Path $runRoot 'current_candidate_diagnostics.exe'
$compilerScript = Join-Path $runRoot 'compile.cmd'
$quotedSources = ($sources | ForEach-Object { '"' + $_ + '"' }) -join ' '
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$publicRoot" $quotedSources /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $compilerScript -Encoding ascii
$record = [ordered]@{started_utc=[DateTime]::UtcNow.ToString('o');requested_tournaments=$Tournaments;first_seed=$FirstSeed;
    compile_exit=$null;test_exit=$null;source_stable=$null;source_hashes=[ordered]@{};
    command="current_candidate_diagnostics.exe $Tournaments $FirstSeed";
    boundary='Unmodified current canonical seven-hero native tournaments plus isolated skill-off formation fixtures; no human pacing, balance promotion, Unreal package, art or release acceptance'}
foreach ($input in $inputs) { $record.source_hashes[$input] = (Get-FileHash -LiteralPath $input -Algorithm SHA256).Hash.ToLowerInvariant() }
Push-Location $runRoot
try {
    & cmd /c $compilerScript 2>&1 | Tee-Object -FilePath compile.log
    $record.compile_exit = $LASTEXITCODE
    if ($record.compile_exit -ne 0) { throw 'Current-candidate diagnostic compilation failed.' }
    $record.executable_sha256 = (Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
    & $executable $Tournaments $FirstSeed 2>&1 | Tee-Object -FilePath tests.log
    $record.test_exit = $LASTEXITCODE
    if ($record.test_exit -ne 0) { throw 'Current-candidate diagnostic execution failed.' }
} finally {
    $record.ended_utc = [DateTime]::UtcNow.ToString('o')
    $record.source_stable = $true
    foreach ($input in $inputs) { if ((Get-FileHash -LiteralPath $input -Algorithm SHA256).Hash.ToLowerInvariant() -ne $record.source_hashes[$input]) { $record.source_stable = $false } }
    $record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath process.json -Encoding utf8
    Pop-Location
}
if (-not $record.source_stable) { throw 'Source changed during execution; recorded run cannot certify the current candidate.' }
& $python (Join-Path $PSScriptRoot 'development_20260930_diagnostics.py') $runRoot --output (Join-Path $runRoot 'readout.json')
if ($LASTEXITCODE -ne 0) { throw 'Diagnostic evidence reconciliation failed.' }
Write-Output $runRoot
