param([string]$BlendFile)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$blenderExe = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
if (Get-Process blender -ErrorAction SilentlyContinue) {
    throw 'Blender is already open. Use its MCP for Blender sidebar to start port 9876; this launcher preserves the existing session.'
}
if (-not $BlendFile) {
    $BlendFile = Join-Path $repoRoot 'art-source\heroes\wc_u_human_guardian\wc_u_human_guardian.blend'
}
$resolvedBlend = (Resolve-Path -LiteralPath $BlendFile).Path
$bootstrap = Join-Path $PSScriptRoot 'start_mcp.py'
$logRoot = Join-Path $repoRoot 'reports\blender-mcp'
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMddTHHmmss'
$env:BLENDER_MCP_DISABLE_TELEMETRY = '1'
Start-Process -FilePath $blenderExe -WindowStyle Hidden -ArgumentList @('--disable-autoexec', ('"' + $resolvedBlend + '"'), '--python', ('"' + $bootstrap + '"')) -WorkingDirectory $repoRoot -RedirectStandardOutput (Join-Path $logRoot "$stamp-blender.log") -RedirectStandardError (Join-Path $logRoot "$stamp-blender-errors.log") -PassThru
