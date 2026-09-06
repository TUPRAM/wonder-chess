param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$reportRoot = [IO.Path]::GetFullPath($OutputDirectory)
if (-not $reportRoot.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Counter evidence must stay inside this workspace' }
if (Test-Path -LiteralPath $reportRoot) { throw 'Use a fresh counter output directory; preserve existing evidence' }
$sourceRoot = Join-Path $reportRoot 'source'
New-Item -ItemType Directory -Path (Join-Path $sourceRoot 'Simulation') -Force | Out-Null
$inputs = @('tests/runtime/measure_update_counters.cpp','tests/runtime/generate_catalog_fixture.py','tests/runtime/run_update_counters.ps1','game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp','game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h','data/units.json','data/traits.json','data/rules.alpha.json','data/neutrals.json','data/bots.json')
$hashes = [ordered]@{}
foreach ($item in $inputs) { $hashes[$item] = (Get-FileHash -LiteralPath (Join-Path $projectRoot $item) -Algorithm SHA256).Hash.ToLowerInvariant() }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'measure_update_counters.cpp') -Destination (Join-Path $sourceRoot 'measure_update_counters.cpp')
Copy-Item -LiteralPath (Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp') -Destination (Join-Path $sourceRoot 'WonderSimulation.cpp')
Copy-Item -LiteralPath (Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h') -Destination (Join-Path $sourceRoot 'Simulation/WonderSimulation.h')
& python (Join-Path $PSScriptRoot 'generate_catalog_fixture.py') --output-dir $reportRoot
if ($LASTEXITCODE -ne 0) { throw 'Canonical fixture generation failed' }
$vswhere = 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$vsRoot = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vsRoot) { throw 'MSVC x64 compiler not installed' }
$vcvars = Join-Path $vsRoot 'VC/Auxiliary/Build/vcvars64.bat'
$executable = Join-Path $reportRoot 'measure_update_counters.exe'
$buildScript = Join-Path $reportRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
@where cl > compiler-location.txt
cl /nologo /Bv /std:c++20 /EHsc /O2 /W4 /I"$sourceRoot" /I"$reportRoot" "$sourceRoot/WonderSimulation.cpp" "$sourceRoot/measure_update_counters.cpp" /Fe:"$executable"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $buildScript -Encoding ascii
$started = [DateTime]::UtcNow.ToString('o')
$compileCode = $null
$runCode = $null
$failureText = $null
Push-Location $reportRoot
try {
    & cmd /c $buildScript 2>&1 | Tee-Object -FilePath 'compile.log'
    $compileCode = $LASTEXITCODE
    if ($compileCode -ne 0) { throw "MSVC compilation failed: $compileCode" }
    & $executable 2>&1 | Tee-Object -FilePath 'run.log'
    $runCode = $LASTEXITCODE
    if ($runCode -ne 0) { throw "Counter measurement failed: $runCode" }
} catch {
    $failureText = $_.Exception.Message
} finally {
    $changed = @()
    foreach ($item in $inputs) {
        if ((Get-FileHash -LiteralPath (Join-Path $projectRoot $item) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hashes[$item]) { $changed += $item }
    }
    $compilerPath = if (Test-Path -LiteralPath 'compiler-location.txt') { Get-Content -LiteralPath 'compiler-location.txt' | Select-Object -First 1 } else { $null }
    $outputs = [ordered]@{}
    foreach ($file in (Get-ChildItem -LiteralPath $reportRoot -File)) { $outputs[$file.Name] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
    [ordered]@{
        status = if ($null -eq $failureText -and $changed.Count -eq 0) { 'PASS_EXECUTION_ONLY' } else { 'FAIL' }
        started_utc = $started; ended_utc = [DateTime]::UtcNow.ToString('o'); compile_exit = $compileCode; process_exit = $runCode
        executable = $executable; failure = $failureText; input_sha256 = $hashes; inputs_changed_during_run = $changed; output_sha256 = $outputs
        compiler = $compilerPath; compiler_sha256 = if ($compilerPath) { (Get-FileHash -LiteralPath $compilerPath -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
        compiler_file_version = if ($compilerPath) { (Get-Item -LiteralPath $compilerPath).VersionInfo.FileVersion } else { $null }
        cpu = (Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name)
        memory_bytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
        render_device = 'none; native CPU simulation only'; gpu_frame_measurement = 'NOT_RUN'
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'process.json' -Encoding utf8
    Pop-Location
}
if ($failureText) { throw $failureText }
if ($changed.Count) { throw ('Counter input changed during run: ' + ($changed -join ', ')) }
