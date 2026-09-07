# WC-U440 source refinement handoff - six existing heroes

These are source/export checkpoints, not finished art approval or evidence of a packaged game. Source files and all declared export hashes were read back in fresh Blender 5.1.1 processes. Current Unreal import, materials, crowded-board review, LOD appearance, audio and continuous artist approval belong to separate gates.

| Hero | Before | After | Source | Export / verification | Revisions source / geometry / animation |
|---|---|---|---|---|---|
| Ada | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T130945Z/ada/before-three-quarter.png>) | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T130945Z/ada/refinement-v3/after-three-quarter.png>) | [blend](<C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend>) | [manifest](<C:/Users/iputu/Documents/Wonder Chess/exports/heroes/wc_u_human_guardian/export_manifest.json>); [readback](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T130945Z/ada/action-trial/published-verification.json>) | 8 / 7 / 8 |
| Mira | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T130945Z/ada/mira-readonly-inspection/before-three-quarter.png>) | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/mira/refinement-v7/after-three-quarter.png>) | [blend](<C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_human_priest/wc_u_human_priest.blend>) | [manifest](<C:/Users/iputu/Documents/Wonder Chess/exports/heroes/wc_u_human_priest/export_manifest.json>); [readback](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/mira/refinement-v7/published-verification.json>) | 7 / 7 / 7 |
| Rowan | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/rowan/before/before-three-quarter.png>) | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/rowan/refinement-v3/after-three-quarter.png>) | [blend](<C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_human_mage/wc_u_human_mage.blend>) | [manifest](<C:/Users/iputu/Documents/Wonder Chess/exports/heroes/wc_u_human_mage/export_manifest.json>); [readback](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/rowan/refinement-v3/published-verification.json>) | 7 / 7 / 7 |
| Liora | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_ranger/before/before-three-quarter.png>) | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_ranger/refinement-v1/after-three-quarter.png>) | [blend](<C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_elf_ranger/wc_u_elf_ranger.blend>) | [manifest](<C:/Users/iputu/Documents/Wonder Chess/exports/heroes/wc_u_elf_ranger/export_manifest.json>); [readback](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_ranger/refinement-v1/published-verification.json>) | 7 / 7 / 6 |
| Elin | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_priest/before/before-three-quarter.png>) | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_priest/refinement-v6/after-three-quarter.png>) | [blend](<C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_elf_priest/wc_u_elf_priest.blend>) | [manifest](<C:/Users/iputu/Documents/Wonder Chess/exports/heroes/wc_u_elf_priest/export_manifest.json>); [readback](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_priest/refinement-v6/published-verification.json>) | 7 / 7 / 7 |
| Sylas | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_rogue/before/before-three-quarter.png>) | [render](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_rogue/refinement-v5/after-three-quarter.png>) | [blend](<C:/Users/iputu/Documents/Wonder Chess/art-source/heroes/wc_u_elf_rogue/wc_u_elf_rogue.blend>) | [manifest](<C:/Users/iputu/Documents/Wonder Chess/exports/heroes/wc_u_elf_rogue/export_manifest.json>); [readback](<C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T133433Z/wc_u_elf_rogue/refinement-v5/published-verification.json>) | 7 / 7 / 6 |

Bounded changes:

- **Ada:** Curved shield, fitted grip and face details; revised Attack/Hit/Victory.
- **Mira:** Connected draped mantle, split coat, staff grip; revised Active/Hit/Victory.
- **Rowan:** Open collar, fitted vest, defined orb bracket and grip; revised two-hand Active.
- **Liora:** Three curved cloak leaves, broader bow grip, quiver clearance; original actions and bowstring driver retained.
- **Elin:** Curved sleeve petals, shoulder clearance, open harp rim and support grip; revised Attack and broad-chord Active.
- **Sylas:** Single curved mantle, distinct curved blades, cosmetic lantern, fog-gray trousers and refined grip; original actions retained.

Verification boundaries:

- Four actual source views per candidate and all seven clips sampled from rendered Blender geometry. GIFs preserve normal speed at 20 FPS using every third authored frame at 60 FPS. Contact sheets were inspected. Encoding plus sheet review does not certify continuous Unreal playback.
- Ada source8 changes three clips only; its four unchanged clips use retained source7 motion evidence in refinement-v3. Her full-frame three-clip metrics are in action-trial/full-frame-motion-metrics.json.
- Rest skeletons and canonical gameplay timing were preserved. Liora and Sylas retain all seven original action curves; their animation revision remains6. Other changed clips are recorded individually in each refinement manifest.
- Each fresh published readback checks14 declared export files, the current source hash, skinning/LOD structure and seven-clip sampled floor/root/scale checks. The scoped helper diff check exited0.
- No final hero art approval, Unreal reimport certification, performance measurements, packaged human play or physical LAN proof is claimed by this report. Root owns those gates.

Open visual concerns for the next engine review:

- Existing faceted body construction, garment seams and restrained face detail still need close gallery and game-camera art judgment; these source revisions must not be called finished based on numeric checks.
- Elin sleeve-petal clearance needs continuous rear/turning review; compare the broad chord with the compact basic under crowd occlusion.
- Liora draw/hold/release, landing and bowstring contact need in-engine review at normal game zoom.
- Sylas currently uses a dominant-blade basic gesture; the dossier request for alternating cuts has not been independently proven. Check both blade arcs against the courier case and neighboring units.
- Review all regenerated LODs, atlas material response, portrait framing and current audio/VFX in Unreal.

Failures are retained in the evidence directories: Mira contact/garment iterations and interrupted export promotion logs; Elin/Sylas shoulder-clipping trials1-4. Corrected outputs have fresh readback evidence. Historical source revisions and existing exports were not erased.

Provenance limit: refinement scripts evolved between retained trials. Early trials do not all contain an immutable copy of the executed script; candidate/source/export hashes and actual render/readback evidence identify those results. The later script-snapshot addition does not retroactively supply earlier snapshots.
