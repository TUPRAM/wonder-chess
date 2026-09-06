# Wonder Chess art handoff

The current art source and production exports are stable. They are original modeled and animated alpha candidates. Final hero art acceptance and packaged-game verification belong to the integration/visual checkpoints; this document does not label them finished or certify a playable release.

## Current artifacts

- Hero sources: `art-source/heroes/<canonical_id>/<canonical_id>.blend`.
- Hero packages: `exports/heroes/<canonical_id>/`: one main skeletal FBX, two LOD FBXs, seven individual animation FBXs, three 1024-pixel PNG maps, a 768-pixel model-rendered portrait and an export manifest.
- Arena source: `art-source/arena/WC_SevenLanternCourtyard.blend`.
- Arena exports: `exports/arena/`: thirteen original static modules, shared atlas and `courtyard_layout.json` containing 176 authored module instances.
- Projectile source: `art-source/effects/WC_ProjectileGlyphs.blend`.
- Projectile exports: `exports/effects/SM_WC_ArrowGlyph.fbx` and `SM_WC_BoltGlyph.fbx`; 64 and 76 triangles respectively. Revision 2 adds nondegenerate per-face UV islands after Unreal reported missing-UV tangent warnings. Dimensions and triangle counts are unchanged. Their actual source renders and correction log are under `reports/WC-340/`.
- Canonical authored data remains in `data/units.json` and the other kit data files. Each hero export manifest embeds its complete art brief and records the canonical units-file hash.

Every hero has 27 bones, one material slot, four-family authored proportions, in-place 60-FPS clips and explicit equipment/socket names. The seven clips are Idle, Move, Attack, Active, Hit, Defeat and Victory; windup/cast release timing comes from the authored canonical unit values. All twelve saved sources are now revision 6 because of the bounded animation refinement. Their geometry remains at the preceding revision shown below.

| Hero | Geometry revision | Main-mesh triangles |
|---|---:|---:|
| Ada Brightshield | 4 | 4,760 |
| Mira Dawnwell | 4 | 3,714 |
| Rowan Emberwick | 4 | 4,170 |
| Liora Leafstep | 5 | 3,136 |
| Elin Moonsong | 5 | 4,582 |
| Sylas Duskrun | 4 | 3,218 |
| Borin Stonebell | 4 | 3,306 |
| Tessa Brassbolt | 5 | 4,020 |
| Dagna Anvilheart | 4 | 3,696 |
| Rok Sunward | 4 | 3,090 |
| Zura Stormcall | 4 | 5,416 |
| Kesh Quickwind | 4 | 3,422 |

These modest meshes are below the brief's suggested 6k–15k LOD0 triangle budget. A low triangle count or intentional faceting alone does not fail visual quality. Acceptance depends on appealing, coherent forms, the authored distinguishing features, silhouette readability and actual deformation at the game camera.

## Executed checks

All twelve source structural inspections passed. The actual Blender deformation audit sampled 1,819 poses across the 84 clips, finding no errors under its stated sole-height, root-translation and unit-scale tolerances. These are sampled numerical invariants, not 1,819 independent gameplay tests or continuous visual approval.

`export-integrity.json` verifies twelve source-file hashes and all 168 required hero files against their manifests, plus the arena files. `rest-skeleton-parity.json` compares all twelve current source rest matrices, bone heads/tails and hierarchy against the preceding saved `.blend1` revisions: no differences. The three revision-5 changes preserve the skeleton; Liora's existing `weapon_l` bone now moves the bowstring midpoint during the draw.

Actual renders include twelve portraits, front/side/back views, all 84 key poses, 96-pixel previews, 36 LOD views, twelve black silhouettes, 45 additional support-hand action poses and crowded-board views at 1920×1080 and 1280×720. The per-render evidence records distinguish revisioned images. The board render predates the three focused revision-5 changes; individual portrait/clip/LOD/silhouette evidence covers those newer sources.

The revision-5 LOD, silhouette and support-motion render updates executed successfully and were reviewed after the three source changes. The assembled LOD grids retain the principal equipment silhouettes, and the sampled support poses show Liora's draw and Elin's chord gesture. Deep elbow creases and simplified hand contacts remain visible; these stills do not certify continuous combat animation.

The integration lane first captured 21 actual Unreal frames showing all twelve heroes across all seven clips at three time fractions. The historical inspection is `unreal-visual-review.md`, with original screenshot hashes in `unreal-visual-review-evidence.json` and images preserved in `unreal-art-review-candidate4/`. No gross skinning collapse, hundredfold shrink, sideways basis jump or detached weapon was visible. Weak Hit/Defeat silhouettes, restrained caster/ranger gestures and small/occluded facial and hand-contact details led to the bounded revision below. This was a pre-package still-frame review.

Revision 6 addresses the first two pose findings in source. All twelve Hit actions have a broader torso recoil. Defeat uses a sustained supported crouch with equipment lowered and turned across the lap; Zura uses a shallower crouch to keep her long coat clear of the floor. The six priest/mage/ranger heroes also have stronger Active/Victory gestures, with the authored attack/cast timing retained. Ada and Rowan were tried first, then the remaining roster was validated and inspected in actual Blender renders. A raised orb arm that obscured Rowan's face, unreachable transition grips and Zura's coat-floor intersections were rejected and corrected during those trials.

`animation-refinement-production.json` is the exact revision-6 import contract for this bounded change: `changed_animation_files` lists the 36 root-relative animation FBX paths, and `heroes[].changed_export_hashes` supplies their SHA-256 values. All 132 other required export files remain byte-identical, including every main mesh, LOD, texture, portrait and the 48 other animation files. In-memory mesh topology, vertex positions, weights, UVs and rest matrices were compared before and after each source update; all matched. All twelve current/preceding saved skeleton comparisons also passed.

The revised clips received 1,830 actual full-mesh evaluations, one at every exported 60-FPS frame. The minimum vertex height, including equipment and cloth, was +0.011878 m. Maximum Defeat ankle displacement from the authored planted position was 0.000005589 m. All revised clips passed the tighter whole-mesh floor criterion, and every hero also passed the existing seven-clip sole/root/scale audit. The current per-hero motion reports are under `animation-refinement/<canonical_id>/`; the older per-hero root reports remain historical evidence. Production updates omitted redundant beauty rendering; isolated Blender trial previews and the actual Unreal revision-6 captures are distinguished from one another.

The integration lane imported all 36 revised sequences and captured a fresh 21-frame Unreal review at 15:01–15:02 local time. All images were opened and inspected across all twelve heroes; `unreal-visual-review-revision6.md` records the results and individual hero observations. `unreal-visual-review-revision6-evidence.json` binds the durable images in `unreal-art-review-revision6/` to their hashes and verifies that all 36 source FBXs still match the import records. The terminal crouch now clearly reads as inactive, Hit recoil is stronger, caster/ranger celebrations separate better from their guard, and the directional-light warning is gone. No gross deformation, scale jump, missing model or detached equipment was visible. This passes the bounded sampled pose checkpoint; final crowded gameplay, exact skill cues and packaged presentation remain separate acceptance work. Subsequent packaged720p/1080p sampled reviews below cover eleven live definitions; they do not replace continuous timing acceptance. Source and export files are held stable for it.

The deliberate fixes include inset eyes, a shaped hair cap and woven braids; Elf proportions; coat and apron hems; source sRGB/file-texture consistency; planted-foot counter-rotation; reachable two-handed equipment poses; Rowan's bronze frame; Liora's lowered bow, visible string draw and crouched slide; Elin's supported harp strings and chord gesture; and Tessa's broad single forehead lens. Logs preserve the failed overextended arm and floor-contact attempts followed by corrected executions.

## Measured export convention

Use `tools/blender/profiles/fbx_skeletal_cm_v1.json` for current skeletal FBXs. Authoring sources remain in meters, +Y forward, +Z up. Temporary copies convert mesh positions, rest-bone translations and animation location curves to centimeter values with unit object scale. The measured Unreal legacy import uses scene/unit conversion enabled, force-front-X **disabled**, named yaw **90**, preserve-local-transform disabled and uniform scale one.

The separate Ada trial passed all seven clips and 210 actual Unreal pose evaluations: reference/sample root scale and translation deltas zero, maximum root rotation error approximately 0.000003416 degrees, mesh height 181.09 cm, toes/cast direction +X. The actual evidence is `import-probe/all7_cm-results.json` and `all7-comparison.json`. Existing Unreal import-data/reference settings also require the integration lane's reimport/cold-load checks; fresh-folder success alone was not sufficient.

Static arena modules retain their separate measured static import convention. Do not apply the new skeletal yaw/force-front settings indiscriminately to the older arena exports. Projectile glyphs use normalized centimeter values and the new convention. Their first actual Unreal import measured +X forward, 76/62 cm lengths and 64/76 triangles correctly, but generated tangent warnings from absent UVs. Revision 2 checks all 140 UV triangles as nondegenerate in Blender; corrected engine reimport and runtime appearance remain integration checks. The pre-correction manifest is retained in `reports/WC-340/projectile-manifest-before-uv-fix.json`.

The integration lane subsequently completed the glyph revision-2 reimport at 14:39:05 local time: commandlet exit 0, import summary 0 errors and 0 warnings, with both meshes still passing their six dimension/direction/count/material checks. Current evidence is `reports/WC-340/effect-import-uv2.json` and `effect-import-uv2-console.log`. Rendered flight and packaged use remain separate checks.

For a future hero revision, run `author_alpha.py` in Blender with an explicit canonical alpha ID. Its skeletal export path now uses normalized copies automatically. For export-only regeneration from saved sources, run `reexport_normalized_roster.py`. Do not overwrite these assets with the superseded meter-valued skeletal FBX candidate preset.

## Remaining acceptance work

The integration lane owns current Unreal assets, cold-load tests, runtime effects/audio, the executable and 1H7B/2H6B/0H8B evidence. No human match, network result, frame-time result or packaged executable is certified by this art handoff.

The art lane subsequently inspected eight actual candidate-6 packaged network combat screenshots at 1280×720. `packaged-candidate6-network720-review.md` and its evidence JSON record that normal battle framing now keeps back/front ranks clear of the header/shop, including twelve-unit combat, and eleven distinct hero definitions have readable sampled crowded appearances. Zura was not observed as a living board character in those selected images; a shop portrait is not counted as crowd evidence. The readiness matrix records this partial 720p gate. The eliminated-host round-12 capture preserved a real P2: its spectator notice covered lower board rows and part of a living unit. That historical defect was subsequently fixed and visually rechecked in both Shipping720p and normal-speed Shipping1080p, as documented below. These accelerated five-times-speed screenshots did not establish normal timing; Zura's crowded presentation and continuous skill/animation acceptance remain required.

Outstanding visual risks include sharp sleeve/elbow creases at deep bends; intentionally simple and similar facial topology; thin strings/hair/eyes disappearing at lower LODs; complete dossier microdetail and gesture fidelity; and the final combination of hero, selection ring, effects and HUD at the real crowded gameplay camera. The source renders improve reviewability but cannot close those engine-side checks. No subjective quality score or finished-hero acceptance has been invented.

The spectator-panel P2 was subsequently visually corrected in four actual post-elimination Shipping images: `shipping-spectator-fix-review.md` and its SHA-bound evidence show the notice confined to the shop area and the correct scouted-bot header. The run intended as a network check actually ran solo and was stopped at round14, so only this visual correction is credited. Zura's live crowded appearance, current1080p and normal-speed complete skill presentation remain pending.

The later routed Shipping run adds21 reviewed active-recovery stills at720p/5x, linked with positive-HP/state6 records for eleven definitions in `shipping-routed-skills720-review.md` and its evidence JSON. Shield/stun cues, thin travel effects and faint area edges are visibly present, but not every recovery frame displays its target release burst. Zura has no recovery image/record in that set. The match-qualified sessions report modes2/3 and completion at round23; network acceptance remains the integration lane's responsibility. The next normal1x1080 run is reviewed separately.

No external character models, texture packs, animation clips, paid services or downloaded media were used. No VEILMARK files were read or reused.

Normal-speed Shipping1080p follow-up: `shipping-normal1080-review.md` and its evidence JSON archive sixteen reviewed actual images, including eleven positive-HP active-recovery definitions and twelve-character battles at rounds9/11. The fixed elimination notice/header is clear at1080p. The archived round13 session was still in progress; this is a bounded still review, not complete-match, continuous timing, manual play or audio acceptance. Zura remains missing from living on-board captures in this set. Production art is unchanged.
