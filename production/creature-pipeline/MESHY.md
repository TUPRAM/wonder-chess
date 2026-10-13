# Meshy source production — G0, G2 and G3

**Version 1.3 default:** new creation includes color, PBR and rigging in one
animation-ready delivery. Follow [ANIMATION_READY.md](ANIMATION_READY.md). The
provider may require sequential jobs; use one bounded approved batch scope.

**Version 1.2 amendment:** apply [G3A/B/C](ENGINEERING.md) independently: construction
and part inventory → temporary deformation/wireframe review → UV and detail transfer.
Meshy optimization is not a substitute for deformation topology. Use qualified
Unreal local repair/UV/baking on candidate copies where needed. Preserve high-detail
source, exact accepted colors and any traceable resampled derivative separately.

## 1. Preconditions and delivery target

Read the hero's entry in [CHARACTER_BRIEFS.md](CHARACTER_BRIEFS.md), the active
catalogue and [VISUAL_STANDARD.md](VISUAL_STANDARD.md). Identify whether the request
is planning, a bounded generation, refinement, rigging or final integration.
Access to a subscription/API is a capability, not an unlimited generation budget.

Deliver an accepted, preserved Meshy visual source with usable optimized geometry,
UVs/maps, a rigid/flexible part plan and an early deformation test. Meshy's job
completion alone does not establish production topology, animation or game readiness.

## 2. Reconcile references before generation

**Default: use Meshy's four-view feature for one creature.** Follow
[FOUR_VIEW.md](FOUR_VIEW.md) to prepare and approve Main/front, anatomical Left,
Back and anatomical Right as four separate files in one consistent pose. Record
the exact set and slot mapping in [view-set.json](templates/view-set.json).
This applies to new geometry; preserve already accepted models during refinement.

Create a construction sheet/record with:

- Full-body Main/front, Left, Back and Right inputs. Keep three-quarter, underside,
  open-jaw and internal-construction views as supplemental review material, not
  mismatched-pose slot inputs. Label newly inferred views as proposals requiring
  review; do not call them exact source crops. Do not mirror asymmetric sides.
- One part inventory: count legs/roots, toes where defined, jaws/petals, pipes,
  floating elements, fins/tentacles and attachments. Mark intentionally asymmetric
  features by the creature's anatomical left/right, not the viewer's left/right.
- A rigid/flexible map: what rotates as one solid part, what bends and what moves
  independently. Show required gaps for opening jaws, petals and appendages.
- Proposed dimensions, ground-contact/hover envelope and intended board-camera
  size. These are an art contract separate from the logical cell footprint.
- Neutral import/rest pose and the first difficult test pose. A nonhumanoid does
  not need to be forced into a humanoid T-pose. Spread contacts enough for separation
  while preserving the approved creature silhouette.
- The accepted color reference, or a clearly labeled first texturing proposal.
  Preserve bright Meshy colors; do not introduce a competing recolor palette.

Review every image for consistent anatomy, branch side, scale and component count.
Prism's old inconsistent sheet cannot become generation input merely because a PNG
exists. For Reefglass, separate geometry design from the later material decision.

**G2 gate:** show the exact four-view set and inventory, obtain the owner's actual construction
decision, and hash those inputs. Existing scoped approval is sufficient when the
same inputs are unchanged. Prepare local inputs and a concrete job before asking
for any missing external upload/credit authorization.

## 3. Generation request packet

Populate [generation-receipt.json](templates/generation-receipt.json) before sending.
Record the provider/model/version shown, operation, source hashes, prompt/settings,
authorized quantity/cap and actual pricing evidence. Unknown provider fields remain
null with an explanation; do not invent a seed, negative-prompt field or determinism.
Attach the accepted view-set record/hash and actual image hashes, slot order and
preflight preview. Review any Meshy-generated missing views before the 3D job.

Prompt structure, adapted to the actual supported interface:

```text
[Stable character identity and full-body silhouette from approved reference].
[Exact rigid parts, moving parts and asymmetric feature].
[Neutral pose, visible separation and articulation clearances].
[Existing accepted Meshy/reference color direction].
Single complete creature, no scenery, display pedestal, labels or extra props.
[Only supported constraints essential to this character].
```

Do not paste a long contradictory list of anatomy synonyms. Reference priority and
finite construction are more useful than requesting generic "ultra detail".
If an endpoint has no negative-prompt option, do not submit an invented parameter.

### Interface and submission

Use the verified project Meshy connector/API for supported operations, or the
website for features unavailable there. Keep the current website/API distinction:
an advertised website capability does not prove the API exposes it.
Use the four-slot website route, or an actually supported multi-image operation.
An MCP command accepting only one image is not an equivalent route. See the exact
website/API mapping in [FOUR_VIEW.md](FOUR_VIEW.md); do not submit four separate
single-image models or silently drop auxiliary inputs.

Before submission, verify authentication with a read-only request and inspect any
existing job. Keep secrets in the existing encrypted local credential store; never
put them in a prompt, checked-in file, screenshot, log or shared URL.

Submit one authorized initial colored/PBR candidate with optimization when
supported; a geometry-only job is an explicit experiment, not the new default.
Record the returned task ID and
submission time immediately. If a call times out or returns an ambiguous failure,
query/list the existing task before creating another. Poll with bounded backoff.
If allowance is insufficient, report the exact deficit; do not buy credits or switch
to another paid service. Reuse authorized unchanged inputs for safe reads/downloads.

## 4. Download and preserve before processing

After actual success, download the original model and every available relevant
texture/export/preview while provider links are valid. Keep an original GLB even
when FBX is the engine transport. Save the full usable bundle before relying on a
bridge or a browser preview. Record sizes and SHA-256; verify files decode/import.

Suggested task folder:

```text
inputs/meshy/<generation_id>/
  input-images/
  request.json                 sanitized actual request
  generation-receipt.json
  raw-model.glb
  exports/                    original FBX if supplied
  textures/                   original source maps
  previews/                   provider and actual inspection captures
```

Original means untouched bytes, not a re-export that happens to look similar.
Later remesh/retexture/rig output receives a separate job folder and parent hash.
Do not overwrite a failed source; it explains why the next candidate exists.

## 5. First model review — before spending on polish

Inspect the new colored model in both neutral/clay and textured shading at full
body and close range. Record missing maps as missing, not passed. Explicit older
geometry-only experiments retain their actual untextured status. Review:

1. Does the silhouette read as the intended hero under the game camera?
2. Are the face/eyes/muzzle or central feature actually constructed, not painted
   onto a flat or broken surface?
3. Are all approved limbs/roots/parts present, separate and on the correct side?
4. Can jaws, petals, elbows, roots, fins and floating parts move without starting
   already fused or deeply intersecting?
5. Do rocky ridges, ceramic pipes and shells have meaningful rigid regions?
6. Are the back and underside coherent? Are stray fragments, holes, internal debris,
   flipped normals or duplicate surfaces likely to break rigging/rendering?
7. Do colors match the selected source, including material boundaries and seams?

Compare matched views against all four accepted inputs, then inspect the underside
and interior separately. Record which view exposes each mismatch. Four submitted
images are input evidence, not proof that the generated body matches them.

Classify defects with images and the affected pose/view. Attractive textures do not
override an anatomy failure. A repairable weight issue can proceed to a small rig
probe; fused geometry that prevents the required motion needs a source correction.

## 6. Optimize, UV and texture without losing identity

Default dependency sequence is **geometry → remesh → UV layout → texture → rig**,
completed within one new-creation task. Request geometry/remesh/PBR together when
the provider supports it; this does not remove their individual technical checks.
If an existing approved colored model is being optimized, preserve its original
maps and compare texture transfer. If optimization changes UVs, textures need a
verified compatible transfer/rebake or a new reviewed texture candidate.

Start with the provisional budgets in [ACCEPTANCE.md](ACCEPTANCE.md); inspect actual
output counts, not just the requested number. Triangle or quad-dominant topology
is an option, not evidence of good joint loops. Remeshing is not guaranteed to
separate fused parts or preserve every ornament.

Keep a higher-quality original for comparison. Compare the reduced result at the
same camera, both close up and gameplay scale: eyes, outline, jaw edge, paws/roots,
bell/pipe rims, fins and attachment clearance. Inspect the difficult bending region.
Increase/decrease density only to address observed quality/performance needs.

Begin with 2K texture maps as a working default. Generate/reference-guide the
initial material only when needed and within the authorized job scope. Preserve
the accepted base color after that review. Check map channels, seams, back,
underside, material separation and any baked shadow. A color mistake needing
retexture returns to visual review; it is not silently painted away in Unreal.

Prefer the accepted four-view color set for multi-view texturing when supported.
Verify actual texture inputs; API geometry references and texture references are
independent. The current website multi-view texture description covers base color
only, while API options differ. Inventory delivered PBR maps and follow the
[material-map distinction](FOUR_VIEW.md) before claiming full material delivery.

## 7. Initial rig and difficult-pose probe

Choose from the actual available Meshy routes:

- Quadruped for Cragstoat if its long spine and contacts are supported.
- Smart/custom route for unusual roots, vines, fins or floating assemblies when
  useful. A rigid component-based Unreal rig may be the simpler route for Prism.
- Humanoid only if the accepted actual anatomy warrants it; class labels such as
  Healer/Mage do not imply a humanoid skeleton.

At the documentation check on 21 September 2026, Meshy quadrupeds support a walk;
Smart Rig exports do not support its animation library. Verify current behavior
before the batch. Plan the complete custom motion set in Unreal regardless of
whether a starting clip is supplied.

Import the rigged output into an isolated Unreal candidate and inspect bone
hierarchy, weights, scale, rigid-region behavior and the character's hardest pose.
Examples: Cragstoat spine/tail during lunge, Root planted roots during torso shift,
Snapvine open jaw plus curved lash, Prism rigid pipes, Reefglass fin/shell clearance.
An empty animation export can still be a useful starting skeleton; label it honestly.

Do not re-rig after UV/weights/animations are locked without a new revision and
dependency revalidation. Do not assume a new Meshy run preserves vertex order,
bone names, topology or texture layout, even with an identical prompt.

## 8. G3 review and failure decision

Present the exact optimized textured model, source comparison, clay views, hard-pose
probe, dimensions, observed counts, defects and generation cost. Obtain forms/color
approval in the combined forms/color/rig review authorized by version 1.3. Prepare
the isolated production rig and inspection study before that review when technically
usable; full animation work follows acceptance. Clearly distinguish source approval
from rig verification and preserve unresolved defects.

| Observed problem | Next action |
|---|---|
| Wrong silhouette/part count | Return to construction/input review; new bounded geometry candidate |
| Fused jaw/limbs required to separate | Source correction/remesh option only if demonstrated; otherwise regenerate |
| Good geometry, poor weights | Preserve mesh and correct weighting/controls in Unreal |
| Good model, wrong colors | New scoped Meshy texture candidate and review; no hidden Unreal tint |
| Same critical defect after two attempts | Method review using before/after evidence; stop spending on the failed approach |
| Tool/model capability missing | Record blocked operation, choose authorized supported route, continue independent work |

When G3 passes, freeze geometry/UV/map hashes and hand off to
[UNREAL_RIG_AND_VALIDATION.md](UNREAL_RIG_AND_VALIDATION.md). Use the same candidate
identity throughout, with a new revision when a dependent source changes.

## Official capabilities — checked 21 September 2026

- [Rigging guide and specific limitations](https://help.meshy.ai/en/articles/16231707-how-to-create-3d-animation-with-auto-rigging).
- [Remesh API](https://docs.meshy.ai/en/api/remesh): target count is approximate; topology choices do not certify deformation.
- [Retexture API](https://docs.meshy.ai/en/api/retexture): inspect current reference/map parameters and account pricing before use.

Use current endpoint documentation when building a request. These links do not
authorize a job, establish account entitlement, or prove the model will match the art.
