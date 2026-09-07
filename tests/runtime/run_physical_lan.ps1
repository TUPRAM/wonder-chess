param(
    [Parameter(Mandatory=$true)][ValidateSet('host','client')][string]$Role,
    [Parameter(Mandatory=$true)][string]$HostAddress,
    [Parameter(Mandatory=$true)][ValidateRange(1024,65535)][int]$Port,
    [Parameter(Mandatory=$true)][string]$PackageRoot,
    [Parameter(Mandatory=$true)][string]$ProvenancePath,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9_-]{0,39}$')][string]$MachineLabel,
    [ValidateSet('scripted','manual')][string]$InputMode='scripted',
    [ValidateRange(1,20)][int]$SimulationSpeed=1,
    [ValidateRange(120,7200)][int]$Seconds=3600,
    [switch]$Launch,
    [switch]$Visible
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'packaged_payload.ps1')

function Test-WCPhysicalLocalPaths([string[]]$Paths) {
    foreach ($path in $Paths) {
        if ($path -notmatch '^[A-Za-z]:[\\/]' -or $path.Contains('"')) { throw 'Package, provenance and output must be absolute local drive paths; UNC/network paths and quotes are not accepted' }
    }
}

function Get-WCPrivateIPv4([string]$Address) {
    if ($Address -notmatch '^([0-9]{1,3}\.){3}[0-9]{1,3}$') { throw 'Use a literal private LAN IPv4 address without a port, URL or hostname' }
    $octets = @($Address.Split('.') | ForEach-Object { [int]$_ })
    if (@($octets | Where-Object { $_ -gt 255 }).Count) { throw 'IPv4 octet exceeds255' }
    $private = $octets[0] -eq 10 -or ($octets[0] -eq 172 -and $octets[1] -ge 16 -and $octets[1] -le 31) -or ($octets[0] -eq 192 -and $octets[1] -eq 168)
    if (-not $private) { throw 'This launcher is scoped to private IPv4 LAN addresses; loopback, wildcard, multicast and public addresses are rejected' }
    return ($octets -join '.')
}

function Test-WCPhysicalRoleAddress([string]$RunRole,[string]$Address,[string[]]$LocalAddresses) {
    if ($RunRole -eq 'host' -and $Address -notin $LocalAddresses) { throw 'The supplied host address is not assigned to this host machine' }
    if ($RunRole -eq 'client' -and $Address -in $LocalAddresses) { throw 'The client points to this same machine; this cannot establish the two-physical-PC gate' }
}

function Test-WCRelocatedPayload($Manifest,[string]$CurrentRoot) {
    if ($Manifest.package_report.exit_code -ne 0 -or $Manifest.configuration -ne 'Shipping') { throw 'A successful Shipping package provenance is required' }
    $originalRoot = [IO.Path]::GetFullPath($Manifest.package_root).TrimEnd('\','/')
    $current = [IO.Path]::GetFullPath($CurrentRoot).TrimEnd('\','/')
    if (-not (Test-Path -LiteralPath $current -PathType Container)) { throw 'Relocated package root does not exist' }
    # Change only this in-memory copy. The captured JSON and original identities
    # remain immutable, and every record retains its original-relative mapping.
    $mapped = $Manifest | ConvertTo-Json -Depth 100 | ConvertFrom-Json
    $mapping = @()
    foreach ($item in @($mapped.files | Where-Object group -eq 'packaged_payload')) {
        $original = [IO.Path]::GetFullPath($item.path)
        if (-not $original.StartsWith($originalRoot + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Original payload entry escapes the captured package root' }
        $relative = $original.Substring($originalRoot.Length + 1)
        if ('Saved' -in ($relative -split '[\\/]')) { throw 'Provenance unexpectedly includes runtime Saved data' }
        $item.path = [IO.Path]::GetFullPath((Join-Path $current $relative))
        $mapping += [ordered]@{relative_path=$relative.Replace('\','/');original_path=$original;current_path=$item.path;expected_sha256=$item.sha256;expected_bytes=$item.bytes}
    }
    $links = @(Get-Item -LiteralPath $current; Get-ChildItem -LiteralPath $current -Recurse -Force)
    if (@($links | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw 'Use an ordinary copied package; reparse points are not accepted as relocated payload evidence' }
    $verification = Test-WCPackagedPayload -Manifest $mapped -PackageRoot $current
    foreach ($required in @('WonderChess.exe','WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe')) {
        if ($required -notin @($mapping.relative_path)) { throw "Required Shipping payload identity absent: $required" }
    }
    return [ordered]@{status='PASS';original_package_root=$originalRoot;current_package_root=$current;mapping=$mapping;payload=$verification
        boundary='Complete copied package compared by original relative paths, size and SHA256; immutable provenance was not rewritten. This is a byte identity check, not networking or physical-PC certification.'}
}

function Get-WCHardwareIdentity {
    $system = Get-CimInstance Win32_ComputerSystem
    $product = Get-CimInstance Win32_ComputerSystemProduct
    $os = Get-CimInstance Win32_OperatingSystem
    $rawIdentity = [string]$product.UUID
    $uuidHash = $null
    if ($rawIdentity -and $rawIdentity -notmatch '^(0+|F+|-)+$') {
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $uuidHash = ([BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($rawIdentity.ToUpperInvariant())))).Replace('-','').ToLowerInvariant() }
        finally { $hasher.Dispose() }
    }
    return [ordered]@{hostname=[Environment]::MachineName;manufacturer=$system.Manufacturer;model=$system.Model;ram_bytes=$system.TotalPhysicalMemory
        smbios_uuid_sha256=$uuidHash;os=$os.Caption;os_version=$os.Version;os_build=$os.BuildNumber
        processors=@(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
        graphics=@(Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,AdapterRAM)
        physical_boundary='OS-reported identity only. Two separate physical devices still require paired operator observation; distinct processes, names or UUIDs alone do not prove physical separation.'}
}

Test-WCPhysicalLocalPaths @($PackageRoot,$ProvenancePath,$OutputDirectory)
$address = Get-WCPrivateIPv4 $HostAddress
$localPackage = (Resolve-Path -LiteralPath $PackageRoot).Path.TrimEnd('\','/')
$manifestPath = (Resolve-Path -LiteralPath $ProvenancePath).Path
$evidence = [IO.Path]::GetFullPath($OutputDirectory).TrimEnd('\','/')
if (-not [IO.Path]::IsPathRooted($OutputDirectory) -or $evidence -eq [IO.Path]::GetPathRoot($evidence)) { throw 'Supply a dedicated absolute evidence directory' }
if ($evidence -eq $localPackage -or $evidence.StartsWith($localPackage + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Evidence must be outside the frozen package directory' }
if (Test-Path -LiteralPath $evidence) { throw 'Evidence already exists; use a fresh directory and preserve the previous attempt' }
$manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$relocation = Test-WCRelocatedPayload -Manifest $manifest -CurrentRoot $localPackage
if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifestHash) { throw 'Provenance changed during preflight' }
$addresses = @(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop | Where-Object AddressState -eq 'Preferred' | Select-Object IPAddress,PrefixLength,InterfaceAlias,InterfaceIndex)
Test-WCPhysicalRoleAddress $Role $address @($addresses.IPAddress)
$hardware = Get-WCHardwareIdentity
$executable = Join-Path $localPackage 'WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe'
$others = @(Get-CimInstance Win32_Process -Filter "Name = 'WonderChess-Win64-Shipping.exe' OR Name = 'WonderChess.exe'" | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($localPackage + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) } | Select-Object ProcessId,ExecutablePath)
if ($others.Count) { throw 'A process from this package is already running; preserve it and choose a later run' }
if ($Role -eq 'host' -and @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object LocalPort -eq $Port).Count) { throw "The host UDP port $Port is already occupied; no existing process was changed" }
$arguments = @('WonderChess','-windowed','-ResX=1920','-ResY=1080','-ForceRes','-dx11','-WCProfile','-WCShots','-WCProjectedBounds',
    "-WCFast=$SimulationSpeed","-WCExitAfter=$Seconds",('-WCEvidenceDir="'+$evidence+'"'))
if ($InputMode -eq 'scripted') { $arguments += @('-WCExercise','-WCAuthorityChecks') }
if ($Role -eq 'host') { $arguments += @('-WCHost',"-Port=$Port") }
else { $arguments += "-WCJoin=${address}:$Port" }
$record = [ordered]@{schema='wonder_chess_physical_lan_launcher_v1';status='PREFLIGHT_ONLY';started_utc=[DateTime]::UtcNow.ToString('o')
    role=$Role;machine_label=$MachineLabel;hardware=$hardware;local_ipv4=$addresses;host_address=$address;port=$Port
    provenance_path=$manifestPath;provenance_sha256=$manifestHash;catalog_digest=$manifest.catalog_digest;candidate=$manifest.candidate
    relocated_payload_verification=$relocation;executable=$executable;arguments=$arguments;working_directory=$localPackage
    launcher_sha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
    payload_helper_sha256=(Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'packaged_payload.ps1') -Algorithm SHA256).Hash.ToLowerInvariant()
    input_mode=$InputMode;simulation_speed=$SimulationSpeed;planned_seconds=$Seconds;process_id=$null;exit_code=$null;listen_owner=$null
    ambient_processes=@(Get-Process -Name UnrealEditor,blender -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,CPU,WorkingSet64)
    physical_lan_acceptance='NOT_RUN';boundary='This record describes one machine. Paired complete tournament, authority/privacy and physical-device evidence require review. No firewall/service/install or transfer action is performed.'}
New-Item -ItemType Directory -Path $evidence | Out-Null
function Save-WCPhysicalLaunch { $record | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath (Join-Path $evidence 'physical-launch.json') -Encoding utf8 }
Save-WCPhysicalLaunch
if (-not $Launch) { Write-Output "PREFLIGHT_ONLY: package bytes verified; no connection or game launch. Record: $evidence\physical-launch.json"; return }
try {
    $style = if ($Visible) { 'Normal' } else { 'Hidden' }
    $process = Start-Process -FilePath $executable -WorkingDirectory $localPackage -WindowStyle $style -ArgumentList $arguments -PassThru
    $null = $process.Handle
    $record.status='RUNNING_AUDIT_PENDING';$record.process_id=$process.Id;$record.launch_utc=[DateTime]::UtcNow.ToString('o')
    Save-WCPhysicalLaunch
    if ($Role -eq 'host') {
        $deadline = [DateTime]::UtcNow.AddSeconds(45)
        do {
            $owned = @(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object { $_.LocalPort -eq $Port -and $_.OwningProcess -eq $process.Id })
            if ($owned.Count) {
                $record.listen_owner=@($owned | Select-Object LocalAddress,LocalPort,OwningProcess)
                Save-WCPhysicalLaunch
                Write-Output "Host game PID $($process.Id) owns UDP port $Port. Start the client on the other physical PC now."
                break
            }
            if ($process.HasExited) { throw 'Host exited before the requested UDP listener was observed' }
            Start-Sleep -Milliseconds 500
        } while ([DateTime]::UtcNow -lt $deadline)
        if (-not $record.listen_owner) { throw 'No matching host-process UDP listener within45 seconds; no firewall or network settings were changed' }
    }
    $deadline = [DateTime]::UtcNow.AddSeconds($Seconds + 90)
    while (-not $process.WaitForExit(1000)) {
        if ([DateTime]::UtcNow -gt $deadline) { throw 'Game exceeded the bounded observation window; process identity retained, and the process was not forcibly terminated' }
    }
    $record.exit_code=$process.ExitCode;$record.status='EXITED_AUDIT_REQUIRED';$record.ended_utc=[DateTime]::UtcNow.ToString('o')
    $record.post_run_relocated_payload_verification=Test-WCRelocatedPayload -Manifest $manifest -CurrentRoot $localPackage
    if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifestHash) { throw 'Immutable provenance changed during the run' }
} catch {
    $record.status='FAILED_OR_INCOMPLETE';$record.error=$_.Exception.Message;$record.ended_utc=[DateTime]::UtcNow.ToString('o')
    Save-WCPhysicalLaunch
    throw
} finally { Save-WCPhysicalLaunch }
Write-Output "Process lifecycle $($record.status), exit $($record.exit_code). Physical LAN acceptance remains NOT_RUN until paired review."
exit $record.exit_code
