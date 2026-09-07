> Current 24-hero implementation checkpoint: [UPDATE24_CHECKPOINT_HANDOFF.md](UPDATE24_CHECKPOINT_HANDOFF.md). The historical twelve-hero handoff below is retained unchanged.

# Wonder Chess Windows alpha — release handoff

**A real Unreal Shipping game is packaged and has passed complete functional match checks. Full playable/presentable-alpha acceptance is still open.** The final candidate completed 100 real all-bot tournaments, two rendered 1H7B matches with restart, and one actual two-process 2H6B tournament. Its final normal-speed 1080p measurement without automatic screenshots completed with frame p95 16.667 ms and p99 16.728 ms in the required busy scene. The user subsequently authorized dismissal of the Windows Security dialog and continuation. The attempted Cancel click was rejected because the native tool cannot target the dialog; manual verification is waiting on user dismissal. Full manual UI, continuous animation/effect and auditory acceptance remain open. Human audio audition and continuous animation/effect approval have not been completed.

This is the current handoff as of 2026-09-06 after the final functional runs, 08:56 UTC performance completion, 08:58 UTC manual recheck and subsequent user-authorized resume attempt. It follows `docs/MASTER_IMPLEMENTATION_v3.md`; kit scaffolds and Python fixtures are not substituted for executed Unreal results. All 32 acceptance IDs are mapped in [final-acceptance-audit.md](WC-360/final-acceptance-audit.md). Root maintains `reports/implementation_state.json` and the separate performance report.

## Launch the actual Windows package

**Executable:** `C:/Users/iputu/Documents/Wonder Chess/builds/WonderChess-Alpha-Candidate/Windows/WonderChess.exe`

Keep the entire `Windows` folder together. Double-click `WonderChess.exe`, or run:

```powershell
Set-Location -LiteralPath 'C:\Users\iputu\Documents\Wonder Chess\builds\WonderChess-Alpha-Candidate\Windows'
.\WonderChess.exe
```

Choose **Play Bot Tournament** for one human and seven persistent bots. **Guided practice | fixed shop seed** teaches buying Ada, deployment, adding Mira for the Human trait and a three-copy merge. Its first preparation stays untimed until Ready; normal tournaments use ordinary shops and timers. The full control guide is [PLAYING_THE_ALPHA.md](../docs/PLAYING_THE_ALPHA.md).

The executable runs without Unreal Editor, Blender, Visual Studio, Codex, a web server or an online AI service. The packaged `Engine/Extras/Redist/en-us/vc_redist.x64.exe` is the existing signed Microsoft Visual C++ 14.44.35211.0 installer, included byte-identically from the installed engine. It can be used if Windows reports missing runtime components. No installer was executed during this work; a clean-machine installation/run is NOT_RUN. The bundled ARM64 installer does not mean an ARM64 game was built.

For the local-network mode, use **Host LAN lobby | 2H6B** and **Join local host**; the host starts once both humans connect. The supported Shipping command lines are:

```powershell
# Host, from the packaged Windows folder:
.\WonderChess.exe -WCHost -Port=7777

# Second process on the same machine:
.\WonderChess.exe -WCJoin=127.0.0.1:7777
```

For another PC, replace `127.0.0.1` with the host's literal IPv4 address and match the port. Actual verification used two real processes on this PC over UDP 7780. Two physical PCs have not been tested. There is no OS firewall permission or security-setting procedure in this handoff. Late joining an active match is rejected; use a new lobby. Non-host loss gives that seat to a bot; host loss aborts the match without inventing a winner.

Buy using the shop button, select a bench unit then click a legal board cell or drag it, and collect three identical same-star copies for an automatic merge. Preparation supports sell, reroll, lock, XP, swaps and trait inspection. Standings select scouting/spectating. Space activates Ready; an accepted preparation edit clears readiness. Right-click/Escape cancels a selection, otherwise opens Options. Tab/Enter navigate visible buttons; arrows or dragging adjust volume. EN/ID, reduced motion and window modes are available. F9 captures the actual game view. These are implemented controls; the full manual alternatives/persistence checklist remains open.

## Exact delivered identity

| Item | Actual identity |
|---|---|
| Bootstrap | `builds/WonderChess-Alpha-Candidate/Windows/WonderChess.exe`; 164,864 bytes; SHA256 `38a46da697e48af83ec0105bd68b44073d95b3b902f710d53ac3f2280d6e8058` |
| Inner Shipping executable | `Windows/WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe`; 144,207,872 bytes; SHA256 `b3114876d3d75e6d89677f42b2a6117b5989ba8dfe91d4f50ef50e965a2103ac` |
| Immutable provenance | `reports/WC-360/alpha-candidate-provenance.json`; SHA256 `89d6e2129cf28e491fb69d9d2fb2c68f2f50e0562dcdbc792322c2fe04786415`; captured 08:40:01.406–08:40:06.780 UTC |
| Payload | 31 files, 592,741,060 bytes, excluding runtime Saved outputs; provenance captures 781 stable input/payload files |
| Build | BuildCookRun 64.28 seconds, exit 0 at 08:39:42.569 UTC; `reports/WC-360/package-alpha-candidate/package-Shipping-20260906T083835Z.json` |
| Catalog | Schema `3.0.0`, balance `alpha_8seat_v0.3.0`, profile `alpha_8seat`; digest `3154592665ce21dc65e5afb06f3769655c8be9ec4157fa6779427c8b8fcc092f` |
| Local source checkpoint | `67c165b66af5b1c0132c275b1613b7482b2acf8b`; source/assets/tests checkpoint. Launcher/guide were updated afterward to the final path. Actual launcher bytes are included in the current immutable manifest; the commit alone is not every delivered file's identity. |

The packaged inner executable matched its source binary. Twelve authored Blender sources, 168 required hero exports and staged canonical/generated data matched captured manifests. Seven actual IoStore/Pak/UFS/reference lists and the 1,448-file cooked tree contain no AdaRoundTrip verification paths; production Ada is present and 659 packages cooked. See `reports/WC-360/alpha-candidate-cook-audit/`. This checks actual cook/staging inputs; it is not an independent container extraction.

The only final game-input change from the preceding native-TAA package is `WCVerification.cpp`, correcting old-namespace seed-summary ownership. Canonical data, game configuration, production assets and networking/core code remain byte-identical. Exact before/after hashes are in `alpha-candidate-cook-audit/provenance-delta.json`. The final build has its own repeated regression, restart and network evidence; earlier packages remain preserved.

## Implemented game and editable sources

Native C++ implements deterministic integer combat, simultaneous actual off-screen encounters, the eight-seat tournament, pairing/ghosts, atomic settlement, elimination/results, persistent legal bots, owner-authenticated idempotent commands, private/public state, economy, deployment/merge/upgrades/leveling and race/class traits. Unreal HUD/components render the interface, arena, heroes, cues and audio. Python supports authoring, editor import and evidence analysis.

| Material | Workspace path, relative to `C:/Users/iputu/Documents/Wonder Chess` |
|---|---|
| Unreal project | `game/WonderChess.uproject` |
| Combat/tournament | `game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp`, `WonderTournament.cpp`; shared interface `Public/Simulation/WonderSimulation.h` |
| Authority/network/controller | `game/Source/WonderChessRuntime/Private/WCMatchRuntime.cpp`, `WCNetworkSession.cpp` |
| Interface/presentation/evidence | Same module: `Private/WCMatchHUD.cpp`, `WCBoardPresenter.cpp`, `WCVerification.cpp` |
| Canonical rules/roster/personas | `data/units.json`, `rules.alpha.json`, `traits.json`, `world.json`, `bots.json`, `data/locales/` |
| Full authored dossiers/derived rows | `docs/heroes/`, `generated/unreal/` |
| Runtime JSON and DataTables | `game/Content/WonderChess/SourceData/`; `game/Content/WonderChess/Data/DT_Units_Alpha.uasset`, `DT_Abilities_Alpha.uasset` |
| Hero source/export/import | `art-source/heroes/<id>/<id>.blend`; `exports/heroes/<id>/`; `game/Content/WonderChess/Heroes/<id>/` |
| Courtyard source/export/import | `art-source/arena/WC_SevenLanternCourtyard.blend`; `exports/arena/`; `game/Content/WonderChess/Arena/` |
| Playable maps | `game/Content/WonderChess/Maps/L_WC_Menu.umap`, `L_WC_Courtyard.umap` |
| Projectile glyphs | `art-source/effects/WC_ProjectileGlyphs.blend`, `exports/effects/`, `game/Content/WonderChess/Effects/` |
| Original audio | `tools/audio/`, `exports/audio/`, `game/Content/WonderChess/Audio/` |
| Native/reference/integration tests | `tests/`, `tests/runtime/`, module automation test sources |

No VEILMARK source, assets, lore or configuration were read, copied or modified. No paid services, external asset packs, downloads or online LLM dependency were used. The other twelve designed heroes remain authored expansion content and are excluded from the alpha shop and asset obligation.

## Completed assets and remaining presentation work

The alpha has twelve original stylized fantasy heroes with actual Blender sources, skeletal Unreal meshes, three texture maps, two additional LODs, portraits and seven animations each. They have distinct authored equipment, materials and family proportions. Actual technical validation covers 84 unique imported clips and 11,988 sampled bone transforms. These are real authored assets; final attractiveness and continuous performance are not inferred from counts.

| Alpha hero | Canonical ID |
|---|---|
| Ada Brightshield | `wc_u_human_guardian` |
| Mira Dawnwell | `wc_u_human_priest` |
| Rowan Emberwick | `wc_u_human_mage` |
| Liora Leafstep | `wc_u_elf_ranger` |
| Elin Moonsong | `wc_u_elf_priest` |
| Sylas Duskrun | `wc_u_elf_rogue` |
| Borin Stonebell | `wc_u_dwarf_guardian` |
| Tessa Brassbolt | `wc_u_dwarf_ranger` |
| Dagna Anvilheart | `wc_u_dwarf_warrior` |
| Rok Sunward | `wc_u_orc_warrior` |
| Zura Stormcall | `wc_u_orc_mage` |
| Kesh Quickwind | `wc_u_orc_rogue` |

The coherent Seven Lantern Courtyard uses thirteen authored modules and 176 placed pieces. The calibrated board measures 200 cm per tile. Two original arrow/bolt glyphs were imported with verified forward axes, bounds and nondegenerate UVs. Thirty-two SoundWaves are imported: nineteen shared sound families, one looping music asset and twelve original dossier-specific active sounds. Signal checks record duration/RMS/peak and zero clipping; human listening has not been performed.

`reports/WC-330/ART_HANDOFF.md` and `hero-readiness-matrix.json` identify source revisions and actual reviews. The 21-frame Unreal review covers all 84 hero/clip combinations at three sampled fractions. The latest `shipping-normal1080-taa-review.md` and `shipping-normal1080-taa-review.json` records fourteen opened normal-speed TAA images and four final-package images. All twelve living recovery definitions, including Zura, are now visible and reviewed. Twelve-piece battles, cyan/orange team markers, health bars and the corrected spectator panel fit the sampled views. Full continuous playback, temporal ghosting, every skill's release/effect synchronization and human audio approval remain open. Pale effect contrast and torso overlap from large shield rings warrant that review. One approximately 3 px conservative Rok bounding-box excursion is preserved without claiming an actual pixel occlusion.

The isolated Ada costume drill **passed source change, same-mesh reimport and a separate cold load**. A gold medallion added 40 Blender vertices/76 triangles; actual Unreal render vertices increased 8,317→8,493. Seven placed actor/component/animation references, material, Skeleton, three LODs and bounds survived. Both processes exited 0 and all 296 protected production Content files were unchanged. Evidence: `reports/WC-330/ada-costume-roundtrip/run_v2-summary.md`, `run_v2-import.json`, `run_v2-cold.json`. Verification-only assets remain excluded from the cooked package; the drill did not change Ada's packaged costume.

Actual final-package battle, round 13, 1920×1080 TAA, scripted 10×. Twelve living pieces are present, with repeated definitions; this is not a claim of twelve distinct heroes in one encounter:

![Actual final Wonder Chess package: round 13 battle](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-360/alpha-candidate-restart/match-1-seat-0-pid-53152-phase-1-round-13.png>)

Image SHA256: `0c30a926211bcd86454119b5595e4b4d26776b049df8faa6f01fc1640de67d26`. The art review binds it to final executable `b3114876…`.

## Actual test and match results

| Verification | Result and evidence |
|---|---|
| Authoring/reference parity | Latest final-candidate reruns passed: 438 specification checks ([kit](WC-360/alpha-candidate-kit.log)), 63 Python tests ([reference](WC-360/alpha-candidate-reference.log)), 27 generated documents ([documents](WC-360/alpha-candidate-documents.log)), six catalog artifacts ([catalog](WC-360/alpha-candidate-catalog.log)), and twelve staged runtime files plus reflected row header ([staged data](WC-360/alpha-candidate-staged-data.log)). These are not combat counts. |
| Native runtime | 2,664,928 assertions passed, including repeated per-tick invariants and 100 full combat tournaments; `reports/WC-310/runtime/post-retained-recap/validation.json`. |
| Targeted native combat | 20 groups / 1,460 Combat executions passed, compile/process 0; `reports/WC-310/runtime/targeted-native/validation.json`. Includes replacement/expiry shields, overflow/heal caps, corner/reservation and stun/dash ordering. |
| Trait fixtures | 138 groups / 2,289 assertions / 266 Combat constructions passed, compile/process 0; `reports/WC-310/runtime/trait-native/validation.json`. All ten traits, matching recipients, duplicates/bench/no-double/overlap; stars 1–3 cover snapshots, controlled emissions use star 1. |
| Final Editor integration | Build passed in 31.15 seconds. Eight actual UE tests passed, 0 warnings/failures, 38.163700 seconds, process 0; `reports/WC-360/alpha-candidate-automation/index.json`. Four original outputs preserved byte-identically in `engine-evidence/`. |
| Final Shipping 0H8B | All 100 seeds 1–100 completed, 16/16 audit checks passed; actual inner 45660 exit 0, batch 49.827053 seconds. `reports/WC-360/alpha-candidate-analysis/regression-analysis.json` and `regression-analysis.md`, `100-engine-matches.json`. Headless/no-sound, not a render benchmark. |
| Final Shipping 1H7B/restart | Two complete rendered matches: seed 314159 reaches round 23, then seed 271828 reaches round 20. Human elimination at rounds 17/10 did not stall bots. 36/36 checks, all 7/8 probes passed, correct summary and snapshot seeds, actual inner 53152 exit 0. `reports/WC-360/alpha-candidate-restart/functional-audit/audit.json`. Scripted 10× functional scope. |
| Final Shipping 2H6B | Both actual human controllers plus six bots complete all 23 rounds with equal results; 47/47 audit checks and 14 authority probes passed. Host inner 49828 owned UDP 7780; client inner 34484. Bootstrap exits 0, inner codes UNKNOWN. `reports/WC-360/alpha-candidate-network/audit/network-analysis.json`. Scripted 5× 1280×720 loopback. |
| Disconnects on preceding native-TAA binary | 22 client-loss/takeover/late-join and 16 host-loss checks passed at 1×, 1280×720; `reports/WC-360/native-taa-disconnect/{client-loss,host-loss}/audit.json`. Final network/core files are unchanged. These tests were not repeated on the final binary. |
| Normal-speed complete tournament on preceding TSR binary | Actual 1H7B completed round 20/results outside Editor; human eliminated round 10, bots continued, process 44708 later exited 0. `reports/WC-360/shipping-normal1080/completed-session.json` and `launch.json`. Separate from final-binary performance run. |
| Full manual UI/audio/continuous presentation | NOT_RUN/BLOCKED at the detailed boundaries below; no automatic success from scripted matches or still images. |

The final 100-tournament batch ran 7,118 real encounters, 1,437 timeouts (20.1883%), 524 ghosts and 69,656 bot commands. There were zero failed trials, unresolved encounters or rejected bot commands. All 100 summaries, 17,728 round-seat rows and per-hero use/placements match the preserved native/UE evidence. Fourteen seeds reached the explicit tournament cap: 7, 18, 29, 34, 35, 36, 45, 46, 49, 65, 74, 80, 86 and 89. Median/p95 simulated match time is 1,020.65/1,121.70 seconds; median/p95 fight time is 31.45/40.00 seconds. No failed seed was dropped. Shipping engine-log counts are unavailable, not asserted to be zero.

The corrected native formation study uses shield-heavy (two Adas), sustain (two Mira Dawnwells), spread ranged, paired Mage and Rogue-pressure teams, equal acquisition cost and stars, eight seeds, both orientations and self-matchups. It records 720 primary comparisons plus 720 read-observed replays, 70 primary timeouts and 23/240 cross-mirror winner changes. This is regression/balance evidence, not solved balance. Focused native cases are not all individually repeated Unreal tests.

Final network replies reconcile as host 37 accepted/5 deliberately rejected and client 48/5. Accepted replies include an intentional duplicate; maximum public JSON is 32,622 UTF8 bytes, excluding transport overhead. The client retained its completed match before entering an aborted menu after the host's planned exit. That later connection state does not erase the completed tournament. Final restart separately records 60/37 accepted replies and 5/6 deliberate rejects across its two namespaces, with no known remaining evidence defect.

Bot policy review confirms bounded commands (maximum 30 against cap 40), at most four paid rerolls and one Ready per living preparation. Six early/mid/late native decisions and deployment snapshots match Shipping output. The immutable native trace also contains 1,081 marginal buy→sale churn candidates across 875 of 13,712 preparations; no item IDs are logged, so identical-copy reversal is unproved. A crowded upgraded bench can constrain sensible spending. These are concrete policy-quality findings, not authority failures or an invitation to silently change balance. Details and exact examples are in the acceptance audit.

## Performance on the named machine

Measured hardware is a Lenovo 82RG, Ryzen 7 6800H (8 cores/16 threads), NVIDIA RTX 3060 Laptop GPU (6,144 MiB VRAM, driver 580.88), 16,312,393,728 bytes RAM, Windows 11 build 26200. Actual rendering uses NVIDIA/D3D11. Installed toolchain: Unreal 5.7.4 CL51494982, MSVC 19.44.35226/toolset 14.44.35207, Windows SDK 10.0.22621.0 and Blender 5.1.1.

The final candidate was measured at native 1920×1080, TAA method 2/quality 3, primary and secondary screen percentages 100, dynamic resolution 0, VSync off, max FPS 60, D3D11, shadow/postprocess quality 3 and no Lumen/reflections. Actual normal 1× process 52460 ran from **08:46:42.593 to 08:56:43.868 UTC and exited 0**. Seed 49/follow Zura supplied 35,455 total profiled frames, including **1,551 frames with twelve visible combatants and all four live encounters**. The bounded 600-second observation ended in round 13 with `complete=false`; whole-match verification is the separate completed functional evidence above.

| Final required busy subset | p50 ms | p95 ms | p99 ms | Maximum ms |
|---|---:|---:|---:|---:|
| Frame | 16.666800 | 16.667002 | 16.727901 | 55.200199 |
| Game thread | 1.896200 | 5.753300 | 7.828300 | 55.124699 |
| Render thread | 2.939300 | 3.662200 | 4.359200 | 6.055800 |
| GPU elapsed frame | 16.657400 | 20.405300 | 21.381100 | 23.574600 |

Eight required-load frame samples exceeded 33.33 ms and none exceeded 100 ms. Across all 35,455 frames, frame p99 was 16.713600 ms, maximum 109.393997 ms, with 37 frames over 33.33 ms and one over 100 ms. Peak physical process RAM was **414,691,328 bytes**. This supports approximately 60 FPS for the measured busy percentiles, with actual hitches retained; it is not a promise of 60 FPS on every frame or another machine.

Source: `reports/WC-360/alpha-candidate-normal1080/frame-analysis.json` and `launch.json`; frame CSV SHA256 `ce922ebb2cf86986ae825094cda4a0fb55cf7beb12ad06a8ab3e349a14698aff`. The process used a hidden window with actual rendering, scripted inputs and state/frame exports; automatic PNG and projected-bound capture were disabled. No other task-owned game/build/render job competed. Existing user Unreal Editor and Blender processes were preserved. This is not a foreground manual benchmark. GPU values are `RHIGetGPUFrameCycles` elapsed-frame telemetry, not per-pass shader timing.

Earlier measurements are preserved for comparison, not substituted for the final result:

| Prior native-1080 busy sample | Required frames | Frame p95 / p99 / maximum ms | >33.33 / >100 ms | Peak physical bytes |
|---|---:|---|---|---:|
| Preceding native TAA, automatic captures | 1,479 | 16.667002 / 49.047802 / 136.643402 | 20 / 9 | 466,599,936 |
| Older TSR baseline, automatic captures | 1,381 | 19.954798 / 46.974201 / 248.057007 | 37 / 6 | 489,902,080 |

Records: `shipping-normal1080-taa/frame-analysis.json`, `shipping-normal1080/frame-analysis.json`, and `performance-and-manual-review.md`. The preceding TAA sample ended in round 13; the older TSR process completed a normal-speed round-20 tournament before exit 0. Earlier TSR is inferred from the installed default and absent override rather than recorded AA telemetry. Seeds/settings/capture instrumentation differ, and the final binary also contains the seed-summary bookkeeping fix, so this is not a controlled single-variable A/B experiment or proof of each hitch's cause.

## Remaining acceptance and exact resume checklist

The packaged game has executed successfully, but the contract's final presentation/manual gates have not passed. Preserve the package and immutable manifest above. The final performance result is recorded above. The user-authorized manual resume is blocked by native-tool targeting; this candidate is not an accepted final playable/presentable alpha. The 08:58:41 UTC zero-game inventory is historical: a fresh final game, bootstrap 55768/inner 55080, is now held open ready to continue after the dialog is dismissed.

1. **Dismiss the tool-inaccessible dialog, then continue the already authorized checks.** The user explicitly authorized dismissing Windows Security and continuing. The root agent attempted Cancel at point (1063, 683), but the native tool rejected the click because that point belongs to `PickerHost.exe`/Windows Security rather than the targeted Wonder Chess window. This was a tool targeting rejection, not an automatic approval-review rejection. A subsequent app inventory listed PickerHost as running with `windows=[]`; only game window 4855012 was targetable. No dismissal or permission grant succeeded. The current blocker is **BLOCKED_NATIVE_TARGET_UNAVAILABLE** (the native tool cannot target the dialog), recorded in [the resume attempt](WC-360/alpha-candidate-manual-resume/attempt.json). The fresh final game (bootstrap 55768/inner 55080) remains open ready for manual testing while the user is asked to click Cancel. Existing user authorization is sufficient to continue; it should not be requested again. The earlier 08:58 run and its actual conversation-only capture remain preserved in `alpha-candidate-manual/blocked.json`. At that earlier checkpoint, the guide's instruction “Do not act on security or privacy permission requests” caused the pause; the user's later explicit override supersedes that reason. The old process was stopped and its zero-game inventory does not describe the newly opened session. None of these observations identifies why Windows displayed the dialog.
2. **UI-01: exercise the actual final package manually.** Launch from the packaged Windows folder; complete title→lobby→practice and normal 1H7B. Buy with the button, inspect without buying, place by click and drag, return to bench, swap, cancel/right-click, merge three copies, test full-bench merge-possible/rejected buys, sell, reroll, lock, XP/level, Ready and combat lockout. Scout/home with selection preserved, reach early elimination/spectate, read results and restart. Capture actual screens and record observed/expected behavior, including failures.
3. **UI-02: inspect actual information.** Check owned versus enemy information boundaries, star-adjusted HP/shield/armor/resistance/rate, Physical/Magic/True damage and delivery labels, active numerical values/timing/range, matching trait recipients and numerical bonuses, selection/team markers, ghost donor labels, timeouts/cap labels, damage/healing/absorbed/health-loss recap and a comprehensible loss. Verify no stale winner or old selection/private state after a restart or host abort.
4. **UI-03: test access and persistence.** At 1920×1080 and 1280×720, check EN/ID text overflow, Tab/Enter visible focus, left/right and dragged volume sliders, reduced motion, fullscreen/window changes and both input alternatives. Change options, close the executable, cold launch and verify persisted settings. Record actual outcomes; key parity alone is insufficient.
5. **ART-02/03 and audio: review continuous normal-speed gameplay.** Play all twelve heroes' seven animations, retaining actual clips/video or timed captures, and check deformation, ground contact, attacks, active release/recovery agreement, projectile/dash direction and impact/effect clarity in twelve-piece battles. Listen to actual music and all shared/dossier-specific cues at the saved volumes; inspect clipping/masking/repetition and whether the mix is nonintrusive. Existing 84 sampled combinations and all-twelve living stills do not replace this temporal/auditory check.
6. **Preserve and bind evidence.** Use a new report directory and `-WCEvidenceDir="<absolute directory>"` for direct game captures, or `-EvidenceDirectory` through `tools/unreal/launch_alpha.ps1`; F9 produces an actual screenshot. Retain failed attempts, executable/source/catalog hashes, actual process IDs/exits, settings and seed. Update the all-32 matrix and root-owned state only from completed evidence. No new balance scope or assets are required merely to close manual review.

Clean-machine prerequisites and a physical second-PC local-network run remain explicitly untested. Actual two-process 2H6B is complete and is not invalidated by that separate boundary. Remaining observed concerns are modest pale effect contrast, a small conservative Rok framing margin, measured instrumentation-run stalls and legal marginal bot churn. The final no-PNG capture improves the recorded busy-frame percentiles while retaining real hitches; unreviewed continuous presentation is not labeled cosmetic or accepted.

## Reproduce existing checks

Run from the Wonder Chess workspace. Use fresh evidence destinations and retain current manifests. No installation or download is needed for these installed tools.

```powershell
python tools/validate_kit.py
python -m unittest discover -s tests -v
python tools/build_documents.py --check
python tools/compile_catalog.py --check
python tools/unreal/sync_runtime_data.py --check

.\tools\unreal\launch_alpha.ps1 -Mode Regression -Trials 100 -EvidenceDirectory 'C:\Users\iputu\Documents\Wonder Chess\reports\WC-360\manual-rerun-100'
.\tests\runtime\run_shipping_network_routed.ps1 -ProvenancePath 'C:\Users\iputu\Documents\Wonder Chess\reports\WC-360\alpha-candidate-provenance.json' -EvidenceName 'manual-rerun-network'
```

Installed Unreal `Engine/Build/BatchFiles/Build.bat` builds target `WonderChessEditor Win64 Development` with the project path, `-WaitMutex -NoHotReloadFromIDE`. `tools/unreal/package_game.ps1` is the actual BuildCookRun wrapper; use a new archive destination when changing source or settings. `reports/WC-360/final-analysis/capture_provenance.py` captures a new immutable identity after a successful package. Do not overwrite old evidence or promote old-binary checks across unverified changes.

The native suites were executed through `tests/runtime/build_and_run.ps1`, `run_targeted_combat.ps1` and `run_trait_combat.ps1`. Their current wrappers use fixed output directories, including the retained `targeted-native` and `trait-native` reports. They are intentionally omitted from the safe rerun block above: preserve those directories and assign a fresh output destination before repeating their compilation. The current package can be regression-tested directly with the fresh evidence path above without rebuilding these suites.

The local source checkpoint preserves authored models, exports, tests and runtime. Seventeen automatic `.blend1` backups, 154 FBX texture-sidecar files and two generated FileOpenOrder logs were kept on disk and excluded from staging. Three identical arena `.001.png` byproducts were intentionally retained in Git because the authored arena manifest lists them; removing them would break a fresh-checkout inventory. Genuine revision `.blend` files and isolated drill assets remain preserved. No unrelated work was deleted or reset.

Historical failures—animation basis/reimport settings, oversized replication, positional Shipping startup URLs, spectator overlap/name display and old namespace seed-summary metadata—remain in their original reports alongside independently executed repairs. The final current functional tests above supersede those particular defects; they do not erase the remaining manual, presentation and performance limits.
