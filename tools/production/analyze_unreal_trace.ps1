param(
    [Parameter(Mandatory=$true)][string]$Trace,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)
$ErrorActionPreference = 'Stop'
$tracePath = (Resolve-Path -LiteralPath $Trace).Path.Replace('\', '/')
$outputPath = [IO.Path]::GetFullPath($OutputDirectory).Replace('\', '/')
if (Test-Path -LiteralPath $outputPath) { throw 'Choose a new analysis directory to preserve existing evidence.' }
New-Item -ItemType Directory -Path $outputPath | Out-Null
$csvPath = "$outputPath/timers.csv"
$commandsPath = "$outputPath/commands.txt"
$logPath = "$outputPath/insights.log"
Set-Content -LiteralPath $commandsPath -Value ('TimingInsights.ExportTimers "' + $csvPath + '"') -Encoding utf8NoBOM
$arguments = '-OpenTraceFile="' + $tracePath + '" -AutoQuit -NoUI -ExecOnAnalysisCompleteCmd="@=' + $commandsPath + '" -ABSLOG="' + $logPath + '"'
$exePath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealInsights.exe'
$analysisProcess = Start-Process -FilePath $exePath -ArgumentList $arguments -WindowStyle Hidden -PassThru
if (-not $analysisProcess.WaitForExit(60000)) {
    throw "Analysis is still running (PID $($analysisProcess.Id)); inspect before retrying."
}
if (-not (Test-Path -LiteralPath $csvPath)) { throw "No timer export; inspect $logPath" }
$rows = @(Import-Csv -LiteralPath $csvPath)
if ($rows.Count -eq 0) { throw 'Timer export contains no rows.' }
$errorLines = @(Select-String -LiteralPath $logPath -Pattern '\bError:')
$result = [ordered]@{
    status = $(if ($errorLines.Count) { 'exported_with_analysis_errors' } else { 'pass' })
    trace = $tracePath
    csv = $csvPath
    timer_rows = $rows.Count
    log_error_count = $errorLines.Count
    scope = 'Trace analysis and timer export only; not performance acceptance'
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$outputPath/result.json" -Encoding utf8NoBOM
$result | ConvertTo-Json -Depth 5
if ($errorLines.Count) { throw 'Inspect trace-analysis errors; export alone does not qualify every channel.' }
