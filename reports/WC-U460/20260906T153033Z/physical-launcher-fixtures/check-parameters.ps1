$ErrorActionPreference='Stop'
$source='C:\Users\iputu\Documents\Wonder Chess\tests\runtime\run_physical_lan.ps1'
$errors=$null;$tokens=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($source,[ref]$tokens,[ref]$errors)
if ($errors.Count) {throw ($errors | Out-String)}
# Execute only the real parameter block, never any launcher body or connection.
$bind=[scriptblock]::Create($ast.ParamBlock.Extent.Text + "`n'PARAMETER_BIND_ONLY'")
$base=@{Role='host';HostAddress='192.168.1.20';Port=7780;PackageRoot='C:\Fixture';ProvenancePath='C:\Fixture.json';OutputDirectory='C:\Evidence\fresh';MachineLabel='PC-A'}
$checks=@()
foreach ($case in @(
    @{name='valid_defaults';key=$null;value=$null;reject=$false},
    @{name='role_rejected';key='Role';value='server';reject=$true},
    @{name='port_zero';key='Port';value=0;reject=$true},
    @{name='port_overflow';key='Port';value=65536;reject=$true},
    @{name='speed_zero';key='SimulationSpeed';value=0;reject=$true},
    @{name='duration_overflow';key='Seconds';value=7201;reject=$true},
    @{name='input_mode_rejected';key='InputMode';value='bot';reject=$true},
    @{name='machine_label_rejected';key='MachineLabel';value='../PC-A';reject=$true}
)) {
    $parameters=$base.Clone()
    if ($case.key) {$parameters[$case.key]=$case.value}
    $caught=$false
    try {$actual=& $bind @parameters; if ($actual -ne 'PARAMETER_BIND_ONLY') {throw 'Body mismatch'}} catch {$caught=$true}
    if ($caught -ne $case.reject) {throw ('Unexpected parameter result: '+$case.name)}
    $checks+=@{name=$case.name;status='PASS';rejection=$caught}
}
$record=[ordered]@{status='PASS';checks=$checks.Count;results=$checks;evidence_kind='PARAMETER_BINDING_ONLY';game_launched=$false;network_connection_attempted=$false;launcher_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'parameter-results.json') -Encoding utf8
$record | ConvertTo-Json -Depth 8
