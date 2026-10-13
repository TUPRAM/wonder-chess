# Acceptance, evidence and default measurements

## Version 1.2 engineering additions

The [engineering contract](ENGINEERING.md) adds independently recorded G3A
construction, G3B deformation and G3C UV/bake checks. Before G8, G7 also requires a
deliberate edit/rebuild, cold reopen, full-byte recovery and usable raw/editable/runtime
bundles. Record this with [revision-recovery.json](templates/revision-recovery.json).

Select [broader budgets](templates/budget-profile.json) for bones/influences,
sections/components, resident textures, animation cost and whole-scene frame times.
Test both heavy duplicates and a mixed board, including bench/preview where visible.
Technical animation checks and artistic action readability are separate decisions.
The [app qualification packet](../../reports/pipeline-tools-20260921/README.md) proves
specific tool operations only; it does not promote a future creature or the shared look.

## How to use this matrix

Each test is **NOT_RUN**, **PASS**, **FAIL**, or **NOT_APPLICABLE_WITH_REASON**.
Use **STALE** when its tested inputs change. A pass requires real observations,
artifact identity and a reviewer/method. "Script written", provider success,
existing file, screenshot path and self-assessed confidence are not acceptance.

Defaults below are proposed starting engineering criteria for future candidates.
Record their adoption or a justified per-asset alternative at G0; do not present
them as previously owner-approved global budgets. Artistic acceptance always
includes actual visual/listening review. User-approved exceptions must identify
the use, tradeoff and affected measurements, not quietly erase a failed result.

## 1. Defaults and measurement boundaries

| Concern | Starting criterion | Required method / caveat |
|---|---|---|
| Source colors | Original accepted base-color files unchanged; no unauthorized tint/grading/emissive compensation | Hash source files and inspect material bindings/graph; rendered match is separately reviewed under G1 |
| Ground penetration | No sampled rendered surface below the intended floor by more than **0.05 cm** | Actual skinned vertices, world space, every relevant LOD; tolerance is numerical, not permission for visible sinking |
| Rest contact | Grounded sole/root contact visually planted; begin with **0–1 cm** clearance | Measure intended contact regions, not bone origins; hovering creatures use their approved hover envelope |
| Straight stance drift | Begin with **≤0.5 cm** horizontal contact drift over a stance interval | Actual surface contact plus actual world movement preferred; label nominal-path approximations and test turning separately |
| IK/deformation | No unexplained reach clamp, stretching, inverted joint, collapsed cross-section or major self-intersection | Full motion and transitions, not just a rest pose; rigid-region distances should remain stable within numeric tolerance |
| Runtime mesh | Start around **35k / 15k / 6k triangles** for LOD0/1/2 | Provisional ceilings inherited from Bellback planning; choose appropriate lower counts for simpler rigid assets; inspect and measure any exception |
| Textures/materials | Start with **2K**, ≤2 sets and ≤4 slots | Working budget, not minimum; actual appearance/overdraw/residency controls final choice |
| Frame time | Goal **1080p, 60 fps**, p95 ≤**16.67 ms** for the agreed test | Named PC, resolution/settings/build, warmup, sample count and capture exclusions; also report median, p99 and hitches |
| Crowd load | **20 visible moving creatures**, effects/audio, plus representative mixed roster | Exercise maximum actual deployment; full-detail stress and realistic automatic-LOD run have different purposes |
| Audio delivery | 48 kHz PCM WAV; preserve original-rate source | Mono for positional one-shots by default; use stereo deliberately; no lossy re-encoding loops |
| Audio headroom | Zero digital/export-clamp clipping; start at ≤**−3 dBFS peak** for delivered one-shots and actual crowd mix | Additional headroom is welcome; no fixed LUFS for every short effect; listening and in-game balance remain required |
| Repetition | Several usable variants for frequent cues; no rapid identical machine-gun repetition | Review at actual action density; exact count chosen per sound family, not generated to meet a quota |

Ground/contact checks cover the tested flat board. They do not certify arbitrary
terrain, collision stepping or every possible live trajectory. Foot locking must
also survive real starts, stops and turns. A shader that hides feet is not a fix.

## 2. Stage evidence matrix

| Stage | Minimum evidence | Who can conclude what |
|---|---|---|
| G0 intake | Actual ID/profile/source hashes, task scope, tools, existing approvals/jobs, budgets, ownership | Operator confirms scope and readiness; no art acceptance |
| G1 shared look | Preserved maps, Meshy/reference image, unlit diagnostic, lit studio/board comparison, profile values/hash, costs | Technical reviewer checks fidelity; owner chooses exact visual profile |
| G2 references | Main/Left/Back/Right set and slot mapping, matched pose/colors/scale, per-view provenance/hash, finite parts and rigid/flexible/contact map, supplemental hidden surfaces | Owner approves exact four-view construction and color direction |
| G3 source | Four-image submission evidence for new geometry; original provenance for accepted-source refinement; preserved downloads/receipts, per-view comparison, optimized counts/UV/maps, clay captures, hard-pose probe, defects | Reviewer checks source usability; owner approves exact forms/color |
| G4 rig | Hierarchy/rest/weight/rigid-region contract, controls/sockets, stress poses, saved/reopened assets | Technical and visual reviewer establish rig/skin behavior; not a full motion pass |
| G5 motion | Clip inventory, events/transitions/cancel map, continuous video/frame sequence, actual surface measures, ground/hover tests | Technical and visual reviewer establish motion behavior; final owner motion choice at G8 |
| G6 audio/VFX | Rights and original hashes, edits, variants, actual event logs, screenshots/mix recording, sample analysis, listening | Technical checks and human listening are separate observations |
| G7 game | Correct asset import/bounds/selection, both orientations, mixed/crowded scenes, LOD checks, hardware timings, reimport, launched package/regressions | Scoped engine/package acceptance; no implicit remote/human/multiplayer approval |
| G8 final | Exact manifest/build hashes, evidence and limitations, owner's actual appearance/motion/sound decision, source package/launch/rollback | Complete only for the explicit accepted use |

## 3. Rig and movement test inventory

Before new geometry in G3, use the [four-view checklist](FOUR_VIEW.md): no missing required slot,
unreviewed inferred surface, mirrored asymmetric side, mixed pose or silently changed
image. Verify the actual UI previews or transmitted input mapping against the saved
set. Failed reference consistency reopens G2. Four-view input count does not pass
anatomy, topology, rig or material-map checks. Preserve prior accepted candidates.

For grounded creatures, test every contact independently, all contacts planted with
body shift, maximal intended stride, elbow/knee bend extremes, head/tail motion,
start/stop, left/right turns, attack windup/contact/recovery, ability release/cancel,
hit interruption, defeat and transitions into/out of valid states.

For flexible vines/fins/roots, additionally inspect every chain at maximum curvature,
attachment seams, overlapping petals/tentacles, silhouette and fast-motion clipping.
For rigid assemblies, test rigid-distance preservation and neighboring part clearance.
For hoverers, test minimum/maximum hover height, bank/turn envelopes and ground shadow.

Sample all required animation frames and representative blends at each actual LOD.
Record source time/frame rate and blend parameters. Include bone/control overlays
where useful, but judge the rendered/skinned surface as well. Do not silently ignore
vertices below the floor because they are not part of the chosen foot mask.

Measure selection/culling bounds through the full pose envelope. Test both teams,
occluded/overlapping creatures, tall upper-body clicks, empty-cell placement and
combat order restrictions. Label synthetic ray/handler tests separately from actual
mouse/keyboard/Slate interactions.

## 4. Event tests that must not be replaced by attractive playback

- Basic attack anticipation may precede release. Impact follows the actual resolved
  target/time; do not claim damage from a contact animation alone.
- Track action/event identity to avoid duplicate cues on repeated ticks or replay.
- Cancellation before release stops pending anticipation/success cues. Already
  released projectiles/queued effects follow the actual runtime contract.
- Show/hear effective healing separately from an attempted pulse with no healing.
- A lane attack can hit an interceptor; endpoint follows the real hit.
- Damage and successful displacement are distinct results for Reefglass.
- Preserve Prism's actual ordered beam events and interruption semantics; don't
  schedule beam two solely from an animation timer.
- Locomotion contacts follow distance/phase and actual travel; no footsteps while
  idle merely because the previous clip is still blending.

Compare actual combat signatures or equivalent authoritative-state evidence against
the unchanged control. Art changes may not change outcomes, stats or authority.

## 5. Performance and audio capture procedure

Record actual CPU/GPU, RAM/VRAM where measured, engine/build, renderer, resolution,
graphics/scalability, frame cap/VSync, camera, actor/triangle counts, effects,
audio voice count, warmup and duration. Include startup/streaming behavior separately
from steady state. Retain raw rows and explain exclusions instead of hiding slow frames.

Use an unrecorded game run for primary frame-time evidence. Capture screenshots or
audio in separate runs when practical; if screenshots affect timing, flag those rows
and recovery intervals, retain them and state exactly which summary excludes them.
Do not run a heavy editor build/render/model generation concurrently with the timed run.
Do not use NullRHI, disabled sound or an artificial fixed timestep to claim normal play.

Capture the game's own master submix for mix review, not microphone or other desktop
audio. Validate PCM, nonzero content, expected duration, export-clamp and sample
clipping, then listen. A silent valid WAV or a short WAV that omits silent intervals
fails. Keep any diagnostic focus/submix overrides scoped to that recording process.

## 6. Bellback evidence: useful example, bounded claims

The [accepted Bellback packet](../../reports/bellback-production-20260920/README.md)
records 4,767 gameplay skinned poses, 241 Control Rig poses, three LODs, twelve
controls, actual packaged event/selection checks, original sound and owner approval.
Its final performance run was **1600×1000**, not a 1080p qualification. Its control
count and 0.6469 cm minimum gameplay clearance are measured results for that mesh,
not requirements to copy into another creature.

It exposed important failures: rear-shin penetration, blend-induced foot dips,
LOD-reduced soles, shadow-only editor captures, muted/short audio recordings and
clipped crowd audio. Use its methods to catch analogous defects; do not transplant
its numerical corrections into a different skeleton.

## 7. Failure, exceptions and signoff

Open critical/major defects block the affected stage. Describe the visible effect,
reproduction pose/event, attempted fix and matched evidence. A cosmetic minor issue
can be accepted only with actual reviewer/owner agreement for the stated use.
Do not relabel unreadable faces, broken articulation or missing sounds as minor
merely to finish. Two failed corrections trigger a method review.

For final review, show the concrete asset in the actual game, continuous movement,
editable rig study and audible mix. Ask for one exact-candidate decision covering
appearance, motion and sound when those are ready together. Explain any truly
unexecuted required check before requesting acceptance. Do not ask the owner to
approve a vague promise of future work.

Save the actual words and file hashes. If the owner requests revision, keep the
accepted parent and record the targeted change. If they accept, record completion
for that candidate and use; do not leave contradictory 'approval pending' labels
in the current handoff. Preserve historical reports as historical evidence.
