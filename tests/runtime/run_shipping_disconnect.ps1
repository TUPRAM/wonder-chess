param(
    [Parameter(Mandatory = $true)][ValidateSet('client-loss', 'host-loss')][string]$Mode,
    [Parameter(Mandatory = $true)][string]$ProvenancePath,
    [string]$EvidenceName = 'shipping-disconnect',
    [string]$OutputDirectory,
    [ValidateRange(30,3600)][int]$HostSeconds,
    [ValidateRange(15,3600)][int]$ClientSeconds,
    [ValidateRange(1,20)][int]$SimulationSpeed=1
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'packaged_payload.ps1')
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$manifestPath = [IO.Path]::GetFullPath($ProvenancePath)
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.package_report.exit_code -ne 0 -or -not $manifest.input_files_stable_during_capture) { throw 'Stable successful Shipping provenance required' }
$packageRoot = $manifest.package_root
$executable = Join-Path $packageRoot 'WonderChess.exe'
$gameExecutable = Join-Path $packageRoot 'WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe'
if ($EvidenceName -notmatch '^[a-z0-9-]+$') { throw 'Evidence name must be a simple report directory name' }
$evidenceRoot = if ($OutputDirectory) { [IO.Path]::GetFullPath($OutputDirectory) } else { Join-Path $taskRoot ('reports/WC-360/' + $EvidenceName + '/' + $Mode) }
$port = if ($Mode -eq 'client-loss') { 7778 } else { 7779 }
if (-not $PSBoundParameters.ContainsKey('HostSeconds')) { $HostSeconds = if ($Mode -eq 'client-loss') { 150 } else { 45 } }
if (-not $PSBoundParameters.ContainsKey('ClientSeconds')) { $ClientSeconds = if ($Mode -eq 'client-loss') { 45 } else { 100 } }
if (($Mode -eq 'client-loss' -and $HostSeconds -le $ClientSeconds+35) -or ($Mode -eq 'host-loss' -and $ClientSeconds -le $HostSeconds+15)) { throw 'Surviving process needs enough time to observe loss and the late-join check' }
if (-not $evidenceRoot.StartsWith((Join-Path $taskRoot 'reports') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Evidence must stay under this workspace reports directory' }
if (Test-Path -LiteralPath $evidenceRoot) { throw "Preserve existing evidence: $evidenceRoot already exists" }
if (-not (Test-Path -LiteralPath $executable)) { throw 'Verified Shipping executable is absent' }
$udp = @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object LocalPort -eq $port)
$tcp = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object LocalPort -eq $port)
if ($udp.Count -or $tcp.Count) { throw "Port $port already has an owner; no process launched" }
$identities = @()
foreach ($path in @($executable, $gameExecutable)) {
    $expected = $manifest.files | Where-Object path -eq $path
    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if (-not $expected -or $actualHash -ne $expected.sha256) { throw "Shipping executable hash no longer matches immutable manifest: $path" }
    $identities += @{path=$path;sha256=$actualHash}
}
$payloadVerification = Test-WCPackagedPayload -Manifest $manifest -PackageRoot $packageRoot
New-Item -ItemType Directory -Path $evidenceRoot | Out-Null
$processes = [System.Collections.Generic.List[object]]::new()
$result = [ordered]@{
    mode = $Mode; port = $port; utc_started = [DateTime]::UtcNow.ToString('o'); status = 'RUNNING'
    package = $packageRoot; executable_identities = $identities; payload_verification = $payloadVerification; port_unowned_before_launch = $true
    provenance_path=$manifestPath; provenance_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    startup_flags='Scoped game-owned -WCHost/-WCJoin routing; current PowerShell policy; actual OS UDP listen owner'
    boundary = 'Actual Shipping packaged local-loopback process lifecycle. 1280x720 at the explicitly recorded speed. Actual departure phase and neutral/PvP kind are determined from evidence. This functional multi-process run is not uncontended1080p performance acceptance. Shipping UE_LOG checks are unavailable, not zero errors.'
    simulation_speed=$SimulationSpeed;bounded_host_seconds=$HostSeconds;bounded_client_seconds=$ClientSeconds
    processes = @(); late_join_launched_after_observed_takeover = $false
}

function Save-Result {
    $result.processes = @($processes | ForEach-Object { $_.Record })
    $result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'trial.json') -Encoding utf8
}

function Launch-Game([string]$Role, [int]$Seconds) {
    $directory = Join-Path $evidenceRoot $Role
    New-Item -ItemType Directory -Path $directory | Out-Null
    $arguments = @('-unattended', '-nosplash', '-windowed', '-ResX=1280', '-ResY=720', '-ForceRes', '-dx11',
        '-WCExercise', '-WCAuthorityChecks', '-WCProfile', '-WCShots', "-WCFast=$SimulationSpeed", "-WCExitAfter=$Seconds",
        ('-WCEvidenceDir="' + $directory + '"'))
    if ($Role -eq 'host') { $arguments += @('-WCHost', "-Port=$port") }
    else { $arguments += "-WCJoin=127.0.0.1:$port" }
    $launched = Start-Process -FilePath $executable -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru -ArgumentList $arguments
    $null = $launched.Handle
    $record = [ordered]@{ role = $Role; bootstrap_pid = $launched.Id; utc_launched = [DateTime]::UtcNow.ToString('o')
        executable = $executable; working_directory = $packageRoot; arguments = $arguments; planned_exit_after_seconds = $Seconds
        exit_observed = $false; exit_code = $null }
    $record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $directory 'launch.json') -Encoding utf8
    $entry = [PSCustomObject]@{ Process = $launched; Record = $record; Directory = $directory }
    $processes.Add($entry)
    Save-Result
    Write-Output "$Role launched bootstrap PID $($launched.Id), planned exit after $Seconds seconds"
}

try {
    Launch-Game 'host' $hostSeconds
    $listenDeadline = [DateTime]::UtcNow.AddSeconds(30)
    $listening = $false
    while ([DateTime]::UtcNow -lt $listenDeadline) {
        foreach ($endpoint in @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object LocalPort -eq $port)) {
            $owner = Get-CimInstance Win32_Process -Filter "ProcessId = $($endpoint.OwningProcess)"
            if ($owner.ExecutablePath -eq $gameExecutable -and $owner.CommandLine.Contains((Join-Path $evidenceRoot 'host'))) {
                $result.listen_owner = @{utc=[DateTime]::UtcNow.ToString('o');local_address=$endpoint.LocalAddress;local_port=$endpoint.LocalPort
                    process_id=$owner.ProcessId;parent_process_id=$owner.ParentProcessId;executable_path=$owner.ExecutablePath;command_line=$owner.CommandLine}
                $listening = $true
                break
            }
        }
        if ($listening) { break }
        if ($processes[0].Process.HasExited) { throw 'Host exited before listen evidence' }
        Start-Sleep -Milliseconds 250
    }
    if (-not $listening) { throw "No verified Shipping UDP port $port owner within30 seconds" }
    $result.listen_confirmed_utc = [DateTime]::UtcNow.ToString('o')
    Write-Output "Actual Shipping host UDP port $port owned by PID $($result.listen_owner.process_id)"
    Launch-Game 'client' $clientSeconds
    $deadline = [DateTime]::UtcNow.AddSeconds([Math]::Max($HostSeconds,$ClientSeconds)+60)
    do {
        foreach ($entry in $processes) {
            $entry.Process.Refresh()
            if ($entry.Process.HasExited -and -not $entry.Record.exit_observed) {
                $entry.Process.WaitForExit()
                $entry.Record.exit_observed = $true
                $entry.Record.exit_code = $entry.Process.ExitCode
                $entry.Record.exit_observed_utc = [DateTime]::UtcNow.ToString('o')
                Write-Output "$($entry.Record.role) bootstrap exited with code $($entry.Process.ExitCode)"
            }
        }
        if ($Mode -eq 'client-loss' -and -not $result.late_join_launched_after_observed_takeover) {
            $hostSessionPath = Join-Path $evidenceRoot 'host/session.json'
            if (Test-Path -LiteralPath $hostSessionPath) {
                try { $session = Get-Content -LiteralPath $hostSessionPath -Raw | ConvertFrom-Json } catch { $session = $null }
                $transitions = @($session.authority_takeover_transitions | Where-Object departed_seat -eq 1)
                if ($transitions.Count -and $processes[1].Record.exit_observed) {
                    $result.takeover_observed_utc = [DateTime]::UtcNow.ToString('o')
                    $result.takeover_status = $transitions[-1].status
                    $result.takeover_phase = $transitions[-1].phase
                    $result.takeover_round = $transitions[-1].round
                    Launch-Game 'late-join' 25
                    $result.late_join_launched_after_observed_takeover = $true
                    Write-Output "Late join launched after actual takeover status $($transitions[-1].status), phase $($transitions[-1].phase) round $($transitions[-1].round)"
                }
            }
        }
        Save-Result
        $running = @($processes | Where-Object { -not $_.Record.exit_observed })
        if ($running.Count) { Start-Sleep -Milliseconds 500 }
    } while ($running.Count -and [DateTime]::UtcNow -lt $deadline)
    if ($running.Count) { throw 'A tracked process has not completed its planned exit; preserved for explicit review' }
    $result.status = 'PROCESSES_EXITED_AUDIT_REQUIRED'
    if ($Mode -eq 'client-loss' -and -not $result.late_join_launched_after_observed_takeover) {
        $result.status = 'INCOMPLETE_NO_TAKEOVER_LATE_JOIN'
    }
} catch {
    $result.status = 'FAILED'
    $result.error = $_.Exception.Message
    Write-Output "Trial error: $($result.error). Task process identities and planned exit timers are retained in trial.json."
} finally {
    $result.utc_finished = [DateTime]::UtcNow.ToString('o')
    Save-Result
}
$result | ConvertTo-Json -Depth 6
if ($result.status -ne 'PROCESSES_EXITED_AUDIT_REQUIRED') { exit 1 }
