# Dragonkin family preparation — not production acceptance

The full Sora, Varek, Iri and Oren dossiers and update briefs were read. The new uniquely owned `tools/blender/prepare_dragonkin_family.py` contains original candidate geometry, rig, motion and structural inspection functions. It writes no `.blend`, texture, portrait, animation export or Unreal asset. No Blender geometry/rig/motion function has been executed. Production remains queued behind the first four additions and the Halfling family.

The command-line entry supports only `--describe`. That pure-Python source-backed contract command and `py_compile` passed. The contract binds current canonical units/dossier hashes and the frozen shared Geometry, hand-contact, normalized exporter and measured FBX-profile hashes. Syntax and hash checks are not a Blender execution pass.

## Prepared decisions

- All four use the existing 27-name humanoid hierarchy and sockets, with explicit new Dragonkin shoulder/head/neck rest proportions. The root stays at the ground, all source coordinates are meters/+Y forward/+Z up, and no wing or tail bone is added. Bone-name matching is not declared retarget compatibility.
- The skull is an original continuous loft whose front sections form the muzzle, not a human head under scale-colored material. Each has a closed mouth seam, nostrils, shaped eyes/brows and short horns. Plantigrade boots, visible joints and restrained scales preserve the authored adult proportions.
- Sora: broad pale armor, rounded muzzle, swept-back horns and short crest, blue tabard, left oval gem shield and right short mace. Motion braces the shield upward and keeps the mace compact.
- Varek: narrow dark-blue coat, angular muzzle, blunt outward horn fins, forked hip-length cloak and flat quiver. The broad horizontal prism bow uses opaque dark/light facets and two-hand contact; the active aligns the bow before a single finite-travel shot.
- Iri: slim copper head/body, close horns and crest, charcoal jacket, coral diagonal sash, paired broad crescents. The active draws one blade inward before a deliberate release; no dash, teleport or immunity is implied.
- Oren: moss-gray rounded face and swept horn arch, white/teal split robes, short mantle and map case. An open hexagonal lantern staff is held separately from the lifted free palm. The active indicates directional shielding, not healing or revival.
- Seven per-frame candidate clips are defined for each hero. Release markers and clip lengths derive from current canonical windup/recovery; damage values are not duplicated. Bone scale/root motion stay fixed; hand reach is measured through the existing analytic solver. Every result still requires actual evaluation, contact correction, render inspection and continuous review.

## Exact next production sequence after release

1. Start only a fresh Sora candidate scene. Call `source_unit`, `build_rig`, `build_geometry`; use the existing measured atlas/mesh/export helpers through a bounded new driver with fresh evidence paths. The library itself never saves or exports.
2. Inspect original head/neck, armor and prop silhouette before animation approval. Execute `bake_actions` and `inspect_family`; perform all-authored-frame deformed floor/bounds/scale checks using the existing owned review workflow. Fix actual contact/clearance failures in fresh retained revisions.
3. Capture four actual views, 96px silhouette, gameplay-camera candidate, model-derived portrait, all seven normal-speed clips and LOD views. Numeric checks do not certify collision clearance or finished art.
4. Root imports the calibrated normalized centimeter exports. Measure Sora's expected208cm body height, +X forward, root scale1, seven clip behavior, actual lobby/gallery/board framing and neighbor clearance. Perform a reversible costume revision/reimport.
5. Only after the Sora family handoff is accepted produce Varek, Iri and Oren, with the same independent evidence obligations.

Known preparation limitation: no candidate scene has been created, so geometry topology, normals, weights, hand targets, floor contact, cloth/crest/horn/weapon clearances and all Blender API calls remain unverified. The helper is an implementation head start, not a modeled/imported/playable Dragonkin claim.
