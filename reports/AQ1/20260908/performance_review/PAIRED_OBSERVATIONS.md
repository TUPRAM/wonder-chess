# AQ1 paired profile observations

The existing analyzer completed once against the two finished inputs. Both recorded seed **828301**, AMD Ryzen 7 6800H, NVIDIA GeForce RTX 3060 Laptop GPU, D3D11, driver 580.88, approximately 16 GB RAM, 1920x1080 at 100% screen percentage, 60 FPS cap and VSync off. All recorded render settings match. Both use uncooked Unreal 5.7.4 Editor target `-game` with scripted seat input, not a packaged/manual run.

| Revision | Subset | Rows | Channel | p50 ms | p95 ms | p99 ms | Max ms |
|---|---|---:|---|---:|---:|---:|---:|
| baseline | all | 20547 | frame_ms | 16.667 | 16.693 | 18.389 | 100.018 |
| baseline | all | 20547 | gpu_ms | 16.254 | 21.444 | 23.947 | 111.238 |
| baseline | twelve_visible_combat | 1106 | frame_ms | 16.667 | 16.698 | 21.166 | 100.018 |
| baseline | twelve_visible_combat | 1106 | gpu_ms | 15.836 | 20.496 | 26.203 | 111.238 |
| baseline | eight_live_neutral_fights | 900 | frame_ms | 16.667 | 16.808 | 24.121 | 53.156 |
| baseline | eight_live_neutral_fights | 900 | gpu_ms | 16.103 | 21.776 | 25.497 | 58.190 |
| candidate | all | 20583 | frame_ms | 16.667 | 16.679 | 18.367 | 235.061 |
| candidate | all | 20583 | gpu_ms | 16.370 | 21.801 | 24.199 | 247.631 |
| candidate | twelve_visible_combat | 1105 | frame_ms | 16.667 | 16.725 | 20.922 | 77.344 |
| candidate | twelve_visible_combat | 1105 | gpu_ms | 15.927 | 21.259 | 24.284 | 43.972 |
| candidate | eight_live_neutral_fights | 897 | frame_ms | 16.667 | 16.864 | 29.589 | 56.801 |
| candidate | eight_live_neutral_fights | 897 | gpu_ms | 16.213 | 21.991 | 29.273 | 49.265 |

Both profiles reach round 10 preparation, with recorded combat only through round 9. The twelve-visible subset covers rounds 7/8/9 (baseline 1,106 rows, candidate 1,105); eight unfinished neutral encounters cover rounds 1/2/3/5 (900 versus 897 rows). Both logical-alive ranges are 0-65 overall. Workload distributions and all 28 common round/phase strata are retained in `performance.json`; record counts and wall timing are not identical. Late neutral waves, full tournaments and lobby/gallery performance are not covered.

Candidate samples span match-relative 5.010936-351.081503 seconds and sum to 346.086946 seconds of frame deltas. Baseline samples span 5.002609-350.167359 and sum to 345.181116 seconds. These are not 360 seconds of sampled combat; the launch exit timer and namespace warmup use separate clocks.

Typical capped frame timing is similar, while candidate GPU p95 is 0.3573 ms above baseline overall. Eight-neutral candidate p99 rises by 5.467596 ms for frame deltas and 3.7763 ms for GPU counters. One run cannot assign these differences to Ada's art. The candidate retains a **235.061401 ms** frame hitch (game 234.706207 ms, asynchronous GPU 247.630905 ms) at round-4 combat, visible_alive=10, wall=71.239959, frame_counter=4417. Baseline maxima are 100.017601 ms frame and 111.238098 ms GPU. Overall frames over 50 ms number 19 baseline and 28 candidate; each has one frame over 100 ms. No outlier was removed.

CSV frame counters have **zero gaps** in both runs. All four CSV-versus-session metric parity checks are true for each input; every GPU sample is available. Both processes exit 0 and candidate load-error lists are empty. There are no logged evidence write failures or Error/Fatal lines in either profile. These integrity checks succeeded; they are not performance acceptance.

Both logs contain the same unresolved material warning: `MID_M_WC_Surface_5` on `WCBoardPresenter_0` lacks `bUsedWithInstancedStaticMeshes=True`; Unreal reports default material fallback and recompilation until saved. The missing VisionOS launcher-icon warnings also recur. The measured workload is therefore this actual uncooked configuration, not an asserted fully correct production render. The material warning is not identified as Ada's material and no causal link to the hitch is established.

`frame_ms` is capped world tick delta, not uncapped GPU cost or presentation time. Game/render/GPU channels use asynchronous engine counters and are not additive. Thermal conditions, background activity and cache residency were not proven identical. The candidate peak process physical memory is 1,714,196,480 bytes versus baseline 2,001,604,608; different residency means this is not an isolated memory saving attributable to Ada.

**Status: paired descriptive measurement complete, with preserved hitches and rendering warning.** No clean performance acceptance, budget exception, full-match result or owner art approval is inferred. `paired_integrity.json` retains warnings and integrity results; the analyzer was not changed, and no new GPU run or test repeat was launched.
