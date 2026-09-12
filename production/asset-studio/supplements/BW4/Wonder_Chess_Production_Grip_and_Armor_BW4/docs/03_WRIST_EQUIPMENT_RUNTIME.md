# 03 — Equipment, wrist and runtime integration

**Task H2. Goal: a fixed grip that survives the existing game, not a new finger rig.**

## 1. Reconfirm the actual seven-clip contract

Read `reviews/fixed_option/REVIEW.md` and its source audit in the local BW3 folder. These underlying files were referenced by the supplied review but not uploaded for independent inspection in this preparation task.

Load a COPY of the canonical game armature, Ada source and seven clips. Identify the real hand/forearm bones, equipment ownership and actions. Do not assume names such as `wrist.R` from MPFB equal canonical names or orientations. Check any later source changes. If a real clip lets go of the sword, a fixed attached hand cannot honestly support that use without an approved presentation change.

Preserve clip lengths, release timing, sockets and rest matrices. Do not globally adopt MPFB's 163-bone rig or copy its Euler channels into the 27-bone game rig.

## 2. Fit the real equipment, not yesterday's test cylinder

Record the blade/guard/pommel separately from the grip. Measure the grip at multiple sections; it may be tapered, oval or faceted. Use a bounding proxy which matches this shape for broad checks, and the actual triangles for final contact/clearance review.

The default is to preserve the current sword. If changing a hilt is proposed, show old/new independently, keep blade scale and silhouette stable, and get the change selected before final grip fitting. Do not quietly enlarge the handle until the web defect disappears.

Keep a single bone-to-equipment chain. A mesh that already includes a sword rigidly weighted to a hand does not need an additional duplicate sword actor parented to a socket. A separate sword object must not be deformed and parent-driven twice. Document the chosen implementation.

## 3. Freeze local geometry, not the shared rig

Prefer constructing the derived closed hand directly in the candidate canonical rest arrangement where practicable. This avoids reverse-engineering a mixed-weight posed cuff.

When a correctly shaped posed copy is used, first capture the selected surface in a known coordinate system. Remove the finger deformers from the DERIVED snapshot only. The new fixed geometry is then bound to the game's existing hand bone. Do not apply Pose as Rest Pose to the shared armature: S07 describes how that changes rest relationships.

### Transform contract (proposed derivation; not executed on Ada here)

Use column vectors and full 4×4 transforms. Define:

- `A_s`: source armature object-to-world matrix at capture time.
- `P_s`: source hand pose matrix in source armature space.
- `M_s`: source mesh object-to-world matrix.
- `v_s`: evaluated source vertex in mesh-local coordinates.
- `u = (A_s P_s)^(-1) M_s v_s`: snapshot vertex in source hand-bone local space.
- `C`: explicitly verified source-hand-local to destination-hand-local alignment, including any intentional unit conversion. Do not assume it is identity because bones have similar names.
- `A_d`: destination armature object-to-world matrix.
- `R_d`: destination hand rest matrix in armature space.
- `M_d`: destination mesh object-to-world matrix.

For a vertex with exactly 100% destination hand influence:

```
v_d = M_d^(-1) A_d R_d C u
world position at time t = A_d P_d(t) C u
```

This follows by substituting `v_d` into single-bone linear skinning; it is not a special-purpose inverse for mixed weights. Verify with actual evaluated geometry at rest and several poses. Check round-trip error in metres, orientation and scale, using the known source uniform-scale history rather than discarding it.

A simpler implementation may work entirely in destination armature space, but it must preserve the same relationships. The old posed MPFB shape, new rest shape and runtime pose must not be applied twice.

## 4. Decide how the wrist joins the forearm

Keep the palm/digits stable relative to the hand bone. The cuff/forearm junction needs a deliberate design:

**Preferred for a fully covered armored wrist:** a closed-hand outer glove with a controlled cuff return, overlapped by the separately fitted sleeve/bracer. The anatomical forearm remains continuous to a concealed, documented export cut. Both moving interfaces need enough coverage; large buried crossings are not acceptable simply because hidden in one camera.

**For a visible joined sleeve/skin transition:** build a transition band in destination rest space, assign appropriate existing hand/forearm weights, and review bending/twist. Do not apply the rigid inverse above to a previously mixed-weight evaluated band and call it exact.

Do not weld arbitrary unequal rings automatically or remove the whole forearm. Source and export roles must remain explicit.

## 5. What hidden-body removal means

A fully opaque, permanent glove can replace the covered skin in a derived runtime output. Keep the indexed source complete. Record every omitted region and ensure it remains occluded in all supported views, clips, transitions and LODs.

This is a representation choice, not a repaired MPFB web. No claim of bare-hand validity, opening/closing validity or reusable anatomical animation follows. If a future costume exposes that area, it needs an appropriate body/hand asset rather than reusing this masked output unchanged.

Never remove glove faces to conceal the failed exterior, and never let a mask create visible cuffs/holes or shadow leaks. Keep separated diagnostic views as evidence of what is and is not delivered.

## 6. Required carrying review

Review Idle, Move, Attack, Active, Hit, Defeat and Victory from their actual game sources. Capture all clips continuously at their authored timing, not just the old 145-frame MPFB probe. Sample extremes and fast intervals more densely where useful. Include representative state transitions such as Move→Attack, Attack→Hit, Active interruption and Defeat.

Inspect:

- Hand–handle local relationship and blade orientation.
- Guard versus index knuckle/cuff; pommel versus heel of palm.
- Wrist gap/crease, sleeve and bracer overlap during twist.
- Sword versus shield/torso through authored swings.
- Normal orientation, visible seams and arm silhouette from gameplay and gallery cameras.

Ordinary light touching and ambiguous nearly coplanar contacts should be classified; confirmed nonadjacent crossings and conspicuous penetration remain blockers. Numerical screens do not certify continuous motion or physically stable grasping.

The rigid hand itself should not be running 15 independent finger controls in the shipping test. The point is to remove that dependency, not hide it in a new scene.

## 7. Isolated Unreal inspection

Use the existing calibrated export profile and unchanged canonical skeleton in a candidate directory. Preserve root, bone names, rest matrices and required attachment transforms. Do not include control bones or create a new rig implicitly.

In the installed import path, explicitly prevent reference-pose replacement. Epic's FBX settings include `Update Skeleton Reference Pose` and `Use T0As Ref Pose`; importing an isolated candidate must not overwrite the shared skeleton's pose. Do not assume the current UI is identical across Interchange and legacy FBX paths; record the actual path and equivalents.

Confirm normals/tangents using the known material convention. Preserve material slot order needed by existing code. Inspect the actual exported/engine mesh, not only the high-subdivision Blender study.

Do not alter the shared socket to fix one hand. First fit the candidate; where an asset-specific socket is genuinely required, use a reviewed candidate/mesh-specific configuration (S10).

Reopen Blender in a new process and cold-load the candidate in Unreal. Re-run the seven clips there. If engine tools are unavailable, label the result AUTHORING_ONLY or SOURCE_CLIPS_REVIEWED, not RUNTIME_ACCEPTED.

## 8. Completion boundary

H2 ends with a reviewable fixed-hand/real-sword assembly. It is not a completed Ada, not a solved dynamic grip generator, and not permission to replace a packaged asset without review.

After H1 is credible, cuff/bracer modeling may proceed. Independent chest/shoulder design can proceed even if runtime access is blocked; it must not inherit a runtime pass.

Tool/engine references: S07–S12 in [research directory](../research/REFERENCES.md).
