# Screenshot-free front-end profile checkpoint

Status: SOURCE IMPLEMENTED; Unreal compile and route execution NOT RUN by this lane. Root owns builds and all runtime launches. Current immutable IntegratedSlice-r2 predates this change and cannot exercise this route.

Owned changes:
- New game/Source/WonderChessRuntime/Private/WCFrontEndProfile.cpp.
- WCFrontEnd.h/.cpp: opt-in tick, state, and suppression of showcase preference persistence only during the opt-in profile.
- WCVerification.h/.cpp: read-only WCReadVerificationClock plus additive numeric frame_counter CSV field. The existing first-five-seconds exclusion remains unchanged.

Run contract after a new build:
- Launch the built game with -WCFrontEndProfile -WCProfile and an explicit fresh -WCEvidenceDir="C:/Users/iputu/Documents/Wonder Chess/reports/WC-U450/<fresh-UTC>/frontend-profile-1080". Use -windowed -ResX=1920 -ResY=1080 for a named resolution. Run an independent fresh 1280x720 instance if needed.
- Normal 1x only. Do not combine with WCFrontEndAudit, screenshot/animation-review/exercise/autostart/host/join/selection/recovery routes, NullRHI, fixed-step timing, or frontend page/hero/clip overrides. WCExitAfter can be omitted; if supplied it must be at least 1810 seconds.
- The profile has its own 1800-second hard bound and exits two seconds after finishing, allowing normal one-second CSV flushing. Expected steady viewing is 1100 seconds, plus readiness and navigation time.
- Retain launch.json with actual executable path/hash, argument vector, PID, UTC, resolution, named hardware, RHI, full payload provenance and ambient competing processes. Use the existing packaged payload preflight before any new Shipping launch.
- Do not change saved language, volume or reduced-motion settings for this route. Its report states whether clips run or hold pose zero according to the current preference. An ordinary-motion run requires the user's current ordinary-motion setting; the route does not override it.

Actual route behavior:
1. Initial lobby, gallery, warm lobby: 20 seconds each after readiness.
2. All 24 heroes, first detail presentation: Idle 10 seconds and Active/Skill 10 seconds per hero, using visible native Meet this hero / Next / Idle / Skill buttons through Slate Enter key down/up.
3. Warm gallery and lobby, 20 seconds each.
4. All 24 heroes again, warm detail revisits: same Idle/Active dwells.
5. Warm gallery and lobby, 20 seconds each, then exit.

Total planned: 103 settled stages, including 96 hero detail stages. Each stage requires expected actual page, hero ID, star 1, exact skeletal mesh and animation asset paths, original scene camera, no missing asset message, and saved motion behavior. Before a settled dwell it requires at least 30 ready frames and 0.5 seconds with original scene imported, streaming work zero, and available editor asset/shader compilation counters idle. Sixty-second settling timeout is a failure. Unexpected match/entry/network state, missing button/asset, changed preferences, screenshot request, changed clock or evidence write failure is a failure. No game entry or inventory commands are dispatched.

Evidence files:
- frontend-profile.json: STARTED then PASS_ROUTE_EXECUTION_ONLY or FAIL, exact completed stage count, actual dwell durations/tick spans, identity, settings and residency context.
- frontend-profile-markers.jsonl: route_ready; action_begin; action_return; measure_begin; measure_end; route_end. Every stage marker contains UTC, CSV-relative wall_seconds, monotonic time, frame_counter, expected/actual page, hero, clip, visit class and actual native button labels.
- Existing namespace-0 frames CSV and session JSON; CSV retains transitions, settling and dwell rows. Existing session GPU-availability semantics stay unchanged.

Interpretation:
- This is first UI presentation / first detail presentation versus warm revisit. AWCBoardPresenter::Initialize eagerly loads and retains all hero meshes, portraits and seven clips before the frontend is available. Object presence recorded by FindObject does not establish disk/cache/texture-mip residency. No forced GC or cache eviction occurs.
- The initial five CSV seconds remain absent; pre-frontend startup and eager asset-loading costs are not measured. Initial settled lobby recording starts only once the verification clock reaches ten seconds.
- CSV is sampled during controller Tick, before HUD-triggered navigation. Steady rows use frame_counter > measure_begin.frame_counter + 1 and <= measure_end.frame_counter, with matching page. The first post-marker row is retained separately as boundary instrumentation; navigation/settling hitches must also be summarized and never silently removed.
- File markers occur at boundaries; the ordinary WCProfile frame/snapshot/session instrumentation remains. This is not an uninstrumented benchmark. Record concurrent Blender/compiler/regression load externally and do not promote confounded runs to final performance acceptance.
- PASS_ROUTE_EXECUTION_ONLY does not establish visual polish, manual interaction, screenshots, continuous animation review, gameplay, LAN or performance acceptance. There are no screenshots or rendered-video outputs in this route.

Fresh verification in this folder:
- reference-tests.log: 133 tests passed.
- frame-tests.log: 10 focused frame-analysis tests passed.
- git diff --check on owned existing source: passed; Git emitted only normal LF/CRLF worktree warnings.
- C++ compilation, complete native profile run, actual percentile/hitch analysis and refusal launches: NOT RUN here, delegated to root build/runtime owner.

Recommended actual checks after compile:
- A complete final-24 normal-1x run at named resolution should report 103/103 completed stages and no PNG files, with 48 Idle and 48 Active settled intervals covering each hero twice.
- A reduced-motion run must keep bPauseAnims true and all settings unchanged; no active-play claim from that workload.
- Separate fresh conflict invocation combining WCFrontEndProfile and WCShots should fail before navigation. A missing required asset must fail and retain completed partial stages. A preexisting profile report must remain unchanged and cause refusal.
- Compare saved WonderChess preferences before/after. Bind the resulting CSV and workload context to separate transition and steady per-page/per-hero percentile and hitch summaries.

Additional report-scoped compatibility fixture: test_profile_csv_compatibility_fixed.py passed 1/1 test, validating additive frame_counter acceptance, three actual page labels, preserved GPU absence, no inferred neutral fights, and WCFrontEndProfile not classified as a capture flag. This is synthetic parser evidence only. The retained first attempt used the wrong expected subset key gallery_frames and errored; the current public key is gallery_list_frames. Both scripts/logs are preserved; no product code changed for this fixture correction.
