# Optional branch — fixed posed game grip

**Proposal for explicit adoption, not the default BW3 animated assignment and not a hidden gate bypass.**

## Why separate it

S1 records an unchanged27-bone game skeleton and proposes a possible future fixed posed hand. The current145-frame opening/closing study is an authoring test, not a retargeted game animation. It is not established that the shipped character needs to open its fingers or release the sword.

Inspect the actual current Idle, Move, Attack, Active, Hit, Defeat and Victory behavior read-only. Determine whether the sword ever leaves the hand, whether an open hand is visible, and what the gallery requires. Do not assume these answers from clip names.

If Ada always carries the sword in the relevant build, a deliberately modeled closed grip may be sufficient for that version. If a clip requires opening/release, the fixed option does not satisfy it unless the game behavior is changed through separate approval.

The objective is a smaller honest production requirement, not tolerating the old self-crossing mesh.

## Proposed construction after adoption

1. Preserve the failed animated study as ART_REVISE. Create a distinct derived hand/glove candidate for a single approved closed grip; keep the original anatomical master open and editable.
2. Start from the best noncollapsed form, not a frozen intersecting result that is merely renamed. Sculpt or directly remodel the thumb/web and fingers into a collision-free closed configuration around the fixed handle. Preserve length, plausible knuckle rhythm, wrist interface and outer silhouette.
3. Check the full closed surface and handle before reusing any source contact metrics. Retopology may be localized; if topology changes, remap contact regions and source relationships deliberately.
4. Retain a visible-body comparison. If a release mesh omits completely glove-covered skin to prevent doubled surfaces, record the derivative visibility decision and verify every possible exposed region. This does not certify the original underlying animated hand. Never delete the source master to conceal its failure.
5. Convert the selected posed hand into the actual runtime-rest hand frame. Use measured source/destination matrices, not matching bone names. A candidate that follows a wrist in Blender is not automatically compatible with the game's different rig.
6. Remove the baked finger deformation from the derived runtime route so it cannot be applied twice. Weight the grip region to the intended runtime hand joint; preserve appropriate wrist transition behavior and inspect the cuff seam with the arm.
7. Attach the sword with one stable grip-relative transform. Preserve existing shared sockets unless a separately authorized candidate-specific attachment is needed. Unreal sockets are bone-relative attachment points [W4]; editing a shared skeleton socket can affect other assets.
8. Inspect actual game clips on the candidate rig and in an isolated Unreal import. Review the rest pose and wrist seam, guard/pommel, normals, scale and any animation that might expose a gap. No production replacement until acceptance.

## Transform convention for an implementation review

For an already evaluated rigid closed-grip surface only, let `p_w` be a source vertex in world space. Let `G_s` be its measured source grip-frame-to-world matrix at the bake pose, `G_t_rest` the corresponding intended target grip-frame-to-world matrix in the runtime rest pose, and `M_t` the target mesh-object-to-world matrix.

A proposed rigid placement is:

`p_target_local = inverse(M_t) @ G_t_rest @ inverse(G_s) @ p_w`

Use homogeneous points and consistent units. The two grip frames must represent the same semantic origin/orientation and measured fit; any explicit fitting transform must be recorded. This is not an inverse of multibone skinning and must not be used to recover a generally deformable rest hand.

Verify zero-pose round-trip error, target hand motion and fixture alignment before export. Account for source uniform scale exactly once. Preserve or repair the wrist interface explicitly; a correct grip transform does not automatically weld the arm seam.

## Acceptance difference

A fixed candidate must pass its closed shape, held-motion, actual equipment, wrist and engine tests. It does not have to invent an unused opening transition. However, it must be labeled fixed, cannot claim the145-frame open-to-close gate, and cannot be promoted as a general animated-hand recipe.

The failed BW2 closure remains failed. This option is appropriate only when its restricted behavior matches the intended game and is explicitly selected.
