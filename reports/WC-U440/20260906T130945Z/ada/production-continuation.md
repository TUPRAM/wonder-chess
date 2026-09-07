# Wonder Chess asset production continuation

This is an execution handoff based on the actual source/export inventory captured in `remaining-roster-source-inventory.json`, not an asset-completion claim. Root imported Ada revision7 for the current Unreal/package checkpoint. Ada source/animation revision8 is now separately published and verified for the next import; its geometry remains revision7. See `action-trial/published-verification.json` and the retained publication failure/correction logs.

## Verified starting inventory

At the inventory snapshot all twelve existing heroes had a source `.blend`, an export manifest whose source SHA-256 matched that file, three skeletal mesh exports and seven named clip records. Ada was source revision7; its subsequent revision8 is recorded above. The other eleven were source revision6. Their existing face, costume, equipment, skinning, rig, texture and animation work must be preserved. At that snapshot the four additional existing-family heroes and the eight Halfling/Dragonkin heroes had no production `.blend` files or export manifests. The canonical 24-hero selection is not evidence of those missing assets.

Ada revision 7 retains the original 27-bone rest skeleton and all seven action curves. Its actual LOD0/1/2 triangle counts are 4,760 / 2,379 / 1,189. Structural and 20 Hz motion checks passed. The 143 rendered samples were encoded and decoded into seven normal-speed 20 FPS review GIFs, with durations matching the 60 FPS source timelines. This is source evidence; Unreal reimport, package framing, actual normal-speed gameplay/audio review and final art acceptance remain separate.

## Finish the reference checkpoint

1. Root imports Ada revision 7 and completes the early package/gallery framing check, retaining the published source hash `a8e0612c8926c0e9f68992ba9f45b9c59f6b724a93451c7aa1106ad1ed6eab02` and manifest hash `41aad307619ab33861bf279b201803be68675167245ffeb6921322bb9991a4fb`.
2. Completed source checkpoint: `action-trial/ada-action-revision8-trial.blend` gives a larger timed sword sweep, a supported Hit pose below the eyes, and a modest shield-led Victory salute. Geometry/rest bones and the other four clips are preserved. Reach, width, eye clearance, foot contact and canonical durations were checked; all three review sequences were rendered at normal speed. Published source SHA `70f97a1d00555cbee1c8bb42b7e6797936e02d1e6167ec16163e94744aeaa2a6`, manifest SHA `b78fdaf00231280b7dd1ed0ac087f70c2519830eea74b0b7821a59737e7f5d41`. Root must import the three changed Attack/Hit/Victory FBXs after its revision7 package checkpoint. No claim of current Unreal revision8 playback follows from source verification.
3. Inspect Ada in the actual lobby/gallery, front row and opposite-side orientation at 720p and 1080p. Review animation continuously at normal speed, including silhouette, shield neighbors and release/audio timing. A failed reference observation determines the corresponding focused fix; it does not justify rebuilding every existing hero.

## Existing eleven: edit saved sources in controlled batches

Every row starts by opening the current source in a separate background Blender process, reading the actual objects/actions and checking the matching manifest hash. Preserve BODY/COSTUME/EQUIPMENT source collections, all unchanged mesh islands, UVs and material references. Use an isolated candidate `.blend`, before/after renders and source signatures. Never invoke `author_alpha.py` to regenerate these heroes from scratch.

| Order | Existing source | First focused inspection/edit from the adopted brief |
|---|---|---|
| 1 | Mira / `wc_u_human_priest` | Face and staff-hand contact; visible directed triage cast, supported upper-body reach and modest recovery; staff must stay clear of neighbors. |
| 2 | Rowan / `wc_u_human_mage` | Face/hair and focus clearance; make gathering, release and recovery distinct within existing timing; retain original coat and Ember Burst identity. |
| 3 | Liora / `wc_u_elf_ranger` | Bow grip/draw-string alignment throughout Attack; boot/hem clearance in retreat; keep the slender body and low foliage silhouette. |
| 4 | Elin / `wc_u_elf_priest` | Two-hand instrument contact, pluck motion and legible song release; inspect forearms and mantle throughout animation rather than only the still portrait. |
| 5 | Sylas / `wc_u_elf_rogue` | Knife grips, cloth panel clearance and readable leap anticipation/landing; preserve the dash-only skill and distinct backline silhouette. |
| 6 | Borin / `wc_u_dwarf_guardian` | Beard/helmet/hand clearance, shield or bell-gear support and planted stomp; protect the measured stocky family proportions. |
| 7 | Tessa / `wc_u_dwarf_ranger` | Support-hand firearm contact, charged-shot brace and shoulder recoil; distinguish the physical active from ordinary fire. |
| 8 | Dagna / `wc_u_dwarf_warrior` | Hammer support grip, sweep reach and clothing clearance; keep the short broad body and make basic/active poses distinct. |
| 9 | Rok / `wc_u_orc_warrior` | Broad anatomy and weapon contact; tempo-window arm marks/pose changes; retain the prior screen-margin concern as a camera regression. |
| 10 | Zura / `wc_u_orc_mage` | Staff/focus and hands, shoulder range, charged storm anticipation and restrained recovery; verify the comparatively large costume and effects remain readable. |
| 11 | Kesh / `wc_u_orc_rogue` | Grips, shoulder/strap clearance and short chase landing; preserve the broad-family identity and distinguish the current-target dash from Sylas. |

Each row's complete source of direction remains `HERO_UPGRADE_BRIEFS.md` and its generated dossier; this table identifies the first inspection target, not an abbreviated replacement brief. Re-export only a complete verified set: source, mesh, two regenerated LODs after geometry changes, the exact seven actions, existing or intentionally revised textures and model-derived portrait. Root serializes Unreal import and package snapshots. Work may overlap only on disjoint hero directories after the reference family and shared material contract are stable.

## Four additions using established families

Create Cass, Neris, Orla and Tala in that order using the already verified standard, slender, stocky and broad family contracts. The existing family rest skeleton may be reused after compatibility checks; the character mesh, clothing, face, equipment and pose work must follow each complete dossier. Do not duplicate an existing finished body and call a recolor a new hero. Preserve one cell and authored height. Verify Neris's damage-then-stun release with the new runtime; Orla's pulse and Tala's group shield need clearly distinct poses and actual recipient feedback.

The existing generic author helper has only the original race branches and palette overrides. Its successful execution alone would not establish correct new hero appearances. A separate additions authoring script needs explicit per-hero garment/weapon/facial construction and materials, with one owner of any shared family definition. Runtime gameplay remains in canonical data/C++.

## Halfling and Dragonkin pilots, then their batches

Pippa is the first Halfling source. Author adult small-body proportions, feet, hand size and equipment reach explicitly; a uniform reduction of a human source is insufficient. Verify feet/scale beside Ada and a Dwarf, then Idle/Move/Attack/Active/Hit/Defeat/Victory and gallery framing. Only after the pilot works proceed with Finn, Nella and Milo, including their distinct weapons/focus and supported skill poses.

Sora is the Dragonkin pilot. Author head/muzzle, horn/crest, neck, armor and grip clearance on the declared draconic family. Verify the same seven clips before Varek, Iri and Oren. No unrequested wings, tails, flight or transformation. Face and crest geometry cannot be a human face covered by glow. The proposed `humanoid_small` and `humanoid_draconic` tags are design identifiers; the current source inventory contains no validated family assets for them yet.

## Evidence required before roster acceptance

Maintain 24 separate asset records and all 168 hero/clip review cells. Record actual source/export/import hashes, tool versions, rig rest signatures, preserved and changed action IDs, clip durations, weight/UV/material checks, LOD triangle counts and actual views. Rendered source sequences, static sheets, normal-speed Unreal review, packaged behavior, audio listening and measured performance are distinct evidence. Finish each defect against the current build; preserve older passes and failures under their original hashes.

Seven original neutral assets remain an additional production obligation under `MONSTER_WAVES.md`; they do not count toward the 24 heroes or 168 hero/clip cells. Allocate each neutral source separately and import through the same measured scale/material pipeline after its mechanical or creature rig has been exercised.
