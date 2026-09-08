$ErrorActionPreference='Stop'
$root='C:\Users\iputu\Documents\Wonder Chess'
$source=Join-Path $root 'tests/runtime/run_physical_lan.ps1'
$errors=$null;$tokens=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($source,[ref]$tokens,[ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }
. (Join-Path $root 'tests/runtime/packaged_payload.ps1')
foreach ($name in @('Test-WCPhysicalLocalPaths','Get-WCPrivateIPv4','Test-WCPhysicalRoleAddress','Test-WCRelocatedPayload')) {
    $definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name},$true)
    Invoke-Expression $definition.Extent.Text
}
$results=[Collections.Generic.List[object]]::new()
function Check([string]$Name,[scriptblock]$Body,[bool]$Reject=$false) {
    $caught=$false;$message=$null
    try { & $Body | Out-Null } catch { $caught=$true;$message=$_.Exception.Message }
    if ($caught -ne $Reject) { throw "Fixture failed: $Name; caught=$caught; $message" }
    $results.Add(@{name=$Name;status='PASS';expected_rejection=$Reject;observed_error=$message})
}
$local=Join-Path $PSScriptRoot 'copied-package'
New-Item -ItemType Directory -Path (Join-Path $local 'WonderChess/Binaries/Win64') -Force | Out-Null
[IO.File]::WriteAllText((Join-Path $local 'WonderChess.exe'),'SYNTHETIC FIXTURE NOT AN EXECUTABLE')
[IO.File]::WriteAllText((Join-Path $local 'WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe'),'SYNTHETIC INNER FIXTURE NOT AN EXECUTABLE')
$original='D:\ImmutableOrigin\Windows'
$rows=@()
foreach ($file in Get-ChildItem -LiteralPath $local -Recurse -File) {
    $rows+=@{group='packaged_payload';path=(Join-Path $original $file.FullName.Substring($local.Length+1));bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
}
$manifest=@{package_root=$original;configuration='Shipping';package_report=@{exit_code=0};input_files_stable_during_capture=$true;files=$rows} | ConvertTo-Json -Depth 20 | ConvertFrom-Json
$originalJson=$manifest | ConvertTo-Json -Depth 20
Check 'relocated_complete_payload_valid' { $v=Test-WCRelocatedPayload $manifest $local; if ($v.payload.file_count -ne 2) {throw 'Wrong count'} }
Check 'original_manifest_remains_identical' { if (($manifest | ConvertTo-Json -Depth 20) -ne $originalJson) {throw 'Mutation'} }
Check 'private_ipv4_normalized' { if ((Get-WCPrivateIPv4 '192.168.001.020') -ne '192.168.1.20') {throw 'Wrong normalization'} }
foreach ($bad in @('127.0.0.1','0.0.0.0','224.0.0.1','8.8.8.8','192.168.1.256','192.168.1.2:7777','localhost','192.168.1.2 -WCHost')) { Check ('reject_address_'+$bad) {Get-WCPrivateIPv4 $bad} $true }
Check 'host_own_address' {Test-WCPhysicalRoleAddress host '10.0.0.2' @('10.0.0.2')}
Check 'host_other_address_rejected' {Test-WCPhysicalRoleAddress host '10.0.0.3' @('10.0.0.2')} $true
Check 'client_remote_address' {Test-WCPhysicalRoleAddress client '10.0.0.2' @('10.0.0.3')}
Check 'client_same_machine_rejected' {Test-WCPhysicalRoleAddress client '10.0.0.2' @('10.0.0.2')} $true
Check 'unc_rejected_without_access' {Test-WCPhysicalLocalPaths @('\\server\share\game')} $true
Check 'relative_path_rejected' {Test-WCPhysicalLocalPaths @('game\Windows')} $true
Check 'local_paths_valid' {Test-WCPhysicalLocalPaths @('C:\Games\Wonder Chess','D:\Evidence\run')}
$changed=$originalJson | ConvertFrom-Json;$changed.files[0].path='D:\elsewhere\escape.exe'
Check 'original_path_escape' {Test-WCRelocatedPayload $changed $local} $true
$changed=$originalJson | ConvertFrom-Json;$changed.files+=@($changed.files[0])
Check 'duplicate_payload_rejected' {Test-WCRelocatedPayload $changed $local} $true
$changed=$originalJson | ConvertFrom-Json;$changed.input_files_stable_during_capture=$false
Check 'unstable_capture_rejected' {Test-WCRelocatedPayload $changed $local} $true
$changed=$originalJson | ConvertFrom-Json;$changed.files[0].sha256='0'*64
Check 'changed_payload_rejected' {Test-WCRelocatedPayload $changed $local} $true
$changed=$originalJson | ConvertFrom-Json;$changed.files=@($changed.files | Where-Object { $_.path.EndsWith('WonderChess.exe') })
Check 'missing_manifest_member_rejected' {Test-WCRelocatedPayload $changed $local} $true
New-Item -ItemType Directory -Path (Join-Path $local 'WonderChess/Saved') | Out-Null
[IO.File]::WriteAllText((Join-Path $local 'WonderChess/Saved/log.txt'),'SYNTHETIC RUNTIME LOG')
Check 'runtime_saved_excluded' {Test-WCRelocatedPayload $manifest $local}
[IO.File]::WriteAllText((Join-Path $local 'unmanifested.pak'),'SYNTHETIC EXTRA PAYLOAD')
Check 'extra_payload_rejected' {Test-WCRelocatedPayload $manifest $local} $true
$out=[ordered]@{status='PASS';evidence_kind='SYNTHETIC_INPUT_AND_PAYLOAD_FIXTURES_ONLY';checks=$results.Count;results=@($results)
    game_launched=$false;network_connection_attempted=$false;physical_lan_acceptance='NOT_RUN'
    launcher_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    helper_sha256=(Get-FileHash -LiteralPath (Join-Path $root 'tests/runtime/packaged_payload.ps1') -Algorithm SHA256).Hash.ToLowerInvariant()}
$out | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'fixture-results.json') -Encoding utf8
Write-Output ($out | Select-Object status,evidence_kind,checks,game_launched,network_connection_attempted,launcher_sha256 | ConvertTo-Json)
