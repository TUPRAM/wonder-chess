<#
Inspect before use. Authored scaffold: NOT executed in PowerShell/Unreal in this kit.
Requires a verified Windows Unreal installation and compatible build tools.
Example: ./tools/unreal/package_game.ps1 -ProjectFile ./game/WonderChess.uproject -ArchiveDirectory ./builds/Win64
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ProjectFile,
    [Parameter(Mandatory=$true)][string]$ArchiveDirectory,
    [ValidateSet('Development','Shipping')][string]$Configuration = 'Development',
    [string]$UatScript = $env:UE_UAT_SCRIPT,
    [string]$LogDirectory = './reports/unreal'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This wrapper targets a native Windows build environment.' }
if ([string]::IsNullOrWhiteSpace($UatScript) -or -not (Test-Path -LiteralPath $UatScript -PathType Leaf)) {
    throw 'Set UE_UAT_SCRIPT or -UatScript to the verified RunUAT.bat path.'
}
if (-not (Test-Path -LiteralPath $ProjectFile -PathType Leaf)) { throw 'The .uproject does not exist.' }
$Project = (Resolve-Path -LiteralPath $ProjectFile).Path
if ([IO.Path]::GetExtension($Project) -ne '.uproject') { throw 'ProjectFile must be a .uproject.' }
$Archive = [IO.Path]::GetFullPath($ArchiveDirectory)
$Logs = [IO.Path]::GetFullPath($LogDirectory)
New-Item -ItemType Directory -Force -Path $Archive, $Logs | Out-Null
$Stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$LogPath = Join-Path $Logs "package-$Configuration-$Stamp.log"
$Arguments = @(
    'BuildCookRun', "-project=$Project", '-noP4', '-platform=Win64',
    "-clientconfig=$Configuration", '-build', '-cook', '-stage', '-pak',
    '-archive', "-archivedirectory=$Archive", '-utf8output'
)
# Confirm these flags using the installed AutomationTool before relying on the wrapper.
& $UatScript @Arguments 2>&1 | Tee-Object -FilePath $LogPath
$Code = $LASTEXITCODE
$Evidence = [ordered]@{
    utc = [DateTime]::UtcNow.ToString('o')
    configuration = $Configuration
    exit_code = $Code
    log_file = [IO.Path]::GetFileName($LogPath)
    packaging_status = $(if ($Code -eq 0) { 'tool_returned_success_launch_not_verified' } else { 'failed' })
    launched = $false
    full_match_verified = $false
}
$Evidence | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $Logs "package-$Configuration-$Stamp.json")
if ($Code -ne 0) { throw "Unreal packaging failed with code $Code. Inspect $LogPath" }
Write-Host 'Packaging command returned success. Independently inspect archive, launch it, and complete a match.'
