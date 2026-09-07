# Wonder Chess 24-hero implementation checkpoint

Updated 2026-09-07T17:30:32.953183+00:00. Source checkpoint `7f50c6c`. The user requested a fast closeout and deferred real-time MCP bridge discussion.

**The Windows Unreal package is produced and exercised. Full release acceptance remains open. The models are authored, imported and animated; they are not certified finished artwork.**

## Launch and source

- Launcher: [WonderChess.exe](<C:/Users/iputu/Documents/Wonder Chess/builds/WonderChess-Update24-Checkpoint-r4/Windows/WonderChess.exe>). Keep the entire Windows folder together.
- Double-click WonderChess.exe, choose **Play > Solo** for one human and seven persistent bots. Choose **Heroes** for the gallery. The LAN menu prepares real local sessions; it is not an online matchmaking service.
- Inner Shipping executable SHA-256: `67b00eeca8f60f6f8bc62df95fb833f1174f3a3c086ef9c452b39ea0262af0f0`.
- Source project: [WonderChess.uproject](<C:/Users/iputu/Documents/Wonder Chess/game/WonderChess.uproject>); C++: [WonderChessRuntime](<C:/Users/iputu/Documents/Wonder Chess/game/Source/WonderChessRuntime>).
- Canonical data: [data](<C:/Users/iputu/Documents/Wonder Chess/data>); generated data: [generated](<C:/Users/iputu/Documents/Wonder Chess/generated>). Schema `3.1.0`, profile `alpha_24`, balance `alpha_24_v0.4.1`, protocol `6`.
- Catalog digest: `95509d001ca0e6c55fa64a616df6e2e9a01a3809a9b9c82d9bd0a725dad3a1ec`.
- Full input/build/payload identity: [provenance.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U430/20260907T171400Z-protocol-fix/provenance.json>). Git HEAD in that record is historical capture context; per-file hashes are authoritative. The source was then committed as `7f50c6c`.

## Implemented and verified boundary

All24 stable hero IDs are in actual combat. The update includes short display names, six races/six classes and reachable2/4 tiers, individual skills, visual-only weapons/armor, monster rounds1/2/3/every positive multiple of5, original Brighthaven lobby, Solo/LAN preparation and entry transition, animated gallery and star-dependent details, and the existing shop/bench/deployment/upgrades/leveling/scouting/elimination/spectating/results/restart loop. No item inventory or equipment drops were added.

Closeout completed Varek/Iri/Oren source and imports, finalized Rok/Kesh/Nella alternating attack windows, forced Unreal marker persistence after an actual cold-load failure, and centralized protocol6 after an actual network audit found stale protocol5 public metadata. Existing rigs, sources and retained failures were preserved.

| Check | Actual result |
|---|---|
| Fresh baseline |400 specification/data checks;147 Python tests;28 generated documents;6 catalog artifacts passed |
| Native current combat |100 tournaments;3,379,152 assertions passed |
| Actual Unreal cold reload |5 tests passed;24 hero meshes,168 unique clips and24,138 sampled bone transforms; neutral/data/window checks passed |
| Final Editor + Shipping build/cook/archive |PASS; corrected qualified-constant run. Initial C2065 failure retained |
| Final packaged gallery |PASS 531 checks;24 models,24 portraits,168 clips;72 star-stat and75 effect-star rows |
| Final packaged0H8B |PASS100 actual-combat tournaments;581,951 audit checks,0 failures |
| Final packaged1H7B/restart |PASS 93 checks;3 complete scripted matches,2 restarts, elimination and spectating |
| Final packaged2H6B loopback |PASS35 paired-state +21 additional checks;both players reached round33;both received protocol6;process exits0 |
| Physical two-machine2H6B |NOT_RUN: second physical machine/address/access not supplied |
| Manual normal-speed complete1H7B |NOT_RUN: native computer-use APIs disabled in current session |
| Continuous168-clip and audio approval |NOT_RUN;movies/PCM/PNG evidence does not establish listening or visual approval |

The final functional runs overlapped accelerated game/regression workloads. They establish behavior, not uncontended performance. Their legal scripted player inputs are not manual play.

Final1H7B outcomes: namespace1:round28, human eliminated round17, placement8; namespace2:round30, human eliminated round16, placement7; namespace3:round29, human eliminated round17, placement7.

## Asset matrix and review media

All24 source/export/import hash bindings pass, with168 hero clips and7 neutral sources/exports/imports containing40 neutral clips. Detailed matrices: [asset-readiness.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/asset-matrix-complete-inputs/asset-readiness.json>), [hero-clips-168.csv](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/asset-matrix-complete-inputs/hero-clips-168.csv>), [neutral-clips.csv](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/asset-matrix-complete-inputs/neutral-clips.csv>).

Actual Unreal capture:3,701 frames over all168 clips at20Hz, encoded into168 movies with readback. [Review movies](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/engine-movies168>); [encoding-report.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/engine-movies168/encoding-report.json>). These were captured before the final metadata-only correction; all579 game_content provenance entries match the final inputs exactly (staged source data is verified separately): [content-continuity.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U430/20260907T171400Z-protocol-fix/content-continuity.json>).

| Hero | Stable ID | Source revision | Imported clips | Finished-art approval |
|---|---|---:|---:|---|
| Ada | `wc_u_human_guardian` | 9 |7|Open|
| Mira | `wc_u_human_priest` | 7 |7|Open|
| Rowan | `wc_u_human_mage` | 7 |7|Open|
| Liora | `wc_u_elf_ranger` | 8 |7|Open|
| Elin | `wc_u_elf_priest` | 7 |7|Open|
| Sylas | `wc_u_elf_rogue` | 9 |7|Open|
| Borin | `wc_u_dwarf_guardian` | 7 |7|Open|
| Tessa | `wc_u_dwarf_ranger` | 7 |7|Open|
| Dagna | `wc_u_dwarf_warrior` | 7 |7|Open|
| Rok | `wc_u_orc_warrior` | 8 |7|Open|
| Zura | `wc_u_orc_mage` | 7 |7|Open|
| Kesh | `wc_u_orc_rogue` | 9 |7|Open|
| Cass | `wc_u_human_warrior` | 5 |7|Open|
| Neris | `wc_u_elf_mage` | 6 |7|Open|
| Orla | `wc_u_dwarf_priest` | 4 |7|Open|
| Tala | `wc_u_orc_guardian` | 6 |7|Open|
| Pippa | `wc_u_halfling_warrior` | 7 |7|Open|
| Finn | `wc_u_halfling_ranger` | 5 |7|Open|
| Nella | `wc_u_halfling_rogue` | 5 |7|Open|
| Milo | `wc_u_halfling_mage` | 2 |7|Open|
| Sora | `wc_u_dragonkin_guardian` | 7 |7|Open|
| Varek | `wc_u_dragonkin_ranger` | 3 |7|Open|
| Iri | `wc_u_dragonkin_rogue` | 1 |7|Open|
| Oren | `wc_u_dragonkin_priest` | 1 |7|Open|

## Measured performance

Final package,150-second normal-speed opening,1920x1080/D3D11/100% screen scale/60fps cap. Lenovo82RG/GR1ZZYLY, AMD Ryzen7 6800H,16GB RAM, active NVIDIA RTX3060 Laptop GPU6GiB. The OS also lists an AMD integrated GPU; the measured active RHI adapter is NVIDIA. Existing user Blender stayed open. No other task game, compiler or encoder was running during this final sample.

| Sample | Frames | Frame p50 ms | Frame p95 ms | Frame p99 ms | Max ms |
|---|---:|---:|---:|---:|---:|
|all_profiled_frames|8341|16.667|16.667|16.678|35.001|
|neutral_combat_frames|2226|16.667|16.667|16.675|29.300|
|eight_live_neutral_encounters|1068|16.667|16.667|16.785|29.300|
|pvp_combat_frames|2409|16.667|16.667|16.681|25.835|

Eight simultaneous neutral encounters: **OBSERVED**. Required busy12-visible-unit load: **NOT_RUN**. Full-match, busy PvP, all-hero lobby/gallery stage profiling remain NOT_RUN. CPU/render/GPU timings, settings, memory and input hashes are in [frame-summary.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U450/20260907T172100Z-r4/normal1080-opening/frame-summary.json>).

## Defects and remaining acceptance

- Art remains prototype-quality in places: simplified facial/anatomical forms, conspicuous rounded joints, sparse costume/material detail and uneven silhouettes. Improve these against the authored dossiers; do not call current technical exports finished heroes.
- Review all168 movies continuously; inspect hands, equipment contact, deformation, footsteps, attack release, effects and transitions in live Unreal. Audition all audio and verify synchronization. Encoded silent review movies do not test audio.
- Balance remains initial tuning:100 tournaments had12,597 fights,1,815,540 events,1,844 combat timeouts and524 ghosts. Simulated duration median1,284.525s, p951,426.95s. Early waves were won800/800 each; round30 only32/132 wins; hero use is uneven (Neris69 unit-rounds versus Dagna12,366). Do not call balance solved.
- Complete manual normal-speed1H7B, physical2H6B on two machines, actual disconnect/recovery on the final build, and full-match/lobby/gallery/busy-load profiling. Existing earlier recovery and loopback records are retained but do not close these current mandatory gates.
- Current computer-use tool explicitly disables native surfaces. No callable Blender real-time bridge was found. The supplied enabled-addon screenshot is not connection proof; connection setup was deferred at the user's request.

## Evidence and exact resume

- provenance: [provenance.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U430/20260907T171400Z-protocol-fix/provenance.json>)
- asset_matrix: [asset-readiness.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/asset-matrix-complete-inputs/asset-readiness.json>)
- hero_clip_matrix: [hero-clips-168.csv](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/asset-matrix-complete-inputs/hero-clips-168.csv>)
- regression_audit: [regression-analysis.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U450/20260907T172100Z-r4/regression-audit-complete/regression-analysis.json>)
- restart_audit: [audit.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U450/20260907T172100Z-r4/restart/functional-audit/audit.json>)
- network_audit: [network-analysis.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U450/20260907T172100Z-r4/loopback/audit/network-analysis.json>)
- gallery_audit: [20260907T172238-frontend-audit.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U430/20260907T171400Z-protocol-fix/gallery1080/20260907T172238-frontend-audit.json>)
- frame_times: [frame-summary.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U450/20260907T172100Z-r4/normal1080-opening/frame-summary.json>)
- movies: [encoding-report.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260907T165200Z-closeout/engine-movies168/encoding-report.json>)
- Retained r3 failures and corrections: [retained-failures.json](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U450/20260907T170300Z-closeout/retained-failures.json>). Earlier wrong-fixture and premature incomplete-evidence audits remain failed; fresh completed audits are separate.

Resume this existing workspace and read AGENTS.md, START_HERE.md, this handoff and implementation_state.json. Keep source commit7f50c6c and the immutable r4 package. Begin the next user-authorized discussion by verifying the actual callable real-time MCP bridge before editing a live Blender scene. Then prioritize Ada visual quality, use the168 review movies and matrix to address each hero, and repeat affected imports/cold tests/package checks. Do not regenerate the project or overwrite retained sources/evidence.

For physical LAN use [PHYSICAL_LAN_WC_U460.md](<C:/Users/iputu/Documents/Wonder Chess/docs/current/PHYSICAL_LAN_WC_U460.md>) and [run_physical_lan.ps1](<C:/Users/iputu/Documents/Wonder Chess/tests/runtime/run_physical_lan.ps1>); the launcher defaults to preflight and needs real machine addresses. Do not label loopback as physical LAN.

Automatic approval review previously rejected moving/cleaning70 misplaced PNGs under C:/reports/WC-U440/20260906T162705Z-elf-shoulders, reason "blocked by policy". They remain untouched. Exact prior handoff: reports/WC-U440/20260906T162705Z-elf-shoulders/elf-source8-handoff.md.

Final post-closeout validation:400 checks,147 tests,28 documents and6 catalog artifacts passed; logs in reports/WC-U460/20260907T173100Z-final-checks.
