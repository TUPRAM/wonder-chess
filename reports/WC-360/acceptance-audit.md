# Playable-alpha acceptance audit

Audit cut-off: **2026-09-06 14:45 Singapore / 06:45 UTC**. Reviewer: Codex toolchain/audit lane. This is a read-only review of current implementation, existing evidence and two actual screenshots. Only this report was written. No editor, game, build or binary mutation was launched by this audit. Later root-owned executions must be assessed separately.

Authority read: `AGENTS.md`, `docs/MASTER_IMPLEMENTATION_v3.md`, `docs/tasks/WC-360.md`, `docs/QA_ACCEPTANCE.md`, `docs/UI_AUDIO_AND_ONBOARDING.md`, `docs/UNREAL_IMPLEMENTATION.md`, and the `wc-release-evidence` skill. The active v3 master remains authoritative where an older task title differs. Existing Python/reference passes do not establish a playable game.

## Current conclusion

**The full native Windows Development package is built. Complete packaged gameplay acceptance is not yet established by the evidence available at this cut-off.** The package log `reports/WC-360/package/package-Development-20260906T064135Z.log` ends `BUILD SUCCESSFUL` and `AutomationTool exiting with ExitCode=0 (Success)`; BuildCookRun took 179.98 seconds. Candidate 5 editor compilation separately passed in 68.02 seconds (`reports/WC-350/candidate5-editor-build.log`).

Actual files exist:

- Launcher: `builds/Windows-Alpha/WonderChess.exe`, 164,864 bytes, SHA256 `e3c22795d6f2265fcbd88b66e1c5b33b7b017aac916be1f3dca4d0232020a93a`.
- Game binary: `builds/Windows-Alpha/WonderChess/Binaries/Win64/WonderChess.exe`, 291,963,392 bytes, SHA256 `11ef996f57ba7aea2ce767e638800b629a6e10157e3b1e2a3d2ab7c8d2fb69e7`.

The whole packaged directory is the deliverable; the small bootstrap executable alone is insufficient. A cold launch from this directory, complete matches, settings persistence and packaged content loads still require their own results. The older `builds/WC-300-Minimal/Windows/WonderChess.exe` is only the previously inspected title checkpoint and must not substitute for this candidate.

## Prioritized open requirements

| Priority | Finding at cut-off | Evidence / next concrete check |
|---|---|---|
| Required release gate, NOT_RUN | Full packaged 1H7B journey, results, restart and elimination/spectating are not yet demonstrated. | The latest manual session `reports/WC-350/manual-ui-v4/match-169-seat-0-pid-39856-session.json` is incomplete in preparation round 1, with two accepted replies. The earlier first-ui run reaches first combat only. Exercise this new executable through two finished namespaces, then inspect visible results and restart. |
| Required release gate, NOT_RUN | Actual separate-process 2H6B, command probes, disconnect takeover, host abort and rejected rejoin are not yet demonstrated. | Prepared recorder/analyzer scripts are implementation, not execution. No paired host/client session evidence was present in the inspected WC-350/WC-360 report inventory. Use distinct processes/directories and the command procedure below. |
| P2 art/readability, open | Defeat is visually weak and full hero attractiveness/detail acceptance remains open. | I opened actual Unreal `game/Saved/WonderChessEvidence/ArtReview/pose-17.png`: all twelve retain an upright, forward-bowed pose at the late Defeat sample. `reports/WC-330/unreal-visual-review.md` also records weak Hit silhouettes, subtle caster/ranger state differences, unresolved fine hand/equipment contact and faceted costume/anatomy. Those are current review findings, not the repaired import-scale defect. The source/export hold means the reviewed roster is still the relevant art baseline. |
| Required release gate, NOT_RUN | Exact busy-combat performance is missing. | Latest manual session has **zero** samples with twelve living visible combatants; it ends in first preparation. Its overall approximately 16.67 ms frame interval is not the required twelve-visible/four-live-encounter performance result. Record named hardware, actual render scale, CPU/render/GPU percentiles, memory and hitches on the qualifying subset. |
| Required usability gate, NOT_RUN | Full click/drag journey, keyboard focus/activation, 720p, EN/ID overflow, fullscreen focus and persistent sliders/reduced motion still need live verification. | The current source implements those controls, and the 1080p preparation screenshot is legible at its recorded scale. No actual 720p, keyboard traversal, drag/swap, settings-relaunch or full recap interaction evidence was found. Source presence does not establish interaction correctness. |
| Required audio/presentation gate, NOT_RUN | All 32 sounds load as saved assets, but actual mixed playback, loudness, repetition, event mapping and music continuity are not yet accepted. | `hero-audio-import-cold.json` is a cold asset read pass. `hero-audio-review.md` explicitly says this lane did not listen. In-game active, area-hit, offscreen-audio suppression, mute/persistence and looping checks remain necessary. |
| Narrow feedback gap, source review | Purchase feedback currently uses authoritative text and highlighted bench/board units; a moving shop-to-bench transfer is not implemented in the inspected HUD. | `UpdateConfirmedFeedback` and `HighlightedUnits` implement truthful confirmation/merge/new-trait feedback. The UI contract separately asks for a small visual transfer. This is a presentation gap, not a failed purchase transaction or a reason to discard the authoritative feedback. |

No new proven P0/P1 crash, wrong-authority mutation or stuck-match defect was identified in this bounded source review. This is not an assurance that unexecuted network, packaged or UI paths are correct. The remaining visual findings cannot be relabeled as a finished-hero pass solely because all mesh and animation imports now validate.

## Current verified evidence and its limits

`reports/WC-360/candidate4-automation/index.json` records **five tests succeeded, zero failed, zero not run**, total 39.6899 seconds:

- `WonderChess.Assets.ImportedAlphaContracts`
- `WonderChess.Data.CanonicalCatalog`
- `WonderChess.Data.RejectInvalidNumericTypes`
- `WonderChess.Runtime.IntegerContracts`
- `WonderChess.Runtime.OneHundredActualCombatTournaments`

The corresponding cold asset report is dated 06:29:11.449 UTC, Unreal `5.7.4-51494982+++UE5+Release-5.7`, catalog digest `3154592665ce21dc65e5afb06f3769655c8be9ec4157fa6779427c8b8fcc092f`. It passed **12 meshes, 84 references to 84 unique animations, and 11,988 sampled bone transforms**. Earlier scale/basis/skeleton and glyph-UV failures are preserved historical failures; the later passing reports supersede them for those specific numerical checks. They do not establish visual attractiveness or packaged rendering.

I counted the candidate 4 tournament CSV: **100 seeds (1–100), 7,118 actual encounters, 1,437 timeout adjudications, 524 ghost encounters, 69,656 bot commands, zero command rejects**. The separate native C++ harness documents 32 mirror formation/side pairs and controlled ability, economic, reservation, pending-projectile and ordering fixtures. Those narrow standalone fixtures are not all individually represented by the five Unreal automation names, and neither suite substitutes for network/UI execution. A final packaged regression run should produce the enhanced provenance, per-hero use/placement, command, failure and timing fields now present in `AWCMatchMode::Regression`.

The supplied baseline execution is preserved in `reports/WC-300/baseline/results.json`: 438 specification/data checks, 63 Python reference tests, 27 generated documents and six catalog artifacts matched; all four supplied commands exited 0. These are baseline data/reference facts, not full-game test counts. Rerun the supplied validators for the final source snapshot when assembling the final handoff.

I also opened `reports/WC-350/manual-ui-v4/match-169-seat-0-pid-39856-phase-0-round-1.png`. It shows actual shop portraits, five offers, eight bench slots, seven named bots, current economy and a labeled guided practice. It contains the older light-priority warning and timed practice label. Candidate 5 source fixes those items; that older screenshot is not proof of the fixes. The camera mostly shows the board at this framing; assess the full arena composition and busy fight in the current package rather than inferring them from an isolated source render.

## Source/default configuration review

The default map, game mode and game instance resolve to the authored menu and compiled runtime classes. Both menu and courtyard maps are explicitly cooked. Heroes, audio, materials, generated DataTables and effects directories are always cooked, while exact JSON source data is staged as UFS for `FFileHelper` reads. The runtime module uses native Engine/Core/JSON/input/render/network dependencies; Python and editor scripting plugins are limited to Editor targets. AndroidFileServer is disabled. No source-directory Python helper is called by the game loop. The strict data loader reports invalid/missing staged data rather than silently substituting invented stats.

`bIncludePrerequisites=False` means the package does not include the Unreal prerequisites installer. Successful execution on this development machine will not prove execution on a clean Windows machine without the required Microsoft runtime. Record that installation boundary; do not claim a clean-machine test that has not occurred. No missing-dependency crash was observed by this audit.

Controller intent derives the seat from the authenticated controller, validates the enum/payload, and submits through the common authority. Private JSON is sent through the owning controller RPC; public deployment JSON omits bench slots/shops/gold/XP. Non-host departure preserves a seat through `TakeOver`; late join/rejoin is explicitly rejected; `UWCNetworkSession` keeps host-loss abort distinct from normal results. Start/restart is host-restricted. These are inspected code paths requiring the actual NET-01/02/03 executions.

The current source also contains untimed first practice, fixed and disclosed shop-seed selection, successful action/merge feedback, explicit physical/magic/true labels, advanced ability timing/range, numerical trait bonuses, early-elimination menu/new-tournament controls, recap metrics derived from events, guarded ready input, looping music, twelve dossier-specific active sound paths and reduced-motion suppression. Older audio-validation and runtime-handoff paragraphs describing missing variants or failing normalized imports are dated pre-fix observations, not current blockers.

Inspected SHA256 source/config snapshot:

| File | SHA256 |
|---|---|
| `game/Source/WonderChessRuntime/Private/WCMatchRuntime.cpp` | `715122ed760f87e28b8347eb59e133f17a4cc635d1caa5d23a86b2ce6038242f` |
| `game/Source/WonderChessRuntime/Private/WCMatchHUD.cpp` | `7be3795f8bf9e17bc1c91aa492204141c332215d5da8729f083b00745f0b01b4` |
| `game/Config/DefaultGame.ini` | `f8ab99c2f5f3c5e193b9ed6879668403fd22ffb208389010714610b6c4eaa38e` |
| `game/Config/DefaultEngine.ini` | `698ef0a983fa9ac5728b27b4c2a17f1837586060d1e7bc4fdc3a53f584e270f8` |

## Exact next execution boundaries

Use the full procedure in `reports/WC-310/runtime/packaged-verification-commands.md`, replacing its placeholder with the actual launcher above. Launch from `builds/Windows-Alpha`, without Unreal Editor, with a fresh absolute evidence directory for each process. Hash both executable files and retain package/build logs with the run. These are **instructions prepared for the next execution, not commands executed by this audit**.

1. Cold visible default launch: `WonderChess.exe -windowed -ResX=1920 -ResY=1080 -d3d11`. Verify actual menu, art/audio, then manual guided practice and full normal 1H7B. Return/restart through the actual UI. Repeat at 1280×720 and after a settings-changing relaunch.
2. Scripted 1H7B/restart: add `-WCExercise -WCAuthorityChecks -WCProfile -WCShots -WCFast=10 -WCRestartOnce -WCExitAfter=360 -WCEvidenceDir="<absolute solo directory>" -abslog="<absolute solo log>"` and `-ExecCmds="r.ScreenPercentage 100"`. Require two finished namespaces. This uses automated commands through a human seat and accelerated simulation; it is not manual usability evidence or normal-speed performance.
3. Actual 2H6B host: first map argument `/Game/WonderChess/Maps/L_WC_Courtyard?listen?WCHumans=2`, then the same exercise/probe/profile/shots settings and its own evidence/log directory. **Do not use WCAutoStart**. Confirm the actual port-7777 listen log, then launch a second process with first argument `127.0.0.1:7777` and a separate evidence/log directory. Require distinct PIDs, 2 human + 6 bot seats, complete matching results and owner-private consistency. Loopback certifies separate-process local networking on one physical PC when it passes; it does not certify two physical PCs.
4. Run `tests/runtime/audit_network_evidence.py <host-match-session> <client-match-session> --require-complete --output <audit.json>` on the shared nonzero finished namespace. Run the frame summarizer separately for each process. A timeout exit does not establish completion.
5. Repeat at normal simulation speed for client departure, host departure and fresh late rejoin; use `audit_session_transitions.py` and inspect the actual abort/rejoin message. Confirm preserved resources and no duplicate seat/gold. For optional `-PktLag=80 -PktLoss=3`, require logs proving those settings were applied; switches alone are not a measured network condition.
6. Packaged actual all-bot regression: `WonderChess.exe -unattended -nosplash -nullrhi -WCRegression=100 -WCEvidenceDir="<absolute regression directory>" -abslog="<absolute regression log>"`. Require attempted=100, failed=0, complete=true, evidence_write_failed=false, all retained trial outcomes and exit 0. This headless combat batch cannot provide rendered performance or human interaction evidence.
7. For the required performance result, run a normal-speed rendered scene with twelve living combatants visible and all four encounters live. The recorded active GPU is NVIDIA GeForce RTX 3060 Laptop GPU; CPU is AMD Ryzen 7 6800H; installed RAM is 16,312,393,728 bytes. Keep the OS-primary AMD integrated adapter distinct from the active RHI adapter. Report actual render percentage, driver, viewport, sample counts, CPU/render/GPU percentiles, hitches and memory; an absent qualifying subset remains NOT_RUN.

The final handoff needs a refreshed central implementation state, package executable hashes/path and launch instructions, source/data/asset paths, completed versus open art defects, actual manual/scripted/network boundaries, final all-bot results, named-hardware performance and an explicit passed/failed/not-run matrix. This audit intentionally does not modify the root-owned central manifest or promote unexecuted gates.

## Addendum: packaged discovery and installed-engine checks

After the initial cut-off, the root lane launched the actual candidate 5 executable and reported a Windows Security firewall modal. This audit did not operate the modal, change an OS/network permission or alter the executable. A read-only `Get-NetTCPConnection -OwningProcess 14868` returned **0.0.0.0:35495, Listen**; no UDP endpoint was returned for the same PID by `Get-NetUDPEndpoint`. The actual packaged log `candidate5-solo-restart/game.log:852` reports `LogTrace: Display: Control listening on port 35495`. This confirms an optional diagnostic TCP listener. Its role in triggering the firewall modal is a strong inference, not an observed Windows firewall causation record.

Installed UE 5.7 source evidence under `C:/Program Files/Epic Games/UE_5.7/Engine/`:

- `Source/Runtime/TraceLog/Private/Trace/Control.cpp:109` opens port 1985, then selects a fallback in 32768–40959 if unavailable. `Writer_UpdateControl` opens it independently of enabled trace channels. The Windows implementation binds all local IPv4 addresses.
- `Source/Runtime/TraceLog/Public/Trace/Config.h:89` supports the compile-time `UE_TRACE_ALLOW_TCP_CONTROL=0`. A definition applied only to the Wonder Chess module cannot rewrite the installed precompiled TraceLog library. Changing `bEnableTrace` requires a unique build environment; installed engine targets default to a shared environment. This is not an immediately verified project-only Development fix.
- `-notraceserver` prevents automatic launch of the separate Unreal Trace Server; it does not disable this in-process listener. `-notracethreading` switches to end-frame updates. `-traceautostart=0` disables automatic connection behavior but does not skip trace initialization/control updates. `FTraceAuxiliary::Shutdown` only stops platform events in this version, so it is not a listener-disable API.
- UdpMessaging/TcpMessaging being mounted does not prove either transport is running. The inspected modules require `-Messaging` in packaged games, or UDP `EnabledByDefault` (default false). Their removal is not supported as the explanation for this observed TCP listener.

**Standard Shipping is a plausible separate-artifact solution to this optional Development listener.** Installed `TargetRules.cs:1250` returns `bEnableTrace=false` for Shipping, and the Trace config defaults experimental Shipping tracing to zero. Control code therefore compiles out under ordinary Shipping defaults. This is a source-supported prediction requiring an actual Shipping build and read-only endpoint check; it is not a claim that Shipping has been produced or verified.

The custom WC regression/exercise/authority/profile/screenshot paths are ordinary C++ without Shipping guards. Their JSON/CSV writes remain implemented. Shipping caveats matter to the test procedure: default UE_LOG output is stripped; command-line `ExecCmds` is excluded in `UnrealEngine.cpp:2239`; `NetDriver.h:446` defines `DO_ENABLE_NET_TEST` as false in Shipping. Therefore retain Development for log-rich/packet-emulation tests; do not assert `PktLag`/`PktLoss` application or `ExecCmds` render scaling in Shipping. Configure normal graphics settings through supported project/settings paths and inspect actual saved values. Public screenshot/frame/GPU timing APIs remain callable, but nonzero actual Shipping measurements still need execution. No broad permission change or engine modification is recommended.

### Confirmed camera occlusion and computed next candidate

I opened actual packaged screenshot `reports/WC-360/candidate5-solo-restart/match-1-seat-0-pid-14868-phase-1-round-6.png`. The far-row ranged hero and its overhead indicators overlap the top header and the opponent strip. This is a confirmed **P2 combat readability defect** in candidate 5, additional to the earlier art findings.

The actual camera is `(2450,0,2600)`, pitch -50/yaw 180, orthographic width 3700 with horizontal FOV maintained. At 1920×1080 its vertical projection is:

`screenY = 540 - (1920 / OrthoWidth) * (-sin(50°) * (worldX - 2450) + cos(50°) * (worldZ - cameraZ))`.

The calculation reproduces the screenshot's board top/bottom and therefore gives a useful bounded estimate for the root's proposed adjustment:

| Quantity, screen pixels at 1080p | Current width 3700 / Z 2600 | Proposed width 4300 / Z 2800 |
|---|---:|---:|
| Board edge top / bottom (X=-800/+800, Z=0) | 115.3 / 751.3 | 232.0 / 779.3 |
| Far cell-center feet (X=-700) | 155.1 | 266.2 |
| Far 220 cm head | 81.7 | 203.0 |
| Far fixed HUD star label (Z=205, minus 30 px) | 56.7 | 177.3 |
| Near cell-center feet (X=700) | 711.6 | 745.1 |
| Tile width | 103.8 | 89.3 |

The proposed values clear the opponent strip ending at Y=171 and put the near-row feet above the bench panel at Y=782. Board-edge clearance is only 2.7 px, while actual cell-center feet have more margin. A hypothetical 300 cm raised pose reaches Y=180.1. Current imported reference bounds peak at approximately 215.2 cm; animated equipment excursions were not bounded by this calculation. The change makes heroes approximately 14% smaller. Width4200/Z2770 still puts the far star label at Y=160.6 inside the opponent strip, so it does not solve the complete overhead-indicator requirement with the present HUD.

Recommendation: the root's width4300/Z2800 is a reasonable measured framing candidate. Verify it in the actual package with a far-row ranged hero, near-row placement, raised equipment, crowded effects and 720p before calling the defect fixed. No camera/HUD source or binary was edited by this audit. The new candidate 5 gameplay files are discovery evidence produced after the original audit cut-off; this addendum does not presume their eventual match-completion result.

## Addendum: actual network failure and bounded bandwidth recommendation

Read-only review at **2026-09-06 14:54 Singapore**. Candidate 5 now has actual two-process discovery evidence in `reports/WC-360/candidate5-network`. This supersedes the earlier NOT_RUN condition with a **confirmed failed transport path**, not a completed 2H6B acceptance pass. The host log contains 60 oversized-bunch mentions, with reported sizes from **73,470 to 99,021 bytes** against the unchanged **65,536-byte** limit. Some mentions may describe the same failed send; this is a log-mention count, not 60 distinct tests. `candidate4-analysis/candidate5-network-size-failure.json` preserves the earlier bounded failure observation and its source hash.

Installed `DataChannel.cpp:1259` rejects these oversized constructed bunches before transmission. This explains the stale/missing client public state independently of the separate slow-window-rendering observation. The root has now changed source encoding to condensed JSON, removed redundant unit/event bodies from retained recap summaries, and schedules combat publication every 0.10 wall seconds (0.25 elsewhere). This audit did not modify that source and has not executed its new wire format.

I applied the same structural transformation in memory to existing actual snapshots, using compact JSON solely to estimate size:

| Actual source snapshot set | Samples | Estimated compact/summary-only maximum | Maximum combat unit entries | Estimated public bytes/sec at 10 Hz |
|---|---:|---:|---:|---:|
| Candidate 5 network host | 327 | 32,641 | 48 | 326,410 |
| Candidate 5 solo/restart | 801 | 32,729 | 48 | 327,290 |

All sampled public strings are ASCII. These are estimates from parsed saved data, not measurements of the new Unreal serializer, FString wire encoding, packet overhead or retransmissions. The corresponding maximum compact JSON before stripping recap unit/event bodies was 59,298/59,514 bytes; stripping duplicated recap bodies is materially useful even with condensed formatting. Verify the new serialized/bunch maximum in the next actual run and retain the existing 64 KB limit. Future non-ASCII strings can alter FString serialization size and require renewed measurement.

The actual host handshake (`candidate5-network/host/game.log:878`) reports **client netspeed 100000**. Installed `BaseEngine.ini:1782–1783` sets Player Internet/LAN speeds to 100,000, and `BaseEngine.ini:1803–1804` sets IpNetDriver MaxClient/MaxInternetClient rates to 100,000. `NetConnection.cpp:4984` converts `CurrentNetSpeed * seconds * 8` to bits, confirming these rates are bytes/second. Thus the actual negotiated budget is below one third of the proposed public-only peak rate.

Minimal project recommendation for the next candidate's `DefaultEngine.ini`:

```ini
[/Script/Engine.Player]
ConfiguredInternetSpeed=1000000
ConfiguredLanSpeed=1000000

[/Script/OnlineSubsystemUtils.IpNetDriver]
MaxClientRate=1000000
MaxInternetClientRate=1000000
```

This is a local game bandwidth budget of 1 MB/s for the one remote client in the two-human alpha, with approximately three times the estimated public payload rate available for fragmentation, private RPCs, control traffic and retries. It is not an OS permission, firewall rule, packet-size change or measured throughput claim. Both Player rates matter: `NetConnection.cpp:564` selects the LAN value only when the URL contains `LAN`; the current host/client URLs do not. Confirm the actual new handshake value and stable client state rather than assuming config was applied.

No initial additional actor/global tick changes are justified. Installed AActor initializes NetUpdateFrequency=100/minimum=2; AGameStateBase is always relevant and gives NetPriority=10. The base IpNetDriver server tick setting is 30 Hz, above the 10 Hz application target. The older GameNetworkManager defaults of total32,000/max7,000/min4,000 are real, but its `UpdateNetSpeeds` is not called from this inspected GameModeBase path; the actual handshake also shows 100,000. Avoid speculative manager overrides unless a later actual rate is reduced by that path.

A 32 KB property still fragments into numerous UDP packets. `DataChannel.cpp:1416` promotes a send with at least eight partial bunches to reliable and pauses that actor channel until acknowledgment. Do not disable that mechanism or raise bunch/packet/reliable-buffer limits to mask failures. It means a 0.10-second publisher is a target, not proof of a 0.10-second delivered cadence under latency/loss. Measure actual client public-state change intervals. The current evidence recorder writes sampled snapshots every 0.5 wall seconds, so those files alone cannot resolve a 100 ms delivery interval. The existing authoritative combat/timing fields can still establish correctness at their sampled points.

At WCFast=10, a 100 ms wall interval advances one second of combat simulation. Such a correctness run cannot certify that a 250 ms projectile is visibly presented at normal speed. Inspect projectile/animation synchronization separately at WCFast=1 with rendered frames.

The next proposed two-window test at 1280×720, positions (0,0) and (640,340), keeps each window partly visible and reduces competing render load. The previous approximately 250 ms timings with occluded windows are observed poor performance; a specific GPU occlusion mechanism was not established by this audit. The new arrangement must be measured, and its timings remain a dual-process 720p correctness/diagnostic condition. They do not replace the contract's normal-speed 1080p twelve-visible/four-encounter performance result.
