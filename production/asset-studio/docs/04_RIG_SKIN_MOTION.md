# Phases 5–7 — Rigging, skinning and complete motion

## 1. Rig requirements before construction

Declare rest pose, joint placement, rotations, gameplay clips, hand contacts, facial needs, attachments, body families and supported stretch. Preserve current production IDs and a tested export-skeleton convention unless an explicit migration is approved. Bone name equality alone does not establish compatible rest poses or animations.

Human/Elf, Dwarf, Orc and later creatures may need separate foundations or retarget mappings. Reuse is a testable opportunity, not a rule that everyone must be a scaled version of Ada. Determine whether a braid/tabard needs bones, static geometry or constrained motion. Do not add physics to disguise bad weight painting.

## 2. Authoring rig versus export skeleton

The authoring rig may contain IK/FK controls, widgets, constraints, mechanisms and helper bones. The export skeleton is a deliberate stable hierarchy of deforming joints plus required root/socket/helper transforms. A root or weapon socket can be non-deforming and still be required. “Export deform bones only” is not sufficient if it drops those interfaces.

Rigify is an optional rig-authoring aid. Its documentation explicitly separates control/bone generation from skinning [B4]. Verify availability and the installed version rather than assume an old menu path. Keep the metarig and a rebuild recipe. Do not export all ORG/MCH/CTRL/widget machinery indiscriminately.

Bake evaluated motion from the authoring rig onto the export skeleton. An exported FBX does not carry Blender's entire interactive constraint/control system. Verify the baked result without the original controls. Preserve original rig for editing; do not destructively strip it as the only source.

## 3. Joint placement and orientation

Place shoulders inside the anatomical shoulder volume rather than at the armor edge. Locate elbow/knee bends deliberately. Match wrist/ankle pivots and hand/foot axes to motion. Check clavicle motion and hip clearance. Configure pole vectors and rotation roll so the same bend direction remains stable.

Use clear naming plus an explicit conversion map when existing names differ from Blender .L/.R conventions. Symmetrize only around the approved anatomical plane. Do not mirror a root-motion or weapon socket accidentally. Check negative scale and bone roll rather than blindly apply transforms after animation exists.

## 4. Skinning initialization

Automatic weights are a starting estimate, not a skinning approval. They can misassign nearby surfaces; Blender's documentation notes that manual correction may be necessary [B5]. Choose automatic, transferred or manual initial weights by part.

Soft body/cloth transition areas get distributed influences. Rigid weapons should attach through the chosen socket or rigid weighting policy. Armor plates should retain shape where designed; blended rubbery pauldrons are not acceptable merely because the weight sum is one. Layered garments may need copied body weights with carefully modified hems and joint areas.

Normalize active deform weights; remove tiny unintended influences; limit to the approved platform profile; then inspect again because limiting influences changes deformation. Ignore intentional non-skin mask groups when validating deform weights. Check unweighted vertices and influence on control bones. The proposed <=4 influences is a portable starting target, not a universal engine limit.

## 5. Pose stress suite

For each body family define repeatable poses within intended motion, such as elbow 45/90/130 degrees; shoulder horizontal/raised; wrist flex and pronation; fist/grip; knee 45/90/120; hip flex; torso twist; neck turn; and the actual full shield/weapon poses. These are proposed test samples, not medical/anatomical limits or a command to force every character through impossible rotations.

Inspect both sides, camera-facing and hidden parts, and in-between motion. Look for volume collapse, candy-wrapper twisting, detached lips/eyes, armor squashing, sleeve penetration, thumb/handle contact, pelvis/tabard intersections and sole contact. Fix geometry when the cause is geometry, joints when the cause is joint placement, and weights when the cause is weighting.

Blender Preserve Volume can change deformation behavior through its quaternion-based method [B6]. Do not approve a pose only with a deformation method that the chosen Unreal path does not reproduce. Review the runtime-compatible deformation, or implement/test an explicit correction route.

## 6. Corrective shape keys and extra bones

Use a corrective only after identifying an unavoidable residual deformation issue. Record driver/input pose and intended magnitude. A Blender driver is not automatically a runtime corrective. If a morph target or pose-driver is required in Unreal, implement and test it explicitly. Keep vertex ordering stable for morph data. A remesh after corrective authoring invalidates that work.

Rigid/socket attachments must work in every required clip. If equipment is deliberately embedded in the skeletal mesh, retain semantic part IDs in source and document its export mapping. Do not change socket transforms to hide a bad grip in one pose at the expense of the others.

## 7. Required hero animation clips

Idle, Move, Attack, Active, Hit, Defeat and Victory are the baseline from the existing Wonder Chess contract. Additional ranged aim/turn/dash variants are profile decisions. Every hero/clip combination gets continuous review; shared animation does not remove that requirement.

Define FPS, frame ranges, loop policy, neutral pose, root-motion policy, contact events and intended action timing. In-place movement remains the proposed game default; the simulation controls logical location. Root locomotion, dash interpolation and attack displacement must not fight one another.

Animation should communicate anticipation, release and recovery. Map actual release to the game's authoritative event time through the chosen playback/timing policy. An animation notify can request sound or particles, but it must not independently apply combat damage that the simulation already applies.

## 8. Motion tests and temporal sampling

Review the full clips at normal speed and slowed playback. Do not judge an attack solely by one frame with a readable sword. Sample transitions between idle/move/attack, interruption by stun/hit, defeat during an action, facing changes and repeated attacks at the allowed rate range. Check foot sliding and weapon/hand contact through the entire arc.

Record motion extrema, socket trajectories, root drift, loop seam error, hand-contact deviations and visible penetration. Use metrics to find suspect frames, not to declare those frames artistically correct. Contact tolerance must be scale- and shot-dependent; there is no universal gap that is always invisible.

## 9. Export bake

Keep rest data and animation clips separate initially. Bake only selected clips over exact frame ranges onto the explicit export set, preserve required root/helpers and avoid unintended actions/NLA tracks. Verify the versioned profile against local APIs. Export one named animation per file when that simplifies the current importer contract [E1].

After import, check duration, range, root orientation, feet, grasp, normals and sockets. Compare actual key poses and continuous playback. Reimport a source change and confirm that animation/skeleton bindings do not silently reset.

## 10. Gate

Skin acceptance needs numeric weight observations plus actual pose images/video. Motion acceptance needs full clips/transitions plus event timing and contact evidence. A valid skeleton or an FBX file is not proof of correct deformation.
