param([Parameter(Mandatory=$true)][string]$ProvenancePath,
      [string]$EvidenceName = 'shipping-network-routed',
      [string]$OutputDirectory,
      [ValidateRange(60,3600)][int]$Seconds=720,
      [ValidateRange(1,20)][int]$SimulationSpeed=5,
      [ValidateRange(1024,65535)][int]$Port=7780)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'packaged_payload.ps1')
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$manifestPath = [IO.Path]::GetFullPath($ProvenancePath)
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.package_report.exit_code -ne 0 -or -not $manifest.input_files_stable_during_capture) { throw 'Packaging success and stable provenance are required before launch' }
$packageRoot = $manifest.package_root
$executable = Join-Path $packageRoot 'WonderChess.exe'
$gameExecutable = Join-Path $packageRoot 'WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe'
if ($EvidenceName -notmatch '^[a-z0-9-]+$') { throw 'Evidence name must be a simple report directory name' }
$evidenceRoot = if ($OutputDirectory) { [IO.Path]::GetFullPath($OutputDirectory) } else { Join-Path $taskRoot ('reports/WC-360/' + $EvidenceName) }
if (-not $evidenceRoot.StartsWith((Join-Path $taskRoot 'reports') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Evidence must stay under this workspace reports directory' }
if (Test-Path -LiteralPath $evidenceRoot) { throw 'Preserve existing Shipping network evidence; directory already exists' }
$portOwners = @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object LocalPort -eq $port)
if ($portOwners.Count) { throw "UDP port $port is already owned" }
$identities = @()
foreach ($path in @($executable, $gameExecutable)) {
    $expected = $manifest.files | Where-Object path -eq $path
    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if (-not $expected -or $expected.sha256 -ne $actualHash) { throw "Delivery executable digest mismatch: $path" }
    $identities += @{path=$path;sha256=$actualHash}
}
$payloadVerification = Test-WCPackagedPayload -Manifest $manifest -PackageRoot $packageRoot
New-Item -ItemType Directory -Path $evidenceRoot | Out-Null
$processes = [System.Collections.Generic.List[object]]::new()
$result = [ordered]@{utc_started=[DateTime]::UtcNow.ToString('o');status='RUNNING';port=$port;port_unowned_before_launch=$true
    provenance_path=$manifestPath;provenance_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    executable_identities=$identities;payload_verification=$payloadVerification;processes=@();listen_boundary='Actual OS UDP endpoint ownership, because this Shipping binary does not emit UE_LOG files.'
    startup_flags='Scoped game-owned -WCHost/-WCJoin routing; no positional Shipping startup URL'
    profiling_confounders='Concurrent workload is recorded at launch. Two rendered processes and automatic captures confound uncontended performance measurement.'
    simulation_speed=$SimulationSpeed;bounded_host_seconds=$Seconds;ambient_processes=@(Get-Process -Name UnrealEditor,blender -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,CPU,WorkingSet64)
    boundary='Two real packaged Shipping processes with human controller RPCs over loopback. 1280x720 at the explicitly recorded simulation speed. Scripted controller commands; not physical LAN, manual play, or normal1080p rendering acceptance.'}
function Save-Trial {
    $result.processes = @($processes | ForEach-Object { $_.Record })
    $result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'trial.json') -Encoding utf8
}
function Launch-Game([string]$Role,[int]$Seconds) {
    $directory = Join-Path $evidenceRoot $Role
    New-Item -ItemType Directory -Path $directory | Out-Null
    $arguments = @('-windowed','-ResX=1280','-ResY=720','-ForceRes','-dx11','-WCExercise','-WCAuthorityChecks',
        '-WCProfile','-WCShots','-WCProjectedBounds',"-WCFast=$SimulationSpeed","-WCExitAfter=$Seconds",('-WCEvidenceDir="'+$directory+'"'))
    if ($Role -eq 'host') { $arguments += @('-WCHost',"-Port=$port") }
    else { $arguments += "-WCJoin=127.0.0.1:$port" }
    $process = Start-Process -FilePath $executable -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru -ArgumentList $arguments
    $null = $process.Handle
    $record = [ordered]@{role=$Role;bootstrap_pid=$process.Id;utc_launched=[DateTime]::UtcNow.ToString('o');arguments=$arguments
        executable=$executable;working_directory=$packageRoot;planned_exit_after_seconds=$Seconds;exit_observed=$false;exit_code=$null}
    $record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $directory 'launch.json') -Encoding utf8
    $processes.Add([PSCustomObject]@{Process=$process;Record=$record;InnerProcess=$null})
    Save-Trial
    Write-Output "$Role launched actual bootstrap PID $($process.Id), planned exit after $Seconds seconds"
}
try {
    Launch-Game 'host' $Seconds
    $listenDeadline = [DateTime]::UtcNow.AddSeconds(35)
    $listenOwner = $null
    while ([DateTime]::UtcNow -lt $listenDeadline) {
        $endpoints = @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object LocalPort -eq $port)
        foreach ($endpoint in $endpoints) {
            $owner = Get-CimInstance Win32_Process -Filter "ProcessId = $($endpoint.OwningProcess)"
            if ($owner.ExecutablePath -eq $gameExecutable -and $owner.CommandLine.Contains($evidenceRoot)) {
                $listenOwner = @{utc=[DateTime]::UtcNow.ToString('o');local_address=$endpoint.LocalAddress;local_port=$endpoint.LocalPort
                    process_id=$owner.ProcessId;parent_process_id=$owner.ParentProcessId;executable_path=$owner.ExecutablePath;command_line=$owner.CommandLine}
                break
            }
        }
        if ($listenOwner) { break }
        if ($processes[0].Process.HasExited) { throw 'Shipping host exited before actual UDP listen ownership' }
        Start-Sleep -Milliseconds 500
    }
    if (-not $listenOwner) { throw 'No verified actual Shipping host UDP listener within35 seconds' }
    $result.listen_owner = $listenOwner
    $processes[0].InnerProcess = [Diagnostics.Process]::GetProcessById($listenOwner.process_id)
    $null = $processes[0].InnerProcess.Handle
    $processes[0].Record.inner_pid = $listenOwner.process_id
    $processes[0].Record.inner_exit_observed = $false
    $processes[0].Record.inner_exit_code = $null
    Save-Trial
    Write-Output "Shipping host UDP port $port owned by actual game PID $($listenOwner.process_id)"
    Launch-Game 'client' ($Seconds+30)
    $deadline = [DateTime]::UtcNow.AddSeconds($Seconds+90)
    do {
        foreach ($entry in $processes) {
            if (-not $entry.InnerProcess) {
                $inner = @(Get-CimInstance Win32_Process -Filter "Name = 'WonderChess-Win64-Shipping.exe'" | Where-Object {
                    $_.ExecutablePath -eq $gameExecutable -and $_.CommandLine.Contains((Join-Path $evidenceRoot $entry.Record.role))
                })
                if ($inner.Count -eq 1) {
                    $entry.InnerProcess = [Diagnostics.Process]::GetProcessById($inner[0].ProcessId)
                    $null = $entry.InnerProcess.Handle
                    $entry.Record.inner_pid = $inner[0].ProcessId
                    $entry.Record.inner_exit_observed = $false
                    $entry.Record.inner_exit_code = $null
                }
            }
            if ($entry.InnerProcess) {
                $entry.InnerProcess.Refresh()
                if ($entry.InnerProcess.HasExited -and -not $entry.Record.inner_exit_observed) {
                    $entry.InnerProcess.WaitForExit()
                    $entry.Record.inner_exit_observed = $true
                    $entry.Record.inner_exit_code = $entry.InnerProcess.ExitCode
                    $entry.Record.inner_exit_observed_utc = [DateTime]::UtcNow.ToString('o')
                }
            }
            $entry.Process.Refresh()
            if ($entry.Process.HasExited -and -not $entry.Record.exit_observed) {
                $entry.Process.WaitForExit()
                $entry.Record.exit_observed=$true
                $entry.Record.exit_code=$entry.Process.ExitCode
                $entry.Record.exit_observed_utc=[DateTime]::UtcNow.ToString('o')
                Write-Output "$($entry.Record.role) bootstrap exited with code $($entry.Process.ExitCode)"
            }
        }
        Save-Trial
        $running = @($processes | Where-Object { -not $_.Record.exit_observed -or ($_.InnerProcess -and -not $_.Record.inner_exit_observed) })
        if ($running.Count) { Start-Sleep -Milliseconds 750 }
    } while ($running.Count -and [DateTime]::UtcNow -lt $deadline)
    if ($running.Count) { throw 'Tracked game has not reached planned exit; retain identity for review' }
    $result.status = 'PROCESSES_EXITED_AUDIT_REQUIRED'
} catch {
    $result.status='FAILED'
    $result.error=$_.Exception.Message
    Write-Output "Trial failed: $($result.error). Planned process timers remain active; inspect trial.json."
} finally {
    $result.utc_finished=[DateTime]::UtcNow.ToString('o')
    Save-Trial
}
Write-Output "Shipping network lifecycle: $($result.status)"
if ($result.status -ne 'PROCESSES_EXITED_AUDIT_REQUIRED') { exit 1 }
