param([int]$Seeds = 1)
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runRoot=Join-Path $projectRoot ('reports/vnext/timeout-probe/'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
$compilerRoot=& 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $compilerRoot){throw 'MSVC unavailable'}
$vcvars=Join-Path $compilerRoot 'VC/Auxiliary/Build/vcvars64.bat'
$includeRoot=Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$privateRoot=Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation'
$sources=@('WonderSimulation.cpp','WonderTournament.cpp','WonderSave.cpp') | ForEach-Object{Join-Path $privateRoot $_}
$sources+=Join-Path $PSScriptRoot 'vnext_timeout_probe.cpp'
$quotedSources=($sources | ForEach-Object{'"'+$_+'"'}) -join ' '
$executable=Join-Path $runRoot 'timeout_probe.exe'
$script=Join-Path $runRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$includeRoot" $quotedSources /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $script -Encoding ascii
$record=[ordered]@{started_utc=[DateTime]::UtcNow.ToString('o');compile_exit=$null;test_exit=$null;source_hashes=[ordered]@{};boundary='Read-only canonical source; isolated native causal probe fixtures are not adopted balance tuning'}
foreach($source in $sources+@((Join-Path $includeRoot 'Simulation/WonderSimulation.h'),(Join-Path $includeRoot 'VNext/WonderVNextCatalog.generated.h'))){$record.source_hashes[$source]=(Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant()}
Push-Location $runRoot
try{
    & cmd /c $script 2>&1 | Tee-Object -FilePath compile.log
    $record.compile_exit=$LASTEXITCODE
    if($record.compile_exit -ne 0){throw 'Probe compile failed'}
    & $executable $Seeds 2>&1 | Tee-Object -FilePath tests.log
    $record.test_exit=$LASTEXITCODE
    if($record.test_exit -ne 0){throw 'Probe failed'}
}finally{
    $record.ended_utc=[DateTime]::UtcNow.ToString('o')
    $record|ConvertTo-Json -Depth 5|Set-Content -LiteralPath process.json -Encoding utf8
    Pop-Location
}
