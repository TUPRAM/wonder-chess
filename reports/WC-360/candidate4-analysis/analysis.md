# Candidate4 actual engine regression analysis

Candidate4 completed 100 actual eight-bot tournaments in the WindowsEditor runtime automation test. Seeds 1-100 produced 7118 encounters, 1437 timeouts (20.1883%), 524 ghost encounters, 69656 bot command log entries and 0 rejected bot commands.

Comparison with the SHA256-verified latest post-event-metadata standalone archive: all 100 summary rows (9 fields each) and all 17728 round/seat rows (11 fields each) agree exactly after CSV integer normalization. There are no missing, extra or duplicate round/seat keys. Round completeness, nonnegative health/gold and common settlement/state hashes also pass the structural checks.

The 100-match automation test reports Success, 0 errors, 0 warnings and 38.883514 seconds execution time. The complete candidate4 batch reports 5 successful automation tests, 0 failed and 0 not run. This duration measures the C++ test, not rendered frame rate or packaged startup.

Round counts: {18: 1, 19: 6, 20: 8, 21: 23, 22: 15, 23: 17, 24: 30}. Simulated match duration milliseconds: {'count': 100, 'minimum': 852450, 'mean': 1015698.5, 'median': 1020650.0, 'p95': 1121700, 'maximum': 1160500}.

30 seeds reach the authored 24-round ceiling. Of those, 14 retain more than one positive-health seat and therefore satisfy the implemented capped-adjudication condition. Inferred cap seeds: [7, 18, 29, 34, 35, 36, 45, 46, 49, 65, 74, 80, 86, 89]. This is derived from actual final rows plus the cap rule; the CSV does not explicitly record the capped flag. Shared-first-place seeds: [].

Engine CSVs do not contain individual fight lengths, hero compositions/use or effect-event totals. The separate standalone archive contains 1,390,777 effect events and preparation-lock composition rows. Its hero usage below remains supplementary standalone evidence despite exact shared result/hash parity. Placements indicate seats that used a hero at any captured round; they are not evidence that the hero caused that result.

| Hero | Deployed unit-rounds | Seat-rounds | Seat-tournaments used | Maximum star | First-place seats that used hero |
|---|---:|---:|---:|---:|---:|
| wc_u_dwarf_guardian | 11225 | 10146 | 753 | 3 | 96 |
| wc_u_dwarf_ranger | 6411 | 5820 | 535 | 3 | 89 |
| wc_u_dwarf_warrior | 9661 | 8818 | 719 | 3 | 88 |
| wc_u_elf_priest | 1546 | 1526 | 252 | 3 | 22 |
| wc_u_elf_ranger | 7988 | 7174 | 675 | 3 | 84 |
| wc_u_elf_rogue | 3994 | 3949 | 462 | 2 | 53 |
| wc_u_human_guardian | 11109 | 9758 | 732 | 3 | 95 |
| wc_u_human_mage | 1877 | 1857 | 292 | 3 | 41 |
| wc_u_human_priest | 2299 | 2238 | 395 | 3 | 46 |
| wc_u_orc_mage | 326 | 317 | 53 | 2 | 11 |
| wc_u_orc_rogue | 8672 | 7974 | 669 | 3 | 73 |
| wc_u_orc_warrior | 10623 | 9580 | 721 | 3 | 80 |

All three current core source hashes match the preserved standalone source snapshot. This readback is not a substitute for a delivered build manifest. Input file hashes, exact comparisons, supplemental provenance and all metric boundaries are in comparison.json. The executable/core source/data are unchanged by this analysis.

The candidate4 asset automation also reports success, but art attractiveness, deformation, feet/forward calibration, in-game clarity and audio remain their separate evidence gates. No packaged, 1H7B, 2H6B or performance acceptance is inferred from these CSVs.
