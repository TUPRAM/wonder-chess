# One-time, same-volume moves. No overwrite, source cleanup or Git reset.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$wcRoot = [IO.Path]::GetFullPath('C:\Users\iputu\Documents\Wonder Chess')
$wcActive = [IO.Path]::GetFullPath('C:\Users\iputu\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\CodexWorktrees\wc\m7')
$wcExternal = [IO.Path]::GetFullPath('C:\Users\iputu\Documents\Project Support\Wonder Chess')
$wcLocal = [IO.Path]::GetFullPath('C:\Users\iputu\AppData\Local\WonderChess')
$wcAudit = Join-Path $wcRoot 'support\operations\migration-20260915'
$wcArchive = Join-Path $wcRoot 'support\archives\previous-checkout-20260915'
if (-not (Test-Path -LiteralPath (Join-Path $wcAudit 'before-summary.json'))) { throw 'Hash inventory must complete first.' }
if ((Get-Content -LiteralPath (Join-Path $wcActive '.git') -Raw).Trim() -ne 'gitdir: C:/Users/iputu/Documents/Wonder Chess/.git/worktrees/m7') { throw 'Unexpected linked worktree identity.' }

function Move-WcItem([string]$Source, [string]$Destination, [string]$AllowedSourceRoot) {
    $resolvedSource = (Resolve-Path -LiteralPath $Source).Path
    $resolvedAllowed = (Resolve-Path -LiteralPath $AllowedSourceRoot).Path
    $resolvedTarget = [IO.Path]::GetFullPath($Destination)
    if ($resolvedSource -ne $resolvedAllowed -and -not $resolvedSource.StartsWith($resolvedAllowed.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Source escaped its approved root: $resolvedSource" }
    if (-not $resolvedTarget.StartsWith($wcRoot + '\support\', [StringComparison]::OrdinalIgnoreCase) -and (Split-Path $resolvedTarget) -ne $wcRoot) { throw "Destination escaped project: $resolvedTarget" }
    if (Test-Path -LiteralPath $resolvedTarget) { throw "Refusing to overwrite: $resolvedTarget" }
    if ((Get-Item -LiteralPath $resolvedSource -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Review reparse point first: $resolvedSource" }
    New-Item -ItemType Directory -Path (Split-Path $resolvedTarget) -Force | Out-Null
    Move-Item -LiteralPath $resolvedSource -Destination $resolvedTarget
    [ordered]@{source=$resolvedSource;destination=$resolvedTarget;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $wcAudit 'moves.jsonl') -Encoding utf8
    Write-Output "Moved: $resolvedTarget"
}

# Project-only bridge has an open executable inside the tool directory being moved.
$wcServers = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*Documents\Project Support\Wonder Chess\blender-mcp-1.9.1\blender-mcp-main\.venv\Scripts\python.exe*' -and $_.CommandLine -like '*-m blender_mcp.server*' })
foreach ($wcServer in $wcServers) { Stop-Process -Id $wcServer.ProcessId -ErrorAction Stop }
foreach ($wcItem in @(Get-ChildItem -LiteralPath $wcRoot -Force)) {
    if ($wcItem.Name -in @('.git','support')) { continue }
    Move-WcItem $wcItem.FullName (Join-Path $wcArchive $wcItem.Name) $wcRoot
}
foreach ($wcItem in @(Get-ChildItem -LiteralPath $wcActive -Force)) {
    if ($wcItem.Name -eq '.git') { continue }
    Move-WcItem $wcItem.FullName (Join-Path $wcRoot $wcItem.Name) $wcActive
}
Move-WcItem $wcExternal (Join-Path $wcRoot 'support\external') $wcExternal
Move-WcItem $wcLocal (Join-Path $wcRoot 'support\local-state\WonderChess') $wcLocal
foreach ($wcItem in @(Get-ChildItem -LiteralPath 'C:\Users\iputu\Downloads' -Filter 'Wonder_Chess_*.zip' -File)) {
    Move-WcItem $wcItem.FullName (Join-Path $wcRoot ('support\archives\downloads\' + $wcItem.Name)) 'C:\Users\iputu\Downloads'
}
Move-WcItem 'C:\Users\iputu\AppData\Local\Temp\wc_u_human_guardian_24904_autosave.blend' (Join-Path $wcRoot 'support\archives\recovered-autosaves\wc_u_human_guardian_24904_autosave.blend') 'C:\Users\iputu\AppData\Local\Temp'
Write-Output 'Payload moves complete. Verify every hash before changing Git worktree registration.'
