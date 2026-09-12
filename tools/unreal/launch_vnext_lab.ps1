[CmdletBinding()]
param(
    [string]$Executable = '',
    [ValidateRange(1,2147483647)][int]$Seed = 314159,
    [ValidateRange(960,7680)][int]$Width = 1600,
    [ValidateRange(720,4320)][int]$Height = 1000,
    [switch]$Exercise,
    [string]$EvidenceDirectory = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if (-not $Executable) { $Executable = Join-Path $projectRoot 'builds/WonderChess-VNext-Lab-r3/Windows/WonderChess.exe' }
$gamePath = [IO.Path]::GetFullPath($Executable)
if (-not (Test-Path -LiteralPath $gamePath -PathType Leaf)) { throw "Build the successor package first. Missing executable: $gamePath" }
if ([IO.Path]::GetExtension($gamePath) -ne '.exe') { throw 'Executable must identify a packaged Windows game.' }
$arguments = @('-WCLab', '-WCProfileName=wonder_vnext', "-WCSeed=$Seed", '-windowed', "-ResX=$Width", "-ResY=$Height", '-nosplash')
if ($Exercise) {
    if (-not $EvidenceDirectory) { $EvidenceDirectory = Join-Path $projectRoot ('reports/vnext/engine-lab/' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')) }
    $evidenceRoot = [IO.Path]::GetFullPath($EvidenceDirectory)
    if (Test-Path -LiteralPath $evidenceRoot) { throw 'Use a fresh evidence directory.' }
    New-Item -ItemType Directory -Path $evidenceRoot | Out-Null
    $arguments += @('-WCLabExercise', '-unattended', ('-WCEvidenceDir="' + $evidenceRoot + '"'), ('-abslog="' + (Join-Path $evidenceRoot 'engine.log') + '"'))
    $process = Start-Process -FilePath $gamePath -ArgumentList $arguments -WorkingDirectory (Split-Path $gamePath) -WindowStyle Hidden -PassThru
    [ordered]@{ utc=[DateTime]::UtcNow.ToString('o'); pid=$process.Id; executable=$gamePath;
        sha256=(Get-FileHash -LiteralPath $gamePath -Algorithm SHA256).Hash.ToLowerInvariant(); arguments=$arguments;
        boundary='Launched only. Require lab-exercise.json, captures and process inspection for verification.'
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'launch.json') -Encoding utf8
    Write-Output "Exercise launched with PID $($process.Id). Evidence: $evidenceRoot"
} else {
    Start-Process -FilePath $gamePath -ArgumentList $arguments -WorkingDirectory (Split-Path $gamePath) | Out-Null
    Write-Output 'Opened the six-creature tactical laboratory. Its 3D forms are gameplay proxies awaiting the new art pipeline.'
}
