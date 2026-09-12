# Native normal-speed run: recorded evidence analysis

Generated 2026-09-08T17:25:33.398504+00:00; PID 36432; status **COMPLETE_READ**.

Wall durations include unidentified Solo Options pauses. All recorded frame samples and spikes are included. The writer's first-five-seconds and post-completion omissions remain explicit limits.

| Namespace | Declared speed | Observed wall seconds | CSV frames | Finished state | Round-one through finish | Accepted/rejected command replies |
| --- | --- | ---: | ---: | --- | --- | --- |
| 0 | 1 | 161.790 | 9407 | False | False | 0/0 |
| 1 | 1 | 1836.482 | 106155 | True | True | 13/0 |
| 2 | 1 | 77.685 | 4330 | False | False | 2/0 |

## Namespace 0

Recorded authority seeds: []. Scripted default seed fields are not substituted for the authority seed.

| Frame subset | Samples | p50 ms | p95 ms | p99 ms | Maximum ms | >50 ms | >100 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_recorded | 9407 | 16.667 | 16.667 | 16.706 | 20.644 | 0 | 0 |
| phase:-1:entry_or_frontend | 9407 | 16.667 | 16.667 | 16.706 | 20.644 | 0 | 0 |

Recorded machine: AMD Ryzen 7 6800H with Radeon Graphics         ; active adapter NVIDIA GeForce RTX 3060 Laptop GPU; RHI D3D11; viewport 1920×1080; engine 5.7.4-51494982+++UE5+Release-5.7.

Human elimination observed: False. Round/phase continuation, rankings, all per-round timings, encounter progress, command replies, settings and maximum-spike context are in run_analysis.json.

## Namespace 1

Recorded authority seeds: [846842640]. Scripted default seed fields are not substituted for the authority seed.

| Frame subset | Samples | p50 ms | p95 ms | p99 ms | Maximum ms | >50 ms | >100 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_recorded | 106155 | 16.667 | 16.667 | 16.754 | 185.648 | 311 | 196 |
| combat_neutral | 11974 | 16.667 | 16.667 | 16.777 | 158.841 | 37 | 30 |
| combat_pvp | 58577 | 16.667 | 16.667 | 16.752 | 167.337 | 149 | 109 |
| phase:0:preparation | 27327 | 16.667 | 16.667 | 16.722 | 138.160 | 44 | 20 |
| phase:1:combat | 70551 | 16.667 | 16.667 | 16.756 | 167.337 | 186 | 139 |
| phase:2:settlement | 8276 | 16.667 | 16.667 | 36.312 | 185.648 | 81 | 37 |
| phase:3:finished | 1 | 16.667 | 16.667 | 16.667 | 16.667 | 0 | 0 |
| twelve_unit_visible_combat | 5654 | 16.667 | 16.672 | 17.228 | 155.405 | 51 | 44 |
| visible_combat | 70544 | 16.667 | 16.667 | 16.756 | 167.337 | 186 | 139 |

Recorded machine: AMD Ryzen 7 6800H with Radeon Graphics         ; active adapter NVIDIA GeForce RTX 3060 Laptop GPU; RHI D3D11; viewport 1920×1080; engine 5.7.4-51494982+++UE5+Release-5.7.

Human elimination observed: True. Round/phase continuation, rankings, all per-round timings, encounter progress, command replies, settings and maximum-spike context are in run_analysis.json.

## Namespace 2

Recorded authority seeds: [2061823456]. Scripted default seed fields are not substituted for the authority seed.

| Frame subset | Samples | p50 ms | p95 ms | p99 ms | Maximum ms | >50 ms | >100 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_recorded | 4330 | 16.667 | 16.667 | 16.726 | 139.167 | 3 | 2 |
| combat_neutral | 298 | 16.667 | 16.667 | 16.728 | 139.167 | 1 | 1 |
| phase:0:preparation | 3811 | 16.667 | 16.667 | 16.725 | 121.809 | 1 | 1 |
| phase:1:combat | 298 | 16.667 | 16.667 | 16.728 | 139.167 | 1 | 1 |
| phase:2:settlement | 221 | 16.667 | 16.667 | 16.680 | 96.291 | 1 | 0 |
| visible_combat | 297 | 16.667 | 16.667 | 16.728 | 139.167 | 1 | 1 |

Recorded machine: AMD Ryzen 7 6800H with Radeon Graphics         ; active adapter NVIDIA GeForce RTX 3060 Laptop GPU; RHI D3D11; viewport 1920×1080; engine 5.7.4-51494982+++UE5+Release-5.7.

Human elimination observed: False. Round/phase continuation, rankings, all per-round timings, encounter progress, command replies, settings and maximum-spike context are in run_analysis.json.

## Input diagnostics

Identical repeated CSV headers recognized: 1. Their exact file, physical line, header occurrence and fields are recorded in run_analysis.json. Arbitrary malformed rows remain parse errors.

## Restart evidence

[
  {
    "from_namespace": 0,
    "to_namespace": 1,
    "prior_finished_observed": false,
    "new_round_one_observed": true,
    "eight_positive_health_seats_observed": true,
    "eight_zero_placements_observed": true,
    "state_level_restart_after_completion": false,
    "initial_owner_private_summary": {
      "seat": 0,
      "gold": 10,
      "xp": 0,
      "level": 3,
      "revision": 4294967297,
      "sequence": 0,
      "locked": false,
      "unit_count": 0
    },
    "boundary": "Namespace/round/seat reset evidence; does not prove which UI button was used or full fresh-state correctness."
  },
  {
    "from_namespace": 1,
    "to_namespace": 2,
    "prior_finished_observed": true,
    "new_round_one_observed": true,
    "eight_positive_health_seats_observed": true,
    "eight_zero_placements_observed": true,
    "state_level_restart_after_completion": true,
    "initial_owner_private_summary": {
      "seat": 0,
      "gold": 10,
      "xp": 0,
      "level": 3,
      "revision": 8589934593,
      "sequence": 0,
      "locked": false,
      "unit_count": 0
    },
    "boundary": "Namespace/round/seat reset evidence; does not prove which UI button was used or full fresh-state correctness."
  }
]

## Boundaries

- All recorded CSV samples are retained, including spikes. The engine writer omits the first 5 seconds of each namespace and stops profiling after completion/abort; this analysis cannot recover unrecorded frames.
- Normal speed means the recorded simulation_speed_multiplier is 1. Elapsed duration is wall time, including Solo Options pauses. No explicit bOptions/paused signal exists in the inspected CSV, snapshot, or session formats; paused combat frames cannot be separated reliably.
- frontend_page describes the frontend page, not the in-game Solo Options overlay. Repeated state snapshots are not treated as proof of a pause.
- Visible combat means phase=1 and visible_alive>0; the twelve-unit subset means phase=1 and visible_alive>=12. Both can include unidentified paused frames.
- GPU zero/unavailable samples are counted as unavailable, not as zero-cost GPU frames. Other finite nonnegative timing samples are retained.
- Percentiles use sorted_values[floor((n-1)*p)], matching WCVerification.cpp. Frame interval, game-thread active time, render-thread active time and RHI GPU timing are distinct metrics.
- State evidence of completion, elimination and namespace restart does not prove continuous visual quality, results-screen interaction, audio quality, all animation clips, network hosting, or release acceptance.
- Manual command acknowledgments do not necessarily include request payload/type. Missing intent-request records are not inferred from reply IDs or state changes.

No audio or continuous visual review was performed by this analyzer. See run_analysis_spikes.csv for every recorded row where any available timing metric exceeded 33.333 ms, and run_analysis.json for the top 20 rows per metric without outlier trimming.
