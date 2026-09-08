$ErrorActionPreference='Stop'
$root = $PSScriptRoot
$parseErrors=$null; $parseTokens=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $PWD 'tests/runtime/run_shipping_solo.ps1'),[ref]$parseTokens,[ref]$parseErrors)
if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
$definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Test-WCPackagedPayload'},$true)
. ([scriptblock]::Create($definition.Extent.Text))
$fixture=Join-Path $root 'fixture-package'; New-Item -ItemType Directory -Path $fixture | Out-Null
$file=Join-Path $fixture 'payload.pak'; [IO.File]::WriteAllText($file,'authored fixture payload')
$entry=[pscustomobject]@{group='packaged_payload';path=$file;bytes=(Get-Item $file).Length;sha256=(Get-FileHash $file).Hash.ToLowerInvariant()}
$manifest=[pscustomobject]@{input_files_stable_during_capture=$true;files=@($entry)}
$cases=[Collections.Generic.List[string]]::new()
function Reject($Name,$Value) {
    $rejected=$false
    try { $null=Test-WCPackagedPayload -Manifest $Value -PackageRoot $fixture } catch { $rejected=$true }
    if (-not $rejected) {throw ('False acceptance: '+$Name)}
    $cases.Add($Name)
}
$good=Test-WCPackagedPayload -Manifest $manifest -PackageRoot $fixture
if ($good.status -ne 'PASS' -or $good.file_count -ne 1) {throw 'Valid fixture failed'}
$cases.Add('valid payload hashes and membership accepted')
Reject 'missing payload group rejected' ([pscustomobject]@{input_files_stable_during_capture=$true;files=@()})
Reject 'unstable provenance rejected' ([pscustomobject]@{input_files_stable_during_capture=$false;files=@($entry)})
Reject 'duplicate entry rejected' ([pscustomobject]@{input_files_stable_during_capture=$true;files=@($entry,$entry)})
$escape=[pscustomobject]@{group='packaged_payload';path=(Join-Path $root 'outside.pak');bytes=0;sha256='0'}
Reject 'manifest path escape rejected' ([pscustomobject]@{input_files_stable_during_capture=$true;files=@($escape)})
$missing=[pscustomobject]@{group='packaged_payload';path=(Join-Path $fixture 'absent.pak');bytes=0;sha256='0'}
Reject 'missing manifested file rejected' ([pscustomobject]@{input_files_stable_during_capture=$true;files=@($missing)})
New-Item -ItemType Directory -Path (Join-Path $fixture 'Saved') | Out-Null
[IO.File]::WriteAllText((Join-Path $fixture 'Saved/runtime.log'),'runtime only')
$good=Test-WCPackagedPayload -Manifest $manifest -PackageRoot $fixture
if ($good.status -ne 'PASS') {throw 'Saved exclusion failed'}
$cases.Add('runtime Saved directory explicitly excluded')
[IO.File]::WriteAllText($file,'changed fixture payload!')
Reject 'modified payload bytes rejected' $manifest
[IO.File]::WriteAllText($file,'authored fixture payload')
[IO.File]::WriteAllText((Join-Path $fixture 'unexpected.pak'),'unexpected')
Reject 'unmanifested payload file rejected' $manifest
[ordered]@{status='PASS';checks=$cases.Count;cases=@($cases);boundary='Synthetic preflight helper tests, no executable launched'} | ConvertTo-Json -Depth 5 | Tee-Object -FilePath (Join-Path $root 'runner-negative-checks.json')
