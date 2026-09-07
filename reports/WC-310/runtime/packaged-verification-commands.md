# Packaged verification execution procedure

Prepared instrumentation is not executed acceptance evidence. The next full packaged candidate path must come from a successful root-owned package build. The existing WC-300 minimal package does not contain the full current recorder or game integration and must not be substituted.

Set `$Exe` to that actual packaged `WonderChess.exe` and `$Evidence` to a fresh absolute evidence directory, then run the following from PowerShell. Paths are passed as process arguments, not shell-evaluated strings. The full source path and executable SHA256 must be recorded with each run. Launch the executable from its packaged directory, without Unreal Editor. These commands use background windows for scripted verification; separate interactive UI/audio checks still require a visible game window.

```powershell
$Exe = (Resolve-Path -LiteralPath '<actual full packaged candidate>/WonderChess.exe').Path
$Evidence = [System.IO.Path]::GetFullPath('<fresh absolute evidence directory>')
New-Item -ItemType Directory -Path $Evidence -Force | Out-Null
Get-FileHash -Algorithm SHA256 -LiteralPath $Exe | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Evidence 'executable-sha256.json')
$Common = @('-unattended', '-nosplash', '-windowed', '-ResX=1920', '-ResY=1080', '-ForceRes', '-d3d11', '-WCExercise', '-WCAuthorityChecks', '-WCProfile', '-WCShots', '-ExecCmds="r.ScreenPercentage 100"')
```

For one human plus seven bots with an actual restart request after the first results, launch one process. It uses human-seat controller RPCs to buy, deploy, level and ready while the normal seven bots run. The game rules remain unchanged; `WCFast=10` advances fixed simulation steps ten times faster and must be disclosed in the results. The script stops after two finished namespaces or the specified wall timeout; the timeout by itself does not prove completion.

```powershell
$SoloDir = Join-Path $Evidence 'solo-restart'
New-Item -ItemType Directory -Path $SoloDir -Force | Out-Null
$Solo = Start-Process -FilePath $Exe -WorkingDirectory (Split-Path -LiteralPath $Exe) -WindowStyle Hidden -PassThru -ArgumentList ($Common + @('-WCFast=10', '-WCRestartOnce', '-WCExitAfter=360', ('-WCEvidenceDir="' + $SoloDir + '"'), ('-abslog="' + (Join-Path $SoloDir 'game.log') + '"')))
$Solo.Id
```

For a complete two-human/six-bot local-network run, use distinct directories and actual processes. The host waits for both connected human controllers before the exercise starts the tournament. Do not add `WCAutoStart`, which can start before the second process arrives. The client joins the listen server through loopback IP; this certifies separate-process local networking on one physical machine when it passes, not two physical PCs or an external LAN.

```powershell
$HostDir = Join-Path $Evidence 'host'
$ClientDir = Join-Path $Evidence 'client'
New-Item -ItemType Directory -Path $HostDir,$ClientDir -Force | Out-Null
$HostArgs = @('/Game/WonderChess/Maps/L_WC_Courtyard?listen?WCHumans=2') + $Common + @('-WCFast=10', '-WCExitAfter=360', ('-WCEvidenceDir="' + $HostDir + '"'), ('-abslog="' + (Join-Path $HostDir 'game.log') + '"'))
$ClientArgs = @('127.0.0.1:7777') + $Common + @('-WCFast=10', '-WCExitAfter=350', ('-WCEvidenceDir="' + $ClientDir + '"'), ('-abslog="' + (Join-Path $ClientDir 'game.log') + '"'))
$HostProcess = Start-Process -FilePath $Exe -WorkingDirectory (Split-Path -LiteralPath $Exe) -WindowStyle Hidden -PassThru -ArgumentList $HostArgs
```

Inspect the host log for its actual listening state before issuing the client launch; elapsed time alone is not evidence that listen succeeded. Once the host has logged an initialized listen driver on port7777:

```powershell
$ClientProcess = Start-Process -FilePath $Exe -WorkingDirectory (Split-Path -LiteralPath $Exe) -WindowStyle Hidden -PassThru -ArgumentList $ClientArgs
@{host_pid=$HostProcess.Id;client_pid=$ClientProcess.Id;host_args=$HostArgs;client_args=$ClientArgs} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $Evidence 'launch.json')
```

Use the match-prefixed session files for the shared nonzero namespace when auditing complete matches; a later deliberate process exit may make a surviving client return to menu. Both processes must record results before exit for completion acceptance. Run `audit_network_evidence.py --require-complete` on that pair and `summarize_frame_evidence.py` on each process. The exact12-visible/4-live-encounter subset,1920x1080 viewport, actual render percentage, GPU samples and named hardware all remain separate reported conditions. Fast simulation and simultaneous second-process rendering affect performance and must not be hidden.

For client departure, repeat with fresh directories and `WCFast=1`, host `WCExitAfter=120`, client `WCExitAfter=60`. The real client process exits, authority must preserve its seat resources and install a bot, and the host must continue. Audit with `audit_session_transitions.py client-loss`. For host departure, use host60/client120 and `audit_session_transitions.py host-loss`; inspect the client-visible abort message separately. The driver stops automatic commands and restarts after persistent abort. Fresh rejoin needs a third real process after takeover, with a new evidence directory; current runtime explicitly refuses joining or rejoining a running match and returns it to menu. Record the actual rejection message and absence of assigned active human seat; no rejoin result is presumed by this document.

An additional delayed/lossy repeat can append `-PktLag=80 -PktLoss=3` to both network process argument arrays. Installed UE5.7 source `Engine/Private/Net/NetEmulationHelper.cpp:534` parses these only under `DO_ENABLE_NET_TEST`; `NetDriver.cpp:740` applies command-line settings. Require actual game logs saying `PktLag set to 80` and `PktLoss set to 3` before claiming emulation was active. It is nominal80ms outgoing emulation plus3% outgoing packet loss per enabled driver, not a measured80ms RTT or physical network condition. Do not count the command-line switches alone as applied latency/loss.

At preparation and combat, inspect actual screenshots for shop/bench/board readability, selection, HUD scale and unit placement; at elimination inspect spectating; at results inspect final places and restart. These image/audio/human interaction judgments cannot be inferred from JSON test passes. Automatic screenshots are captured per phase/round; optional art-review scenes are separate from full-match evidence.
