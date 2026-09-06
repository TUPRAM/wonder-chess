param([Parameter(Mandatory=$true)][string]$ProvenancePath,
      [Parameter(Mandatory=$true)][string]$EvidenceName)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$manifestPath = [IO.Path]::GetFullPath($ProvenancePath)
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.package_report.exit_code -ne 0 -or -not $manifest.input_files_stable_during_capture) { throw 'Successful packaging and stable immutable provenance are required' }
if ($EvidenceName -notmatch '^[a-z0-9-]+$') { throw 'Evidence name must be a simple report directory name' }
$directory = Join-Path $taskRoot ('reports/WC-360/' + $EvidenceName)
if (Test-Path -LiteralPath $directory) { throw 'Preserve prior regression evidence; choose a fresh directory' }
$executable = $manifest.packaged_game_executable
$recorded = $manifest.files | Where-Object path -eq $executable
$hash = (Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
if (-not $recorded -or $hash -ne $recorded.sha256) { throw 'Packaged executable differs from immutable provenance' }
New-Item -ItemType Directory -Path $directory | Out-Null
$arguments = @('WonderChess', '-nullrhi', '-nosound', '-WCRegression=100', ('-WCEvidenceDir="' + $directory + '"'))
$started = [DateTime]::UtcNow.ToString('o')
$process = Start-Process -FilePath $executable -WorkingDirectory $manifest.package_root -WindowStyle Hidden -PassThru -ArgumentList $arguments
$null = $process.Handle
$launch = [ordered]@{status='RUNNING';utc=$started;process_id=$process.Id;executable=$executable;executable_sha256=$hash
    working_directory=$manifest.package_root;arguments=$arguments;provenance_path=$manifestPath
    provenance_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    boundary='Actual packaged100-tournament headless C++ regression. May overlap accelerated functional sessions; not a rendering/audio/performance run.'}
$launch | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $directory 'launch.json') -Encoding utf8
Write-Output "Headless100 actual inner process PID $($process.Id) started"
$deadline = [DateTime]::UtcNow.AddSeconds(240)
while (-not $process.WaitForExit(1000)) {
    if ([DateTime]::UtcNow -gt $deadline) { throw 'Regression exceeded240 seconds; process identity retained for explicit review' }
}
$process.WaitForExit()
$exit = [ordered]@{started_utc=$started;ended_utc=[DateTime]::UtcNow.ToString('o');process_id=$process.Id;executable=$executable;exit_code=$process.ExitCode}
$exit | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $directory 'process-exit.json') -Encoding utf8
$launch.status='EXITED_AUDIT_REQUIRED'
$launch | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $directory 'launch.json') -Encoding utf8
Write-Output "Headless100 actual inner process PID $($process.Id) exited code $($process.ExitCode)"
if ($process.ExitCode -ne 0) { exit 1 }
