# MPFB 2.0.17 installed-source rig and body-control review

Date: 2026-09-09. Status: READ_ONLY_SOURCE_INSPECTION. No Blender calls, rig execution, body changes, or pose-quality claims were made by this reviewer.

Scope: BW1's isolated body/costume and articulation proof. Canonical game skeleton and the MP1 derived head remain outside this research task.

Installed source root used for every reference below:
`C:/Users/iputu/AppData/Roaming/Blender Foundation/Blender/5.1/extensions/user_default/mpfb/`

## Standard rig entrypoint

With the full indexed MPFB candidate active in Object mode:

```python
bpy.context.scene.MPFB_ADR_standard_rig = 'default'
bpy.context.scene.MPFB_ADR_import_weights = True
bpy.ops.mpfb.add_standard_rig()
```

Exact source: `ui/rigging/standardrig/operators/addstandardrig.py:17` (operator ID), `ui/rigging/standardrig/standardrigpanel.py:17` (ADR_ scene prefix), `services/blenderconfigset.py:11` and `:30` (MPFB_ prefix). The supported service is `HumanService.add_builtin_rig(basemesh, 'default', import_weights=True)` in `services/humanservice.py:1552`.

Use `default`, not the panel default `default_no_toes`, when toe articulation is needed. Installed `data/rigs/standard/rig.default.json` has 163 bones. `weights.default.json` has 163 weight groups covering all 19,158 source indices; its license field is CC0. Coverage includes helper vertices. This establishes available initial weights, not good deformation.

## Transform and source-integrity precautions

`entities/rig.py:864` reads local vertex coordinates, using a temporary key from the current shape-key mix and then removing that temporary key. Joint positions come from named joint-helper groups or explicit source indices. `services/humanservice.py:1602` reparents the mesh and moves its location onto the armature, but does not copy object rotation/scale. MP1's source has an object rotation/scale, so directly accepting the resulting rig transform risks a mismatch.

Suggested procedure, to be verified live by the owning agent:

1. Save the candidate body's world matrix.
2. Temporarily set that candidate's object matrix to identity; do not bake transforms into indexed mesh/key data.
3. Create the rig in this local frame.
4. Set the created rig's world matrix to the saved body matrix.
5. Set the body's parent inverse and basis matrices to identity.
6. Compare world-space mesh bounds and joint landmarks before/after. Abort or restore the candidate if they change unexpectedly.

This is a source-derived method recommendation, not an executed rigging result. Original MP1 files and any independent contextual head must not be changed.

## Rest pose, axes and useful bones

The rig fits the current mixed source shape and helper locations; it does not automatically impose a T-pose. Freeze the observed source rest pose for garment fitting. Bone local Y follows head to tail; roll values come from the installed rig definition. Standard rig creation sets pose rotation mode XYZ (`services/rigservice.py:1554`).

Useful anatomical-right bones:

- Arm: `shoulder01.R`, `upperarm01.R`, `upperarm02.R`, `lowerarm01.R`, `lowerarm02.R`, `wrist.R`.
- Thumb: `finger1-1.R`, `finger1-2.R`, `finger1-3.R`.
- Four fingers: `finger2-1.R` through `finger5-3.R`.
- Leg: `pelvis.R`, `upperleg01.R`, `upperleg02.R`, `lowerleg01.R`, `lowerleg02.R`, `foot.R`, and toe chains.
- Anatomical-left counterparts end in .L. Do not infer side from screen position or world X after rotation.

The bundled `entities/rigging/righelpers/fingerhelpers/defaultfingerhelpers.py:9` treats ordinary finger flexion primarily as local X and the first thumb segment separately (opposition includes Z). Those limits guide bounded tests; they do not prove grip fit. Arm and leg helper files likewise separate bend from axial twist across their two-segment bone arrangement.

## Garment weighting without neighboring-finger confusion

Prefer exact source correspondence for helper-derived meshes:

1. Preserve original source index for each output vertex.
2. Copy only rig-bone groups from that source vertex.
3. For new vertices, interpolate from the known construction edge/source face.
4. Normalize/prune deliberately and inspect each digit in the required poses.
5. Assign rigid protection to an explicit attachment bone rather than unrestricted soft limb weights.

Bundled weights cover the helper vertices, making this route possible. Mesh copying/extraction can preserve group memberships, but explicit source-index provenance keeps the mapping inspectable.

The supported MHCLO method `ClothesService.interpolate_weights(basemesh, clothes, rig, mhclo)` (`services/clothesservice.py:426`) interpolates skeletal weights using each garment vertex's three recorded source indices and fitting coefficients. `ClothesService.set_up_rigging(..., interpolate_weights=True, import_subrig=False, import_weights=False)` (`:524`) also parents and adds an Armature modifier.

Caution: interpolation creates groups rather than replacing an existing set. A repeated call without scoped clearing can create suffixed duplicate groups. Preserve correspondence, visibility, thickness and cloth-pinning groups; they are not skeletal weights. Body weight application itself is by source index in `services/rigservice.py:878`.

## Small native body-control set

These are actual registered scene RNA properties. Activate the full indexed body before reading or assigning them; the getter/setter resolves the active basemesh. All controls below have dimensionless range [-1, 1], using paired decrease/increase targets. Zero is the neutral amount for that control, not necessarily the body's entire neutral shape.

| Purpose | Exact scene property | Definition in data/targets/target.json |
|---|---|---|
| Shoulder distance | torso_measure_shoulder_dist_decr_incr | line 3493 |
| Ribcage width | torso_torso_scale_horiz_decr_incr | line 3425 |
| Ribcage depth | torso_torso_scale_depth_decr_incr | line 3442 |
| Torso V shape | torso_torso_vshape_decr_incr | line 3527 |
| Waist circumference | torso_measure_waist_circ_decr_incr | line 3578 |
| Hip circumference | torso_measure_hips_circ_decr_incr | line 3510 |
| Upper-arm length | arms_measure_upperarm_length_decr_incr | line 63 |
| Lower-arm length | arms_measure_lowerarm_length_decr_incr | line 211 |
| Upper-leg height | legs_upperlegs_height_decr_incr | line 2162 |
| Lower-leg height | legs_lowerlegs_height_decr_incr | line 2217 |
| Right hand scale | hands_r_hand_scale_decr_incr | line 1555 (sided category) |
| Right foot depth | feet_r_foot_scale_depth_decr_incr | line 1303 (sided category) |
| Right shoulder muscle | arms_r_upperarm_shoulder_muscle_decr_incr | line 137 (sided category) |

Sided properties also have `_l_` counterparts. Category/section punctuation is converted to underscores (`services/uiservice.py:294`). Dynamic registration and [-1,1] range are in `ui/model/_modelsubpanels.py:314`; setters are at `:217` and `:258`. Assign ordinary RNA, for example `bpy.context.scene.torso_measure_shoulder_dist_decr_incr = value`; this invokes the installed target loader/setter. There is no need for a bespoke target-loading operator.

Set modeling options deliberately:

```python
bpy.context.scene.MPFB_MDP_prune = False
bpy.context.scene.MPFB_MDP_symmetry = True
bpy.context.scene.MPFB_MDP_refit = False
```

- Prune defaults true and can delete zero-valued shape keys. Disable it to retain source-key history.
- Symmetry defaults false. True updates the opposing side when a sided paired control changes; this does not retrospectively reconcile existing asymmetry.
- Refit defaults false. Leave off during a bounded fit, then use `bpy.ops.mpfb.refit_human()` only when installed attached assets/rigs should be refitted. Operator: `ui/model/operators/refithuman.py:16`.

Macro properties `mpfb_macropanel_muscle`, `mpfb_macropanel_weight`, `mpfb_macropanel_height`, and `mpfb_macropanel_proportions` exist with [0,1] ranges (`ui/model/_macrosubpanel.py:19`, `:93`, `:149`). They reapply broad macro targets and can change the body's head. Regional controls are the narrower first choice. No demographic labels are proposed for artistic fitting.

No specific slider amounts were accepted in this review. Record measured dimensions before/after a small control change, inspect the saved full-body views, then keep only useful changes.
