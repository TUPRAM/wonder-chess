[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateSet('import_arena','import_alpha_assets','import_data_tables','import_neutral_assets','import_lobby_assets','create_lobby_sky')][string]$Task,
    [Parameter(Mandatory=$true)][string]$Editor,
    [Parameter(Mandatory=$true)][string]$ReportDirectory,
    [string[]]$Hero = @(),
    [switch]$IncludeAudio,
    [switch]$AudioOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($Task -cne $Task.ToLowerInvariant()) { throw 'Task names must use their exact lowercase spelling.' }
$Root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$Reports = [IO.Path]::GetFullPath((Join-Path $Root 'reports'))
$Output = [IO.Path]::GetFullPath($ReportDirectory)
if (-not $Output.StartsWith($Reports + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Choose a fresh report directory inside this project reports folder.'
}
if (Test-Path -LiteralPath $Output) { throw 'Existing evidence directory will not be overwritten.' }
if (-not (Test-Path -LiteralPath $Editor -PathType Leaf)) { throw 'The supplied Unreal editor executable is absent.' }
if (($Hero.Count -gt 0 -or $IncludeAudio -or $AudioOnly) -and $Task -ne 'import_alpha_assets') {
    throw 'Hero/audio selection is only supported for import_alpha_assets.'
}
if ($AudioOnly -and $Hero.Count -gt 0) { throw 'Audio-only import cannot also select heroes.' }
$Rules = Get-Content -LiteralPath (Join-Path $Root 'data/rules.alpha.json') -Raw | ConvertFrom-Json
foreach ($Id in $Hero) {
    if ($Id -cnotin $Rules.alpha_unit_ids) { throw "Unknown alpha hero: $Id" }
}
$Project = (Join-Path $Root 'game/WonderChess.uproject').Replace('\','/')
# Unreal's Python command parser interprets backslash escapes even inside quotes.
$Script = (Join-Path $PSScriptRoot 'run_editor_task.py').Replace('\','/')
New-Item -ItemType Directory -Path $Output | Out-Null
$Arguments = @(('"'+$Project+'"'), '-unattended', '-nop4', '-NullRHI', '-nosplash',
    ('-ExecutePythonScript="'+$Script+'"'), ('-abslog="'+($Output+'/editor.log').Replace('\','/')+'"'))
$Names = @('WC_EDITOR_TASK','WC_EDITOR_REPORT_DIR','WC_IMPORT_HERO','WC_IMPORT_AUDIO','WC_IMPORT_AUDIO_ONLY')
$Previous = @{}
foreach ($Name in $Names) { $Previous[$Name] = [Environment]::GetEnvironmentVariable($Name, 'Process') }
$Result = [ordered]@{task=$Task; status='STARTED'; started_utc=[DateTime]::UtcNow.ToString('o'); editor=$Editor;
    arguments=$Arguments; heroes=$Hero; include_audio=[bool]$IncludeAudio; audio_only=[bool]$AudioOnly;
    script_sha256=(Get-FileHash -LiteralPath $Script).Hash.ToLower(); pid=$null; exit_code=$null; task_success=$false}
$Process = $null
try {
    $env:WC_EDITOR_TASK=$Task
    $env:WC_EDITOR_REPORT_DIR=$Output
    $env:WC_IMPORT_HERO=$Hero -join ','
    $env:WC_IMPORT_AUDIO=if($IncludeAudio){'1'}else{'0'}
    $env:WC_IMPORT_AUDIO_ONLY=if($AudioOnly){'1'}else{'0'}
    $Process = Start-Process -FilePath $Editor -ArgumentList $Arguments -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput ($Output+'/stdout.log') -RedirectStandardError ($Output+'/stderr.log')
    $Process.Handle | Out-Null
    $Result.pid=$Process.Id
    $Result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath ($Output+'/process.json') -Encoding UTF8
    Write-Output "Running $Task in $Output (PID $($Process.Id))"
    $Process.WaitForExit()
    $Result.exit_code=$Process.ExitCode
    $TaskReport=Join-Path $Output ($Task+'.json')
    if (-not (Test-Path -LiteralPath $TaskReport -PathType Leaf)) { throw 'Editor exited without the required task report; inspect editor.log.' }
    $TaskResult=Get-Content -LiteralPath $TaskReport -Raw | ConvertFrom-Json
    $Result.task_success=($TaskResult.success -eq $true)
    if ($Process.ExitCode -ne 0 -or -not $Result.task_success) { throw 'Editor task failed; inspect its report and editor.log.' }
    $Result.status='TASK_EXECUTED_IMPORT_DETAILS_REQUIRE_INSPECTION'
} catch {
    $Result.status='FAIL'
    $Result.error=$_.Exception.Message
    throw
} finally {
    $Result.finished_utc=[DateTime]::UtcNow.ToString('o')
    $Result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath ($Output+'/process.json') -Encoding UTF8
    foreach ($Name in $Names) {
        if ($null -eq $Previous[$Name]) { Remove-Item -LiteralPath ('Env:'+$Name) -ErrorAction SilentlyContinue }
        else { [Environment]::SetEnvironmentVariable($Name, $Previous[$Name], 'Process') }
    }
    if ($null -ne $Process) { $Process.Dispose() }
}
Write-Output $Result.status
