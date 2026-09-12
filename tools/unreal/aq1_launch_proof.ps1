[CmdletBinding()]
param(
    [ValidateSet('GalleryMotion','MatchCapture','MatchProfile')][string]$Mode='GalleryMotion',
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z][A-Za-z0-9_]{0,63}$')][string]$Revision,
    [Parameter(Mandatory=$true)][string]$EvidenceDirectory,
    [string]$Editor='C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe',
    [ValidateRange(60,7200)][int]$ExitAfter=900,
    [switch]$Baseline
)
$ErrorActionPreference='Stop'
$ProjectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$Project=Join-Path $ProjectRoot 'game/WonderChess.uproject'
$Evidence=[IO.Path]::GetFullPath($EvidenceDirectory)
$ReportsPrefix=(Join-Path $ProjectRoot 'reports')+[IO.Path]::DirectorySeparatorChar
if(-not $Evidence.StartsWith($ReportsPrefix,[StringComparison]::OrdinalIgnoreCase)){throw 'EvidenceDirectory must be below this repository reports directory.'}
if(Test-Path -LiteralPath $Evidence){throw 'Use a fresh evidence directory; retained evidence must not be overwritten.'}
if(-not(Test-Path -LiteralPath $Editor -PathType Leaf)){throw 'UnrealEditor executable is missing.'}
if(-not $Baseline){
    $Candidate=Join-Path $ProjectRoot "game/Content/WonderChess/Candidates/AQ1/$Revision/SK_wc_u_human_guardian.uasset"
    if(-not(Test-Path -LiteralPath $Candidate -PathType Leaf)){throw 'Candidate mesh has not been imported into this revision.'}
}
New-Item -ItemType Directory -Path $Evidence | Out-Null
$Arguments=@($Project,'-game','-windowed','-ResX=1920','-ResY=1080','-ForceRes',"-WCEvidenceDir=$Evidence","-abslog=$(Join-Path $Evidence 'game.log')")
if(-not $Baseline){$Arguments+="-WCAQ1HeroRoot=/Game/WonderChess/Candidates/AQ1/$Revision"}
switch($Mode){
    'GalleryMotion' {$Arguments+=@('-WCReviewMotion','-WCReviewHero=wc_u_human_guardian')}
    'MatchCapture' {$Arguments+=@('-WCExercise','-WCShots','-WCExerciseSeed=828301','-WCFollowHero=0',"-WCExitAfter=$ExitAfter")}
    'MatchProfile' {$Arguments+=@('-WCExercise','-WCProfile','-WCExerciseSeed=828301','-WCFollowHero=0',"-WCExitAfter=$ExitAfter")}
}
$Record=[ordered]@{
    started_utc=[DateTime]::UtcNow.ToString('o')
    mode=$Mode
    baseline=[bool]$Baseline
    candidate_revision=$(if($Baseline){$null}else{$Revision})
    executable=$Editor
    arguments=$Arguments
    boundary='Unreal -game with current compiled Editor target and uncooked candidate content. Scripted human-seat input in match modes. Not a packaged build or manual human test. Visual captures and normal-speed profiling run separately.'
    status='STARTED'
}
$Record|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $Evidence 'launch.json') -Encoding UTF8
$QuotedArguments=$Arguments | ForEach-Object { '"'+($_ -replace '"','\"')+'"' }
$Process=Start-Process -FilePath $Editor -ArgumentList $QuotedArguments -PassThru -WindowStyle Hidden
$Record.process_id=$Process.Id
$Record|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $Evidence 'launch.json') -Encoding UTF8
$Process.WaitForExit()
$Record.exit_code=$Process.ExitCode
$Record.ended_utc=[DateTime]::UtcNow.ToString('o')
$Record.status='PROCESS_EXITED_INSPECTION_REQUIRED'
$ReportedErrors=@(Select-String -LiteralPath (Join-Path $Evidence 'game.log') -Pattern 'WC_AQ1_INVALID_ROOT|WC_AQ1_MISSING_ASSET' | ForEach-Object {$_.Line})
$Record.candidate_load_errors=$ReportedErrors
if($ReportedErrors.Count -gt 0){$Record.status='FAILED_CANDIDATE_LOAD'}
$Record|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $Evidence 'launch.json') -Encoding UTF8
if($ReportedErrors.Count -gt 0){throw 'Unreal reported an invalid or incomplete Ada candidate; inspect game.log even if its startup exit code is zero.'}
if($Process.ExitCode -ne 0){throw "Unreal proof process exited $($Process.ExitCode); inspect game.log."}
