param([Parameter(Mandatory = $true)][ValidateNotNullOrEmpty()][string]$BlendFile)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$blenderExe = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
if (Get-Process blender -ErrorAction SilentlyContinue) {
    throw 'Blender is already open. Use its MCP for Blender sidebar to start port 9876; this launcher preserves the existing session.'
}
$resolvedBlend = (Resolve-Path -LiteralPath $BlendFile).Path
if (-not $resolvedBlend.StartsWith($repoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
    -not (Test-Path -LiteralPath $resolvedBlend -PathType Leaf) -or
    [IO.Path]::GetExtension($resolvedBlend) -ine '.blend') {
    throw 'BlendFile must be an existing .blend file inside this repository.'
}
$checkedPath = Get-Item -LiteralPath $resolvedBlend
while ($checkedPath.FullName -ne $repoRoot) {
    if ($checkedPath.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'BlendFile must not traverse a symbolic link or junction.'
    }
    $checkedPath = if ($checkedPath -is [IO.DirectoryInfo]) { $checkedPath.Parent } else { $checkedPath.Directory }
    if (-not $checkedPath) { throw 'Could not establish repository ownership of BlendFile.' }
}
$bootstrap = Join-Path $PSScriptRoot 'start_mcp.py'
$logRoot = Join-Path $repoRoot 'reports\blender-mcp'
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMddTHHmmssfff'
$env:BLENDER_MCP_DISABLE_TELEMETRY = '1'
# This launcher is explicitly for the user's visible, interactive editing session.
Start-Process -FilePath $blenderExe -WindowStyle Normal -ArgumentList @('--factory-startup', '--disable-autoexec', ('"' + $resolvedBlend + '"'), '--python', ('"' + $bootstrap + '"')) -WorkingDirectory $repoRoot -RedirectStandardOutput (Join-Path $logRoot "$stamp-blender.log") -RedirectStandardError (Join-Path $logRoot "$stamp-blender-errors.log") -PassThru
