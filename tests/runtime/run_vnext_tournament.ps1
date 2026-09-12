param([ValidateRange(1,10000)][int]$Tournaments = 10, [string]$OutputDirectory = '', [ValidateRange(1,10000)][int]$FirstSeed = 1)
$ErrorActionPreference = 'Stop'
if ($FirstSeed + $Tournaments - 1 -gt 10000) { throw 'The final seed must not exceed 10000.' }
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runRoot = if ($OutputDirectory) { [IO.Path]::GetFullPath($OutputDirectory) } else {
    Join-Path $projectRoot ('reports/vnext/native/' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
}
if (Test-Path -LiteralPath $runRoot) { throw 'Use a fresh output directory to preserve previous evidence.' }
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
& python (Join-Path $projectRoot 'tools/vnext/catalog.py') --check --stage
if ($LASTEXITCODE -ne 0) { throw 'Successor generated/staged parity failed.' }
$vswhere = 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$compilerRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $compilerRoot) { throw 'MSVC x64 toolchain unavailable.' }
$vcvars = Join-Path $compilerRoot 'VC/Auxiliary/Build/vcvars64.bat'
$publicRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$privateRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation'
$sources = @('WonderSimulation.cpp', 'WonderTournament.cpp', 'WonderSave.cpp') | ForEach-Object { Join-Path $privateRoot $_ }
$sources += Join-Path $PSScriptRoot 'vnext_tournament_tests.cpp'
$identityFiles = $sources + @((Join-Path $publicRoot 'Simulation/WonderSimulation.h'), (Join-Path $publicRoot 'VNext/WonderVNextCatalog.generated.h'))
if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'vnext_bot_tests.h')) { $identityFiles += Join-Path $PSScriptRoot 'vnext_bot_tests.h' }
$inputHashes = [ordered]@{}
foreach ($source in $identityFiles) { $inputHashes[$source] = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() }
$quotedSources = ($sources | ForEach-Object { '"' + $_ + '"' }) -join ' '
$executable = Join-Path $runRoot 'wonder_vnext_tournaments.exe'
$compilerScript = Join-Path $runRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$publicRoot" $quotedSources /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $compilerScript -Encoding ascii
$started = [DateTime]::UtcNow.ToString('o')
Push-Location $runRoot
try {
    & cmd /c $compilerScript 2>&1 | Tee-Object -FilePath 'compile.log'
    $compileExit = $LASTEXITCODE
    if ($compileExit -ne 0) { throw "Native compilation failed: $compileExit" }
    & $executable $Tournaments $FirstSeed 2>&1 | Tee-Object -FilePath 'tests.log'
    $testExit = $LASTEXITCODE
    $hashes = [ordered]@{}
    foreach ($source in $identityFiles) {
        $hashes[$source] = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $sourceStable = @($identityFiles | Where-Object { $hashes[$_] -ne $inputHashes[$_] }).Count -eq 0
    [ordered]@{ started_utc=$started; ended_utc=[DateTime]::UtcNow.ToString('o'); compile_exit=$compileExit;
        process_exit=$testExit; requested_tournaments=$Tournaments; first_seed=$FirstSeed; source_hashes=$inputHashes; source_stable=$sourceStable;
        executable_sha256=(Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath 'process.json' -Encoding utf8
    if ($testExit -ne 0) { throw "Native successor tests failed: $testExit" }
    if (-not $sourceStable) { throw 'Source changed during execution; this run cannot certify the final candidate.' }
} finally { Pop-Location }
