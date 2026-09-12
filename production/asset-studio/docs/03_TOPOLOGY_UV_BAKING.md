# Phases 3–4 — Retopology, UVs and reliable surface transfer

## 1. Topology exists to serve shape and motion

Not every model needs a separate retopology stage of manual rebuilding. A deliberately modeled clean source may already be suitable. A sculpt or generated mesh usually needs inspection and possibly substantial reconstruction. The deliverable is tested game geometry, not a claim that a specific button was used.

Quads are useful for editable surface flow and deformation, not a universal runtime requirement. The engine ultimately uses triangles [E1]. A rigid plate may use controlled triangles and planar n-gons during authoring. Avoid uncontrolled n-gons in deforming or curved areas. Freeze deterministic triangulation for baking/export and test the same triangulation in Unreal.

## 2. Retopology setup

Keep approved forms unmodified as a reference. Create a separate runtime cage. Configure face snapping, projection and/or Shrinkwrap against the intended surface; exact UI labels differ by installed version. Avoid projecting an elbow onto the opposite side of an arm or through thin armor. Offset to prevent z-fighting during work, then inspect actual gaps.

Use Poly Build, extrusion, approved retopo tools or careful mesh editing to create flow around eyes, mouth and major joints. Loops follow the intended deformation, not a memorized universal diagram. Preserve rounded fingers, mouth corners and garment borders. Place poles away from the most stressed hinge/crease where practical.

## 3. Tests before UV approval

Inspect loose vertices/edges, duplicate faces, zero-area faces, degenerate triangles, normals, self-intersections and unintended non-manifold edges. The bundled observation script covers only a subset and states its limitations; it is not an exhaustive geometric certificate.

Declare allowable boundaries for open sleeves, skirts, hair cards or mesh parts. Do not close them merely to satisfy a generic watertightness check. Internal geometry should be removed only when it cannot be exposed by animation, customization or camera. Do not leave an amputated hidden torso that becomes visible during a shield animation.

Use an early proxy rig or representative deformation test before committing final topology. Bend elbow/knee, raise the arm and test torso rotation. Correct loops and volume now rather than painting around a geometric deficiency later. For hard-surface props, test assembly movement, silhouette and pivot behavior instead.

## 4. UV planning

Choose texture sets by runtime use, material sections and sharing. Source material slots can be more numerous than the packed runtime sections, but the final material strategy must be explicit. Prefer one 0–1 set or a controlled atlas for the initial heroes; UDIM/virtual-texture workflows require a concrete engine and platform justification.

Place seams where they are less visible and align with construction where useful: inner limbs, garment seams, armor breaks, behind the hair. Do not place every seam purely for packing efficiency. A hard-normal edge generally needs careful UV/tangent treatment; review the actual bake rather than treating every UV seam as a required hard edge.

Measure texel density by surface region. Allocate extra resolution to face/emblem/hands only when the actual camera uses it. Do not pack a face into a tiny island and expect a larger atlas to solve the problem. Intentional mirrored/stacked UVs must be declared. Unique emblems, asymmetric damage and independently baked normal surfaces need isolated space as appropriate.

## 5. Padding and mipmaps

Inspect the checker pattern for stretching and scale jumps. Plan island padding and texture dilation for the smallest reviewed mip, not just the full-resolution map. For example, an 8-pixel gutter at 2K becomes roughly 1 pixel after three halvings; this is an illustration of mip erosion, not a universal safe value. Test the actual mips and filtering in Unreal.

A high UV occupancy percentage is not a quality guarantee. More packing can increase bleeding, prevent useful gradients or complicate shared materials. Document density exceptions rather than allowing accidental variation.

## 6. Baking recipe

Keep high-detail source, low mesh and cage separated and versioned. Choose selected-to-active or the equivalent approved baker with matching names/groups. Use an exploded bake or component isolation when neighboring parts contaminate projection. Tune cage/ray distance to the mesh; arbitrary world-size defaults can miss or hit the wrong surface.

Bake tangent-space normals for animated assets where that matches the runtime pipeline. Blender documents tangent-space baking and selected-to-active surface transfer [B3]. Record mesh hash, triangle ordering, UV hash, smoothing/tangents, cage, ray distance, image settings and tool version. A topology/triangulation/UV change invalidates the normal bake.

Inspect errors at armpits, thin rims, finger gaps, shield backing and armor seams. Test at the native texture and lower mips. Blank neutral normal maps may be valid on a deliberately simple surface, but must not be labeled a completed high-to-low bake.

## 7. Normal and color contract

Record source tangent basis, normal-channel orientation and any conversion. Do not globally flip a channel on every asset by habit. Verify a known convex/concave calibration shape under light in both Blender and Unreal. Apply the chosen +Y/-Y normal conversion exactly once. Engine import options distinguish imported normals/tangents from computed ones [E2].

BaseColor is color data with the intended sRGB interpretation; normal/roughness/metallic/AO/masks are linear data. Define ORM explicitly as R=occlusion, G=roughness, B=metallic when using that packing. Do not let a node name stand in for tested channel routing. Save an unlit base-color view and lit material views.

## 8. Texturing and stylized look

Develop color/material IDs first, then broad gradients, controlled roughness variation, useful seams, selected wear and restrained microdetail. Steel, ivory fabric, skin, hair, leather and gold must read as distinct surfaces. Avoid uniformly shiny plastic and avoid multiplying painted shadows by heavy AO until folds become black.

The desired painterly 3D appearance is not literal projection of the concept's lighting. Use controlled hand-painted color/value decisions, appropriate material response and lighting. Evaluate under neutral light plus at least one materially different game light. The asset should remain identifiable rather than depend on a single portrait setup.

Blender painting is sufficient for the core workflow. A specialized texturing app is optional, not a requirement hidden inside the pipeline. Record its version, export preset, license and source files if used.

## 9. UV/material gate

Require runtime cage, explicit triangulation, checker review, declared overlaps, density/padding policy, named bake recipe, actual maps, color-space/channel verification and native/mip review images. Likeness must remain intact. Do not accept a 4K palette swatch atlas as evidence of authored cloth and armor surfaces.
