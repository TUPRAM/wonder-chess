param(
    [Parameter(Mandatory=$true)][ValidateSet('baseline','cocoon_reservation')][string]$Variant,
    [ValidateRange(1,50)][int]$Tournaments=25,
    [ValidateRange(1,10000)][int]$FirstSeed=7001,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if($FirstSeed+$Tournaments-1 -gt 10000){throw 'Development interval excludes reserved confirmation seeds.'}
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runRoot=[IO.Path]::GetFullPath($OutputDirectory)
if(Test-Path -LiteralPath $runRoot){throw 'Use a fresh evidence directory.'}
$python=Join-Path $projectRoot '.venv/Scripts/python.exe'
if(-not(Test-Path -LiteralPath $python)){throw 'Verified project Python unavailable.'}
& $python (Join-Path $PSScriptRoot 'catalog.py') --check --stage
if($LASTEXITCODE -ne 0){throw 'Canonical/generated/staged parity failed.'}
& $python (Join-Path $PSScriptRoot 'development_20260930_reservation.py') prepare $runRoot --variant $Variant
if($LASTEXITCODE -ne 0){throw 'Isolated experiment source preparation failed.'}
$compilerRoot=& 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $compilerRoot){throw 'Installed MSVC unavailable.'}
$vcvars=Join-Path $compilerRoot 'VC/Auxiliary/Build/vcvars64.bat'
$publicRoot=Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$privateRoot=Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation'
$sources=@((Join-Path $runRoot 'source/WonderSimulation.cpp'),(Join-Path $privateRoot 'WonderTournament.cpp'),(Join-Path $privateRoot 'WonderSave.cpp'),(Join-Path $runRoot 'source/diagnostics.cpp'))
$inputs=$sources+@((Join-Path $privateRoot 'WonderSimulation.cpp'),(Join-Path $publicRoot 'Simulation/WonderSimulation.h'),
    (Join-Path $publicRoot 'VNext/WonderVNextCatalog.generated.h'),(Join-Path $projectRoot 'data/vnext/catalog.json'),
    (Join-Path $PSScriptRoot 'development_20260930_cocoon_observer.h'),(Join-Path $projectRoot 'tests/runtime/vnext_combat_tests.cpp'),
    (Join-Path $privateRoot 'WonderManaTests.h'),(Join-Path $privateRoot 'WonderCombatClarityTests.h'))
$executable=Join-Path $runRoot 'isolated_cocoon_study.exe'
$compile=Join-Path $runRoot 'compile.cmd'
$quotedSources=($sources|ForEach-Object{ '"'+$_+'"' }) -join ' '
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$publicRoot" $quotedSources /Fe:"$executable"
@exit /b %errorlevel%
"@|Set-Content -LiteralPath $compile -Encoding ascii
$record=[ordered]@{started_utc=[DateTime]::UtcNow.ToString('o');variant=$Variant;requested_tournaments=$Tournaments;first_seed=$FirstSeed;
    compile_exit=$null;test_exit=$null;source_stable=$null;source_hashes=[ordered]@{};
    command="isolated_cocoon_study.exe $Tournaments $FirstSeed";
    boundary='Isolated output-directory compilation; canonical source untouched; development bot/fixture evidence only; no human pacing or balance promotion'}
foreach($input in $inputs){$record.source_hashes[$input]=(Get-FileHash -LiteralPath $input -Algorithm SHA256).Hash.ToLowerInvariant()}
Push-Location $runRoot
try{
    & cmd /c $compile 2>&1|Tee-Object -FilePath compile.log
    $record.compile_exit=$LASTEXITCODE
    if($record.compile_exit -ne 0){throw 'Isolated cocoon study compile failed.'}
    $record.executable_sha256=(Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
    & $executable $Tournaments $FirstSeed 2>&1|Tee-Object -FilePath tests.log
    $record.test_exit=$LASTEXITCODE
    if($record.test_exit -ne 0){throw 'Isolated cocoon study contracts/execution failed.'}
}finally{
    $record.ended_utc=[DateTime]::UtcNow.ToString('o');$record.source_stable=$true
    foreach($input in $inputs){if((Get-FileHash -LiteralPath $input -Algorithm SHA256).Hash.ToLowerInvariant() -ne $record.source_hashes[$input]){$record.source_stable=$false}}
    $record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath process.json -Encoding utf8
    Pop-Location
}
if(-not $record.source_stable){throw 'Inputs changed during run; experiment cannot certify this candidate.'}
& $python (Join-Path $PSScriptRoot 'development_20260930_diagnostics.py') $runRoot --output (Join-Path $runRoot 'readout.json')
if($LASTEXITCODE -ne 0){throw 'Isolated evidence reconciliation failed.'}
Write-Output $runRoot
