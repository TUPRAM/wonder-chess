# Candidate5 actual packaged regression

PASS: all 100 requested seeds are retained, completed with final phase Finished, and have no failed trials, rejected bot commands or unresolved encounters.

The actual packaged executable ran from 2026-09-06T06:45:17.197Z to 2026-09-06T06:46:42.177Z; recorded batch wall time was 84.970866 seconds on AMD Ryzen 7 6800H with Radeon Graphics. Engine 5.7.4-51494982+++UE5+Release-5.7, MSVC full version 194435226. The launch used NullRHI and no sound. This establishes packaged C++ simulation execution, not rendering or audio.

Totals: 7,118 encounters, 1,437 timeouts (20.1883%), 524 ghosts, 69,656 bot commands, zero rejects and zero unresolved encounters. Exact comparisons pass for all 100 candidate4 tournament summaries and all 17,728 round/seat rows, including their64-bit state hashes.

Explicit capped-adjudication seeds (14): [7, 18, 29, 34, 35, 36, 45, 46, 49, 65, 74, 80, 86, 89]. These confirm the earlier candidate4 inference. Match duration milliseconds: {'count': 100, 'min': 852450, 'median': 1020650.0, 'mean': 1015698.5, 'p95': 1121700, 'max': 1160500}. Individual fight duration milliseconds: {'count': 7118, 'min': 12900, 'median': 31450.0, 'mean': 31675.25288002248, 'p95': 40000, 'max': 40000}.

The runner's actual per-hero use and final-placement associations reconcile to the captured combat-lock deployments and independently match the preserved standalone composition analysis. Unlike candidate4's aggregate-only CSV, this packaged report directly records those observations. A seat counted below used the hero at least once; that association is not a causal strength estimate.

| Hero | Deployed unit-rounds | Seat-rounds | Seat-tournaments used | First-place seats that used hero |
|---|---:|---:|---:|---:|
| wc_u_dwarf_guardian | 11225 | 10146 | 753 | 96 |
| wc_u_dwarf_ranger | 6411 | 5820 | 535 | 89 |
| wc_u_dwarf_warrior | 9661 | 8818 | 719 | 88 |
| wc_u_elf_priest | 1546 | 1526 | 252 | 22 |
| wc_u_elf_ranger | 7988 | 7174 | 675 | 84 |
| wc_u_elf_rogue | 3994 | 3949 | 462 | 53 |
| wc_u_human_guardian | 11109 | 9758 | 732 | 95 |
| wc_u_human_mage | 1877 | 1857 | 292 | 41 |
| wc_u_human_priest | 2299 | 2238 | 395 | 46 |
| wc_u_orc_mage | 326 | 317 | 53 | 11 |
| wc_u_orc_rogue | 8672 | 7974 | 669 | 73 |
| wc_u_orc_warrior | 10623 | 9580 | 721 | 80 |

The runtime-loaded profile and five canonical input hashes agree with candidate5 provenance. The actual inner executable SHA256 also matches that immutable manifest. The engine log records all100 attempts, zero failures, a status0 exit request and orderly closure, with no Error-level log lines. Parent launch metadata currently records bootstrap PID/arguments but not an OS-observed exit code; the report preserves that distinction.

The complete JSON source remains at reports/WC-360/candidate5-regression/regression.json. candidate5-regression-analysis.json records comparisons, failure checks, input hashes, launch arguments, ghost donor/recipient distributions and exact measurement boundaries. This run does not certify1H7B/2H6B, visual quality, audio, frame-time targets or manual usability.
