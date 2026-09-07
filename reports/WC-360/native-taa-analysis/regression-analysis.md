Shipping actual packaged regression: PASS

Actual Shipping packaged 0H8B simulation and recorded deployment/settlement evidence. Not human interaction, networking, rendered frame performance or art/audio acceptance.

All 100 requested seeds are retained and finished. The game reports zero failed trials, zero rejected bot commands, zero unresolved encounters and successful evidence writes. Recorded batch elapsed time was 50.775217 seconds, 2026-09-06T08:17:16.308Z to 2026-09-06T08:18:07.084Z, on AMD Ryzen 7 6800H with Radeon Graphics. This NullRHI/no-sound run is simulation execution, not a render or audio benchmark.

Totals: 7,118 encounters, 1,437 timeouts (20.1883%), 524 ghost encounters and 69,656 bot commands. All 100 candidate6 engine summary rows and 17,728 round/seat rows match, including all state and settlement hashes. A separate direct comparison with the SHA256-verified latest standalone archive also passes for every summary and round/seat row.

Explicit capped-adjudication seeds (14): [7, 18, 29, 34, 35, 36, 45, 46, 49, 65, 74, 80, 86, 89]. Match duration milliseconds: {'count': 100, 'min': 852450, 'median': 1020650.0, 'mean': 1015698.5, 'p95': 1121700, 'max': 1160500}. Individual fight duration milliseconds: {'count': 7118, 'min': 12900, 'median': 31450.0, 'mean': 31675.25288002248, 'p95': 40000, 'max': 40000}.

The table counts actual living-seat combat-lock deployments. Final-placement associations are descriptive; using a hero does not establish that hero caused the result. The actual per-hero rows reconcile to captured deployments and match the preserved standalone composition analysis.

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

Runtime-loaded profile and all five canonical data hashes agree with native-taa-provenance.json. The actual Shipping inner executable SHA256 matches that immutable manifest.

The separately captured process record reports exit_code0. No Shipping game.log is present, so engine log error/exit checks remain NOT_RUN. This headless regression overlapped the beginning of the two-process functional network run and is not a rendering performance benchmark.

This audit binds the actual native-TAA Shipping execution to its immutable source/data/content/package manifest. The earlier Shipping executions remain preserved separately; this headless run does not measure TAA rendering.
