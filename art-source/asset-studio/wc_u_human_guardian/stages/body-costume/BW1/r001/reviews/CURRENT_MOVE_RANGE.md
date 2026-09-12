# Current Ada Move range: source-derived BW1 test input

Measured 2026-09-09 in a separate Blender 5.1.1 background process with automatic scripts disabled. No source file was saved, no live Blender session was accessed, and no retarget, engine import or game-source change occurred.

## Authority and preservation

`reports/implementation_state.json:update_delivery` identifies the preserved 24-hero r4 checkpoint and its asset-readiness matrix. That matrix identifies Ada source revision 9, animation revision 8, `humanoid_standard` / `WC_family_v1`.

The current source Blender file, export manifest, Move FBX and Move Unreal `.uasset` all still match the hashes recorded by that checkpoint. The source was re-hashed after the read-only measurement and remained unchanged. Exact hashes and report paths are in `current_move_measurements.json`.

Source inspected:

`art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend`

Action: **`AN_wc_u_human_guardian_Move`**, frames **1–61** at **60 FPS**, duration **1.0 second**. The source, export manifest and existing Unreal import report agree on this duration. The source armature contains **27 bones**.

## Measured source animation

The action was assigned to the source armature in memory, its action slot selected, NLA tracks muted, and evaluated at **481 samples spaced 0.125 frame apart**. Values below are source bone `matrix_basis` XYZ Euler rotations relative to the source rest orientation, not universal anatomical joint angles.

| Source joint, both sides | Local X minimum | Local X maximum | Other axes |
|---|---:|---:|---|
| `thigh_l`, `thigh_r` | −22° | +22° | Y/Z 0° |
| `calf_l`, `calf_r` | −19° | 0° | Y/Z 0° |
| `foot_l`, `foot_r` | −22° | +41° | Y/Z 0° |
| `toe_l`, `toe_r` | 0° | 0° | Y/Z 0° |

No constraints were present on these source leg bones. These are sampled extrema; this test does not claim symbolic extrema for every continuous F-curve interval.

The source's anatomical-right leg has these coordinated extremes:

- Frame 16: thigh −22°, calf −19°, foot +41°.
- Frame 46: thigh +22°, calf 0°, foot −22°.

The left leg has the opposite phase. The large foot-local range counter-rotates the combined upper/lower leg swing; it should not be interpreted as an isolated 41° world-space foot pitch.

For a geometric cross-check, the angle between the evaluated thigh and calf directions ranges approximately **3.281°–22.281°** (including the bent source rest shape). Foot direction pitch in the armature YZ plane remains approximately **−22.667° to −18.445°**. The angle between calf and foot directions ranges **49.162°–112.162°**; this includes the source foot bone's sloping rest direction and is not a clinical ankle-flexion measurement.

## What BW1 may claim

This supplies a **current-source-informed range target** for provisional local boot/leg testing. It is more specific than arbitrary walk-like angles.

The source 27-bone rig is not directly compatible with the temporary **163-bone MPFB rig** described by the main BW1 task. Bone names, rest axes, hierarchy, joint locations and rest foot directions differ. Mapping signs or setting these numeric Euler values directly on MPFB does not establish equivalent motion. The full root trajectory, pose phase, sole contact and skinning also need review.

Therefore label any manually authored MPFB step proof **“current-source range-informed local step test”**, not “actual game Move clip retargeted” or “game walking coverage passed.” A future deliberate retarget/reconstruction and full pose review would be needed for that stronger claim. This task did not inspect a newly running packaged game or decode Unreal's compressed animation tracks.

Files:

- `current_move_measurements.json`: all measured samples, rest heads/tails, ranges, constraints and hash reconciliation.
- `inspect_current_move.py`: bounded read-only Blender measurement script; run only in a separate process with the verified source opened and `--disable-autoexec`. It writes the local JSON report, never the source.
