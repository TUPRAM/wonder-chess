# Shipping compatibility and player-documentation audit

Read-only source, installed-engine and package inspection by the toolchain audit lane. Initial cut-off: **2026-09-06 15:14 Singapore**. No build, editor, game, installer or permission change was launched by this audit. Only this report and `docs/PLAYING_THE_ALPHA.md` are edited.

## Observed build state

Candidate 6 Development packaging completed with exit 0 at `2026-09-06T07:10:03.8549610Z`, recorded in `reports/WC-360/package-candidate6/package-Development-20260906T070812Z.json`. Its package is `builds/Windows-Alpha-Candidate6`, with a top-level bootstrap `WonderChess.exe` and the game executable under `WonderChess/Binaries/Win64`. Packaging success is separate from the root/runtime lanes' match and UI evidence.

The intended final archive directory is `builds/WonderChess-Alpha-Windows`. At the initial cut-off its directory had been created for the root-owned Shipping build but contained no delivered files. A final launcher at `builds/WonderChess-Alpha-Windows/WonderChess.exe` was therefore still pending inspection. Unreal's archive command may introduce a `Windows` subdirectory; inspect the completed layout before publishing an executable path.

`tools/unreal/package_game.ps1` passes its explicit `-Configuration Shipping` argument to UAT as `-clientconfig=Shipping`; this can select Shipping despite `DefaultGame.ini` retaining `BuildConfiguration=PPBC_Development`. The completed receipt/build log, rather than the INI label alone, must identify the delivered configuration.

## Shipping behavior supported by the inspected implementation

| Area | Inspected behavior and verification limit |
| --- | --- |
| Game logic, controllers and networking | The Runtime module uses Core, Engine, JSON, input, UI, network and rendering dependencies. The common simulation, bot policy, seat ownership, command validation, replicated snapshots and host-loss handlers are ordinary runtime C++. No Shipping-only alternate game rules or side-effecting `check`/`ensure` calls were found in the project runtime source. Actual Shipping execution is still required. |
| Canonical data | Runtime JSON is loaded with `FFileHelper` from `Content/WonderChess/SourceData`, staged as UFS. JSON and JsonUtilities are runtime module dependencies. Editor-only DataTable import and Python helpers are not called by the packaged game. Strict runtime validation remains compiled. |
| Required content | Both menu/courtyard maps are explicitly cooked. Heroes, Audio, Materials, Data and Effects are always-cook directories, covering the runtime's dynamically constructed hero, animation, portrait and sound paths. PythonScriptPlugin and EditorScriptingUtilities are restricted to Editor targets; AndroidFileServer is disabled. Successful Development cooking is evidence for that artifact, not automatic Shipping asset validation. |
| Audio | Controller code loads authored `USoundWave`/`USoundBase` objects, uses native audio components/PlaySound2D and a 12-voice concurrency object; music looping is set in runtime and saved asset data. No Shipping guard removes these paths. PCM is selected by project configuration. Candidate 6 includes `xaudio2_9redist.dll` and the Ogg/Vorbis engine redistributables. Listening and device initialization must be checked in Shipping. |
| Rendering and options | DefaultGraphicsRHI is DX11; default auto exposure/motion blur, dynamic GI/reflections and virtual shadows are disabled by project config. Native canvas/HUD, skeletal presentation, runtime FPS cap and GameUserSettings/volume/language options are not editor or development features. Do not assume a Shipping visual pass from a Development screenshot. |
| Custom regression | `-WCRegression=<count>` and its actual-combat JSON/CSV writes are not wrapped in automation/Shipping conditionals. The same applies to `-WCFast`, `-WCExercise`, `-WCAuthorityChecks`, `-WCRestartOnce`, `-WCExitAfter` and custom session evidence paths. A Shipping regression must still complete with actual files and exit status before being called passed. |
| Custom profiling | `-WCProfile` writes frame delta, game/render thread cycles, GPU cycles where available, memory and state counts directly. Installed `UnrealClient.cpp:1773` computes GGameThreadTime, `SlateRHIRenderer.cpp:988` computes GRenderThreadTime, and `GPUProfiler.cpp:2722` exposes RHIGetGPUFrameCycles outside a Shipping guard. GPU-zero samples must remain unavailable, not fabricated measurements. Confirm nonzero actual Shipping samples and the qualifying scene. |
| Screenshots | F9 calls FScreenshotRequest directly; `-WCShots` also requests screenshots from native runtime code. This does not depend on the console screenshot command. `FPaths::ScreenShotDir()` resolves ProjectSavedDir + `Screenshots/<platform>/`. Shipping still needs an actual captured image to verify the complete path. |

## Deliberate differences from Development

The root's in-progress Shipping response file at `game/Intermediate/Build/Win64/x64/WonderChess/Shipping/WonderChess-Win64-Shipping.exe/Default.rc2.res.rsp` was inspected. It explicitly defines **UE_BUILD_SHIPPING=1, UE_TRACE_ENABLED=0, WITH_DEV_AUTOMATION_TESTS=0 and USE_LOGGING_IN_SHIPPING=0**. These are generated build inputs, not a claim of a successful final executable.

- Standard Shipping omits normal UE_LOG output. `-abslog` does not restore calls compiled out. Use custom JSON/CSV, process exit status, images and read-only endpoint inspection as Shipping evidence. Keep the Development artifact/logs for detailed discovery evidence.
- Unreal automation tests are excluded. The editor's five automation entries cannot be rerun as Shipping automation; the project's separate custom `-WCRegression` remains implemented.
- Installed `UnrealEngine.cpp:2239` excludes ordinary command-line `ExecCmds` processing in Shipping. Do not rely on `-ExecCmds="r.ScreenPercentage 100"` or similar to establish graphics settings. Inspect actual configuration/settings and measured runtime values.
- Installed `NetDriver.h:446` defines DO_ENABLE_NET_TEST as `!(UE_BUILD_SHIPPING)`. Packet-lag/loss command-line switches do not establish emulation in Shipping. Retain Development for those checks.
- Installed `TargetRules.cs:1250` disables tracing for ordinary Shipping, consistent with the generated UE_TRACE_ENABLED=0. The optional Development Trace Control TCP listener should therefore be absent. This needs an actual Shipping process endpoint check; no claim is made that all networking is absent. A deliberately hosted two-human session needs its game transport.

## Prerequisites and clean-machine boundary

Current `DefaultGame.ini` sets **bIncludePrerequisites=False** and the packaging wrapper does not request a prerequisites installer. The completed Candidate 6 NonUFS manifest and file inventory contain no UE prerequisites installer and no `MSVCP140.dll`, `VCRUNTIME140.dll` or `VCRUNTIME140_1.dll`.

Actual MSVC 14.44 `dumpbin /dependents` against Candidate 6's game executable reports those three Microsoft VC runtime DLLs as imports, along with Windows Universal CRT API-set DLLs. Engine redistributables such as tbbmalloc and XAudio2 are included separately. This demonstrates a concrete dependency on compatible installed Microsoft runtime components; it does not diagnose a missing DLL on the current machine or establish an exact minimum supported redistributable version.

The development PC already has Visual Studio/Unreal and runtime components. No clean Windows installation, second physical computer, clean VM, driver matrix or missing-prerequisite installation workflow has been tested by this audit. The package is a folder distribution, not a verified installer. Preserve all adjacent packaged files. Do not advise players to obtain arbitrary DLLs individually. The Shipping import table and final staged file inventory must be checked again after its build completes.

## Documentation changes and remaining handoff checks

`docs/PLAYING_THE_ALPHA.md` now distinguishes direct executable **`-WCEvidenceDir="..."`** from the PowerShell helper's **`-EvidenceDirectory '...'`**. It supplies `-Executable` explicitly because the helper currently defaults to the older `builds/Windows-Alpha` artifact. The guide continues to mark the final package path as pending, describes two-process/single-PC networking as the current verification boundary, and makes no clean-machine or finished-art claim.

After Shipping is complete, inspect the top-level launcher, target receipt, executable hashes/imports, staged prerequisites and cook manifests; update the guide's package-status sentence with the actually delivered path. Then the root/runtime lanes must separately demonstrate direct cold launch, F9/custom evidence writes, visible/audio play, complete solo/restart/network sessions, no unexpected standalone listener and real frame/GPU samples. This read-only audit does not substitute for those executions.

## Native-resolution preset investigation

Follow-up requested by the root at approximately 15:16 Singapore. This is an installed-source recommendation, not an assertion about the already-cooked Candidate 6 or first Shipping archive. The root owns any configuration change and subsequent repackage.

`LegacyScreenPercentageDriver.cpp:35` initializes `r.ScreenPercentage` to 0. `PullRunTimeRenderingSettings` at lines 215–225 uses a positive value as Manual; a zero value delegates to the default mode, which is BasedOnDisplayResolution on desktop. Therefore `r.ScreenPercentage=0` in prior evidence is a heuristic selection, not an observed 100% render scale.

`GameViewportClient.cpp:115` separately initializes `r.SecondaryScreenPercentage.GameViewport` to 0. At lines 1566–1581 a positive setting gives `min(setting/100,1)`, while zero calls GetDPIDerivedResolutionFraction. Following that helper to `UnrealClient.cpp:2638` reveals that **this installed version applies DPI only inside WITH_EDITOR/GIsEditor and otherwise returns1.0**. The earlier warning sent to the root based on the CVar help text was too broad and was explicitly corrected. Secondary100 is a clear explicit value, but is not required to defeat packaged-game DPI scaling in this version. It does not change OS DPI or permissions.

The appropriate explicit preset in project `[SystemSettings]` is:

```ini
r.ScreenPercentage=100
r.SecondaryScreenPercentage.GameViewport=100
r.DynamicRes.OperationMode=0
```

Installed `UnrealEngine.cpp:475` defaults dynamic-resolution operation mode to0; `GameUserSettings.cpp:262` defaults its user setting tofalse. `UnrealEngine.cpp:13903` enables it only for mode2 or mode1 plus the user setting. Explicit mode0 therefore also protects this preset from a previously saved true user preference. The separate development-only TestScreenPercentage override is excluded in ordinary Shipping.

No additional desktop default-mode setting is necessary because the positive primary value already chooses Manual. ScreenPercentage MinResolution and MaxResolution default to0 (no clamp); this audit found no project override. `IConsoleManager.h:149–155` gives SystemSettingsIni priority0x05000000, above scalability0x02000000 and GameSetting0x03000000, so ordinary scalability/user-setting application cannot replace the explicit primary value. Higher-priority deliberate overrides still require inspection.

Record actual primary, secondary and dynamic-operation-mode CVar values alongside the viewport size in the final session evidence; these values plus the inspected path support the native preset. Actual viewport dimensions, loaded settings, GPU timing and screenshots still need verification after the root's repackage. The inspected DX11 frame-timing implementation (`D3D11RHI.cpp:370–387`) calls FrameTiming.Start/End and pushes GPU frame cycles without a Shipping guard, supporting the project's custom GPU metrics on this configured RHI.

## Second Shipping package captured, before prerequisite staging

The second Shipping UAT run completed at `2026-09-06T07:20:38.6688327Z`, exit0, BuildCookRun130.97 seconds. Actual layout is **`builds/WonderChess-Alpha-Windows/Windows/WonderChess.exe`**. The inner file is `Windows/WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe`. The parent later requested a further package to include prerequisites; preserve this capture as the observed pre-prerequisite artifact, not the identity of that future package.

`reports/WC-360/shipping-final-provenance.json` was created without overwriting earlier evidence at UTC07:21:06–07:21:16. It records774 source/config/data/art/build/package inputs, stable during hashing. All12 current hero sources and168 declared exports matched their manifests; canonical/generated/staged bytes matched; the packaged inner executable matched the build output. Packaged payload was29 files/555,143,284 bytes excluding runtime Saved directories.

| Captured item | SHA256 |
| --- | --- |
| Bootstrap,164,864 bytes | `38a46da697e48af83ec0105bd68b44073d95b3b902f710d53ac3f2280d6e8058` |
| Shipping game,144,094,208 bytes | `bee75ae9de12c86e78993eb72055b6ec0a8ac359f4886cb7f76ea307736dc77b` |
| Immutable provenance JSON | `1b36a7c2ab6a57a9fc17edb35cd6b1141cbb62c6a7a3184061cf07e04a225fa4` |

`shipping-final-dependents.txt` preserves actual dumpbin output for that packaged inner executable. It still imports MSVCP140, VCRUNTIME140 and VCRUNTIME140_1 externally. Its staged inventory contains XAudio2 redistributable DLLs but no VC runtime installer. This audit did not launch the game; the root/runtime lanes own runtime checks.

## Existing prerequisites and supported staging path

The root subsequently requested an offline prerequisite-staging investigation. **Existing installers are available** under installed UE `Engine/Extras/Redist/en-us`: `vc_redist.x64.exe` (25,646,472 bytes) and `vc_redist.arm64.exe` (11,733,048 bytes), both version14.44.35211.0. Windows Authenticode reports both signatures Valid, signed by Microsoft Corporation. Their exact hashes, metadata and boundaries are in `reports/WC-360/prerequisites-audit.json`. Neither installer was run or downloaded.

Installed `WinPlatform.Automation.cs:198–202` stages both files as NonUFS when Params.Prereqs is true. The old UEPrereqSetup_x64 staging line is commented out in this engine version. The correct direct AutomationTool flag is **`-prereqs`**. `ProjectParams.cs:929` reads that flag. The reflected editor packaging property is **`IncludePrerequisites`**, without a leading b (`ProjectPackagingSettings.h:423`); `TurnkeySupportModule.cpp:506` turns it into `-prereqs`. Therefore the earlier observed `bIncludePrerequisites=False` string is not the effective property in this installed version; the original wrapper's omitted flag and actual staged inventory establish the previous omission. For the root's direct UAT wrapper, pass `-prereqs` explicitly. The expected output is `Windows/Engine/Extras/Redist/en-us/vc_redist.x64.exe` and the ARM64 companion.

No adjacent current license/README was supplied beside the installed Unreal redistributables. The local VisualC++2010 license file concerns a different runtime and was not used to infer rights. Microsoft's current VS2022 redistribution list permits distribution of unmodified runtime redistributables with a program by validly licensed Visual Studio users, subject to the associated license terms. VS Community2022 is installed; this audit has not independently examined the user's license eligibility. This supports the ordinary installed-toolchain packaging path, not an unrestricted-license claim. [Microsoft VS2022 distributable code](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution#visual-c-runtime-files), [Microsoft deployment guidance](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files?view=msvc-170).

Including the existing installer removes the need to download that prerequisite separately. It does not itself prove installer execution, clean-machine launch, automatic bootstrap installation, Windows-on-ARM compatibility or a minimum supported runtime version. Compare staged installers byte-for-byte against the measured signed originals after the next package; preserve this package's evidence and capture the new artifact separately.

## Delivery package with prerequisites: observed completion

The root's delivery UAT run completed at **2026-09-06T07:24:49.1662608Z**, Shipping, exit0, BuildCookRun58.65 seconds, recorded in `reports/WC-360/package-shipping-delivery/package-Shipping-20260906T072347Z.json`. The actual player launcher remains `builds/WonderChess-Alpha-Windows/Windows/WonderChess.exe`.

This audit then compared both staged installers with the measured originals and rechecked their signatures. Both are byte-identical and Authenticode Valid. `reports/WC-360/shipping-delivery-prerequisites.json` records **PASS_STAGED_PREREQUISITE_IDENTITIES**, with installer execution and clean-machine testing explicitly NOT_RUN.

The new immutable **`reports/WC-360/shipping-delivery-provenance.json`** was captured at UTC07:25:41–07:25:46. Its SHA256 is `6f44003df4431b8a80ca9d4357c37ac14349e18e71c579873d1f7ed79f7bff42`. All776 recorded inputs/file sets were stable, the packaged game matched the build output, twelve hero sources/168 declared exports matched their manifests, and staged data matched canonical/generated files. The package now contains31 payload files totaling592,522,948 bytes, excluding runtime Saved directories. Bootstrap and inner executable hashes are unchanged from the preceding table; the newly included prerequisites and updated cook/config/tooling identity are separately covered by this new capture. The previous provenance JSON's hash was rechecked and remains unchanged.

The player guide now gives the confirmed Windows-child path, correctly distinguishes the two screenshot-directory flags and describes optional use of the included x64 Microsoft installer. It explicitly retains the untested installer/clean-machine boundary. This report does not convert inclusion of installers into a verified installation workflow. The root/runtime lanes continue actual Shipping gameplay, networking and performance checks; no game or installer was launched by this lane.
