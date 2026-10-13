# Unreal rig, animation and validation procedure

**Version 1.2 amendment:** [engineering](ENGINEERING.md) defines rig families,
separate deform skeleton/authoring controls/runtime clips, expanded budgets and
mandatory controlled revision/cold reopen/recovery. Use the
[qualified toolchain](TOOLCHAIN.md) and explicit Unreal validator runner. An empty
contract or a process that never invokes the Python validator cannot pass. Check
actions at normal speed for weight and intent as well as numeric contact accuracy.

**Scope:** G4 rig, G5 motion, G7 packaged verification and G8 acceptance/promotion for the Meshy-to-Unreal creature pipeline. G0–G3 establish the environment, look, references and Meshy candidate; [audio](AUDIO.md) is G6. This is a reusable procedure, not evidence that the five new creatures have been produced or tested. No Blender step is required.

The [Bellback review](../../reports/bellback-production-20260920/README.md) is an executed example. Its bone names, proportions, material edits, gait and acceptance do not transfer to another creature. Follow the [Unreal implementation contract](../../docs/UNREAL_IMPLEMENTATION.md), current `wonder_vnext` catalogue and each [character brief](CHARACTER_BRIEFS.md).

## Input contract and ownership

Before G4, preserve the original Meshy downloads, maps, generation/remesh settings, task identifiers and source hashes. Work in a new candidate folder under the existing hero's asset directory and a separate Unreal content revision. Record the stable gameplay ID, exact source files, Unreal version, importer settings and candidate owner. One writer owns each skeleton/mesh/rig family; checkpoint before reimport or weight changes.

Obtain the exact G3 forms approval before dependent production rigging and animation. A bounded early rig probe during G3 may reveal impossible joints or fused parts; it is feasibility evidence, not a substitute for forms approval.

The initial Meshy rig is an input candidate. Unreal production work must establish deformation, controls, motion, sockets, selection and game behavior. An exported skeleton or successful import does not establish any of these qualities.

**Preserve Meshy's light colors.** Keep original base-color pixels and neutral material tint. Verify color-space flags, map-channel assignments and normal-map convention against the actual export. Compare neutral lighting and the planned soft board lighting. Do not copy Bellback's historical muzzle tint, roughness remapping or emissive adjustment into new heroes. Correct lighting through the shared G1 look review; extra material changes need an explicit reason and review.

## G4 — Import and prove the rig

Version 1.3 new-creation requests include this stage before the combined
forms/color/rig review. Use [wc-creature-rigging](../../.agents/skills/wc-creature-rigging/SKILL.md)
and the [animation-ready contract](ANIMATION_READY.md). A static textured import
or an untested provider skeleton does not complete this scope.

### 1. Establish units, orientation and bounds

Import into an isolated candidate destination, keeping the untouched source recoverable. Check actual mesh dimensions in centimeters, facing direction, origin, root transform, reference pose and skeleton hierarchy. Compare these against the hero brief and the actual board tile; use measured dimensions to derive any scale correction.

Do not assume a 100-unit root, Bellback's `2.2 / 1.7` scale, its 6 cm board offset, its foot regions or its bone indices. Check parent-scale composition before adding animation. Place a visible ground plane at a recorded world height. For floating heroes, define a visible hover reference height and a separate lowest-appendage clearance requirement.

Inspect front, side, rear and underside views. Record triangle counts, material slots, texture sizes, skin influences, disconnected fragments, required sockets and both imported and animated bounds. Bounds extensions used to avoid culling must not silently enlarge selection targets.

### 2. Map anatomy before solving movement

Create a per-hero mapping from semantic roles to actual imported bones: root/body, head, jaw, limbs, flexible chains and rigid structures. Validate that every required bone exists and has the expected parent. Reject an unsuitable skeleton rather than renaming an unrelated humanoid hierarchy and calling it complete.

- Cragstoat needs a long flexible torso, believable paws and stable rocky ridges.
- Grandmother Root needs its approved support anatomy and garden attachments evaluated together.
- Snapvine needs controlled root/stem/jaw movement, not assumed quadruped legs.
- Prism Organ needs rigid ceramic/glass parts with deliberate floating motion.
- Reefglass needs shell stability and independently readable soft appendages.

Use these as inspection priorities; the approved forms determine the final controls. Retain useful Meshy weights and correct specific failures in Unreal. Preserve geometry/UVs unless an explicitly reviewed change requires otherwise. Separate rigid weighting from flexible weighting so stone, ceramic, glass or attachments do not bend unintentionally.

### 3. Test difficult poses first

Before polishing idle animation, test maximum intended crouch/compression, full limb reach, sharp turns, attack contact, recoil and the proposed defeat pose. Include the largest jaw or appendage motion. Check elbows/knees from the side and both sides of the torso, not only an attractive front angle.

Check silhouette, pinching, volume loss, limb-length preservation, self-intersection, attachment drift and the lowest surface point. Record unreachable targets instead of hiding them with stretching or a whole-body lift. If the rig cannot support a required pose, resolve its construction or revise the pose before dependent clips multiply the problem.

### 4. Provide an editable inspection study

Expose meaningful controls and label their spaces and limits. Foot/appendage targets, bend-direction controls, body and rigid-part controls should visibly affect the intended regions. Bellback's twelve-control/eight-second study is an example, not a universal control count or script.

Save, close the editor and reopen the exact map/sequence. Check key values, actor binding, visible deformation and control response after reopening. A live-session preview alone can hide unsaved keys or broken bindings. Record the sequence, frame range, control names and actual captured frames.

**Capture lesson:** Bellback's editor-only actor initially produced shadows without a visible creature in SceneCapture's game view. Check actor/component visibility and editor-only flags; refresh the render state after changes. Keep the diagnostic map excluded from cooking while allowing its actor to render in the inspection scene. Do not use a passing numeric pose check to excuse a blank image.

**G4 exit:** measured import manifest, anatomical mapping, saved rig, difficult-pose evidence, cold-reopen control evidence and unresolved defects. Technical passage does not grant human forms approval.

## G5 — Author motion and connect presentation

### Clip and event contract

Provide Idle, Move, Attack, Hit, Defeat and Victory, plus start/stop, turns and each hero's actual ability presentation. Ability behavior is required for all five heroes; a separate file named `Active` is optional when documented clips or blends provide that behavior. Bellback's asset named `Active` represents a passive guard reaction; names must not invent mechanics.

Read timing and outcomes from canonical/generated data and existing combat events. Damage, healing, control, target choice and movement remain authoritative game operations. Animation notifies may request cosmetic sounds/effects; they must not apply damage twice or alter results. Verify a deterministic combat-event/result signature against the same fixture with the candidate presentation disabled.

Author readable anticipation, contact and recovery around the existing action timing. Keep a committed attack readable through a brief hit overlay; resolve defeat once and clear stale clips/events when an actor is reused. Test start, stop, target change, turns, movement interruption, ability interruption and restart.

### Grounding and travel

For grounded creatures, drive walking phase from actual displayed travel distance and the measured distance represented by a gait cycle. Match foot-contact cues to that phase. Starting, stopping or changing speed must not reset the gait arbitrarily or duplicate a footstep. Floating creatures need a deliberate translation/hover relationship rather than artificial foot planting.

Bone height is not sole height. Measure the actual skinned foot/contact surface, including each saved LOD. If post-blend contact correction is needed, implement it for that hero's anatomy and verify it after all relevant layers. Bellback's flat-board two-bone solver and per-LOD sole constants are explicitly candidate-specific; do not reuse them for other shapes or claim terrain support.

### Actual-surface verification

Evaluate Unreal's actual skinned mesh through the runtime animation path, not only exported transforms or offline mathematical rigs. Inspect every clip, required overlay and important transition at every LOD, including loop seams and the difficult poses. Include an underside/side camera and visible ground reference.

Use the proposed thresholds in [ACCEPTANCE.md](ACCEPTANCE.md), calibrated per hero at G0. They are starting policy, not historical measurements or automatic art approval. Begin with 60 pose samples/second, exact contacts/extrema and transition blends at 25/50/75%; densify around failures. Evaluate numerical floor tolerance, rest clearance and stance drift separately. Grounded-creature contact rules do not impose a zero-height hover on floating designs. Measure rigid-region drift against its intended rigid transform and inspect the result visually.

For live turns/start/stop, track contacts in world space. A straight-stride audit with nominal forward travel does not certify turning trajectories. Record solver corrections, reach clamps and sample coverage; a finite sampled pass is not proof about every possible pose.

**G5 exit:** saved clips and timing contract, native surface measurements, actual image/video review, movement/transition checks, and unchanged gameplay signatures. Surface pass plus convincing motion are both required.

## G7 — LODs, selection, package and performance

### Preserve appearance through reduction

Generate and save one new skeletal LOD at a time, then verify its mesh data before proceeding. This avoided an observed Bellback reduction failure. Choose reductions and screen thresholds from actual board-camera comparison; 35k/15k/6k triangles remain provisional starting targets, not universal limits.

Check silhouette, eyes/jaws, thin stems, glass edges, disconnected components and skinning after reduction. Re-measure contact surfaces and rerun G5 across the saved LODs. Check LOD transitions during movement. Preserve source-to-import geometry/weight comparisons where relevant; quantization tolerances must be explicit.

### Selection and packaged behavior

Test actual imported/animated bounds with component scale and rotation. Include upper-body clicks whose ground projection falls in another cell, overlapping pieces, nearest-hit order, empty-cell placement and combat's command restrictions. Synthetic rays through the normal input dispatch establish geometry/handler evidence; separately exercise real mouse/UI routing and board-camera usability.

Package early into a fresh archive directory. Cook runtime meshes, materials, textures, animations, sounds and required presentation dependencies explicitly. Keep editor scripts, authoring JSON and diagnostic maps/Control Rig studies outside the runtime dependency chain. The current project marks `WonderChessArtTools`, Python and Control Rig as editor-only; a future runtime Control Rig design requires an explicit dependency change and package verification.

Reopen saved assets before final cooking. After reimport, verify references, skeleton compatibility, materials, sockets, controls and motion again. Do not assume reimport preserves an Unreal-authored skeleton or weight edits. Retain the previous working candidate for rollback.

Run the executable outside the editor, inspect logs and real frames, then exercise buying/deployment, combat, save/resume, restrictions, match completion and restart. A successful UAT exit means packaging completed; it does not establish successful launch or gameplay.

### Representative performance and audio

Measure both twenty moving copies of a demanding candidate and a twenty-unit mixed roster using the actual new materials, animations, shadows and effects. Record hardware, resolution, RHI, build configuration, frame cap, LOD distribution, sample count and median/p95/p99 frame time. Investigate stalls and memory growth. Apply the proposed 1080p/60 fps policy and explicitly recorded per-asset targets in [ACCEPTANCE.md](ACCEPTANCE.md); a measurement at another resolution cannot establish that pass.

Keep raw samples. Flag capture/warm-up work and document exclusions instead of silently discarding slow frames. Bellback excluded screenshot processing and one second of recovery from its steady-state summary. Keep gameplay simulation running and compare results.

Record the actual sound mix separately from the primary performance run. Validate full duration including silence, nonzero content, export-clamp hits and headroom; listen in the crowded scene. Temporary focus/submix recording overrides must remain run-specific. See [AUDIO.md](AUDIO.md).

### Verified Bellback command examples

These paths/flags belong to the existing Bellback implementation. **They are documentation examples, not new-hero commands or instructions to rerun accepted evidence.** Use a fresh evidence/archive path for an authorized rerun.

```powershell
# From the repository root: existing interactive inspection and packaged candidate.
& '.\support\tools\bellback_production\Open Bellback Rig.cmd'
& '.\support\tools\bellback_production\Play Bellback Candidate.cmd'

# Verified package wrapper; choose NEW archive/log directories before execution.
.\tools\unreal\package_game.ps1 -ProjectFile .\game\WonderChess.uproject `
  -ArchiveDirectory .\builds\Bellback-rerun-NEW `
  -LogDirectory .\reports\Bellback-rerun-NEW\package `
  -UatScript 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat'
```

The recorded r4 route used `-WCLab -WCProfileName=wonder_vnext -WCStorybook -WCCombatClarityExperiment -WCBellbackCandidate -WCBellbackPerformance -windowed -ResX=1600 -ResY=1000 -nosplash -unattended`, fresh absolute `-WCEvidenceDir` and `-abslog` paths, and the temporary `-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0` override. Its route rejects `-NullRHI`, `-benchmark`, `-UseFixedTimeStep` and `-nosound`.

The separate recorded audio route added `-WCBellbackCaptureAudio` and `-ExecCmds="t.MaxFPS 60,au.NeverDisableSubmixes 1,au.LogSubmixAutoDisable 1"`. These flags do not implement equivalent tests for another hero. Build its fixture and evidence contract explicitly.

## G8 — Acceptance, promotion and recovery

Provide one review package containing neutral/soft-board views, all motion, editable controls, actual game audio, packaged screenshots, performance and known limitations. Hash the exact source inputs, recipes, Unreal assets and executable being reviewed. Record owner acceptance against those hashes; do not transfer Bellback's approval to a different candidate.

Promote only the reviewed revision through the normal presentation registry/integration path. Preserve earlier candidates and the ability to restore the previous presentation. Update the asset's stage evidence and implementation state without declaring the whole roster, pacing study or release accepted.

Bellback's final evidence covers 4,767 gameplay poses, 241 cold-reopened control poses, three LODs and a local Development package. Its 3.869 ms p95 for twenty moving Bellbacks at 1600×1000 is a historical baseline on one PC, not a 1080p pass or a promise for mixed creatures, remote hardware or Shipping. Reuse its method and failure lessons; collect new evidence for every new asset.

### Implementation references

- [Bellback import recipe](../../support/tools/bellback_production/import_production.py): candidate-specific weights/materials; inspect before adapting.
- [Native runtime presentation](../../game/Source/WonderChessRuntime/Private/WCBellbackPresentation.cpp): distance-driven gait, event presentation and per-LOD contact correction.
- [Native skin/render validation](../../support/tools/bellback_production/validate_render.py), [cold-reopen inspection](../../support/tools/bellback_production/validate_inspection.py), [LOD audit](../../support/tools/bellback_production/lods_and_mesh_audit.py).
- [Packaged exercise](../../game/Source/WonderChessRuntime/Private/WCBellbackExercise.cpp), [final measured status](../../reports/bellback-production-20260920/completion-status.json), [packaging configuration](../../game/Config/DefaultGame.ini).
