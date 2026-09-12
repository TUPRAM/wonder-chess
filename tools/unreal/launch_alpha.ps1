[CmdletBinding()]
param(
    [ValidateSet('Play','Listen','Join','Regression')][string]$Mode='Play',
    [string]$Executable=(Join-Path $PSScriptRoot '../../builds/WonderChess-Update24-Checkpoint-r4/Windows/WonderChess.exe'),
    [string]$HostAddress='127.0.0.1',
    [ValidateRange(1,65535)][int]$Port=7777,
    [ValidateRange(1,1000)][int]$Trials=100,
    [switch]$Exercise,
    [switch]$RestartOnce,
    [ValidateRange(1,100)][int]$Speed=1,
    [ValidateRange(0,7200)][int]$ExitAfter=0,
    [string]$EvidenceDirectory
)
$ErrorActionPreference='Stop'
$Game=(Resolve-Path -LiteralPath $Executable).Path
$Arguments=@('-windowed','-ResX=1920','-ResY=1080','-ForceRes')
switch($Mode){
    'Listen' {$Arguments=@('-WCHost',"-Port=$Port")+$Arguments}
    'Join' {
        $Address=$null
        if(-not [Net.IPAddress]::TryParse($HostAddress,[ref]$Address) -or $Address.AddressFamily -ne [Net.Sockets.AddressFamily]::InterNetwork){throw 'HostAddress must be a literal IPv4 address.'}
        $Arguments=@("-WCJoin=${HostAddress}:$Port")+$Arguments
    }
    'Regression' {$Arguments=@('-nullrhi','-nosound',"-WCRegression=$Trials")}
}
if($Exercise){$Arguments+='-WCExercise'}
if($RestartOnce){$Arguments+='-WCRestartOnce'}
if($Speed -ne 1){$Arguments+="-WCFast=$Speed"}
if($ExitAfter){$Arguments+="-WCExitAfter=$ExitAfter"}
if($EvidenceDirectory){
    $Evidence=[IO.Path]::GetFullPath($EvidenceDirectory)
    New-Item -ItemType Directory -Force -Path $Evidence | Out-Null
    $Arguments+=@('-WCProfile','-WCShots',"-WCEvidenceDir=$Evidence","-abslog=$(Join-Path $Evidence 'game.log')")
}
Write-Host "Launching $Game ($Mode). Scripted input: $Exercise; simulation speed: ${Speed}x."
& $Game @Arguments
