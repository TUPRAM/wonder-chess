# Character production briefs — first five after Bellback

**Pipeline version:** 1.1. **Authored:** 2026-09-21. **Status:** reusable production instructions; character outputs and open construction decisions are not approved by this document.

Use this manual with the [pipeline entry point](README.md). It records how the five creatures differ; it does not replace the shared production gates or create a new gameplay authority.

## 1. Authority, order and common requirements

The [canonical catalogue](../../data/vnext/catalog.json) controls identity, mechanics, targeting and numbers. The [generated dossiers](../../docs/vnext/generated/hero_dossiers.md) are convenient reading. Read current values at the start of every candidate and preserve a dated source snapshot/hash with it. Do not copy damage, speed, cooldown or ability timing into a separate authoritative spreadsheet or animation constant.

| Order | Character / stable ID | Canonical body family | Canonical identity and ability |
|---|---|---|---|
| 1 | Cragstoat / `wc_vn_cragstoat` | `elongated_quadruped` | Beast / Warrior; Stonebound Lunge (`momentum_charge`) |
| 2 | Grandmother Root / `wc_vn_grandmother_root` | `root_walker` | Plant / Healer; Stay and Blossom (`stationary_grove`) |
| 3 | Snapvine / `wc_vn_snapvine` | `creeping_vine` | Plant / Assassin; Thornline (`screened_strike`) |
| 4 | Prism Organ / `wc_vn_prism_organ` | `floating_assembly` | Construct / Mage; Crossing Hymn (`crossing_beams`) |
| 5 | Reefglass / `wc_vn_reefglass` | `cuttlefish` | Tidekin / Controller; Leading Tide (`tidal_push`) |

**Before order 1:** approve the common soft-lighting comparison using Bellback and its original Meshy colors. Sound auditions may run alongside design review. Each model must pass its own construction/forms gate before dependent rig production. Rig stress tests precede complete animation and sound polish.

### Rules inherited by every brief

- Meshy supplies candidate geometry, optimization and textures; Unreal supplies production controls, corrections, motion and integration. Do not introduce Blender work.
- Preserve the exact accepted Meshy base-color files, hashes and palette. No creature/team tint, saturation adjustment, painted highlight or body-wide emissive brightening. Solve readability through the accepted shared lighting; declare material-specific effects separately.
- Use the [four-view input procedure](FOUR_VIEW.md): Main View uses the front; Left and Right show the creature's anatomical left and right; Back shows its rear. Decide appendage counts, attachments, underside, rest pose, moving clearances and rigid regions before generation. Generated view labels do not prove orthographic accuracy.
- Record one-cell occupancy, full bounds, ground/hover clearance and animation envelopes in the candidate brief. Values are proposed until measured and reviewed; do not silently inherit Bellback's dimensions, skeleton or joint counts.
- Preserve the untouched downloaded model, textures, generation settings and task IDs. A remesh creates a new candidate. Geometry/UV changes after skinning invalidate dependent weights, animation and texture evidence until rechecked.
- Test Meshy's available rig route on a disposable copy. A returned skeleton is a starting point; unsuitable anatomy proceeds to a deliberate Unreal rig, with a recorded reason. Never force every creature onto a humanoid or Bellback skeleton.

### Four-view consistency checks

Use one approved **Main View / Left / Back / Right** set, with the same full-body pose, proportions, jaw/petal state, colors and part inventory. Record each image's slot and anatomical side. Opposite views show genuine opposite surfaces: do not mirror asymmetric anatomy or decoration. A concealed part is occluded, not absent. Newly inferred hidden surfaces remain proposals until reviewed.

Keep three-quarter, underside, open/closed-jaw, interior and exploded details as supplemental construction evidence; do not substitute a different pose into one of the four generation slots. Four external images cannot resolve an unseen interior or certify true orthography. Use **approved construction counts**, not invented canonical counts: Cragstoat's quadruped body family establishes four legs, but toe, root, petal, tentacle and Prism component counts still require their own construction decision. This procedure grants no new reference, forms or generation approval.

| Character | Required correspondence across the four inputs |
|---|---|
| **Cragstoat** | Match muzzle length, spine curve, belly height, tail root/length and rocky ridge attachments. Track all four legs despite occlusion. Left/Right retain any approved unequal ridge pattern and anatomical side. Back resolves the same hindquarters and tail attachment without adding another face. Match the approved toe inventory. |
| **Grandmother Root** | Match support roots, branch attachments and garden opening. Left/Right establish cavity depth and rear wall; Back resolves trunk and garden support instead of repeating the front face or cavity. Flowers and asymmetric branches retain their parents and sides. Keep petals in the same state in every input. |
| **Snapvine** | Match vine anchors, coil direction, petal layering, jaw hinge and thorn arrangement. Use one jaw opening across the four inputs. Back resolves the rear flower and vine attachments rather than repeating the front mouth. Preserve any approved hooked-root asymmetry. Review other jaw states and underside separately. |
| **Prism Organ** | Track every indexed pipe, hoop, key, emitter and cradle, including occluded parts. Preserve pipe heights/order, emitter sides and glass-panel layout. Back resolves consistent rear attachments rather than copying the front. The four-view feature does not close PR-REF-001–005: reconcile those defects before submission. The earlier numerical inventory remains proposed. |
| **Reefglass** | Match shell shape/thickness, eye locations, fin attachments and approved tentacle inventory. Left/Right preserve designed asymmetry; Back resolves rear shell and fin joins without adding facial features. Internal currents remain consistent visible contents, not extra appendages. Use one fin/tentacle pose and comparable transparency across all inputs; material alternatives are separate candidates. |

### Required motion and event contract

Every character needs **Idle, Move, Attack, ability behavior, Hit, Defeat and Victory**, plus demonstrated start, stop, left/right turn, interruption and transition behavior. The tables below label ability behavior **Active** for convenience: all five require it, but a separate file named `Active` is optional. Behaviors may use separate clips or documented blends; none may disappear merely because seven files exist. The canonical runtime determines what the ability does and when. Provide an editable control study and clean baked playback without authoring controls.

Use [`VisualActions()` and actual combat events](../../game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp), with the existing [presentation layer](../../game/Source/WonderChessRuntime/Private/WCVNextCombatPresentation.cpp), to bind anticipation, release, travel, impacts and outcomes. Notifies may emit presentation; they never apply damage or choose targets. Deduplicate one-shots by action/event identity, including distinct pulse/beam occurrences. Distinguish an interrupted unreleased cast from packets already released: follow the simulation's remaining actions rather than cancelling every pending effect by assumption.

All sound descriptions below are **generation/recording briefs**, not selected providers, licensed outputs or accepted audio. Make dry isolated layers and variations; preserve prompts, model/license evidence, untouched outputs and edited WAVs. Avoid generating a single long action sound that cannot follow variable runtime timing.

## 2. Cragstoat

### Construction and first rig test

**Canonical:** a long, low predator, rocklike shoulder ridges, elastic expressive spine, rising tail and successive footfall sparks communicating momentum. Preserve predatory length without turning it into a short stocky Bellback variant.

**Resolve before generation:** muzzle/eye design; toe count and sole shape; shoulder-ridge count/attachment; tail length and root; spine rest curve; belly clearance; which rocks are separate rigid masses. Confirm all four legs separate in silhouette, readable elbows/hocks, and unobstructed joint gaps. These details are proposals until the reference pack is accepted.

**Moving:** spine, neck/head, tail, shoulders, hips and four limb chains. **Rigid:** each declared rock plate retains shape under its assigned driver. Weight transitions belong in organic regions, not through the middle of a rock.

Start with a verified quadruped rig candidate; provide root/body, articulated spine, four foot targets and bend-direction controls, head and tail controls. **First difficult test:** compress into a launch pose, extend through a lunge, then land and turn with planted paws. Check belly/ground clearance and rock intersections throughout, not just at endpoints.

### Motion and sound sheet

| Behavior | Animation and event-bound audio |
|---|---|
| Idle / Move / start-stop-turn | Alert breathing and tail; stalking walk with distance-matched steps; soft paw contacts plus occasional restrained stone ticks |
| Attack | Short readable strike; anticipation follows the basic attack action, contact follows actual impact; dry contact/stone layer only on the relevant result |
| Active | Momentum posture builds from actual state; committed lunge follows legal simulated movement, followed by recovery; separate push-off, rushing air, landing and damage-impact layers |
| Hit / Defeat / Victory | Compact recoil; low settled collapse with tail stopping; alert triumphant tail/body pose; short stone/body layers, bounded victory accent |
| Cancel | Relax the pending launch when the action is cancelled; no fabricated dash, landing or damage sound |

**Acceptance cases:** zero/accumulated momentum, open approach, blocked landing, target moved, quarter/half turns, repeated attacks and defeat during preparation. Verify stance contact at every LOD, no tail striking adjacent pieces, and unchanged combat signature with presentation enabled. Open decisions: gait character, rock inventory, muzzle, tail motion range and nonverbal voice/no voice.

## 3. Grandmother Root

### Construction and first rig test

**Canonical:** orchard elder walking on broad roots, sheltered garden in her torso; settling roots and opening petals announce positional healing. Preserve a readable elder identity and garden opening under the board camera.

**Resolve before generation:** support-root count and contact pads; front/back orientation; face placement; garden cavity depth and inner surfaces; branch/arm presence; petal inventory and hinges. Require separate broad roots, open garden space and visible attachment of flowers. Do not let the generator fuse soil, petals and face into one undifferentiated mass.

**Moving:** locomotion roots, trunk sway, expressive head and chosen branch/petal controls. **Rigid or restrained:** garden container/support structure; soil and small decorations follow declared parents without unsupported floating. Foliage motion must not obscure the face or telegraph.

Verify Smart Rig only as an initial candidate. Plan an Unreal root-walker skeleton around the accepted support count, with independent contact targets and body balance. **First difficult test:** shuffle one root, settle all supports, lower the body and open the garden while the rooted contacts remain stable.

### Motion and sound sheet

| Behavior | Animation and event-bound audio |
|---|---|
| Idle / Move / start-stop-turn | Gentle canopy movement; alternating root shuffle; lift before relocation, settle after stopping; wood, soil and leaf layers |
| Attack | Deliberate seed-release gesture consistent with existing seed projectile presentation; release rustle and separate actual hit sound |
| Active | Root-settle anticipation, opening petals, sustained grove pose; soft flowering layer and heal accents at actual resolved healing pulses |
| Hit / Defeat / Victory | Trunk recoil; garden closes into a stable resting pose; flowers reopen gently; restrained creak, foliage and warm tonal accent |
| Cancel / displacement | Retract only the pending/tethered presentation no longer supported by runtime; move roots with the displaced unit; stop invalid future healing accents |

**Acceptance cases:** wounded allies, full-health allies, no eligible allies, movement before release, displacement during grove, repeated pulses and defeat. A ring may describe an active area; a successful-heal sound requires a real heal result. Check root contact, petal collisions, visible inner garden and distinction from Bellback. Open decisions: root count, face/branches, botanical inventory, attack gesture and heal timbre.

## 4. Snapvine

### Construction and first rig test

**Canonical:** low creeping flower, folded petals concealing a thorn-lined jaw; thin root line previews a committed screened strike. Preserve flower/jaw readability rather than producing a humanoid plant.

**Resolve before generation:** vine-chain count and anchors, jaw hinge/opening, thorn arrangement, tongue or hooked-root presence, petal layering, underside/contact patches. A hooked root is an earlier presentation proposal, not a canonical requirement. Obtain closed and open-jaw construction views; teeth must not merge across the mouth.

**Moving:** vine chains, jaw, petals and body lift. **Rigid:** thorns remain attached to their jaw/petal regions without stretching. Build controllable bend chains with a clearly defined supported curl range; automatic weights require particular scrutiny around close coils.

**First difficult test:** tightly coil, open the jaw, extend into the intended strike pose and recoil without self-intersection or ground penetration. Test animation at actual board scale before adding tiny thorns.

### Motion and sound sheet

| Behavior | Animation and event-bound audio |
|---|---|
| Idle / Move / start-stop-turn | Petal breathing and creeping contact waves; coil release to move, gather to stop; quiet dry foliage and sliding root layers |
| Attack | Short thorn/jaw release matching the existing ranged basic-action contract; isolated launch and actual impact sounds |
| Active | Tension and directional commitment; lash/snap on release along authoritative cells; impact at the actual recipient, including an intercepting defender |
| Hit / Defeat / Victory | Vine recoil; relaxed grounded coil and closed jaw; controlled petal display; fibre snap/rustle, restrained closing and unfurling layers |
| Cancel | Release tension without playing a successful contact at the originally intended backline target |

**Acceptance cases:** clear strike lane, screened lane, moving/defeated target, edge cells, rotated creature and cancelled windup. Check jaw/petal overlap, thorn rigidity and full coil envelope. Do not stretch the whole mesh across several cells to represent a line effect; use separate presentation where required. Open decisions: support anatomy, jaw hinge, lash source and permitted extension.

## 5. Prism Organ

### Construction gate and first rig test

**Canonical:** suspended ceramic organ pipes around a stained-glass resonator; two distinguishable notes and crossing ground lines announce ordered beams. No humanoid body is required.

Read the existing [brief](../../art-source/asset-studio/wc_vn_prism_organ/BRIEF.md) and **[ART_REVISE review](../../art-source/asset-studio/wc_vn_prism_organ/inputs/references/r001/VISUAL_REVIEW.md)**. Its reference is not ready for modeling. Resolve PR-REF-001 through 005: six pictured versus four proposed keys; inconsistent emitter attachments; contradictory pipe order/heights; unresolved stained-glass core; missing consistent cradle/hoop interfaces. Generated “front/side/back” labels also do not establish calibrated geometry.

The earlier five-pipe, four-key, two-hoop/two-emitter inventory and dimensions are **proposals**, not approved counts. Lock a numbered parts diagram, attachment map and assembled/exploded correspondence before another generation. Carry the same inventory into every view.

**Rigid:** ceramic, metal frames, glass panels and indexed fragments. **Moving:** whole-assembly hover, limited parented pipe/key motion and declared emitter controls. Prefer a purpose-built rigid-joint Unreal rig; skin each rigid piece deliberately. **First difficult test:** maximum allowed hover tilt plus both emitter poses, preserving pipe/hoop clearance and exact part count.

### Motion and sound sheet

| Behavior | Animation and event-bound audio |
|---|---|
| Idle / Move / start-stop-turn | Coherent hover, restrained lean and settling; low ceramic air tone only where useful, with bounded concurrency |
| Attack | Short pipe/core emission consistent with basic projectile timing; separate breath release and glass contact |
| Active | Ordered anticipation and beam releases; distinct first/second notes follow their separate authoritative impact timing and cells |
| Hit / Defeat / Victory | Rigid assembly recoil; bounded settling/disassembly; brief coordinated lift/resonance; ceramic taps and glass notes |
| Cancel | Fade unreleased anticipation; preserve any already-released effects still present in the simulation |

**Acceptance cases:** both beams, shared/crossing recipients, empty cells, interruption before release, between-beam state changes and four facings. Creature rotation must not rotate the simulation's row/column cross. No duplicate notes per victim. Open decisions: all unresolved inventory/attachments, glass construction, emitter indexing and two-note interval.

## 6. Reefglass

### Material experiment, construction and first rig test

**Canonical:** glass-shelled cuttlefish, ribbonlike fins, visible internal currents; cupped fins and a narrow leading wave communicate directional displacement.

**Before final material selection:** compare restrained translucent glass and a mostly opaque glass-like alternative under the same approved soft lighting and Meshy palette. Capture both teams, pale/dark board areas, overlap and a crowded board; measure sorting/overdraw and readability. Preserve the original texture files in both variants. Neither version is accepted by this manual. Resolve glass visibility before spending on final internal detail.

**Resolve before generation:** shell thickness/openings; eye placement; fin attachment/width; tentacle count, length and resting clearance; internal current geometry versus material effect. Define a nominal hover and lowest animated point. Avoid fused tentacles or glass enclosing uninspectable floating fragments.

**Rigid:** shell and declared hard structures. **Moving:** fins, tentacles and body orientation; internal-current treatment follows a bounded effect design. Plan a custom fin/tentacle rig, evaluating automatic weights only as a candidate. **First difficult test:** cup fins forward, pitch into release, recoil and turn while every appendage remains clear of the ground and shell.

### Motion and sound sheet

| Behavior | Animation and event-bound audio |
|---|---|
| Idle / Move / start-stop-turn | Hovering swim, travelling fin wave, gentle acceleration/settling; sparse water movement, no footsteps |
| Attack | Small release gesture matching the crescent projectile; short water flick and separate actual contact |
| Active | Fin cup and pressure rise, leading wave on release; distinct wave-impact and successful-displacement accents only when those events occur |
| Hit / Defeat / Victory | Shell/body recoil; controlled settling within the reviewed envelope; lifted fins and calm current; muted glass/water accents |
| Cancel | Relax unreleased pressure without a fabricated breaking wave or push |

**Acceptance cases:** legal push, blocked destination, board edge, multiple lane recipients, rotated creature and interrupted windup. Damage may occur without displacement; the sound must preserve that distinction. Verify minimum hover clearance at all LODs and transparent overlap from the actual camera. Open decisions: material variant, tentacle inventory, eye/shell construction and defeat resting height.

## 7. Per-character release matrix

Record each row separately for each stable ID; Bellback's pass is tooling precedent, not inherited evidence.

| Gate | Required evidence |
|---|---|
| Construction/forms | Exact reference/candidate hashes, component inventory, all-side images, open-defect list and specific human acceptance |
| Color/lighting | Unchanged accepted Meshy texture hashes, material graph audit, matched close-up/board comparisons under the shared light profile |
| Rig | Named controls, declared rigid regions, difficult-pose study, actual exported/runtime skin deformation and control-free baked playback |
| Motion/contact | Full clips and transitions at normal/slow speed; sampled ground or hover clearance and contact drift at every LOD |
| Gameplay cues | Real event trace matched to animation/audio/video; normal, blocked, cancelled and already-released cases; unchanged simulation results |
| Sound | Provider/license record, source and edited WAVs, variations/concurrency, actual game mix without clipping, human listening decision |
| Packaged performance | Actual mixed-roster crowded-board run, LOD switching, selection bounds, memory/frame-time observations, package/reimport regression |
| Release | Exact artifact IDs, reproducible review links, no unresolved major defects and explicit owner appearance/motion/sound acceptance |

Resolve failed rows in the responsible stage. Do not recolor a creature to conceal poor lighting, obscure a deformation with effects, or spend on another generation to avoid identifying the defect. Preserve failed candidates and record the next bounded correction.
