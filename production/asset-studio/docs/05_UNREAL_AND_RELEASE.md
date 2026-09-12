# Phases 8–10 — Optimization, Unreal integration and release

## 1. Compatibility first

Record actual Blender, exporter/add-on, Unreal, importer path and shader configuration. Do not automatically upgrade either editor for this task. A documentation page using a later version is reference, not authorization to migrate the project.

Use the measured Wonder Chess scale/axis profile where current. Otherwise calibrate a measured tile/cube, forward/up markers and a tiny rig/clip. Source meters and engine centimeters require a deliberate conversion; scale must not be applied twice through geometry, skeleton, object transforms and importer settings.

The Epic FBX documentation describes a 2020.2 pipeline and compatibility caveats [E1]. This does not mean Blender exposes a “2020.2” dropdown or that every exporter version is equivalent. Test the actual pair. Record legacy/Interchange route and relevant options; do not silently alternate importers.

## 2. Export set

Export deliberate runtime mesh parts, explicit skeleton/root/helpers, required morphs and named clips. Exclude references, authoring controls, cages, high-poly source, cameras, lights and alternate candidates. Preserve material-slot order and the documented socket contract.

Evaluate modifiers on controlled export copies. Do not apply the armature in a random animation frame or bake the pose as rest by accident. Keep normals/triangulation/tangent decisions consistent with the normal bake. Hash source, mesh, UVs, rig, maps, export preset and output files.

## 3. Materials and importer

Create/reuse controlled master materials and instances instead of accepting arbitrary material graphs from FBX. Verify BaseColor, normal orientation, ORM masks, emissive intensity, alpha mode and compression/color-space settings. Epic distinguishes computing normals, importing normals, and importing normals with tangents [E2]; select and test one route deliberately.

Do not enable “update reference pose” or “use first frame as rest” as a generic repair for a mismatched skeleton. Such changes can affect other assets sharing that skeleton. Import into an isolated candidate folder first, with explicit references to the intended skeleton. Keep current gameplay assets untouched until promotion.

Unreal Python is editor automation, not shipping runtime scripting [E3]. The pipeline may use it for imports/inspection, but gameplay stays in the existing runtime implementation.

## 4. Collision and bounds

A logical one-cell board footprint is not the mesh's bounding box or ragdoll. Preserve gameplay occupancy separately. Selection/hit-testing collision must be useful and predictable. Create simple collision appropriate to the asset, not a highly detailed collider for every armor plate.

Inspect skeletal bounds across all animations so shields, swords and VFX do not disappear through culling. Oversized bounds also cost visibility/performance. Static props need the correct pivot and collision purpose. Physics assets are deliberate, not a requirement to use default spheres on every hero.

## 5. LOD and representation

Start with a correct model, then create reduced representations. Preserve face silhouette, hands, emblem readability and weapon tips where they remain visible. Decimation ratios are candidate starting settings, not an approval rule. Inspect actual screen-size transitions and animated deformations at each LOD. Keep attachments and material layout consistent where required.

The supplied budget file uses the old 15K triangle envelope as a starting hero target and allows a separately approved 25K comparison. No minimum triangle count. Source sculpt density is not shipping density. Review texture residency, material sections, skinning, shadows, transparent overdraw and particle cost, not triangles alone.

Use additional representations for tiny portraits or menu closeups only when justified. Do not ship a high-detail gallery mesh everywhere merely because it looks good in one screenshot. Mobile needs a measured physical-device validation later; desktop success is not proof of mobile viability.

## 6. Gameplay-camera acceptance

Build or use a fixed asset-review map and then the real arena. Test a full encounter at the actual maximum visible hero count, skills, bars, selection rings and camera zoom. Include duplicate same-hero teams, mirror matchups and crowded positions. Determine whether distinguishing features survive colorblind-friendly/team-color alternatives and grayscale inspection.

Test both friendly and enemy orientation. A shield that frames a face in a gallery can hide an ally at gameplay elevation. Do not change combat geometry to accommodate decorative equipment clipping unless a gameplay change is explicitly approved.

## 7. Performance report

Record device, build, resolution, graphics preset, map, visible actors/effects, camera path, warmup and capture method. Inspect CPU/GPU frame times, spikes, memory/residency and relevant draw/overdraw costs. Separate initial shader/streaming behavior from warmed steady-state while reporting both. Target 1080p/60 on a named PC only as a goal until measured.

No invented frame rates, Lighthouse-style art scores or implied eight-human networking proof from an asset test. Network game logic remains unchanged; the art update must not create new authoritative dependencies on animation ticks or camera visibility.

## 8. Reimport and package test

Make a small deliberate source revision, export and reimport. Verify actor references, skeleton assignment, material instances, portrait references, socket transforms, clip binding and bounds. Check content cooking so reference images/high-poly source and private prompts do not become accidental shipping payloads.

Launch an actual packaged build and inspect the accepted asset. Editor-only success is not release acceptance. Save logs and captures tied to the same exported hashes. If Blender or Unreal is unavailable, this gate is blocked rather than satisfied by generated scripts.

## 9. Release bundle

Include asset manifest, approved concept/construction references where permitted, editable source, authoring rig/metarig, runtime mesh, textures and texture-source recipe, clips, exports, presets, reports, licenses/provenance and known issues. Preserve versioned dependencies and rollback destination. Do not redistribute unrelated fonts, licensed source packs or competitor assets.

Release signoff is Pram's approval of the exact candidate hash and intended use. Promotion to canonical paths is a separate reviewed filesystem/integration change with backup. The included ledger does not perform destructive promotion.
