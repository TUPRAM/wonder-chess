# 01 — Targeted repository and visual findings

## Evidence boundary

Repository snapshot: `9623fd82f98ff80a90985b9f552d8851ccece30f` (main at inspection). This is a targeted review of the character-generation, Ada refinement, source data, export manifest, and Blender skill—not a full game-code audit. The supplied local screenshot cannot be proven to match the committed `.blend` revision.

The screenshots show a sword/shield character in a gray solid viewport. That view reveals form and faceting, but it does **not** establish that the asset lacks materials. Likewise, the Auto Chess gallery demonstrates a visual target; it does not reveal the underlying topology, budgets, texture sizes, or production methods.

Source identifiers below resolve in `SOURCE_INDEX.json`.

## Finding 1 — This is not merely a tiny polygon budget

**Observed [R2]:** Ada's export manifest reports source revision 9, 9,068 triangles, 27 bones, one material, and Blender 5.1.1. Its status still says Unreal reimport and visual acceptance are pending.

**Inference:** Her coarse appearance cannot reasonably be diagnosed as 'MCP can only generate a few polygons.' The allocation and design of those polygons matter. Count is not a measure of character appeal.

**Action:** Capture the actual current mesh statistics and normalized clay/material views before changing budgets. First improve silhouette, shaped surfaces, and shading. Consider an explicit higher-budget candidate only where a visible comparison justifies it.

## Finding 2 — The base generator has a limited shape vocabulary

**Observed [R1, code lines 44–107, 326–400 approximately]:** Bodies are assembled through ellipse-based lofts, tubes, ellipsoids, and extruded polygon plates. Armored shoulders use eight-sided lofts. Ada's sword and shield originate as extruded planar outlines.

**Inference:** This makes technically valid, repeatable construction relatively easy, but offers limited anatomical, tailored, or forged surface design unless an artist/agent reshapes the results. Broad facets on shoulders and bracers are consistent with the supplied screenshot.

**Action:** Retain these functions for blockouts and repeatable props. Add a genuine surface-design phase with shaped armor caps, a curved shield face, a tapered blade cross-section, and deliberate head/hand construction. Do not simply multiply every segment count.

## Finding 3 — Smoothing is coupled to palette index

**Observed [R1, make_mesh, approximately lines 435–452]:** `poly.use_smooth = col in (6,7,8,9,14)`. Smoothing therefore depends on the color category rather than a surface's intended continuity. Much armor and cloth remains flat-shaded in the foundational generator.

**Inference:** Some 'low resolution' appearance is a shading-design problem, separate from silhouette resolution.

**Action:** Use semantic part/surface definitions for smooth regions and intentional sharp edges. Check actual evaluated/exported results. Smooth shading alone does not change a coarse outline, supply missing anatomy, or give a flat shield curvature.

## Finding 4 — Texture dimensions overstate surface information

**Observed [R1, material_for and make_mesh]:** The default 1024-square texture is a 4-by-4 palette atlas with mild tonal variation. The normal image is filled with `(0.5, 0.5, 1)` rather than baked sculpted information. ORM contains simplified per-swatch values. Faces are routed into color swatches, not a detailed character-specific paint layout.

**Inference:** Raising this texture to 2048 or 4096 without changing its content mostly produces larger swatches. A flat normal map is not a hidden source of edge, seam, or anatomy detail.

**Action:** Keep palette reuse where appropriate, but author targeted UV coverage and actual surface information for the face, armor, coat, shield, and sword. A detailed material is not mandatory everywhere; intentional visual separation is.

## Finding 5 — The latest polish is real, but its constraints preserve the largest problems

**Observed [R3]:** `polish_ada_gallery.py` performs fitted facial details and fused grip work, preserves animation invariants, saves candidates, and uses voxel remeshing. It is not correct to say no refinement has occurred.

However, it deliberately preserves the original head shell, ears/braid, coat, tabard, armor, shield, sword, rest skeleton, and animation curves. It locates the original head shell through a 112-vertex component condition. The hand pass has a target of roughly 2,000 triangles per hand after remeshing/decimation; that is a script target, not an independently measured final count.

**Inference:** Local improvements cannot fully solve a weak primary design when that design is explicitly outside the allowed edit scope. Increasing eyelid/grip complexity while preserving coarse shoulder and shield shapes risks disproportionate effort.

**Action:** Keep the useful candidate/snapshot approach. Relax shape-preservation constraints for an isolated art candidate. Preserve gameplay interfaces, not an unattractive surface shell. Review proportions and large forms before adding detail.

## Finding 6 — Fragile selectors make major art edits risky

**Observed [R3]:** Refinement selection uses component counts, exact group assumptions, and palette-derived identities. New retopology may invalidate them even when the character is otherwise correct.

**Action:** In the candidate pipeline, identify parts through stable semantic objects/attributes such as `head_surface`, `shield_shell`, `armor_pauldron_l`, and `hand_grip_r`. Do not rerun old count-based surgery after changing topology. Retire it for the candidate or fail explicitly on an unsupported revision.

## Finding 7 — Good technical practices already exist

**Observed [R1, R2, R3, R5]:** The project has contact checks, animation refinements, source snapshots, measured export-profile references, render helpers, LOD variants, open-review fields, and a skill that explicitly rejects primitive blockouts as completed art.

**Action:** Preserve that infrastructure. The fix is an approved visual benchmark and enforceable art gates, not deleting the project or adding another generic 'quality checklist' that passes itself.

## Finding 8 — Rebuilding from the original generator can erase improvements

**Observed [R1, author]:** The generator resets the scene with `read_factory_settings(use_empty=True)`, reconstructs the character, and saves to canonical source/export locations. The foundational path exports meshes and LODs before visual acceptance; `--all` batches eligible heroes.

**Action:** Do not use this as an incremental refinement command on improved assets. Keep it labeled as a blockout/reconstruction route. Accepted sources and candidates need separate paths and an explicit promotion step. Run scene-resetting scripts only in isolated Blender processes with known saved work.

## Immediate priorities

1. Establish a clean before-view and decide whether the objection is form, shading, material content, or all three.
2. Rebuild Ada's large shapes against an approved design; hands and face must be integrated, not pasted onto the old shell.
3. Replace the color-index shading policy and flat placeholder surface maps selectively.
4. Test one candidate in Unreal with actual gameplay framing and existing animations.
5. Scale to representative body types only after visual acceptance.

## Do not infer these things

Do not infer exact current screenshot triangle counts, absence of materials, successful engine import, artistic acceptance, or competitor budgets. Do not infer that additional MCP integrations are enabled merely because their code exists. Do not treat all 24 characters as having identical defects without inspecting them.
