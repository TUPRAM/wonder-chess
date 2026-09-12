# 1. Free sources: a small curated study set

**Verified at the listing/documentation level on 9 September 2026. Archive contents, actual topology, rig performance and compatibility were not inspected in Blender here.** Source IDs map to `SOURCE_REGISTRY.json`.

## Recommended acquisition order

| Priority | Source | What to study/use | Important restriction or uncertainty |
|---|---|---|---|
| 0 | Existing MPFB core full body (`mpfb_license`) | One coherent torso, arms, hands, legs and feet with preserved target correspondence | Already in the uploaded source scene. Do not download a second body merely to make progress look new. Core graphics CC0; code license is separate. |
| 1 | Hands01 (`mpfb_hands`) | `mindfront_hand_fingers_correction`, `mindfront_hand_thenar_eminence`, `mindfront_hand_hypothenar`, `jujube_knobby_knuckles` | CC0 targets, not detached hand models. Apply selectively; do not automatically maximize realistic knuckle detail on a stylized hero. |
| 1 | Gloves01 (`mpfb_gloves`) | `toigo_gloves_short` by MargaretToigo; `culturalibre_hero-heroine_gloves_1` | Listed CC0. Inspect one or two garments for thumb/cuff/knuckle construction, then adapt only if they suit Ada. |
| 1 | Shoes01 (`mpfb_shoes`) | `culturalibre_hero_boots_1`; `toigo_ankle_boots_female` or `_male` | Listed CC0. These names do not establish heel shape or suitability; select practical flat-footed construction after inspection. The pack is larger than a single model. |
| 2 | Blender Human Base Meshes v1.4.1 (`blender_bases`) | Compare anatomy, proportions and control surfaces against the MPFB body | Named bundle CC0, Blender 4.2 LTS+. Do not conflate it with other CC-BY demo files or assume every sculpt base is rigged. |
| 2 | Quaternius Universal Base Characters (`quaternius_bases`) | Stylized proportion, limb volume and animation-oriented topology reference | CC0 free subset in OBJ/FBX/glTF. Full collection, native .blend source and engine projects are associated with the Source tier. |
| 2 | Quaternius Modular Character Outfits — Fantasy (`quaternius_fantasy`) | Clothing segmentation, protected joints, costume silhouette and material boundaries | Same free-subset distinction. The full catalog's 12 outfits/62 parts are NOT guaranteed to all be free. Different base/rig means fitting is required. |
| 3 | DmytroKovkun's “Knight medieval no textures” (`knight_cc0`) | Armor shell boundaries, layering, attachment and articulation hypotheses | Creator lists CC0, Blender 2.7x, no rig or textures. Requires login to download; do not bypass it. Old file must open in isolation with automatic scripts disabled. |
| Optional | Leon Steiner's “Gambeson” (`gambeson`) | Padded-garment fullness, seam/ridge hierarchy and broad folds | Creator lists CC Attribution. Attribution and changed-work records are needed for direct reuse; not part of the initial training set. Do not promise the creator's full modifier/sewing history is present. |
| Later | Poly Haven / ambientCG (`polyhaven`, `ambientcg`) | Appropriate cloth, leather and metal surface inputs | CC0 downloadable assets. Source images, web text, service/API terms and access rate rules are separate considerations. |

## Why these sources, rather than random detached limbs

The MPFB body already offers coherent source correspondence. Independent hands/legs can differ in topology, scale, proportions, joint placement and rest pose. My recommended policy is to study their useful construction rather than graft them onto Ada by default.

Keep two visible levels of knowledge for each source:

- **Observed:** actual available meshes, UVs, groups, topology, material slots and imported pose behavior.
- **Inferred:** a plausible method for recreating that construction.

A flattened mesh does not tell us the creator's historical operation sequence. A screenshot of clothing does not prove sewing patterns or simulation settings. Label inference instead of inventing a tutorial history.

## Exact minimum acquisition pilot

Use at most one useful glove and one boot sample first. Optionally load one Quaternius free sample if it can be acquired without account/payment barriers. If unavailable, continue with original MPFB helper-derived parts; archive availability is not permission to bypass access restrictions.

1. Open the source page and follow the creator's download route. Record publisher, author, exact title and URL.
2. Save the actual license/README delivered with the archive, plus the source-page license statement and acquisition date.
3. Inspect archive paths, extension list, embedded executables/scripts, texture dependencies, size, and unexpected file contents. Never enable untrusted scripts merely to load a model.
4. Hash the acquired archive. Work in a project-local quarantine area, not a global asset installation.
5. Import only the selected candidate to an isolated Blender file. Preserve rest transforms and original data before conversion.
6. Render front/side/back, underside/openings where relevant, wireframe and one useful pose. Measure mesh/material/texture information rather than trusting the marketplace polygon label.
7. Record `PAGE_REVIEWED`, `ARCHIVE_INSPECTED`, `IMPORTED`, `POSE_TESTED`, `VISUALLY_ACCEPTED`, and `REPLAY_PROVEN` separately. Later states require actual evidence.

## License handling for the machine project

MPFB core graphics and MPFB code have different licenses. Do not treat CC0 mesh/target permissions as a license to relicense the add-on's GPL code. Verify obligations before distributing modified add-on code or a combined product. No blanket legal conclusion about your future architecture is provided here.

For the first training experiment, adopt a conservative project rule: original/commissioned assets with explicit relevant rights, or clearly documented CC0 assets whose origin and file-level terms have been reviewed. Put unclear, NC, ND, editorial-only, NoAI-marked or conflicting-license items outside the automated training corpus pending resolution. This is a pipeline policy, not an assertion that every training use under every jurisdiction has identical legal treatment.

CC-BY adaptations retain author/license/changes information. Recreation is not a way to erase a source's rights. Do not use extracted Auto Chess, Magic Chess or other proprietary character assets.

## Source access limitations

The official Blender demo listing was available through search and its official archive index; direct page retrieval failed in this session. MakeHuman pack mirror clicks were not downloadable through the browser tool. These are acquisition tasks for the local Codex workflow, not evidence that the packs are unavailable. No archive hash is invented in the registry.
