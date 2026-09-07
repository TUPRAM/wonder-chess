param([Parameter(Mandatory=$true)][string]$OutputDirectory,[Parameter(Mandatory=$true)][string]$BaselineDirectory)
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$outputRoot=[IO.Path]::GetFullPath($OutputDirectory)
$baselineRoot=[IO.Path]::GetFullPath($BaselineDirectory)
foreach($path in @($outputRoot,$baselineRoot)) {
    if(-not $path.StartsWith($projectRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Native window evidence must remain in this workspace' }
}
if(Test-Path -LiteralPath $outputRoot) { throw 'Use a fresh evidence directory' }
foreach($file in @('WonderSimulation.cpp','Simulation/WonderSimulation.h')) {
    if(-not(Test-Path -LiteralPath (Join-Path $baselineRoot $file) -PathType Leaf)) { throw 'Captured pre-change native source is required' }
}
New-Item -ItemType Directory -Path $outputRoot | Out-Null
$currentRoot=Join-Path $outputRoot 'current-source'
$comparisonRoot=Join-Path $outputRoot 'baseline-source'
foreach($folder in @($currentRoot,$comparisonRoot)) {
    New-Item -ItemType Directory -Path (Join-Path $folder 'Simulation') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $folder 'Presentation') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderTournament.cpp') -Destination (Join-Path $folder 'WonderTournament.cpp')
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'runtime_tests.cpp') -Destination (Join-Path $folder 'runtime_tests.cpp')
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'update_contract_tests.h') -Destination (Join-Path $folder 'update_contract_tests.h')
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp') -Destination (Join-Path $currentRoot 'WonderSimulation.cpp')
Copy-Item -LiteralPath (Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h') -Destination (Join-Path $currentRoot 'Simulation/WonderSimulation.h')
Copy-Item -LiteralPath (Join-Path $projectRoot 'game/Source/WonderChessRuntime/Public/Presentation/WCAttackWindow.h') -Destination (Join-Path $currentRoot 'Presentation/WCAttackWindow.h')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'attack_window_tests.cpp') -Destination (Join-Path $currentRoot 'attack_window_tests.cpp')
Copy-Item -LiteralPath (Join-Path $baselineRoot 'WonderSimulation.cpp') -Destination (Join-Path $comparisonRoot 'WonderSimulation.cpp')
Copy-Item -LiteralPath (Join-Path $baselineRoot 'Simulation/WonderSimulation.h') -Destination (Join-Path $comparisonRoot 'Simulation/WonderSimulation.h')
& python (Join-Path $PSScriptRoot 'generate_catalog_fixture.py') --output-dir $outputRoot
if($LASTEXITCODE -ne 0) { throw 'Fixture generation failed' }
$vswhere='C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
$vsRoot=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $vsRoot) { throw 'MSVC compiler unavailable' }
$vcvars=Join-Path $vsRoot 'VC/Auxiliary/Build/vcvars64.bat'
$script=Join-Path $outputRoot 'compile.cmd'
@"
@call "$vcvars"
@if errorlevel 1 exit /b 1
@where cl > compiler-location.txt
cl /nologo /Bv /std:c++20 /EHsc /O2 /W4 /I"$currentRoot" /I"$outputRoot" "$currentRoot/WonderSimulation.cpp" "$currentRoot/attack_window_tests.cpp" /Fe:"$outputRoot/attack_windows.exe"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$currentRoot" /I"$outputRoot" "$currentRoot/WonderSimulation.cpp" "$currentRoot/WonderTournament.cpp" "$currentRoot/runtime_tests.cpp" /Fe:"$outputRoot/current.exe"
@if errorlevel 1 exit /b 1
cl /nologo /std:c++20 /EHsc /O2 /fp:fast /W4 /I"$comparisonRoot" /I"$outputRoot" "$comparisonRoot/WonderSimulation.cpp" "$comparisonRoot/WonderTournament.cpp" "$comparisonRoot/runtime_tests.cpp" /Fe:"$outputRoot/baseline.exe"
@exit /b %errorlevel%
"@ | Set-Content -LiteralPath $script -Encoding ascii
$record=[ordered]@{status='STARTED';started_utc=[DateTime]::UtcNow.ToString('o');boundary='Actual native CPU combat and presentation-time helpers; no Unreal viewport, cooked asset or performance acceptance';compile_exit=$null;focused_exit=$null;baseline_exit=$null;current_exit=$null;failure=$null;input_files=@{}}
foreach($file in Get-ChildItem -LiteralPath $currentRoot,$comparisonRoot -File -Recurse) { $record.input_files[$file.FullName]=(Get-FileHash -LiteralPath $file.FullName).Hash.ToLowerInvariant() }
$record.input_files[(Join-Path $outputRoot 'CatalogFixture.h')]=(Get-FileHash -LiteralPath (Join-Path $outputRoot 'CatalogFixture.h')).Hash.ToLowerInvariant()
$record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $outputRoot 'process.json') -Encoding utf8
Push-Location $outputRoot
try {
    & cmd /c $script 2>&1 | Tee-Object -FilePath compile.log
    $record.compile_exit=$LASTEXITCODE
    if($record.compile_exit -ne 0) { throw 'Native window/equivalence compilation failed' }
    & (Join-Path $outputRoot 'attack_windows.exe') 2>&1 | Tee-Object -FilePath focused.log
    $record.focused_exit=$LASTEXITCODE
    if($record.focused_exit -ne 0) { throw 'Focused native window tests failed' }
    foreach($variant in @('baseline','current')) {
        $run=Join-Path $outputRoot $variant
        New-Item -ItemType Directory -Path $run|Out-Null
        Push-Location $run
        try { & (Join-Path $outputRoot ($variant+'.exe')) 100 2>&1 | Tee-Object -FilePath run.log; $record[$variant+'_exit']=$LASTEXITCODE }
        finally { Pop-Location }
        if($record[$variant+'_exit'] -ne 0) { throw ($variant+' actual-combat regression failed') }
    }
    & python (Join-Path $PSScriptRoot 'compare_attack_window_combat.py') $outputRoot
    if($LASTEXITCODE -ne 0) { throw 'Before/after actual-combat outputs differ' }
    $record.status='PASS_NATIVE_EXECUTION_AND_EQUIVALENCE_ONLY'
} catch { $record.status='FAIL'; $record.failure=$_.Exception.Message }
finally {
    $record.ended_utc=[DateTime]::UtcNow.ToString('o')
    $record.cpu=(Get-CimInstance Win32_Processor|Select-Object -ExpandProperty Name)
    $record.compiler=if(Test-Path -LiteralPath compiler-location.txt){Get-Content compiler-location.txt|Select-Object -First 1}else{$null}
    $record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath process.json -Encoding utf8
    Pop-Location
}
if($record.status -eq 'FAIL') { throw $record.failure }
