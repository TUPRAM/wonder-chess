# 2. Ada: connected body, hands, legs and costume pilot

## Objective

Produce an actual editable full-body Ada candidate from the retained MPFB source, with a readable layered costume blockout and two detailed articulation proofs: one arm/hand assembly and one leg/boot assembly. Preserve the head study at ART_REVISE. The task does not issue head, full-character or game-release approval.

This is not another facial iteration, a new game project, or an instruction to build a large automation platform first. Use existing AS1 review, HV1 hair procedures when later needed, working MCP and safe snapshot conventions.

## Inputs and authority

Read the current repository instructions and canonical Ada record, the approved full-body reference, the supplied MP1 REVIEW and verification, and the current local .blend. Resolve newer user edits before continuing.

Known scene names from the report: `MP1_SOURCE_CONTROLS` (full 19,158-vertex source with 38 shape keys); `MP1_ADA_HEAD` (derived head and diagnostic eyes); `MP1_ARCHIVED_TRIALS`. Object names and counts must be checked locally, not assumed unchanged.

Reference identity controls visual decisions. Game data controls gameplay and IDs. Research models are construction references or licensed adaptation candidates; they do not silently replace Ada's design.

### Independent task scope

The user now requests body/costume work. Record that scope explicitly. It may proceed while likeness is unresolved, but it does not bypass or falsify head approval. Do not clear the old method-stop status by renaming a report.

## A. Preserve the correct source and recover the body

1. Make a collision-safe new study file and immutable pre-edit checkpoint. Hash original MP1 files and required references. Do not overwrite them or canonical runtime imports.
2. Duplicate the full source with independent mesh/shape-key data as appropriate; verify that edits to the duplicate do not mutate the master through linked datablocks.
3. Inspect the preview Mask modifiers and render allowlists. Reveal the body on the candidate only; do not export helper cages, joint cubes or hidden failed experiments as skin.
4. Keep the full indexed master uncut. Do not weld, remesh, decimate, delete helpers, apply shape-changing modifiers or reorder vertices on the source that MPFB targets expect.
5. Preserve the derived head exactly. Its local sculpt/slider history may differ from the full body's evaluated head: establish source-index correspondence or a deliberate neck interface before any later integration. Do not assume matching appearance means matching indices.
6. For this body proof, use the existing head as a separately labeled contextual object with only one visible head surface. Do not hide a bad neck seam beneath a collar and declare final integration passed. A visible neck interface remains an explicit later task.
7. Reopen the saved candidate in a separate Blender process and verify required scenes and datablocks are retained. The MP1 report already documented an omitted-scene save defect; check persistence rather than merely observing a successful Save operation.

## B. Fit the body as a whole

Use the actual installed MPFB controls to adjust broad proportions. Discover control IDs/ranges locally. Do not invent slider names or use ethnic/demographic labels as proxies for the intended artistic proportions.

Record height, shoulder width, ribcage/pelvis relationship, arm length, palm width, leg length, knee/ankle positions and foot length in scene units. Start from the existing canonical scale and approved silhouette. Do not force measurements from an oblique painted reference to be orthographic ground truth.

Freeze one A-pose/rest-pose convention for body, garment fitting and future rig work. Compare front, true side, rear and both three-quarter views; include feet. Preserve useful adult proportions, a grounded stance and the heroic shoulder/waist relationship without making armor part of the anatomy.

Hands and feet remain part of the coherent base body. Only use Hands01 morphs after observing their effect in isolation; source target names are examples, not automatically recommended amounts. Do not apply targets to the extracted 4,271-vertex head.

Deliver a full-body clay silhouette now. Small facial imperfections are not a reason to return to a head-only run.

## C. Record the costume's layer graph

Use this construction order for the approved Ada design, reconciling any newer approved details first:

| Layer | Ada pieces | Construction concern |
|---|---|---|
| Skin foundation | Body/hands/feet | Stable source, anatomy and rest pose |
| Soft inner layer | Leggings, padded ivory coat, sleeves, collar | Fullness and clearance; preserve major openings |
| Outer cloth/leather | Navy front/rear split tabard, belt, straps | Hanging shape, readable hems, bend clearance |
| Rigid protection | Breast/back plates, nested pauldrons, bracers, knees, greaves | Separate manufactured surfaces, controlled overlap |
| Hands/feet outer layer | Gloves, boots | Grip and ankle behavior |
| Equipment | Left-arm shield, right-hand sword | Contact, handedness, swing space, sockets |

Model separate editable parts with semantic names. No runtime item inventory is introduced. Authoring modularity is for reuse and maintenance, not an instruction to add many draw-heavy runtime components.

## D. Build the padded coat and sleeves

1. Use the integrated MPFB MakeClothes helper-derived route or an independently authored low-density garment envelope fitted to the candidate body. The documented `helper-tights` extraction is one starting example, not a requirement to copy skin contours tightly.
2. On the garment copy, retain relevant faces and create deliberate collar, sleeve and hem boundaries. Extend and shape panels to the coat design; keep the original body/source intact.
3. Establish room for the arm and torso beneath the cloth. Use restricted fitting/projection only where appropriate; armpits and folds need independent volume instead of skin-tight shrinkwrapping.
4. Choose modifier order intentionally. If using Mirror, define the local symmetry plane. If using Solidify, inspect scale, thickness, inner/outer offset and rim behavior. Do not apply unknown stacks blindly.
5. Add major folds around elbow, shoulder and belt compression only after the silhouette works. Quilt/stitch patterns are later surface work except for silhouette-critical seams. Do not generate a dense grid of raised geometry across every fabric panel.
6. When writing an MHCLO asset, obey that installed MakeClothes version's fitting constraints. Its single-correspondence-group requirement is not the later skeletal skinning rule. Keep a separate fitting-authoring copy when necessary; do not destroy multiple-bone skinning weights to satisfy correspondence validation.
7. Record this as a candidate sleeve/coat construction recipe, not a proven reusable garment until it fits another allowed body preset and survives motion.

## E. Hands and gloves: repair through a coherent hand

Inspect the MPFB palm, thumb base, finger lengths and wrist transition before importing anything. Import at most two license-reviewed glove candidates and choose based on actual topology and pose behavior, not thumbnails.

A glove may be adapted from a useful candidate or built from a hand-derived envelope. Keep five coherent digits, web spaces, a knuckle arc, cuff opening and opposing thumb. Avoid repeated coil fingers, disconnected palm pads and a hidden hand intersection.

Create open, relaxed, sword-grip and shield-grip diagnostic poses. Build the grip around the actual handle dimensions; align the handle to the palm and then wrap digits rather than moving the weapon to compensate for a broken hand.

Skin-weight transfer is an initialization only. Use rest-pose alignment, appropriate mapping limits and part/side restrictions; adjacent fingers can receive incorrect influences from unconstrained nearest-surface transfer. Inspect each digit and wrist after transfer.

Rig decisions must respect the actual current export skeleton. Do not silently add finger bones or change the shared rest pose in the existing game. A temporary local rig can prove finger shape; integrating new controls/bones requires a separate skeleton compatibility decision.

## F. Armor: derive fit, then design manufactured surfaces

Use the body or coat as a fitting guide, not as the final armor's shape. Construct a breastplate with controlled major planes, edge thickness, neckline and lower contour. Avoid a smooth inflated shell or anatomically literal plating that contradicts the concept.

Build a shoulder assembly from separately editable cap/lame pieces with clear overlap and attachment assumptions. Rotate the arm through the intended range before detailing the trim. A pauldron must not behave like soft skin or slice through the upper arm.

Bracers and greaves wrap their limb segments, with clearance and readable openings. Do not bridge elbows/knees with one rigid shell. Keep straps and closures purposeful; use the external knight model to inspect construction principles only when acquired safely.

Test one pauldron with the same sleeve/glove arm chain. This exposes interacting defects that isolated static parts conceal.

## G. Legs, boots and knee protection

Use the full base's knees, calves, ankles and feet; no separate downloaded leg grafts. Select a useful licensed boot sample only after viewing side, underside, cuff and foot cavity. Preserve Ada's practical grounded footwear rather than adopting a high heel from an unrelated sample.

Construct the boot with a deliberate sole/toe box, heel, upper and cuff. The foot-following region and shaft may need different deformation treatment. A greave should follow the intended shin segment, not stretch with toe controls.

Review flat stance, foot roll/step, ankle flexion, bent knee, kneel and the actual walking range. Keep a margin against leggings/body exposure when relevant. Concealed geometry may be masked on a derived runtime copy only after testing; do not delete the master to hide penetration.

## H. Temporary deformation and presentation proof

Use the installed rigging method in an isolated candidate. Map existing actions only after comparing hierarchy, axes, rest pose, scale, sockets and root-motion assumptions. Matching bone names alone is insufficient.

Mandatory evidence: full-body front/side/back/three-quarter clay; costume layer view; hand/grip closeups; one arm assembly over shoulder/elbow/wrist motion; one boot/leg assembly in stance and bend; a short motion recording; actual edit-mode topology for each studied part.

Do not claim static BVH screening proves all contacts. Report penetrations by pose/time and distinguish harmless concealed overlap from visible holes, rigid intersections or grip loss.

## I. Finish the first assignment with real assets

Required output is the saved/reopened body-study .blend, body preset and versioned settings, detailed arm and leg proofs, selected source provenance, observations/inferred methods/executed recipe distinction, and a short defect report. Everything remains a candidate until the appropriate AS1 review.

One demonstrated adaptation is more useful than many downloaded models. Keep acquisition bounded and do not block on optional login/paid packs. No full texture production, final animation bank, full character export, new ML training, game rewrite or release claim is part of this first proof.

After the proof: complete the remaining costume, integrate the final head/neck through a deliberate method, inspect all seven hero clips, then follow the existing Unreal candidate/reimport path. Use MPFB's Export Copy if available and appropriate; explicitly choose mask/helper/subdivision treatment. Do not bake an authoring-level high subdivision just because an export checkbox defaults that way.

## J. Earn reuse

Take the accepted sleeve, glove and boot recipes to one second compatible body and one deliberately challenging proportion within the declared family. Record fit/pose failures. Only then promote the construction to a reusable skill/tool. Dwarves, Halflings, broad Orcs and Dragonkin require their own compatibility tests; body-wide scaling is not proof of a supported family.

## Technical references

MPFB helper extraction and constraints: `mpfb_clothes`; fitting tools: `mpfb_assets`; export-copy behavior: `mpfb_export`; Solidify: `solidify`; weight-transfer initialization: `data_transfer`; runtime modularity: `ue_modular`. Exact URLs are in `SOURCE_REGISTRY.json`. All detailed Ada construction and acceptance choices above are proposed project instructions, not claims that these operations have been executed.
