param([Parameter(Mandatory = $true)][string]$OutputDirectory)
# Builds and runs vnext_hero_power.cpp: each hero's measured strength, ability share and cast timing.
# Measurement only. Writes hero_power.csv and process.json into a fresh output directory.
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runRoot = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $runRoot) { throw 'Use a fresh output directory to preserve previous evidence.' }
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
& python (Join-Path $projectRoot 'tools/vnext/catalog.py') --check --stage
if ($LASTEXITCODE -ne 0) { throw 'Successor generated/staged parity failed.' }
$vswhere = 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$compilerRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $compilerRoot) { throw 'MSVC x64 toolchain unavailable.' }
$vcvars = Join-Path $compilerRoot 'VC/Auxiliary/Build/vcvars64.bat'
$publicRoot = Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public'
$sources = @((Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp'),
    (Join-Path $PSScriptRoot 'vnext_hero_power.cpp'))
$identityFiles = $sources + @((Join-Path $publicRoot 'Simulation/WonderSimulation.h'), (Join-Path $publicRoot 'VNext/WonderVNextCatalog.generated.h'))
$inputHashes = [ordered]@{}
foreach ($source in $identityFiles) { $inputHashes[$source] = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() }
$quotedSources = ($sources | ForEach-Object { '"' + $_ + '"' }) -join ' '
$executable = Join-Path $runRoot 'wonder_vnext_hero_power.exe'
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
    & $executable 2>&1 | Tee-Object -FilePath 'run.log'
    $runExit = $LASTEXITCODE
    [ordered]@{ started_utc=$started; ended_utc=[DateTime]::UtcNow.ToString('o'); compile_exit=$compileExit;
        process_exit=$runExit; source_hashes=$inputHashes;
        boundary='Synthetic five-against-five fights with traits off; not bot play, not human evidence, not balance acceptance'
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath 'process.json' -Encoding utf8
    if ($runExit -ne 0) { throw "Hero power measurement failed: $runExit" }
} finally { Pop-Location }
