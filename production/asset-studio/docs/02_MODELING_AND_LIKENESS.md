# Phase 2 — Modeling, construction and early likeness

## 1. Pick a modeling route deliberately

**Direct subdivision/mesh modeling:** appropriate when surfaces are controllable with a clean cage, especially armor, weapons, props and simple stylized organic parts. Primitive blockout is the start, not the required final vocabulary.

**Sculpt plus retopology:** appropriate when organic primary/secondary forms are easier to establish in a dense continuous surface. Retain a clean low-frequency shape; adding pores does not repair a wrong jaw.

**Approved base mesh:** appropriate for humanoid anatomy when provenance, topology and style actually fit the target. Adapt proportions before binding production animation. An unsuitable realistic or cartoon base is not automatically a shortcut.

**Image-to-3D candidate:** optional only through available approved tools/services. Use consistent single-object views. Treat result as raw source needing likeness, hidden-surface, topology, UV and deformation checks. Do not feed a collage containing hands, swords and whole bodies to an object generator and assume the result will separate cleanly.

**Hybrid:** recommended per part, not an excuse for unmatched styles. Example: one stylized anatomy foundation, sculpted head, mesh-modeled plates, curve-based straps/braid and baked textile relief.

## 2. Part planning and non-destructive assembly

Keep source collections for references, blockout, organic forms, costume, rigid equipment, rig, high-detail source, export mesh and review helpers. Use stable `wc_part_id` custom properties and named parts. Preserve meaningful objects rather than fusing everything early. Final game exports can combine approved components; source editability is a different concern from draw-call count.

Do not use a component's vertex count, UV swatch or order in an object list as its identity. Keep high-poly and runtime collections separate. Never leave a source-only object accidentally visible in export or review.

## 3. Blockout

Establish head/ribcage/pelvis/limb proportions, negative spaces, center of mass and major costume volumes. Compare front, profile, three-quarter and actual gameplay elevation. Check hands, feet and hidden side behind the shield. Match camera and pose before correcting the shape.

Use primitives freely at this point. A successful blockout is one that makes proportion decisions easy to see; it is not judged for pores, eyelashes or rivets. Reject large proportion errors before refinement. Candidate budget and time belong in the operation log.

## 4. Symmetry

Use Mirror on anatomically symmetric source meshes with an explicit mirror object/plane. Merge and clipping tolerances are relative to asset scale. Blender mirrors local axes around an origin or chosen mirror object; changing object transforms affects that construction [B1].

Do not mirror unique equipment, hair part, scars, costume closures or asymmetrical stance into existence. Keep asymmetrical parts separate. Inspect center seams and normals. Mirroring UVs later is another choice; unique crests and asymmetrical texture marks must not be accidentally reversed.

## 5. Fusion and Boolean use

Join Objects does not weld surfaces. Boolean union or voxel remesh can create a useful continuous organic sculpt source, but does not automatically create deformation topology. Keep backups before remeshing; topology-dependent UVs, shape keys, skinning and other data need explicit preservation/transfer or rebuilding. Blender's remesh documentation also notes interaction limits with modifiers and Multiresolution [B2].

Fuse skin volumes only where continuity is intended. Armor above a sleeve, hair locks, belt straps and shield components usually need their construction boundaries preserved. Open garment borders can be intentional. “Everything is one watertight solid” is not a universal game-asset rule.

## 6. Organic refinement

Work from large masses to medium planes to selected small details. Define forehead/brow/eye sockets/cheeks/muzzle or nose/jaw/chin/neck as related forms. Eyes sit within eyelids; a bright eyeball attached to a head is not eye anatomy. Mouth closure and corners need a coherent surface, not a floating black opening unless it is the intended expression.

For hands, construct palm volume, finger bases, knuckle progression and opposing thumb. Review neutral and grip states. Repeated rings around a handle are a diagnostic blockout, not accepted fingers. Large feet need a defined sole, toe break and heel/contact plane.

Use Grab/Elastic/Draw/Clay/Smooth/Crease or equivalent operations for specific shape changes. Select brush scale and symmetry consciously; endlessly smoothing removes useful planes. Subdivision adds editable density, not artistic judgement.

## 7. Hard-surface refinement

Build armor as shells with controlled thickness, edge transitions, plausible overlap and attachment. Avoid inflated domes for every pauldron. The breastplate should have deliberate planes/openings and an intentional lower contour; do not sculpt anatomy as armor without a design reason.

A sword requires blade section, ridge or planar transitions, taper, edge, guard, grip and pommel. A shield requires front convexity, rim section, backing, grip and arm clearance. A sun disk should follow the approved relief—not become a ball because a sphere is easy to generate.

Use bevels where they improve highlight or silhouette at the intended distance. Bevel width is a world-size decision; extremely small bevels may be invisible, oversized bevels may melt the design. Preserve intended hard boundaries with explicit shading rules, not material-color indices.

## 8. Costume and hair

Define garment order and thickness: skin -> underlayer -> belt/armor -> draped layers. Folds emerge from tension, compression and gravity at specific anchors. Broad folds and layer separation matter more than uniformly distributed noise. Keep hem lengths and openings consistent across views. Articulation needs clearance, not magical intersection.

Model hair as purposeful clumps or cards appropriate to the target. For the initial stylized heroes, mesh clumps and a restrained braid are simpler than grooming simulation. Braid strands need an organized flow and collisions with collar/shoulders. Fine fibers are optional and should not hide a weak large shape.

## 9. Likeness gate BEFORE retopology, texturing and final rig

Submit gray clay front/side/three-quarter, reference-context comparison, full silhouette and critical closeups. For Ada, first submit head/torso/one shoulder rather than a complete repeated failure. The gate evaluates shape and identity, not render decoration.

Review categories independently: likeness, proportions, construction, negative spaces and readability. Do not average them with export success. A major face failure blocks even when the shield is excellent. No global score such as “95% match” without a defined valid measurement.

After two unsuccessful bounded iterations, change route or seek a focused human shape pass. Preserve the best checkpoint. Do not generate twelve characters until one reference asset demonstrates that the method can achieve the quality target.

## 10. Matched comparison rules

Render with fixed camera, orthographic scale/focal length, pose, lighting and exposure. Include clay, simple material IDs and beauty as separate views. Do not hide defects with bloom, depth of field, a different crop or black shadows. Full body includes feet, hair tips and weapons.

Silhouette/landmark aids require aligned same-pose views. The supplied image helper does not auto-register, warp or calculate aesthetic quality. Pixel overlap is diagnostic only. A portrait cannot prove back-side construction, and a correct static pose cannot prove motion.
