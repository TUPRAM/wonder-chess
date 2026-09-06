# Blender production brief — Wonder Chess alpha

## 1. Art target

Make stylized, warm high-fantasy tabletop champions with deliberate silhouettes and readable surfaces, not photorealistic miniatures or generic recolored mannequins. The reference view is an oblique strategy camera showing the whole eight-by-eight arena; close-up beauty renders are supplemental. Use the exact per-hero art fields in `ALPHA_24_ASSET_BRIEFS.md` and canonical JSON.

Reference arena: **The Seven-Lantern Courtyard**, Brighthaven. Warm limestone playing surface, blue-roofed distant buildings, oak trim, a few flags and potted plants, and a low wall separating spectators’ implied world from the board. Keep the background quieter than the heroes. No full crowd, dynamic rain, cloth simulation or large fog volume in the alpha.

The adopted playable package contains all 24 heroes and seven original neutral archetypes. Preserve existing Human/Elf/Dwarf/Orc assets, refine Ada first, then complete the existing twelve, four additions, and validated Halfling/Dragonkin family pilots followed by their batches. Use the individual update briefs; uniform scaling of a human body cannot certify a new family.

## 2. Camera and scale before detail

Use the calibration asset to prove one-meter and two-meter measurements. Author Blender scene in meters, Z up, consistently oriented +Y forward in the source. Unreal is +X forward, +Z up in the selected project convention, with centimeters. Export/import may handle basis conversion differently across versions: measure a named forward arrow and animated root, record the working preset, and never repair every actor with arbitrary scale 100 or rotated child components.

Start with a 1600 cm square board made of 64 tiles at 200 cm pitch. Place a full-height Ada (182 cm), a Dwarf and an Orc mock silhouette before sculpting detail. Choose the actual camera focal length, angle and distance by fitting the board with shop/HUD safe areas. Proposed starting view: perspective camera around 50–55 degrees downward and restrained field of view; this is an iteration input, not an exact universal setting.

Deliver camera preset data and screenshots at 1920×1080 and 1280×720. Check 96-pixel character previews, normal game zoom, 12-unit fights and neighbor occlusion. Freeze the gameplay camera before producing fine texture work. Do not use cinematic depth of field or motion blur to hide deformation.

## 3. Reference hero: Ada Brightshield

Read the full Ada dossier. Block the broad shoulders, shield arc, torso taper and sword silhouette. Confirm her feet/height and low-resolution crest. Develop broad costume planes, then joints and bevels. Separate armor from flexible cloth in source, but consolidate to one or two material slots at export. Model the face intentionally; do not leave a featureless sphere.

Build named source collections: BODY, COSTUME, EQUIPMENT, RIG, PRESENTATION_HELPERS and EXPORT. Create useful mesh topology around shoulders, elbows, hips and knees. Hide structural intersections under armor where appropriate, but never use intersecting primitive stacks as the final model. Avoid tiny decorative details that become noise.

Create UVs and texture maps; decide atlas grouping. Establish normal, roughness and base-color conventions. Rig, skin and animate all seven clips. Reconstruct materials in Unreal, inspect actual gameplay poses, create portrait from the accepted model, and perform one deliberate source revision/reimport. Only then mass-author the remaining heroes.

## 4. Rig families and joints

Recommended families: standard humanoid (Ada/Mira/Rowan); slender humanoid (Elves, potentially compatible retarget profile); stocky humanoid (Dwarves); broad humanoid (Orcs). Family is a source-rig/proportion contract, not a promise all four must use identical Unreal skeleton assets. Evaluate shared skeleton compatibility or IK retargeting in the installed engine and record the actual result. Keep a family version and approved rest pose.

Use a single `root` at ground origin, pelvis, three spine segments, neck/head, clavicles, upper/lower arms/hands and upper/lower legs/feet/toes. Add only needed facial/accessory bones. Prefer roughly sixty or fewer deforming bones and four influences per vertex. Use a small set of rigid accessory bones for scarf/coat follow-through when necessary. Hair, long cloth and props must not depend on simulation for correctness.

Provide sockets `weapon_r`, `weapon_l`, `cast_origin`, `head_ui`; portrait cameras and control bones are not exported as gameplay bones. Keep equipment geometry in the skeletal asset or as approved socket-attached props; document the choice per unit. Selection collider remains an abstract stable proxy, not complex prop collision.

Verify weight normalization, no unweighted visible vertices, no accidental scale animation, root position and family rest poses. Review shoulders at high elevation, elbows at maximum bend, crouched hips and the dwarf beard/helmet clearance. “Same bone names” is not an acceptance test.

## 5. Materials and visual identity

Use shared `M_WC_Hero` and controlled instances; atlas use is optional where it preserves per-character identity. Separate cloth, skin/scales, leather, metal and small magical accents through texture/roughness, not a material slot for every accessory. Normals and ORM-like masks are linear; base color is sRGB; confirm the actual engine importer’s conventions. If packing occlusion/roughness/metallic, record channel order and use the same master everywhere.

Start at 1024-pixel character maps, 2048 only when the actual camera proves the need. Use opaque materials for the body and most props. Avoid refraction-heavy crystals, transparent hair cards and permanently glowing full-body surfaces. Team readability uses rings, icons and accents rather than replacing all costume colors.

Budget target per hero: 6k–15k LOD0 triangles, up to two materials. Two lower-detail meshes start near 50% and 25%, with silhouette/small-feature checks. These are unprofiled design budgets. Overdraw, skeletal cost and shader complexity need actual measurement.

## 6. Animation contract

Seven clips for every hero: Idle, Move, Attack, Active, Hit, Defeat, Victory. Author at 60 FPS, aligning 50 ms gameplay intervals to three-frame increments. The simulation decides release times; animation notifies may drive sounds/particles only. Default loops: idle two seconds, move one second; hit 0.4 seconds; defeat one second; victory 1.5 seconds. Per-unit action windup/recovery comes from data, with visual release aligned accordingly.

In-place movement; no root-motion gameplay. Ordinary walk playback may adapt to actual move speed, but never changes logical arrival timing. During attack/cast, show an anticipation pose, recognizable release and return. Hits should not restart endlessly and lock the character visually. Stun uses a readable interrupted stance/indicator; do not substitute a hurt loop that keeps executing gameplay actions.

For dash, use a short directional movement pose while the presentation interpolates the authoritative move. No teleport smoke that conceals an incorrect destination. Healing and shield animations must be distinguishable. Area effects require a visible range edge. Defeat is non-graphic and clears visual targeting promptly; a staged dissolve does not delay logical elimination.

Stars use UI pips and restrained trim/glow, not separate bodies. Animation sharing is allowed only after every hero/clip pair is reviewed, including all 168 hero/clip combinations. This is an acceptance matrix, not necessarily 168 unique animation files. Neutrals require their separate applicable clip set and continuous review.

## 7. Arena kit

Create original modular tile, alternate tile surface, board edge, corner, low wall segment, bench plinth, flagpole, simple banner, lantern, planter, stair and distant building facade. Props are decorative; no destructible obstacles or terrain bonuses. Distinct placement/hover/selection rings are authored for readability, not baked into tile textures.

Use mesh instances for repeated geometry. Give terrain materials enough value separation to show cell boundaries without a noisy checkerboard dominating the heroes. Reserve space for an enemy header, local bench and shop. A bench plinth corresponds to a logical slot but is not its authority.

The `create_calibration_scene.py` helper creates measured test objects only; it is not the finished courtyard. It is intentionally unable to satisfy the arena art gate on its own.

## 8. Export and import

Keep source `.blend` and named exports under each hero directory. Export mesh/rig and one selected action per animation file initially. Record Blender version, add-on/API availability, selected objects, modifiers, normals, bone axes, unit scale, leaf-bone setting, animation bake settings and actual importer (legacy/Interchange). Do not assume Blender offers an FBX version selector identical to other DCC tools. Epic’s FBX pipeline documentation is the engine-side reference; compatibility must be demonstrated.

Do not blindly apply transforms after animation. Complete transform normalization at the correct modeling/rigging stage. The helper `inspect_scene.py` collects measurable facts and detects some problems, not artistic acceptance. The exporter helper refuses implicit whole-scene export and requires a named collection/profile. Validate it on a copy and confirm correct actor scale before using on all heroes.

Per hero: `SK_<id>.fbx`; `AN_<id>_<clip>.fbx`; `T_<id>_BaseColor.png`, normal and declared mask files; a 512–1024 portrait rendered from the approved model; source `.blend`; export manifest; measured preflight; reference screenshots; and actual Unreal capture. These paths describe requested outputs, not files already present in this handoff.

## 9. Review and automation

Use repeatable scripts for construction, export and reports; combine them with visual review. Capture front, side, back, three-quarter, grayscale silhouette, all seven clips and a crowded-board sequence. Keep a per-hero status: brief → blockout → model → rig → animation → imported → reviewed → accepted. Each stage points to evidence, not merely a Boolean.

Accept an asset only when it has a consistent identity, correct scale/foot contact, visible material separation, stable motion, appropriate effects, a matching portrait and preserved references after reimport. Reject wrong race/proportions, accidental extra equipment, floating feet, limb collapse, missing textures, incorrect normals or camera-obscuring effects. Original generation alone is not proof of quality.

Supplied scripts are scaffolds pending actual Blender execution in the user’s environment. Do not mark them executed because ordinary Python compiled their syntax. No Blender installation or generated 3D asset is bundled with this kit.
