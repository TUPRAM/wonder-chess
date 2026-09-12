# AQ1 measured performance review

Actual completed normal-speed profiling inputs; no generated timings or performance pass inferred.

## Baseline

Source: `C:\Users\iputu\Documents\Wonder Chess\reports\AQ1\20260908\profile_before`.

AMD Ryzen 7 6800H with Radeon Graphics / NVIDIA GeForce RTX 3060 Laptop GPU / D3D11 / driver 580.88 (internal:32.0.15.8088, unified:580.88). RAM record: 15.2GB (16GB approx) Virtual=38.6GB.

Resolution [1920, 1080], frame cap 60, VSync 0, seed 828301. Final round 10, phase 0, terminal complete=False.

Recorded match-relative wall span [5.002609, 350.167359] seconds. The process exit request and five-second per-namespace warmup are separate clocks; do not call this 360 seconds of sampled combat.

| Subset | Samples | Summed frame seconds | Channel | p50 ms | p95 ms | p99 ms | Maximum ms | >33.333 ms samples |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| all | 20547 | 345.181 | frame_ms | 16.667 | 16.693 | 18.389 | 100.018 | 51 |
| all | 20547 | 345.181 | game_ms | 4.357 | 11.861 | 17.412 | 98.687 | 50 |
| all | 20547 | 345.181 | render_ms | 6.898 | 10.334 | 11.886 | 32.712 | 0 |
| all | 20547 | 345.181 | gpu_ms | 16.254 | 21.444 | 23.947 | 111.238 | 33 |
| combat | 12884 | 216.371 | frame_ms | 16.667 | 16.700 | 18.916 | 100.018 | 26 |
| combat | 12884 | 216.371 | game_ms | 4.446 | 12.927 | 18.311 | 98.687 | 26 |
| combat | 12884 | 216.371 | render_ms | 6.923 | 10.317 | 11.956 | 32.712 | 0 |
| combat | 12884 | 216.371 | gpu_ms | 16.169 | 22.401 | 24.482 | 111.238 | 24 |
| twelve_visible_combat | 1106 | 18.733 | frame_ms | 16.667 | 16.698 | 21.166 | 100.018 | 4 |
| twelve_visible_combat | 1106 | 18.733 | game_ms | 4.510 | 14.239 | 19.741 | 98.687 | 4 |
| twelve_visible_combat | 1106 | 18.733 | render_ms | 7.032 | 10.622 | 12.032 | 14.679 | 0 |
| twelve_visible_combat | 1106 | 18.733 | gpu_ms | 15.836 | 20.496 | 26.203 | 111.238 | 6 |
| eight_live_neutral_fights | 900 | 15.236 | frame_ms | 16.667 | 16.808 | 24.121 | 53.156 | 5 |
| eight_live_neutral_fights | 900 | 15.236 | game_ms | 4.287 | 14.877 | 23.401 | 51.530 | 5 |
| eight_live_neutral_fights | 900 | 15.236 | render_ms | 6.819 | 10.041 | 11.671 | 13.800 | 0 |
| eight_live_neutral_fights | 900 | 15.236 | gpu_ms | 16.103 | 21.776 | 25.497 | 58.190 | 2 |

Per-round/phase distributions, channel histograms, thresholds, worst frames and source hashes are in the JSON companion.

## Candidate

Source: `C:\Users\iputu\Documents\Wonder Chess\reports\AQ1\20260908\profile_candidate_r01`.

AMD Ryzen 7 6800H with Radeon Graphics / NVIDIA GeForce RTX 3060 Laptop GPU / D3D11 / driver 580.88 (internal:32.0.15.8088, unified:580.88). RAM record: 15.2GB (16GB approx) Virtual=38.6GB.

Resolution [1920, 1080], frame cap 60, VSync 0, seed 828301. Final round 10, phase 0, terminal complete=False.

Recorded match-relative wall span [5.010936, 351.081503] seconds. The process exit request and five-second per-namespace warmup are separate clocks; do not call this 360 seconds of sampled combat.

| Subset | Samples | Summed frame seconds | Channel | p50 ms | p95 ms | p99 ms | Maximum ms | >33.333 ms samples |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| all | 20583 | 346.087 | frame_ms | 16.667 | 16.679 | 18.367 | 235.061 | 53 |
| all | 20583 | 346.087 | game_ms | 4.223 | 11.618 | 17.543 | 234.706 | 50 |
| all | 20583 | 346.087 | render_ms | 6.734 | 9.960 | 11.437 | 24.747 | 0 |
| all | 20583 | 346.087 | gpu_ms | 16.370 | 21.801 | 24.199 | 247.631 | 31 |
| combat | 12860 | 216.289 | frame_ms | 16.667 | 16.689 | 19.189 | 235.061 | 28 |
| combat | 12860 | 216.289 | game_ms | 4.323 | 12.696 | 18.641 | 234.706 | 25 |
| combat | 12860 | 216.289 | render_ms | 6.797 | 10.042 | 11.510 | 16.449 | 0 |
| combat | 12860 | 216.289 | gpu_ms | 16.268 | 22.655 | 24.732 | 247.631 | 26 |
| twelve_visible_combat | 1105 | 18.736 | frame_ms | 16.667 | 16.725 | 20.922 | 77.344 | 4 |
| twelve_visible_combat | 1105 | 18.736 | game_ms | 4.564 | 14.905 | 20.594 | 76.848 | 4 |
| twelve_visible_combat | 1105 | 18.736 | render_ms | 7.240 | 10.528 | 11.899 | 12.916 | 0 |
| twelve_visible_combat | 1105 | 18.736 | gpu_ms | 15.927 | 21.259 | 24.284 | 43.972 | 3 |
| eight_live_neutral_fights | 897 | 15.247 | frame_ms | 16.667 | 16.864 | 29.589 | 56.801 | 5 |
| eight_live_neutral_fights | 897 | 15.247 | game_ms | 4.229 | 15.278 | 28.041 | 56.570 | 4 |
| eight_live_neutral_fights | 897 | 15.247 | render_ms | 6.607 | 9.839 | 11.486 | 12.395 | 0 |
| eight_live_neutral_fights | 897 | 15.247 | gpu_ms | 16.213 | 21.991 | 29.273 | 49.265 | 8 |

Per-round/phase distributions, channel histograms, thresholds, worst frames and source hashes are in the JSON companion.

## Interpretation boundaries

- frame_ms is the world tick Delta*1000 under the engine frame cap, not an uncapped benchmark or presentation-time trace.
- game_ms/render_ms use engine active-thread counters; gpu_ms uses RHIGetGPUFrameCycles. These asynchronously reported channels are not additive or guaranteed to describe the same frame.
- All rows after the built-in five-second namespace warmup are retained, including transitions and hitches; no failed/slow sample is silently removed.
- Eight-neutral subset requires combat and exactly eight unfinished neutral encounters; it is eight simulations, not eight rendered boards. Twelve-visible subset requires combat and visible_alive>=12.
- One capped run per revision is descriptive. Same seed/flags alone do not prove identical scene mix, exact wall timing, cache state, thermal or background conditions.
- Uncooked Editor target -game with scripted seat input is not packaged/manual human evidence. No terminal tournament result is inferred from process exit0.
- closed frontend_page provides no lobby/gallery profile. Late neutral waves absent from recorded combat are not extrapolated.

## Candidate comparison

Matched settings: True. Mismatches: [].

The JSON gives candidate-minus-baseline differences for common round/phase strata and each workload subset. Different sample counts and scene mixes are retained; no arbitrary regression threshold or numeric approval is applied.

## Reviewed integrity and warnings

Both inputs have zero frame-counter gaps and all four CSV/session metric parity checks true. No evidence write failures or Error/Fatal lines were found. Both logs retain the same `MID_M_WC_Surface_5` instanced-static-mesh usage/default-material warning plus missing VisionOS launcher-icon warnings. The candidate retains a 235.061401 ms frame hitch and 247.630905 ms GPU maximum at round-4 combat. Do not claim a fully clean production render or isolated Ada cost. See `PAIRED_OBSERVATIONS.md` and `paired_integrity.json` for the reviewed scope and exact warning evidence.
