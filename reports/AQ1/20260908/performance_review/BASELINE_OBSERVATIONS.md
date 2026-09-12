# Baseline profile interpretation

The baseline launched at 2026-09-08T01:50:54Z and exited successfully at 01:57:19Z. `-WCExitAfter=360` measures from the verification module's process timer; the match namespace began later. The CSV covers match-relative **5.002609–350.167359s**, a 345.164750s wall span, with **345.181116s summed world-frame delta**. It is not 360 seconds of sampled combat. The built-in first-five-second match warmup is excluded by instrumentation; no additional sample trimming was applied.

Actual hardware/settings are Ryzen 7 6800H, active NVIDIA RTX 3060 Laptop GPU, D3D11, NVIDIA 580.88 (32.0.15.8088; driver date 2025-07-27), 1920×1080 at 100% resolution, VSync off, 60 FPS cap, normal simulation speed1x. Engine log reports 15.2GB physical memory (approximately 16GB); startup physical availability was 1845.95MB. OS-primary GPU metadata names the integrated AMD GPU, but the **chosen rendering adapter is NVIDIA**. Peak process physical usage in the session is 2,001,604,608 bytes. Neither RAM capacity nor this single process measurement indicates another machine's performance.

**Coverage:** 20,547 timing rows, zero frame-counter gaps; GPU timing available for every recorded row. Preparation and settlement are retained along with combat. Rounds1–9 combat completed; final state was round10 preparation, `complete=false`, timed exit requested. Neutral combat profile covers rounds1/2/3/5, not round10 or15. `frontend_page` is always `closed`: no lobby or gallery profile is present.

Overall frame p50/p95/p99/max: **16.667 / 16.693 / 18.389 / 100.018ms**. Game-thread active p95/p99: **11.861 / 17.412ms**; render-thread active **10.333 / 11.886ms**; reported GPU **21.444 / 23.947ms**. Thread/GPU counters are asynchronous and must not be added to frame time. Capped world-tick Delta is not uncapped throughput or presentation timing.

**Hitches:** 144 frame intervals >20ms; 51 >33.333ms; 19 >50ms; 1 >100ms. The largest is round9 combat start at match-wall311.378s, 12 visible /48 living logically/four fights, frame100.018ms, game98.687ms, render10.659ms, GPU111.238ms. These coincident recorded channels suggest a frame stall but do not establish its cause. Other large intervals occur in preparation too; no outlier was discarded.

**Twelve-visible combat:** 1,106 samples, 18.733s summed frame delta, rounds7–9. Frame p95/p99/max **16.698 /21.166 /100.018ms**; 4 frame intervals >33.333ms, 3 >50ms, 1 >100ms. GPU p95/p99 **20.496 /26.203ms**. This short subgroup cannot represent every later crowded fight.

**Eight live neutral fights:** 900 samples, 15.236s summed frame delta, rounds1/2/3/5. Frame p95/p99/max **16.808 /24.121 /53.155ms**; 5 frame intervals >33.333ms, 1 >50ms. GPU p95/p99 **21.776 /25.497ms**. These are eight actual concurrent simulations while one board is rendered, not eight visible arenas.

For the candidate, use the same seed828301, exercise/follow-hero flags, requested360s, normal speed, resolution/cap/VSync, engine, hardware and graphics. The comparator checks these settings and reports raw matched round/phase strata. Retain each run's scene coverage and row counts: same seed does not force identical wall-clock exposure to rounds or visual camera switches. A single capped A/B run supports descriptive comparison, not a precise causal triangle-cost estimate or final frame-rate acceptance. Thermal/cache/background state is not proven identical by these files.

`performance.json` preserves actual distributions, histograms, workload counts, source hashes and ten worst frames. `verification.json` records actual analyzer checks. Candidate comparison remains NOT_RUN until a completed candidate profile is supplied.
