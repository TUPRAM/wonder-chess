param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'packaged_payload.ps1')
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$output=[IO.Path]::GetFullPath($OutputDirectory)
if (-not $output.StartsWith((Join-Path $workspace 'reports')+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Fixture evidence must stay under workspace reports' }
if (Test-Path -LiteralPath $output) { throw 'Preserve previous fixture evidence' }
New-Item -ItemType Directory -Path $output|Out-Null
$results=@()
foreach($case in @('valid','changed-ucas','unexpected-file','missing-file','duplicate-entry','outside-root','legacy-executable-only','runtime-saved')) {
    $package=Join-Path $output $case
    New-Item -ItemType Directory -Path $package|Out-Null
    $payload=@()
    foreach($name in @('fixture.exe','fixture.pak','fixture.ucas')) {
        $path=Join-Path $package $name
        [IO.File]::WriteAllText($path,'File-fixture bytes only; never a game executable or gameplay evidence.')
        $payload += [PSCustomObject]@{group='packaged_payload';path=$path;bytes=(Get-Item -LiteralPath $path).Length;sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
    }
    $manifest=[PSCustomObject]@{package_root=$package;package_report=@{exit_code=0};configuration='Shipping';input_files_stable_during_capture=$true;files=$payload;catalog_digest=('a'*64)}
    switch($case) {
        'changed-ucas' {[IO.File]::AppendAllText((Join-Path $package 'fixture.ucas'),'changed')}
        'unexpected-file' {[IO.File]::WriteAllText((Join-Path $package 'unexpected.dll'),'extra')}
        'missing-file' {$manifest.files += [PSCustomObject]@{group='packaged_payload';path=(Join-Path $package 'missing.utoc');bytes=1;sha256=('0'*64)}}
        'duplicate-entry' {$manifest.files += $payload[0]}
        'outside-root' {$external=Join-Path $output 'outside.fixture';[IO.File]::WriteAllText($external,'outside');$manifest.files += [PSCustomObject]@{group='packaged_payload';path=$external;bytes=7;sha256=(Get-FileHash -LiteralPath $external).Hash.ToLowerInvariant()}}
        'legacy-executable-only' {$manifest.files=@([PSCustomObject]@{group='built_executable';path=$payload[0].path;sha256=$payload[0].sha256})}
        'runtime-saved' {New-Item -ItemType Directory -Path (Join-Path $package 'WonderChess/Saved') -Force|Out-Null;[IO.File]::WriteAllText((Join-Path $package 'WonderChess/Saved/session.json'),'Runtime fixture excluded from payload')}
    }
    $accepted=$false;$detail=$null;$verification=$null
    try {$verification=Test-WCPackagedPayload -Manifest $manifest -PackageRoot $package;$accepted=$true} catch {$detail=$_.Exception.Message}
    $expected=$case -in @('valid','runtime-saved')
    $results += [ordered]@{case=$case;pass=($accepted -eq $expected);expected_acceptance=$expected;actual_acceptance=$accepted;detail=$detail}
    $manifestPath=Join-Path $output ($case+'-manifest.json')
    $manifest|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $manifestPath -Encoding utf8
    $trial=[ordered]@{provenance_path=$manifestPath;provenance_sha256=(Get-FileHash -LiteralPath $manifestPath).Hash.ToLowerInvariant();payload_verification=$verification}
    $trial|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $output ($case+'-trial.json')) -Encoding utf8
}
$report=[ordered]@{boundary='File fixtures test preflight acceptance and rejection only. No game launched; no network or gameplay certification.';checks=$results;passed=@($results|Where-Object pass).Count;failed=@($results|Where-Object {-not $_.pass}).Count}
$report|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $output 'preflight-fixture-results.json') -Encoding utf8
$report|ConvertTo-Json -Depth 8
if($report.failed){exit 1}
