param(
    [Parameter(Mandatory=$true)][string]$Contract,
    [Parameter(Mandatory=$true)][string]$Output,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [string]$TraceFile,
    [string]$TraceChannels = 'cpu,frame,bookmark'
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$contractPath = (Resolve-Path -LiteralPath $Contract).Path
$outputPath = [IO.Path]::GetFullPath($Output)
$contractData = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
if (-not $contractData.contracts -or @($contractData.contracts.PSObject.Properties).Count -eq 0) {
    throw 'Supply actual contracts. An unfilled template is not a valid batch.'
}
if (Test-Path -LiteralPath $outputPath) { throw 'Choose a new evidence output path; existing evidence is preserved.' }
$parentDir = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $parentDir | Out-Null
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (-not (Test-Path -LiteralPath $editorPath)) { throw "Unreal commandlet not found: $editorPath" }
$oldContract = $env:WC_ASSET_CONTRACT_FILE
$oldOutput = $env:WC_ASSET_VALIDATION_OUTPUT
try {
    $env:WC_ASSET_CONTRACT_FILE = $contractPath
    $env:WC_ASSET_VALIDATION_OUTPUT = $outputPath
    $projectPath = (Join-Path $repoRoot 'game\WonderChess.uproject').Replace('\', '/')
    $scriptPath = (Join-Path $repoRoot 'tools\production\unreal_validate_contracts.py').Replace('\', '/')
    $logPath = "$outputPath.log".Replace('\', '/')
    $traceArgs = @()
    if ($TraceFile) {
        $tracePath = [IO.Path]::GetFullPath($TraceFile).Replace('\', '/')
        if (Test-Path -LiteralPath $tracePath) { throw 'Choose a new trace file.' }
        $traceArgs = @("-trace=$TraceChannels", "-tracefile=$tracePath", '-notraceserver')
    }
    & $editorPath $projectPath '-run=pythonscript' "-script=$scriptPath" '-unattended' '-nop4' '-nosplash' '-nullrhi' "-abslog=$logPath" @traceArgs *> "$outputPath.console.log"
    $editorExit = $LASTEXITCODE
    if ($editorExit -ne 0) { throw "Unreal returned $editorExit; inspect $outputPath.console.log" }
    if (-not (Test-Path -LiteralPath $outputPath)) { throw 'Unreal produced no validation result.' }
    $result = Get-Content -LiteralPath $outputPath -Raw | ConvertFrom-Json
    if ($result.status -ne 'pass') { throw "Asset checks failed: $outputPath" }
    Write-Output "PASS: $outputPath"
} finally {
    $env:WC_ASSET_CONTRACT_FILE = $oldContract
    $env:WC_ASSET_VALIDATION_OUTPUT = $oldOutput
}
