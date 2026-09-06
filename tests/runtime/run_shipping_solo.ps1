param(
    [Parameter(Mandatory=$true)][ValidateSet('normal1080','normal1080-taa','restart')][string]$Mode,
    [Parameter(Mandatory=$true)][string]$ProvenancePath,
    [ValidateRange(1,2147483647)][int]$ExerciseSeed=271828,
    [ValidateRange(-1,23)][int]$FollowHero=-1,
    [string]$OutputDirectory,
    [ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9_-]*$')][string]$EvidenceName,
    [ValidateRange(10,3600)][int]$Seconds,
    [ValidateRange(1,100)][int]$SimulationSpeed,
    [ValidateRange(1,2)][int]$Restarts=1,
    [switch]$NullRHI,
    [switch]$NoAutomaticShots
)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$manifestPath = (Resolve-Path -LiteralPath $ProvenancePath).Path
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$packageRoot = $manifest.package_root
$executable = Join-Path $packageRoot 'WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe'
$expected = $manifest.files | Where-Object path -eq $executable
$actualHash = (Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
if (-not $expected -or $actualHash -ne $expected.sha256) { throw 'Shipping executable does not match the immutable manifest' }
if ($manifest.package_report.exit_code -ne 0) { throw 'Manifest does not record successful packaging' }
$otherGames = @(Get-CimInstance Win32_Process -Filter "Name = 'WonderChess-Win64-Shipping.exe' OR Name = 'WonderChess.exe'" | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($taskRoot, [StringComparison]::OrdinalIgnoreCase) })
if ($otherGames.Count) { throw 'Another task-owned game is running; preserve it and launch this verification after it exits' }
$evidenceLabel = if ($EvidenceName) { $EvidenceName } else { 'shipping-' + $Mode }
$evidenceRoot = if ($OutputDirectory) { [IO.Path]::GetFullPath($OutputDirectory) } else { Join-Path $taskRoot ('reports/WC-360/' + $evidenceLabel) }
if (-not $evidenceRoot.StartsWith((Join-Path $taskRoot 'reports') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Evidence must stay under this workspace reports directory' }
if (Test-Path -LiteralPath $evidenceRoot) { throw 'Evidence already exists; preserve it' }
New-Item -ItemType Directory -Path $evidenceRoot | Out-Null
$speed = if ($PSBoundParameters.ContainsKey('SimulationSpeed')) { $SimulationSpeed } elseif ($Mode -eq 'restart') { 10 } else { 1 }
$durationSeconds = if ($PSBoundParameters.ContainsKey('Seconds')) { $Seconds } elseif ($Mode -eq 'normal1080') { 1400 } elseif ($Mode -eq 'normal1080-taa') { 600 } else { 320 }
$arguments = @('WonderChess','-windowed','-ResX=1920','-ResY=1080','-ForceRes','-dx11',
    '-WCExercise','-WCAuthorityChecks','-WCProfile','-WCShots','-WCProjectedBounds',
    "-WCFast=$speed","-WCExitAfter=$durationSeconds",('-WCEvidenceDir="' + $evidenceRoot + '"'))
if ($NullRHI) {
    $arguments = @($arguments | Where-Object { $_ -notin @('-dx11','-WCShots','-WCProjectedBounds') }) + '-nullrhi'
}
elseif ($NoAutomaticShots) {
    $arguments = @($arguments | Where-Object { $_ -notin @('-WCShots','-WCProjectedBounds') })
}
if ($Mode -eq 'restart') { $arguments += @("-WCRestartCount=$Restarts",'-WCAutoStart') }
if ($ExerciseSeed -ne 271828) { $arguments += "-WCExerciseSeed=$ExerciseSeed" }
if ($FollowHero -ge 0) { $arguments += "-WCFollowHero=$FollowHero" }
$ambient = @(Get-Process -Name UnrealEditor,blender -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,StartTime,CPU,WorkingSet64)
$record = [ordered]@{
    status='STARTED';mode=$Mode;started_utc=[DateTime]::UtcNow.ToString('o');executable=$executable
    executable_sha256=$actualHash;working_directory=$packageRoot;arguments=$arguments
    provenance_path=$manifestPath;provenance_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    ambient_editor_processes=$ambient;other_task_games_before_launch=0;process_id=$null;exit_code=$null;window_style='Hidden'
    null_rhi=[bool]$NullRHI;simulation_speed=$speed;bounded_seconds=$durationSeconds
    automatic_screenshots=(-not $NullRHI -and -not $NoAutomaticShots);projected_bounds=(-not $NullRHI -and -not $NoAutomaticShots)
    boundary='Scripted legal player commands in the actual Shipping game. PNG captures, public-state evidence and frame CSV instrumentation are enabled. Existing user editor applications are preserved. This is not manual usability or audio audition evidence.'
}
if ($NullRHI) { $record.boundary = 'Actual Shipping process with NullRHI and scripted player commands. Public-state and command evidence is enabled; there is no rendered screenshot, GPU timing, visual, audio-audition or performance acceptance claim.' }
elseif ($NoAutomaticShots) { $record.boundary = 'Actual rendered Shipping process with scripted player commands, public-state, command and frame CSV instrumentation. Automatic PNG capture and projected-bounds sampling are disabled. This is measured performance evidence, not manual usability or audio audition; comparisons against other binaries do not establish a same-binary causal A/B result.' }
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'launch.json') -Encoding utf8
& 'C:\Windows\system32\nvidia-smi.exe' '--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu,power.draw,temperature.gpu' '--format=csv' | Set-Content -LiteralPath (Join-Path $evidenceRoot 'gpu-before.csv') -Encoding utf8
$process = Start-Process -FilePath $executable -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru -ArgumentList $arguments
$null = $process.Handle
$record.process_id = $process.Id
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'launch.json') -Encoding utf8
Write-Output "$Mode actual Shipping process $($process.Id) started at $($record.started_utc); ${speed}x simulation; planned $durationSeconds-second bounded exit"
$process.WaitForExit()
$record.exit_code = $process.ExitCode
$record.status = 'EXITED_AUDIT_REQUIRED'
$record.ended_utc = [DateTime]::UtcNow.ToString('o')
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'launch.json') -Encoding utf8
Write-Output ($record | ConvertTo-Json -Depth 6)
exit $process.ExitCode
