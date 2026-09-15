param(
    [ValidateSet('control','root75','mana100','mana20','targeting','clarity')][string]$Variant = 'control',
    [ValidateRange(0,1000)][int]$Seeds = 10,
    [ValidateRange(1,1000000)][int]$FirstSeed = 1,
    [string]$RunLabel = 'diagnostic',
    [switch]$Diagnostics
)
$ErrorActionPreference = 'Stop'
if($RunLabel -notmatch '^[a-z0-9-]+$'){throw 'RunLabel must contain lowercase letters, numbers and hyphens'}
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runRoot = Join-Path $projectRoot ('reports/vnext/milestones/b1-balance/'+$RunLabel+'-'+$Variant+'-'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
$compilerRoot = & 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $compilerRoot){throw 'MSVC unavailable'}
$vcvars = Join-Path $compilerRoot 'VC/Auxiliary/Build/vcvars64.bat'
$includeRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$privateRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation'
$sources = @('WonderSimulation.cpp','WonderTournament.cpp','WonderSave.cpp') | ForEach-Object {Join-Path $privateRoot $_}
$sources += Join-Path $PSScriptRoot 'vnext_balance_experiment.cpp'
$inputs = $sources + @((Join-Path $includeRoot 'Simulation/WonderSimulation.h'),(Join-Path $includeRoot 'VNext/WonderVNextCatalog.generated.h'),(Join-Path $projectRoot 'data/vnext/catalog.json'))
$quotedSources = ($sources | ForEach-Object {'"'+$_+'"'}) -join ' '
$executable = Join-Path $runRoot 'balance_experiment.exe'
$script = Join-Path $runRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$includeRoot" $quotedSources /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $script -Encoding ascii
$record = [ordered]@{started_utc=[DateTime]::UtcNow.ToString('o');variant=$Variant;requested_tournaments=$Seeds;first_seed=$FirstSeed;compile_exit=$null;test_exit=$null;source_hashes=[ordered]@{};source_stable=$null;boundary='Native in-memory experiment; no canonical balance promotion or human acceptance'}
foreach($source in $inputs){$record.source_hashes[$source]=(Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant()}
$record.diagnostics = [bool]$Diagnostics
Push-Location $runRoot
try {
    & cmd /c $script 2>&1 | Tee-Object -FilePath compile.log
    $record.compile_exit = $LASTEXITCODE
    if($record.compile_exit -ne 0){throw 'Balance experiment compile failed'}
    $record.executable_sha256 = (Get-FileHash -LiteralPath $executable).Hash.ToLowerInvariant()
    $runArguments = @($Variant, $Seeds, $FirstSeed)
    if ($Diagnostics) { $runArguments += 'diagnostics' }
    & $executable @runArguments 2>&1 | Tee-Object -FilePath tests.log
    $record.test_exit = $LASTEXITCODE
    if($record.test_exit -ne 0){throw 'Balance experiment failed'}
} finally {
    $record.ended_utc = [DateTime]::UtcNow.ToString('o')
    $record.source_stable = $true
    foreach($source in $inputs){if((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $record.source_hashes[$source]){$record.source_stable=$false}}
    $record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath process.json -Encoding utf8
    Pop-Location
}
if(-not $record.source_stable){throw 'Sources changed during run; inspect recorded build hashes before using evidence'}
Write-Output $runRoot
