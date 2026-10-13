# Wonder Chess creature production handbook

**Version 1.3 — colored, textured, animation-ready delivery, 21 September 2026.**

New creature creation now delivers color, PBR textures and an inspectable rig
together. Follow the [animation-ready contract](ANIMATION_READY.md): prepare an
isolated G3/G4 candidate for one combined review, retaining separate technical
checks. This owner amendment supersedes earlier geometry-only-first delivery and
intermediate forms-approval sequencing for this scope. Full animation, audio and
packaged game acceptance remain additional stages.

Use this handbook to produce a Wonder Chess creature through **Meshy → Unreal**,
including materials, rigging, animation, sound, effects and a packaged game review.
The owner requested this durable workflow after accepting the Bellback production
candidate and then choosing unchanged Meshy colors and softer game lighting.

This version adds repair, deformation, UV/bake, revision and recovery procedures,
working local validators and qualified tool connections. A neutral reference studio
is an isolated calibration candidate. The actual-board lighting and five new
creatures still need their production and review stages; no new service spending
is authorized by this handbook.

## Read only the part needed for the current stage

| Document | Use it for |
|---|---|
| [This handbook](README.md) | Authority, stage order, ownership, records, resume and completion |
| [Visual standard](VISUAL_STANDARD.md) | Exact color-preservation rule and lighting comparison procedure |
| [Meshy procedure](MESHY.md) | References, generation, preservation, optimization, texture and first rig |
| [Four-view inputs](FOUR_VIEW.md) | Main, Left, Back and Right preparation, consistency review and submission |
| [Character briefs](CHARACTER_BRIEFS.md) | Construction, motion and sound decisions for the five named creatures |
| [Unreal procedure](UNREAL_RIG_AND_VALIDATION.md) | Import, controls, deformation, runtime events and package checks |
| [Audio procedure](AUDIO.md) | Free AI options, rights, prompts, editing, import and listening |
| [Acceptance matrix](ACCEPTANCE.md) | Required evidence, default thresholds and failure handling |
| [Templates](templates/README.md) | Copyable candidate, generation, map, cue, review and handoff records |
| [Production engineering](ENGINEERING.md) | Full Mermaid, G3A/B/C, cameras, construction, topology, bakes, rig families, budgets and recovery |
| [Qualified toolchain](TOOLCHAIN.md) | Actual app connections, tested commands, limits and requalification |
| [Animation-ready contract](ANIMATION_READY.md) | Default new-creation outcome, combined review and bounded batch budget |
| [Texture development](TEXTURE_DEVELOPMENT.md) | Initial PBR delivery, preserved source maps and future texture revisions |
| [Skill roadmap](SKILLS_ROADMAP.md) | Available specialist skills, proposed additions and responsibilities |
| [Reusable Codex skill](../../.agents/skills/wc-creature-production/SKILL.md) | Future task entry point |

## 1. Authority: what is fixed and what is still a proposal

1. The owner's latest explicit request controls task scope and overrides older
   workflow preferences. Preserve approval already given for the same unchanged
   candidate; do not request it again simply because a new session starts.
2. [Project instructions](../../AGENTS.md) and
   [successor contract](../../docs/vnext/README.md) retain gameplay authority.
   [data/vnext/catalog.json](../../data/vnext/catalog.json) owns IDs, abilities,
   timings and numbers. This handbook does not create another gameplay catalogue.
3. This handbook is the route-specific amendment for these owner-selected
   Meshy-to-Unreal creatures. **Blender is not a production dependency.** The
   approved Meshy download plus versioned Unreal sources/recipes replace the older
   AS1 assumption that editable geometry/skin must live in a `.blend` file.
4. [AS1](../asset-studio/docs/00_SYSTEM.md) still supplies ownership, provenance,
   technical/visual/human distinctions, immutable evidence and review discipline.
   Do not alter its historical ledger to claim that an old rejected candidate passed.
5. Explicit design approval applies to the exact referenced revision. Numeric
   defaults in this handbook are engineering starting criteria, not measured
   results, approved final anatomy, or promises of quality.
6. Provider features, prices, licenses and account allowances are dated observations.
   Recheck the relevant official source before first use in a new production batch
   and whenever the model, provider terms, account plan or environment changes.

### Fixed owner choices

- Preserve the accepted Meshy base-color textures and palette. No added tint,
  saturation adjustment, repaint, baked highlight or blanket emissive brightening.
- Achieve readable light colors through shared, soft game lighting.
- Team identity uses rings/labels/UI; it does not recolor the creature.
- Meshy creates the visual source; Unreal completes and verifies production.
- Krita is the owner-selected default for precise reference scaling, padding and
  sheet assembly. Preserve original art/colors and save editable `.kra` sources
  plus the four separate PNGs. This choice does not approve redesigned anatomy.
- New creature geometry uses an accepted four-view set: **Main/front, anatomical
  Left, Back and anatomical Right**. Review any inferred views before submission;
  do not silently fall back to one image. Preserve already accepted models.
- Give each anatomy its own rig. Reuse tooling and checks, not Bellback's bone
  indices, scale, sole offsets, shapes or animation as a universal template.
- Grounded creatures keep appropriate contacts; hovering creatures have explicit
  hover height and ground-shadow treatment.
- Preserve originals and earlier accepted candidates. New output is a new revision.
- Gameplay owns movement and effects. Animation/sound depict events; they never
  decide damage, healing, hit targets, displacement or resource gain.

### Current baseline and boundaries

Bellback's accepted implementation is recorded in
[the six-point packet](../../reports/bellback-production-20260920/README.md) and
[exact owner acceptance](../../reports/bellback-production-20260920/owner-acceptance.json).
Its technical evidence is reusable as an example. Its material tint/emissive
recipe is **superseded for the new color standard**; do not run that recipe on a
new creature. Preserve Bellback's accepted files while testing the new look in a copy.

The five other heroes have canonical briefs and existing design material; none
receives a new 3D, material, rig or sound approval from adoption of this handbook.
The actual-board softer lighting profile and free AI sound provider remain to be
tested. Audacity's local editing/export route and the supporting apps have now been
exercised; see the [qualification packet](../../reports/pipeline-tools-20260921/README.md).

## 2. Stage map and dependency order

| Stage | Inputs | Work and concrete output | Exit condition / next stage |
|---|---|---|---|
| **G0 — Intake** | Current request, canonical hero, prior records | Candidate identity, owner, intended use, actual tools, budgets, source hashes, permissions and next operation | Scope and dependencies understood; unresolved required decisions named |
| **G1 — Shared look** | Preserved Meshy material and Bellback copy | Side-by-side Meshy/reference, diagnostic base color, neutral studio and actual-board captures; saved lighting profile | Owner accepts exact shared look; may be reused unchanged by later creatures |
| **G2 — Construction references** | Canonical identity, character brief | Main/Left/Back/Right set, slot/provenance record, finite parts and rigid/flexible/contact map; supplemental hidden-surface evidence | Owner accepts exact four-view construction set before model generation |
| **G3 — Meshy visual source** | Existing G1 profile/comparison, accepted G2 views, scoped batch budget | Multi-view colored/PBR generation, optimization, preservation and independent G3A/B/C checks | Technically usable candidate proceeds to G4; combined forms/color/rig owner review |
| **G4 — Production rig** | Technically usable stable G3 geometry/UVs/maps, rig probe | Named skeleton, weights, rigid regions, controls, sockets and cold-reopen pose study | Technical/visual checks plus combined owner review establish animation-ready handoff |
| **G5 — Motion and events** | G4, current runtime contract | Required clips/transitions, movement mapping, event/cue sheet, actual skinned tests | Movement and event behavior pass; motion available for final human review |
| **G6 — Audio and effects** | G2 identity; G5 timing for final integration | Licensed original layers, variations, cues, actual game mix and effects evidence | Numerical/event checks and listening review complete; human acceptance at G8 |
| **G7 — Game validation** | G1, G3–G6 | LODs, board review, selection/bounds, reimport, mixed and crowded performance, packaged executable and regressions | All checks required for the stated use pass; precise limitations recorded |
| **G8 — Acceptance and delivery** | Exact G7 package and complete evidence | Owner's actual decision, immutable hashes, launchers, editable sources, rollback and status | Owner accepts exact appearance/motion/sound; deliver scoped completed candidate |

G1 is a collection-level dependency, not five separate lighting inventions. G2
planning and small sound auditions may run while G1 is being reviewed. G6 source
research/auditions may run alongside G3; final synchronization depends on G5.
Temporary rig stress tests expose bad geometry early. Version 1.3 also permits
preparing the isolated full G4 rig before combined review; known unusable or
owner-rejected forms still require correction before dependent work.

The new four-view G2/G3 requirements apply to new geometry. Refinement of an already
accepted source retains its actual original input provenance and existing approvals;
do not demand a retroactive four-image submission or regenerate it. Reopen only the
checks affected by the requested refinement.

### AS1 correspondence

G0 maps to brief; G2 to references; G3 covers blockout/forms/topology/UV/material
observations; G4 covers rig/skin; G5 covers motion; G6 adds the audio/VFX route;
G7 covers optimization/engine; G8 records exact-candidate owner acceptance.
Combined authoring operations do not collapse their evidence into one automatic pass.

Within G3, record **G3A construction**, **G3B topology/deformation** and **G3C UV/bake**
independently using [ENGINEERING.md](ENGINEERING.md). A beautiful texture, reduced
polygon count or auto-rig success cannot substitute for these checkpoints. G7 includes
a deliberate revision, cold reopen and fresh recovery before the final G8 decision.

Use AS1's report templates/ledger when the configured route supports the actual
artifacts and dependencies. If an older route insists on Blender artifacts, record
the owner-selected route amendment and the G-stage evidence rather than inventing
files, fabricating checks or force-editing accepted history. A local candidate
completion must not be labeled a full AS1/game release if those broader checks
have not run. Any later ledger adapter is separately tested tooling work.

## 3. Start/resume procedure — same steps every session

1. Read this page, current user scope and the asset's latest handoff. Open only the
   relevant stage manual and direct dependencies.
2. Find the exact hero ID in the current catalogue; read the active runtime profile
   and existing art manifest. Inspect pending revisions and preserve the dirty tree.
3. Verify paths resolve under this project. Never resume an old absolute worktree
   path from historical reports. Check the installed UE/tool versions rather than
   assuming the recorded versions still exist.
4. Read the latest candidate record, parent hashes, approvals, failures and jobs.
   Compare actual source hashes before accepting its status. A changed dependency
   makes affected evidence stale, even when an `accepted` label remains in JSON.
5. Check running editors, provider jobs and file ownership. After timeout, inspect
   output and task status before retrying. Never repeat a paid POST on uncertainty.
6. Name the next smallest meaningful operation and its expected evidence. Do it
   within existing authorization; ask only for missing decisions/rights/spend that
   truly block it. Continue independent authorized work while waiting.
7. Save results, actual commands, logs, hashes and a precise handoff. A missing
   tool blocks its check, not unrelated work. Do not label scripts as executed art.

## 4. Candidate layout and names

Use stable catalogue IDs and zero-padded revisions. These are folder conventions,
not instructions to create every empty directory in advance.

```text
art-source/asset-studio/<asset_id>/
  asset.json                         existing art manifest; preserve history
  inputs/references/four_view_r001/   four images, view-set.json, review/supplemental evidence
  inputs/meshy/<generation_id>/       images, original GLB/FBX/maps, receipt
  inputs/audio/<provider>/<job_id>/   original audio, prompt, terms/provenance
  stages/production_r001/
    candidate.json                   copy of the candidate template, populated
    construction.md                  parts, views, rigid/flexible/contact map
    skeleton.json                    measured names, parent/rest transforms
    material-map.csv
    animation-cue-sheet.csv
    audio-cue-sheet.csv
    recipes/                         scripts/presets specific to this candidate
    review.md
    handoff.md
reports/creature-production/<asset_id>/<candidate_id>/
  technical/                         measured results, commands and logs
  visual/                            actually reviewed images/continuous motion
  audio/                             samples and actual mixed recording
  approvals/                         exact words, scope, time and hashes
game/Content/WonderChess/VNext/Characters/<Name>_r001/
game/Content/WonderChess/Diagnostics/<Candidate>/   editor-only study assets
builds/<descriptive-new-build-name>/               independently launched build
support/archives/<dated-candidate-backup>/
```

Paths in records should be repository-relative with `/`; Unreal asset paths use
`/Game/...`. Credentials stay in the existing user-encrypted local store, outside
project records. Signed download URLs can contain credentials: preserve task ID,
sanitized response and original bytes; redact tokens/signatures from shared receipts.

Never use `latest` as the sole identity of approved art. A convenience latest pointer
must resolve to an immutable candidate and manifest hash. Give every clip, material,
sound and skeleton a deliberate name and record its real imported asset path.

## 5. Ownership, cost and retries

- Assign one writer per creature rig family and Unreal binary; one operator per
  editor session. Parallel workers may inspect snapshots or author separate text,
  sound-source or character files. Shared materials/schema have one named owner.
- Production authorization does not imply unlimited paid generation. Record the
  accepted input, provider/operation, quantity, credit ceiling and task scope before
  submission. This handbook grants **zero new credits** by itself.
- A provider API key, subscription or historical Bellback cap is not new-job
  authorization. Honor current scoped approvals without asking for them again.
- Query existing jobs after network errors. Retry safe reads with bounded backoff;
  do not resubmit an uncertain charged operation until its disposition is known.
- Compare the largest defect before/after each revision. After two bounded attempts
  fail to improve a critical defect, change method or request a focused decision.
  Do not spend indefinitely, hide anatomy under textures or start rebuilding in Blender.

## 6. Approval, invalidation and promotion

Required owner review points are the shared look, construction/reference, final
forms/color and final candidate. A single explicit decision can cover multiple
clearly displayed gates; do not split it into repeated confirmation requests.
Record the actual user words, candidate/review identity, scope and artifact hashes.
Never generate the owner's opinion, signature or approval date.

| Changed item | Reopen affected work |
|---|---|
| Reference/anatomy | Forms, rig, UV/texture, clips and all derived review |
| Any four-view image/slot mapping | New view-set revision and G2 consistency review; affected G3 generation/comparison and downstream work |
| Topology or vertex order | Skin/UV compatibility, LODs, import, deformation and package |
| Skeleton/rest pose | Weights, controls, clips, sockets, import and package |
| UVs/maps/material logic | Color/material comparison, LOD materials, board captures and package |
| Shared lighting/exposure | G1 comparison and each affected creature's board visual review; performance if rendering cost changes |
| Sound source/mix | Rights if source changes; sound event/mix/listening and affected package |
| Gameplay event contract | Cue timing/cancel/target tests and runtime regression |
| Engine/importer/hardware | Relevant compatibility, rendering or performance evidence |

An unchanged approval remains valid for its original scope. New comparison work
does not revoke the old accepted package; preserve it as the rollback target.
After G8, promote only to the intended use authorized in the task. Review the exact
asset/reference/launcher change and back up previous content. Approval of a local
candidate is not authorization to publish, deploy publicly, or replace unrelated art.

## 7. Planned collection order and present next action

Shared look with a Bellback copy → Cragstoat → Grandmother Root → Snapvine →
Prism Organ → Reefglass. Resolve Prism's inconsistent construction references
before its generation. Test Reefglass readability/transparency before a full rig.

**Current scope amendment:** Cragstoat's r001 geometry trial remains preserved.
production_r002 uses a fresh colored, textured candidate from the accepted r003
views and owner-tolerated alignment. Meshy's website rig failed without a credit
deduction; the Unreal fallback rig passed the bounded contact/control study and
FBX reimport. Existing G1 comparison evidence
can inform its combined review; no G1 approval is invented. Consult its latest
handoff for actual execution and budget status rather than treating this text as
evidence that generation or rigging has run.

## 8. Future requests that reliably invoke this workflow

> Use $wc-creature-production for Cragstoat. Read its handoff and resume the first
> incomplete stage. Preserve Meshy's accepted colors, use the approved shared
> lighting, keep Blender out of the route, and report the exact candidate and evidence.

New geometry follows the accepted Main/Left/Back/Right view set automatically under
this workflow. A request to optimize an already accepted source does not regenerate it.

For planning only, add: "Plan/document only; no generation, uploads, installs,
engine changes or spending." For a paid job, state the exact input and credit cap.
For a revision, identify the candidate and visible defect; keep other accepted work.

## 9. Definition of delivery

Deliver the preserved raw source, editable Unreal asset/rig and recipes, textures,
clips, original/processed sound provenance, event mapping, LODs, verified executable,
review evidence, actual owner acceptance, hash manifest and working launch path.
State any scoped limits plainly. A completed creature is not proof of the entire
roster, game pacing, other hardware or multiplayer readiness.

## 10. Maintain the handbook

After editing the handbook, skill or record templates, run this read-only check
from the repository root:

```powershell
& .venv/Scripts/python.exe tools/production/validate_creature_pipeline.py
```

It checks local document links, required manuals and unfilled templates, including
their lack of default approvals and spending. It does not validate a live creature,
external provider terms or game behavior. Save its result with the documentation
revision. Keep each live candidate pinned to the handbook version and hash used;
record relevant later changes and reopen affected checks rather than silently
rewriting its production history.

### Version history

- **1.3 (21 September 2026):** owner-requested colored/PBR/rigged first delivery;
  combined isolated G3/G4 review, dedicated rigging skill, animation-ready contract,
  future texture development and game-production skill roadmap. No new spend is
  granted by this documentation change.

- **1.2 (21 September 2026):** owner-supplied engineering review adopted; G3A/B/C,
  construction/cameras, UV/bake, expanded budgets, deliberate revision/recovery,
  local validators and app qualification. See the dated tool evidence packet.

- **1.1 (21 September 2026):** owner-requested Meshy four-view default; dedicated
  input manual, slot/provenance template, character checks and geometry/texture
  interface distinction. No images or models generated by this update.
- **1.0 (21 September 2026):** initial preserved production handbook and skill.
  Its validation snapshot remains historical evidence for that version.
