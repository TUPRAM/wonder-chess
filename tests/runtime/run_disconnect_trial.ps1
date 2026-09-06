param(
    [Parameter(Mandatory = $true)][ValidateSet('client-loss', 'host-loss')][string]$Mode
)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$packageRoot = Join-Path $taskRoot 'builds/Windows-Alpha-Candidate6'
$executable = Join-Path $packageRoot 'WonderChess.exe'
$evidenceRoot = Join-Path $taskRoot ('reports/WC-360/candidate6-disconnect/' + $Mode)
$port = if ($Mode -eq 'client-loss') { 7778 } else { 7779 }
$hostSeconds = if ($Mode -eq 'client-loss') { 100 } else { 35 }
$clientSeconds = if ($Mode -eq 'client-loss') { 30 } else { 65 }
if (Test-Path -LiteralPath $evidenceRoot) { throw "Preserve existing evidence: $evidenceRoot already exists" }
if (-not (Test-Path -LiteralPath $executable)) { throw 'Verified candidate6 executable is absent' }
$udp = @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object LocalPort -eq $port)
$tcp = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object LocalPort -eq $port)
if ($udp.Count -or $tcp.Count) { throw "Port $port already has an owner; no process launched" }
$manifest = Get-Content -LiteralPath (Join-Path $taskRoot 'reports/WC-360/candidate6-provenance.json') -Raw | ConvertFrom-Json
$expected = $manifest.files | Where-Object path -eq $executable
$actualHash = (Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
if (-not $expected -or $actualHash -ne $expected.sha256) { throw 'Candidate6 bootstrap hash no longer matches immutable manifest' }
New-Item -ItemType Directory -Path $evidenceRoot | Out-Null
$processes = [System.Collections.Generic.List[object]]::new()
$result = [ordered]@{
    mode = $Mode; port = $port; utc_started = [DateTime]::UtcNow.ToString('o'); status = 'RUNNING'
    package = $packageRoot; bootstrap_sha256 = $actualHash; port_unowned_before_launch = $true
    boundary = 'Actual packaged local-loopback process lifecycle. Normal simulation speed, 1280x720. Profiling is confounded by parallel Shipping compilation and is not a performance acceptance run.'
    processes = @(); late_join_launched_after_observed_takeover = $false
}

function Save-Result {
    $result.processes = @($processes | ForEach-Object { $_.Record })
    $result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'trial.json') -Encoding utf8
}

function Launch-Game([string]$Role, [string]$Map, [int]$Seconds) {
    $directory = Join-Path $evidenceRoot $Role
    New-Item -ItemType Directory -Path $directory | Out-Null
    $arguments = @($Map, '-unattended', '-nosplash', '-windowed', '-ResX=1280', '-ResY=720', '-ForceRes', '-dx11',
        '-WCExercise', '-WCAuthorityChecks', '-WCProfile', '-WCFast=1', "-WCExitAfter=$Seconds",
        ('-WCEvidenceDir="' + $directory + '"'), ('-abslog="' + (Join-Path $directory 'game.log') + '"'))
    if ($Role -eq 'host') { $arguments += "-Port=$port" }
    $launched = Start-Process -FilePath $executable -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru -ArgumentList $arguments
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
    Launch-Game 'host' '/Game/WonderChess/Maps/L_WC_Courtyard?listen?WCHumans=2' $hostSeconds
    $listenDeadline = [DateTime]::UtcNow.AddSeconds(30)
    $listening = $false
    while ([DateTime]::UtcNow -lt $listenDeadline) {
        $logPath = Join-Path $evidenceRoot 'host/game.log'
        if (Test-Path -LiteralPath $logPath) {
            $lines = Get-Content -LiteralPath $logPath
            $listening = [bool]($lines | Select-String -SimpleMatch "IpNetDriver listening on port $port")
            if ($listening) { break }
        }
        if ($processes[0].Process.HasExited) { throw 'Host exited before listen evidence' }
        Start-Sleep -Milliseconds 250
    }
    if (-not $listening) { throw "No actual port $port listen log within 30 seconds" }
    $result.listen_confirmed_utc = [DateTime]::UtcNow.ToString('o')
    Write-Output "Actual host listen log confirmed on port $port"
    Launch-Game 'client' "127.0.0.1:$port" $clientSeconds
    $deadline = [DateTime]::UtcNow.AddSeconds(135)
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
                    Launch-Game 'late-join' "127.0.0.1:$port" 25
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
