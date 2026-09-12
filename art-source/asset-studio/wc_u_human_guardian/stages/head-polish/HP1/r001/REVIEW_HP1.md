> Current continuation: [r016 local correction review](local-correction/REVIEW_LOCAL.md). The working file now contains r016; this r014 report and its hashes remain historical evidence for the preserved r014 checkpoint.

# Ada HP1 head polish — r014

**Executed, reviewed, retained at REVISE. The requested near-perfect 2D likeness has not been achieved. No human forms approval was recorded.**

This run continued from the original FH1 r004 head in a separate HP1 work file, using the visible Blender 5.1.1 session and its existing MCP. Native Computer Use was used to reopen/focus and inspect Blender. No current legacy Ada mesh was used as a new foundation. Hair, eyebrows and eyelashes were excluded. The source portrait stayed authoritative; the supplementary construction sheet supported other views.

## Retained files

- [Editable working Blender file](ada_head_polish_work.blend)
- [Frozen r014 checkpoint](ada_head_polish_checkpoint_r014.blend)
- [Executed scene audit](scene_audit.json)
- [File hashes and verification](verification.json)
- [Independent visual review](reviews/independent_head_polish.md)
- [Original-source preservation review](reviews/preservation.md)

Active Blender scene: `HP1_HEAD_POLISH`. Active skin: `HP1_HEAD_POLISH_Head_r014`. `HP1_BASELINE` retains the incoming FH1 head for comparison. Failed and superseded HP1 objects remain hidden. `HP1_CAGE_REVIEW` is a separate evidence scene containing an unsubdivided copy and actual cage edges.

## What changed

- Rebuilt the orbital boundary flow, then changed eyelid topology: actual openings, inset wall, margin, lid volume, crease and independent socket transition.
- Added an independent nasal bulb section. Reduced the overprojected first tip attempt and refined the columella/upper-muzzle relationship.
- Refined the upper-lip volume and shifted the mouth slightly upward/backward for the primary portrait comparison.
- Reduced excessive lateral head breadth and cheek inflation. Lowered the ears with a continuous junction adjustment.
- Rejected the r012 ear-base jaw shelf. Retained a restrained lower jaw turn on the cleaner r011 surface.
- Repaired crossing neck-edge arcs, including an inherited baseline issue.
- Added a weak-perspective primary-portrait camera using approximate manually read landmarks. The neutral front/profile/three-quarter cameras were retained.

## Actual image evidence

The before/after renders below use the same camera and lighting. The sheet helper labels its composition “no registration”; that means the helper performed no image registration. The two source renders themselves use the same saved Blender camera. The illustrated-reference fit is approximate and is not a silhouette metric or an artistic score.

![Same-camera baseline and r014 comparison](C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/captures/primary_before_after.png)

![Retained r014 front](C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/captures/r014_front.png)

![Actual editable cage](C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001/captures/r014_cage_three_quarter.png)

Additional captures include profile, opposite three-quarter, rear, reversed key lighting and eyes hidden to expose the lid openings. Files are in `captures/`. No new AI artwork was generated in HP1.

## Remaining major defects

1. Upper-lid coverage and corner/plane flow still produce too much exposed globe and a startled expression.
2. The nasal underside-to-philtrum profile still forms a swept recess instead of clearly separated but connected columella, short philtrum and upper-muzzle volume.
3. The jaw/lower-cheek contour remains too generic and weak compared with Ada’s firm diagonal turn.
4. Reversed lighting still exposes uneven medial-socket and cheek transitions.

The independent reviewer retained r014 as the best current candidate and identified these as major defects. Successful scripts, a cleaner surface, or valid topology do not clear them. The current method has not resolved the required likeness, so this is an affected-stage art stop with a focused intervention brief, not a completed head or a downstream production gate.

## Focused intervention brief

Preserve r014, the approved reference and the saved cameras. Work on one connected anatomical-right region spanning the medial eyelid, nasal sidewall, columella/philtrum and upper cheek. Use directly edited control-cage planes or a sculpt correction that can be transferred back to this editable surface. Keep the real openings and nasal vaults. Establish the lid/canthus and nasal-base-to-lip profile explicitly; give the cheek its own plane. Show the same front/profile/three-quarter, primary-pose and reversed-key views before mirroring or extending. Reject the r012 ear-base shelf. No hair-family work or production stages.

The optional feedback prompt asks which remaining mismatch is most important: nose/mouth profile, cheek/jaw/chin outline, or eyes/sockets. It does not request or record forms approval. No answer had arrived when this packet was written.

The applicable [wca-organic instruction](C:/Users/iputu/Documents/Wonder Chess/.agents/skills/wca-organic/SKILL.md) states: “Two no-improvement attempts require a method review or focused human intervention.” It also states: “A missing editor or poor required visual result blocks the affected stage.” The visual result, rather than editor access, is the remaining limitation.

## Verification boundaries

The retained skin has **1,670 vertices and 1,612 faces**: 1,608 quads, two five-sided nasal section joins and two six-sided nostril-vault caps. It is one connected component. The four intended open boundaries are the two eyes (20 edges each), mouth (34), and head bottom/neck interface (40). There are no unintended internal non-manifold edges or degenerate faces in this check.

The level-2 evaluated surface has 26,042 vertices, 25,816 faces and 51,632 triangulated equivalents. Blender’s BVH overlap check found **zero non-adjacent self-overlap pairs** after excluding face pairs sharing vertices. This is a single neutral-pose geometric check, not a deformation or production certification. Source/render allowlists and camera matrices are in `scene_audit.json`.

All nine protected FH1/MR1/r003/reference files match their recorded hashes. The active HP1 scene contains only the retained skin and two diagnostic eye meshes as renderable geometry. No hair-family object is linked to that scene. Source preservation and operation scope were checked independently.

Not run: topology for deformation, final UVs/bakes/materials, rigging, animation, LODs, Unreal import, reimport, packaged-game review, or human forms/release approval. Full gameplay test suites were not rerun for these art edits. Operation scripts were parsed and the relevant Blender operations, renders and geometry observations were executed.
