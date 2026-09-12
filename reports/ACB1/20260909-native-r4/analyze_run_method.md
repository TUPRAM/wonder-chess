# Post-run analyzer method

Run only after PID 36432 exits:

```powershell
python reports/ACB1/20260909-native-r4/analyze_run.py --confirm-process-exited
```

The flag is an operator declaration, not automatic process-exit verification. No game controls, native UI, sockets, settings, or existing evidence are changed. The script writes only `run_analysis.json`, `run_analysis.md`, and `run_analysis_spikes.csv` in its output directory. The analyzer itself and this method note are the only files authored by the preservation subagent.

The analyzer streams the per-namespace CSV/JSONL logs, hashes inputs while reading, and records size/mtime stability. It reads the small session summaries for configuration and metadata; the duplicate `session.json` alias is excluded. Parse failures and files changing during the read produce an incomplete status and nonzero exit, with valid available observations retained. No snapshots, timings, spikes, or failed records are silently substituted with a passing default.

An exact repetition of the complete ordered CSV header is recognized as a structural row, with its file, physical line, header occurrence and fields recorded as a diagnostic. This supports the observed namespace-0 return-to-frontend header append. Partial or altered headers and arbitrary malformed timing rows remain errors. Initial analysis outputs were copied with verified SHA-256 preservation to `analysis-initial/` before this correction; the rerun does not erase the initial result.

Every recorded frame participates in its all-recorded, phase, round/phase, and applicable visible-combat subsets. Exact sorted percentiles follow the engine writer's floor-index convention. Maximum values, top 20 rows per timing metric, threshold counts, frame-counter gaps, and every row exceeding 33.333 ms in any available metric are retained. GPU unavailability is counted separately. Frame interval, game-thread active time, render-thread active time and GPU timing remain distinct.

The source writer in `game/Source/WonderChessRuntime/Private/WCVerification.cpp` begins CSV profiling five seconds after each namespace and stops after completion/abort. This analyzer cannot recover those missing frames. It does not trim any additional warmup, pause, screenshot, transition or hitch samples. The phase enum comes from `Public/Simulation/WonderSimulation.h`: preparation 0, combat 1, settlement 2, finished 3, aborted 4.

Standalone Solo Options pauses `Match::Tick` through `bOptions` in `WCMatchRuntime.cpp`. That flag is not present in the inspected frame/snapshot/session schemas. `frontend_page` comes from the frontend page rather than the in-game Options overlay. Therefore wall duration includes unidentified pauses, and combat-phase timing subsets may include paused frames. No active simulation duration or pause-filtered percentile is invented. Normal speed is the recorded startup-derived `simulation_speed_multiplier == 1`; authority seed is reported separately from unused scripted default seed fields.

Snapshots supply state-level evidence for initial round one, eliminations, continued tournament rounds, finished state, placements, encounter progress, and fresh namespace/seat state after a finished match. A namespace change without prior completion is recorded but not called a restart after results. Manual acknowledgment records can prove received accepted/rejected replies; absent intent payloads cannot prove which command was issued or state conservation. All such boundaries remain in the report.

The analyzer does not inspect images or audio, certify continuous movement, infer audio quality from `music_component_playing`, validate machine metadata independently, or issue art/release/hosting/balance acceptance. It was not run on the full dataset while the performance process was active. Pre-run verification covered syntax, help/refusal behavior and tiny in-memory format checks. The final dataset was analyzed only after process exit.

Post-exit correction verification: PID 36432 was confirmed absent before rerunning. The completed read retained 119,892 frame samples across three namespaces, recognized only the exact second header at namespace-0 CSV line 9409, and reported zero parse errors or changing inputs. A tiny test confirmed that an altered header and an arbitrary malformed row remain errors. Every frame group, percentile, maximum and spike record matched the preserved initial analysis; the spike CSV was byte-identical. Namespace 0 was reused on return to frontend, so its overwritten latest session summary and mixed snapshot clock epochs must not be treated as one fresh uninterrupted match. Namespace 1 is the completed tournament; namespace 2 is the observed restart and was stopped during round 2.
