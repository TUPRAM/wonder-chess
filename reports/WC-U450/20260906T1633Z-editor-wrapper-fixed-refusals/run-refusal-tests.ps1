[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Repo = 'C:/Users/iputu/Documents/Wonder Chess'
$Wrapper = Join-Path $Repo 'tools/unreal/invoke_editor_task.ps1'
$Editor = 'C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$Evidence = $PSScriptRoot
if (Test-Path -LiteralPath (Join-Path $Evidence 'result.json')) { throw 'This refusal evidence run already exists.' }
$Cases = Join-Path $Evidence 'cases'
New-Item -ItemType Directory -Path $Cases | Out-Null
$global:WCRefusalLaunchCalls = [Collections.Generic.List[object]]::new()
# A defensive backstop: a failed refusal must never launch the real editor.
function Start-Process {
    [CmdletBinding()]
    param([string]$FilePath,[object]$ArgumentList,[string]$WindowStyle,[switch]$PassThru,
          [string]$RedirectStandardOutput,[string]$RedirectStandardError)
    $global:WCRefusalLaunchCalls.Add([ordered]@{file=$FilePath;arguments=$ArgumentList})
    throw 'TEST_BACKSTOP_EDITOR_LAUNCH_BLOCKED'
}
$Names = @('WC_EDITOR_TASK','WC_EDITOR_REPORT_DIR','WC_IMPORT_HERO','WC_IMPORT_AUDIO','WC_IMPORT_AUDIO_ONLY')
$EnvironmentBefore = @{}
foreach ($Name in $Names) { $EnvironmentBefore[$Name] = [Environment]::GetEnvironmentVariable($Name,'Process') }
$WrapperHash = (Get-FileHash -LiteralPath $Wrapper -Algorithm SHA256).Hash.ToLowerInvariant()
$Rows = [Collections.Generic.List[object]]::new()
function Invoke-RefusalCase {
    param([string]$Name,[hashtable]$Overrides,[string]$Expected,[switch]$Preserve)
    $Parameters = @{ Task='import_alpha_assets';Editor=$Editor;ReportDirectory=(Join-Path $Cases $Name) }
    foreach ($Key in $Overrides.Keys) { $Parameters[$Key]=$Overrides[$Key] }
    $Destination = [IO.Path]::GetFullPath($Parameters.ReportDirectory)
    $Existed = Test-Path -LiteralPath $Destination
    $Marker = Join-Path $Destination 'retained-evidence.bin'
    $Before = $null
    if ($Preserve) {
        New-Item -ItemType Directory -Path $Destination | Out-Null
        [IO.File]::WriteAllBytes($Marker,[byte[]](0,19,44,255,10,13,99,0))
        $Before = (Get-FileHash -LiteralPath $Marker -Algorithm SHA256).Hash
        $Existed=$true
    }
    $CallsBefore=$global:WCRefusalLaunchCalls.Count
    $ErrorText=''
    try { & $Wrapper @Parameters | Out-Null } catch { $ErrorText=$_.Exception.Message }
    $Calls=$global:WCRefusalLaunchCalls.Count-$CallsBefore
    $EnvironmentPreserved=$true; $EnvironmentAfter=@{}
    foreach ($Variable in $Names) { $EnvironmentAfter[$Variable]=[Environment]::GetEnvironmentVariable($Variable,'Process')
        if ([Environment]::GetEnvironmentVariable($Variable,'Process') -cne $EnvironmentBefore[$Variable]) { $EnvironmentPreserved=$false }
    }
    $Created=(-not $Existed) -and (Test-Path -LiteralPath $Destination)
    $HashPreserved=$true
    if ($Preserve) { $HashPreserved=(Get-FileHash -LiteralPath $Marker -Algorithm SHA256).Hash -ceq $Before }
    $Pass=$Calls -eq 0 -and $ErrorText.Contains($Expected) -and -not $Created -and $EnvironmentPreserved -and $HashPreserved
    $Rows.Add([ordered]@{name=$Name;pass=$Pass;actual_error=$ErrorText;expected_error_contains=$Expected;
      parameters=$Parameters;intercepted_launch_calls=$Calls;created_output_directory=$Created;
      environment_preserved=$EnvironmentPreserved;environment_before=$EnvironmentBefore;environment_after=$EnvironmentAfter;existing_marker_hash_preserved=$HashPreserved;marker_sha256=$Before})
}
Invoke-RefusalCase invalid-hero @{Hero=@('wc_u_not_real')} 'Unknown alpha hero'
Invoke-RefusalCase path-shaped-hero @{Hero=@('../../not-a-hero')} 'Unknown alpha hero'
Invoke-RefusalCase outside-reports @{ReportDirectory=$Repo} 'inside this project reports folder'
Invoke-RefusalCase traversal-outside-reports @{ReportDirectory=(Join-Path $Repo 'reports/../docs')} 'inside this project reports folder'
Invoke-RefusalCase reports-root-itself @{ReportDirectory=(Join-Path $Repo 'reports')} 'inside this project reports folder'
Invoke-RefusalCase preexisting-evidence @{} 'Existing evidence directory' -Preserve
Invoke-RefusalCase hero-on-wrong-task @{Task='import_arena';Hero=@('wc_u_human_guardian')} 'only supported for import_alpha_assets'
Invoke-RefusalCase audio-on-wrong-task @{Task='import_data_tables';IncludeAudio=$true} 'only supported for import_alpha_assets'
Invoke-RefusalCase audioonly-on-wrong-task @{Task='create_lobby_sky';AudioOnly=$true} 'only supported for import_alpha_assets'
Invoke-RefusalCase incompatible-audio-hero @{AudioOnly=$true;Hero=@('wc_u_human_guardian')} 'cannot also select heroes'
Invoke-RefusalCase missing-editor @{Editor=(Join-Path $Evidence 'absent-editor.exe')} 'editor executable is absent'
Invoke-RefusalCase invalid-task @{Task='not-a-task'} 'ValidateSet'
Invoke-RefusalCase wrong-case-hero @{Hero=@('WC_U_HUMAN_GUARDIAN')} 'Unknown alpha hero'
Invoke-RefusalCase wrong-case-task @{Task='IMPORT_ALPHA_ASSETS'} 'exact lowercase spelling'
function Invoke-RestorationCase {
    param([string]$Name,[hashtable]$Initial)
    foreach ($Variable in $Names) {
        if ($null -eq $Initial[$Variable]) { Remove-Item -LiteralPath ('Env:'+$Variable) -ErrorAction SilentlyContinue }
        else { [Environment]::SetEnvironmentVariable($Variable,$Initial[$Variable],'Process') }
    }
    $Parameters=@{Task='import_alpha_assets';Editor=$Editor;ReportDirectory=(Join-Path $Cases $Name);Hero=@('wc_u_human_guardian')}
    $BeforeCalls=$global:WCRefusalLaunchCalls.Count
    $ErrorText=''
    try { & $Wrapper @Parameters | Out-Null } catch { $ErrorText=$_.Exception.Message }
    $Preserved=$true
    $After=@{}
    foreach ($Variable in $Names) {
        $After[$Variable]=[Environment]::GetEnvironmentVariable($Variable,'Process')
        if ($After[$Variable] -cne $Initial[$Variable]) { $Preserved=$false }
    }
    $ProcessReport=Get-Content -LiteralPath (Join-Path $Parameters.ReportDirectory 'process.json') -Raw | ConvertFrom-Json
    $Pass=$Preserved -and $global:WCRefusalLaunchCalls.Count-$BeforeCalls -eq 1 -and
        $ErrorText -ceq 'TEST_BACKSTOP_EDITOR_LAUNCH_BLOCKED' -and $ProcessReport.status -ceq 'FAIL' -and
        $null -eq $ProcessReport.pid -and $null -eq $ProcessReport.exit_code
    $Rows.Add([ordered]@{name=$Name;pass=$Pass;kind='finally restoration after intercepted launch, not an editor task';
        environment_before=$Initial;environment_after=$After;environment_preserved=$Preserved;
        intercepted_launch_calls=$global:WCRefusalLaunchCalls.Count-$BeforeCalls;actual_error=$ErrorText;
        process_report_status=$ProcessReport.status;process_report_pid=$ProcessReport.pid;process_report_exit_code=$ProcessReport.exit_code})
    foreach ($Variable in $Names) {
        if ($null -eq $EnvironmentBefore[$Variable]) { Remove-Item -LiteralPath ('Env:'+$Variable) -ErrorAction SilentlyContinue }
        else { [Environment]::SetEnvironmentVariable($Variable,$EnvironmentBefore[$Variable],'Process') }
    }
}
Invoke-RestorationCase restore-absent @{}
Invoke-RestorationCase restore-mixed @{WC_EDITOR_TASK='retained task';WC_IMPORT_HERO='retained hero';WC_IMPORT_AUDIO='0'}
$Failures=@($Rows | Where-Object {-not $_.pass}).Count
$Result=[ordered]@{status=$(if($Failures){'FAIL'}else{'PASS'});executed_utc=[DateTime]::UtcNow.ToString('o');
    method='Actual PowerShell wrapper refusal paths. Start-Process is intercepted as a defensive backstop: zero editor launches. Unexpected attempts remain failing results.';
    powershell_version=$PSVersionTable.PSVersion.ToString();wrapper=$Wrapper;wrapper_sha256=$WrapperHash;
    wrapper_unchanged=((Get-FileHash -LiteralPath $Wrapper -Algorithm SHA256).Hash.ToLowerInvariant() -ceq $WrapperHash);
    tests=$Rows.Count;passed=$Rows.Count-$Failures;failed=$Failures;editor_processes_launched=0;intercepted_launch_calls=$global:WCRefusalLaunchCalls;
    checks=$Rows}
$Result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $Evidence 'result.json') -Encoding utf8
Write-Output ('tests={0} passed={1} failed={2} editor_launches=0' -f $Rows.Count,($Rows.Count-$Failures),$Failures)
if ($Failures) { exit 1 }


