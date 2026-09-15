[CmdletBinding()]
param(
    [ValidateSet('Solo','Lab')][string]$Mode = 'Solo',
    [string]$Executable = '',
    [ValidateRange(1,2147483647)][int]$Seed = 314159,
    [ValidateRange(960,7680)][int]$Width = 1600,
    [ValidateRange(720,4320)][int]$Height = 1000,
    [switch]$Exercise,
    [switch]$ManaExperiment,
    [switch]$Mana20Experiment,
    [switch]$CombatClarity,
    [switch]$ArtSlice,
    [switch]$Storybook,
    [string]$SavePath = '',
    [string]$EvidenceDirectory = '',
    [switch]$ValidateOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if ($ArtSlice -or $Storybook) { $CombatClarity = $true }
if ($CombatClarity -and ($ManaExperiment -or $Mana20Experiment)) { throw 'Combat clarity includes 20 mana; choose one experiment.' }
if ($ManaExperiment -and $Mana20Experiment) { throw 'Choose one mana experiment, 10 or 20 per basic hit.' }
if (-not $Executable) { $Executable = Join-Path $projectRoot $(if ($Storybook) {'builds/WonderChess-Storybook-r20/Windows/WonderChess.exe'} elseif ($ArtSlice) {'builds/WonderChess-2DSlice-r15/Windows/WonderChess.exe'} elseif ($CombatClarity) {'builds/WonderChess-CombatClarity-r13/Windows/WonderChess.exe'} elseif ($Mana20Experiment) {'builds/WonderChess-Mana20-r10/Windows/WonderChess.exe'} elseif ($ManaExperiment) {'builds/WonderChess-Mana-r9/Windows/WonderChess.exe'} else {'builds/WonderChess-Milestones-r6/Windows/WonderChess.exe'}) }
$gamePath = [IO.Path]::GetFullPath($Executable)
if (-not (Test-Path -LiteralPath $gamePath -PathType Leaf)) { throw "Package executable missing: $gamePath" }
if ([IO.Path]::GetExtension($gamePath) -ne '.exe') { throw 'Choose a packaged Windows executable.' }
if ($ValidateOnly) {
    [ordered]@{status='PASS';mode=$Mode;executable=$gamePath;project_root=$projectRoot;launched=$false} | ConvertTo-Json
    return
}
$hashStream = [IO.File]::OpenRead($gamePath)
$hashAlgorithm = [Security.Cryptography.SHA256]::Create()
try { $bootstrapHash = [BitConverter]::ToString($hashAlgorithm.ComputeHash($hashStream)).Replace('-', '').ToLowerInvariant() }
finally { $hashStream.Dispose(); $hashAlgorithm.Dispose() }
if (-not $EvidenceDirectory) { $EvidenceDirectory = Join-Path $projectRoot ('reports/vnext/milestones/launch-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')) }
$evidenceRoot = [IO.Path]::GetFullPath($EvidenceDirectory)
if (Test-Path -LiteralPath $evidenceRoot) { throw 'Use a fresh evidence directory to preserve earlier results.' }
New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null
$arguments = @($(if ($Mode -eq 'Solo') {'-WCSolo'} else {'-WCLab'}), '-WCProfileName=wonder_vnext',
    "-WCSeed=$Seed", '-windowed', "-ResX=$Width", "-ResY=$Height", '-nosplash', '-UDPMESSAGING_TRANSPORT_ENABLE=0',
    ('-WCEvidenceDir="' + $evidenceRoot + '"'), ('-abslog="' + (Join-Path $evidenceRoot 'engine.log') + '"'))
if ($ManaExperiment) { $arguments += '-WCManaExperiment' }
if ($Mana20Experiment) { $arguments += '-WCMana20Experiment' }
if ($CombatClarity) { $arguments += '-WCCombatClarityExperiment' }
if ($ArtSlice) { $arguments += '-WCArtSlice' }
if ($Storybook) { $arguments += '-WCStorybook' }
if ($SavePath) { $arguments += ('-WCSavePath="' + [IO.Path]::GetFullPath($SavePath) + '"') }
if ($Exercise) { $arguments += @($(if ($Mode -eq 'Solo') {'-WCSoloExercise'} else {'-WCLabExercise'}), '-unattended') }
$process = Start-Process -FilePath $gamePath -ArgumentList $arguments -WorkingDirectory (Split-Path $gamePath) -WindowStyle Hidden -PassThru
[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=$process.Id;mode=$Mode;exercise=[bool]$Exercise;
    storybook=[bool]$Storybook;art_slice=[bool]$ArtSlice;combat_clarity=[bool]$CombatClarity;mana_experiment=[bool]$ManaExperiment;mana20_experiment=[bool]$Mana20Experiment;executable=$gamePath;bootstrap_sha256=$bootstrapHash;
    arguments=$arguments;boundary='Launched only. This is a six-creature study candidate with proxy art. Inspect process, logs, input evidence and exercise result separately.'
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'launch.json') -Encoding utf8
Write-Output "$Mode candidate launched with PID $($process.Id). Evidence: $evidenceRoot"
