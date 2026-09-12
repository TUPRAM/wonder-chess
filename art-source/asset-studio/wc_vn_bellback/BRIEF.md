# Bellback — dorsal-bell creature pilot

**Current state: intake authored; formal references pending.** The user selected the shared mythic-storybook direction with “Use this direction.” This records creative identity selection only. The actual Bellback reference, forms and release gates have not been accepted. No Blender scene, finished mesh, rig or Unreal import exists in this lane.

## Identity and compatible art amendment

Bellback is a planted mossy quadruped with a readable animal face, broad paws and a **large dorsal bell**. Retain the substantial bell silhouette from the owner-selected plate while removing most tiny bells, branches and incidental ornament. Primary forms, anatomical continuity and a clear guardian posture matter before surface decoration.

The dorsal bell replaces the earlier chest-suspended art description. This is a presentation amendment; the unit ID `wc_vn_bellback`, directional guard, gameplay timing, statistics and logical footprint remain unchanged. The source-catalog art wording must be reconciled after the current engine build; this brief does not independently maintain gameplay values.

## Dimensions and construction targets

The manifest proposes a 2.2 m total height including the bell, 1.8 m body length, 1.6 m body width and a 1.7×1.7 m maximum foot-contact envelope within the 2 m tactical tile. These are **initial targets**, not measurements or approved final proportions. Check the actual strategy-camera projection and adjacent-unit overlap before committing forms. Source coordinates remain +Y forward, +Z up, meters.

Use the creature AS1 route. A quadruped rig must reflect leg joint directions, foot contacts and body weight. The bell shell and mount are separate rigid forms; a small constrained clapper may provide motion without introducing gameplay physics. No existing human armature is presumed suitable.

The provisional budgets in `asset.json` guide method selection: 35k/15k/6k triangles across three LODs, four material slots, two texture sets at up to 2048 pixels. They do not establish a measured renderer budget. Adjust only with a documented camera/performance result and compatible asset review.

## Part inventory and references

[Semantic parts](inputs/semantic_parts_r001.json) identifies the body, head/jaw/eyes, front and rear leg pairs, paws, dorsal bell/clapper/mount, primary root surfaces, moss clumps and bell trim. Part names carry meaning and remain stable through modeling; do not locate a limb by vertex count.

The existing [direction image](inputs/direction_r001.png) is aesthetic authority only. The new [r001 reference candidate](inputs/references/r001/bellback_reference_candidate.png) has been viewed, but is not a reconciled or approved construction sheet. Its [provenance and review](inputs/references/r001/provenance.json) record exact hashes and gaps. The complete reference pack must include:

- A coherent full-body front, true side and back at consistent scale/pose, plus the selected three-quarter identity.
- Explicit bell shell, dorsal mount and clapper relationships; occluded attachments are proposed construction, not observed facts.
- Unobstructed front/hind joint directions, paw shape, ground contacts and a motion-clearance sketch.
- Head/muzzle and eye relationships readable at the intended strategy camera.
- A documented resolution of asymmetrical roots/moss and a simplified ornament inventory.

Generated views remain construction candidates until checked for identity consistency and reconciled into a single feasible body. A panel label saying “side” is not an orthographic guarantee. No overlay measurements are valid until camera and pose are compatible.

Two explicit proposed corrections resolve prompt/image disagreement for the next review: use **four broad toes per foot**, and place the one short branch on **anatomical right (+X)**. The front image shows the branch on viewer-left and the back shows it on viewer-right. These are proposed consistent construction decisions; the generated pixels do not prove hidden geometry or constitute owner approval of the corrections. Keep the dorsal bell; author its concealed mount and motion clearance instead of copying contradictory projections.

## Review and next operation

The formal reference report remains `not_run` for reconciled views and undecided construction. Obtain actual owner approval of the reconciled packet before complex modeling. The relevant rule is in the AS1 reference manual: “Pram approves that this is the intended character before complex modeling begins.” Direction selection alone does not clear that gate.

Next operation: inspect the generated Bellback view candidate, compare its identity with the selected dorsal-bell plate, and record contradictions and missing construction information. Continue to a measured blockout only through the appropriate reference gate. No modeling tool or editor was invoked for this intake.
