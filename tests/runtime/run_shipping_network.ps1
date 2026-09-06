$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$packageRoot = Join-Path $taskRoot 'builds/WonderChess-Alpha-Windows/Windows'
$executable = Join-Path $packageRoot 'WonderChess.exe'
$gameExecutable = Join-Path $packageRoot 'WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe'
$evidenceRoot = Join-Path $taskRoot 'reports/WC-360/shipping-network'
$port = 7780
if (Test-Path -LiteralPath $evidenceRoot) { throw 'Preserve existing Shipping network evidence; directory already exists' }
$portOwners = @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object LocalPort -eq $port)
if ($portOwners.Count) { throw "UDP port $port is already owned" }
$manifestPath = Join-Path $taskRoot 'reports/WC-360/shipping-delivery-provenance.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$identities = @()
foreach ($path in @($executable, $gameExecutable)) {
    $expected = $manifest.files | Where-Object path -eq $path
    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if (-not $expected -or $expected.sha256 -ne $actualHash) { throw "Delivery executable digest mismatch: $path" }
    $identities += @{path=$path;sha256=$actualHash}
}
New-Item -ItemType Directory -Path $evidenceRoot | Out-Null
$processes = [System.Collections.Generic.List[object]]::new()
$result = [ordered]@{utc_started=[DateTime]::UtcNow.ToString('o');status='RUNNING';port=$port;port_unowned_before_launch=$true
    provenance_path=$manifestPath;provenance_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    executable_identities=$identities;processes=@();listen_boundary='Actual OS UDP endpoint ownership, because this Shipping binary does not emit UE_LOG files.'
    boundary='Two real packaged Shipping processes with human controller RPCs over loopback. 1280x720 and simulation speed5; not normal1080p rendering acceptance.'}
function Save-Trial {
    $result.processes = @($processes | ForEach-Object { $_.Record })
    $result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'trial.json') -Encoding utf8
}
function Launch-Game([string]$Role,[string]$Map,[int]$Seconds) {
    $directory = Join-Path $evidenceRoot $Role
    New-Item -ItemType Directory -Path $directory | Out-Null
    $arguments = @($Map,'-windowed','-ResX=1280','-ResY=720','-ForceRes','-dx11','-WCExercise','-WCAuthorityChecks',
        '-WCProfile','-WCShots','-WCProjectedBounds','-WCFast=5',"-WCExitAfter=$Seconds",('-WCEvidenceDir="'+$directory+'"'))
    if ($Role -eq 'host') { $arguments += "-Port=$port" }
    $process = Start-Process -FilePath $executable -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru -ArgumentList $arguments
    $record = [ordered]@{role=$Role;bootstrap_pid=$process.Id;utc_launched=[DateTime]::UtcNow.ToString('o');arguments=$arguments
        executable=$executable;working_directory=$packageRoot;planned_exit_after_seconds=$Seconds;exit_observed=$false;exit_code=$null}
    $record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $directory 'launch.json') -Encoding utf8
    $processes.Add([PSCustomObject]@{Process=$process;Record=$record})
    Save-Trial
    Write-Output "$Role launched actual bootstrap PID $($process.Id), planned exit after $Seconds seconds"
}
try {
    Launch-Game 'host' '/Game/WonderChess/Maps/L_WC_Courtyard?listen?WCHumans=2' 270
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
    Save-Trial
    Write-Output "Shipping host UDP port $port owned by actual game PID $($listenOwner.process_id)"
    Launch-Game 'client' "127.0.0.1:$port" 280
    $deadline = [DateTime]::UtcNow.AddSeconds(310)
    do {
        foreach ($entry in $processes) {
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
        $running = @($processes | Where-Object { -not $_.Record.exit_observed })
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
