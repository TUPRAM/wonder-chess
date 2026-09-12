param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (-not $output.StartsWith((Join-Path $workspace 'reports') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Use a fresh evidence directory under workspace reports.'
}
if (Test-Path -LiteralPath $output) { throw 'Preserve previous launch-resolution evidence.' }
$launcher = Join-Path $workspace 'tools/unreal/launch_alpha.ps1'
$source = Get-Content -LiteralPath $launcher -Raw
$tokens = $null; $parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($launcher, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
$parameter = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'Executable' }
$command = $parameter.DefaultValue.Find({ param($node) $node -is [System.Management.Automation.Language.CommandAst] }, $true)
if (-not $command -or $command.GetCommandName() -ne 'Join-Path' -or $command.CommandElements.Count -ne 3 -or
    $command.CommandElements[1] -isnot [System.Management.Automation.Language.VariableExpressionAst] -or
    $command.CommandElements[1].VariablePath.UserPath -ne 'PSScriptRoot' -or
    $command.CommandElements[2] -isnot [System.Management.Automation.Language.StringConstantExpressionAst]) {
    throw 'Expected the launcher executable default to be a literal path relative to its own directory.'
}
# Read the parsed default only. Never invoke or dot-source the launch script.
$resolved = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $launcher) $command.CommandElements[2].Value))
$state = Get-Content -LiteralPath (Join-Path $workspace 'reports/implementation_state.json') -Raw | ConvertFrom-Json
$expected = [IO.Path]::GetFullPath((Join-Path $workspace $state.update_delivery.package_launcher))
$provenancePath = Join-Path $workspace $state.update_delivery.provenance
$provenance = Get-Content -LiteralPath $provenancePath -Raw | ConvertFrom-Json
$payloadLauncher = @($provenance.files | Where-Object { $_.group -eq 'packaged_payload' -and $_.path -eq $resolved })
$inner = Join-Path (Split-Path -Parent $resolved) 'WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe'
$innerHash = if (Test-Path -LiteralPath $inner -PathType Leaf) { (Get-FileHash -LiteralPath $inner -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
$checks = @(
    [ordered]@{name='Default resolves to the recorded current Update24 launcher';pass=($resolved -eq $expected)},
    [ordered]@{name='Resolved launcher exists';pass=(Test-Path -LiteralPath $resolved -PathType Leaf)},
    [ordered]@{name='Default launcher belongs to the current immutable payload';pass=($payloadLauncher.Count -eq 1)},
    [ordered]@{name='Default package contains the recorded current Shipping executable';pass=($innerHash -eq $state.update_delivery.inner_executable_sha256)}
)
$failed = @($checks | Where-Object { -not $_.pass }).Count
$report = [ordered]@{
    status = $(if ($failed) { 'FAIL' } else { 'PASS_LAUNCH_RESOLUTION_ONLY' })
    utc = [DateTime]::UtcNow.ToString('o')
    launcher_source = $launcher
    launcher_source_sha256 = (Get-FileHash -LiteralPath $launcher -Algorithm SHA256).Hash.ToLowerInvariant()
    resolved_default = $resolved; expected_current_launcher = $expected
    inner_executable = $inner; inner_executable_sha256 = $innerHash
    provenance = $provenancePath
    provenance_sha256 = (Get-FileHash -LiteralPath $provenancePath -Algorithm SHA256).Hash.ToLowerInvariant()
    checks = $checks; passed = $checks.Count - $failed; failed = $failed
    boundary = 'Parsed launch-path and existing payload identity only. No launcher or game executed; no gameplay, rendering, network or release acceptance.'
}
New-Item -ItemType Directory -Path $output | Out-Null
[IO.File]::WriteAllText((Join-Path $output 'launcher-source.ps1.txt'), $source)
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $output 'launch-resolution.json') -Encoding utf8
$report | ConvertTo-Json -Depth 5
if ($failed) { exit 1 }
