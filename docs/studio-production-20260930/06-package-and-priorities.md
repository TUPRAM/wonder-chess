# 6. Standard package contract and eight priority specifications

All packages below are **proposals**, not newly installed skills or observed execution. Their boundaries follow the audit: current route conflicts, gameplay uncertainty, unfinished player journeys, anatomy-specific delivery and exact-build evidence deserve work before catalogue breadth.

## Package contract

```text
capabilities/<stable-id>/
  SKILL.md                    # portable purpose, triggers, boundaries and bounded procedure
  agents/openai.yaml          # activation metadata; not execution proof
  contracts/input.schema.json # typed IDs, revisions, units, capabilities and permission scope
  contracts/output.schema.json
  operators/                 # executable deterministic operations and adapter entry points
  adapters/unreal/            # version-qualified tool bridge, separate from generic policy
  config/wonder-chess.json    # canonical paths, gates and route; no copied gameplay stats
  recipes/<family>.json       # semantic anatomy/material/assembly recipe
  fixtures/development/      # editable cases used during implementation
  fixtures/qualification/    # fixed/withheld cases, separated from development
  tests/                     # positive, negative, recovery and regression tests
  examples/                  # actual inputs/outputs with scope and limitations
  evidence/manifest.json     # hashes, versions, invocation, results, independent decisions
  CHANGELOG.md               # maintainer, migration and deprecation contract
```

The owner-led repository can host these directories without a registry service. Code and schemas are versioned; generated output is replaceable; receipts and human decisions are immutable records. A verified bridge is required wherever an operator needs editor inspection or mutation. Instructions must include the precise manual fallback when no bridge is available.

Each input schema requires task/asset/profile IDs, schema and package versions, input hashes, owned paths, dependency revisions, units and coordinates, resource limits, permission scope and requested completion contract. Each output requires actual artifacts, hashes, achieved dimensions, evidence references, known defects, failure category and next action. Unreal geometry uses explicit centimeters and documented handedness/up/forward axes; imported glTF meters must be converted once and checked. Bone transforms specify space and rest pose. Timings state simulation units and event identity; frame count alone is insufficient.

Every invocation checks preconditions, selected tool version, supported capability and exclusive ownership. It checkpoints before mutation, bounds attempts, handles timeout as unknown until inspected, validates output and publishes only within the authorized scope. Failure categories are INPUT_INVALID, DEPENDENCY_MISSING, CAPABILITY_UNSUPPORTED, PERMISSION_MISSING, RESOURCE_LIMIT, TOOL_FAILED, QUALITY_FAILED, EVIDENCE_STALE and OWNER_DECISION_PENDING. Failed output stays isolated; recovery never silently overwrites accepted work.

Human approval remains separate from tool execution. A generation receipt, valid export or checklist does not approve likeness, motion, listening, comprehension or release. Versions need maintainer Pram or a named delegated maintainer, limitations, migration notes and a deprecation date only after dependent routes have a replacement. Never erase old gate identities during migration.

## SP-01 — production-task

**Purpose/trigger:** turn an owner-requested bounded change into one reviewable handoff; invoke before multi-step work or resume. Do not use it to choose new creative direction or expand wca-orchestrate. Inputs are intent, current ledger/candidate, route, file ownership, allowances and existing decisions. Output is a schema-valid task record, dependency graph and scoped handoff referencing existing ledgers.

**Invocation:** `production-task plan task=wc-journey-shop-001 candidate=development-r3 scope=shop-return`. Input example: `{profile:"wonder_vnext", owned_paths:["<selected UI files>"], max_external_credits:0, checkpoint:"<source digest>"}`. Output example: `{execution:"NOT_RUN", dependencies:["current recipe identity"], next_action:"capture current shop journey", approval_refs:[]}`. Angle brackets denote values resolved at execution, never fabricated hashes.

**Procedure/verification:** resolve source authority once, check scoped approvals, reserve one writer, create checkpoint and acceptance criteria, dispatch only unblocked operations, attach outputs with actual hashes, validate resume after input changes. Test duplicate task IDs, path escape, conflicting writer, lost bridge and stale approval. Replay a stopped task without duplicating its paid job.

**Failure/recovery:** a Meshy timeout is UNKNOWN, not failed. Resume from the receipt/job ID, poll/download existing output read-only, then decide whether a new authorized attempt is needed. No receipt means reconcile the provider account before retry. Human authority covers new scope, credits and creative/release decisions. Reuse level: generic orchestration with Wonder Chess policy adapter.

## SP-02 — runtime-contract

**Purpose/trigger:** repair wc-data-contract routing and bind a bounded rule/data change to authoritative C++ and generated views. Invoke for hero, trait, relic, save/protocol or command changes. Exclude tuning without an experiment hypothesis and unrelated art. Inputs: profile, canonical source revision, exact mechanic specification, compatibility policy and affected fixtures. Outputs: proposed/implemented delta according to scope, generated identities, transaction/parity results and migration report.

**Invocation:** `runtime-contract verify profile=wonder_vnext task=silkmother-expiry source=data/vnext/catalog.json`. Input example: `{change:"cocoon expiry", simulation_authority:"C++", compatibility:"explicit version", source_digest:"<resolved>"}`. Output example: `{authored:true, executed:"NOT_RUN", impacted:["expiry", "recap", "save identity", "motion event timing"]}` until real results exist.

**Procedure/verification:** select successor or legacy lane explicitly; author only in canonical data/appropriate C++; compile through tools/vnext/catalog.py; validate schemas, units, generated headers/runtime bytes and engine adapter; test expiry, interruption, duplicate/reordered requests, combat cutoff and forbidden private data. Reconcile viewed/off-screen events and package identity for affected mechanics. A meaningful test asserts externally observable rules or invariants, not a restatement of the implementation.

**Failure/recovery:** source and staged digest disagree: block execution, preserve prior candidate and regenerate once through its owner; do not patch widgets or runtime JSON independently. Human authority approves changed game contract or migration scope. Reuse: generic contracts/validators, Unreal adapter and Wonder Chess gameplay policy. Existing helper tests support feasibility; the new package itself remains NOT_RUN.

## SP-03 — gameplay-experiment

**Purpose/trigger:** investigate a falsifiable formation, economy or pacing question with ordinary legal acquisition and representative bots. Inputs: frozen control/candidate IDs, one hypothesis, declared metrics/strata, seeds, bot policies, required human comparison and change budget. Outputs: preregistration, per-run raw data, paired analysis, defects and retain/revise/reject recommendation. It cannot establish enjoyment from bot outcomes.

**Invocation:** `gameplay-experiment plan hypothesis=shop-accessible-trap-counter control=development-r3 change=one-interaction`. Input example: `{holdout_use:false, policies:["existing","declared perturbation"], metrics:["acquisition","combat timeout","round cap","normal-speed duration"]}`. Output example: `{decision:"UNDETERMINED", sample_size:0, recommendation:"collect registered baseline first"}`.

**Procedure/verification:** distinguish battle timeout from tournament cap, fixed formations from legally recruited teams, preparation from combat/paused time. Reconcile combat logs with event counts; compare mirrored useful/unfavorable cases and policy perturbations. Register one change, failure criteria and interpretation before examining outcomes. Keep reserved confirmation seeds unused until the declared confirmation stage and verify reservation at execution. Report denominator and uncertainty for each stratum.

**Failure/recovery:** a bot counter buys unavailable heroes or uses hidden information: invalidate that experiment arm, repair the policy/fixture and rerun only affected cases. Retain failed acquisition attempts. Stop tuning when it erases a pillar or exceeds one authorized change. Pram decides design tradeoffs; independent humans decide whether the experience is understood. Reuse: generic experiment operators with game-specific metric/command adapters.

## SP-04 — player-journey

**Purpose/trigger:** specify, implement and verify one complete player interaction rather than static interface art. Inputs: actual current screen/state graph, task, commands, errors, input/localization/accessibility matrix and exact package. Outputs: journey specification, affected interface source/assets, physical-control evidence, defects and study-ready build. Invoke for shop, bench, relic, recap, save/load, settings or later lobby flows; scope one journey per task.

**Invocation:** `player-journey plan journey=full-bench-buy-merge-return candidate=development-r3`. Input example: `{states:["preparation","shop","bench full","merge","combat cutoff"], languages:["en","id"], input:["pointer","keyboard"]}`. Output example: `{engineering:"NOT_RUN", human_first_use:"NOT_RUN", task_rubric:"unassisted buy/reject/return"}`.

**Procedure/verification:** map expected and rejected commands to feedback, focus, selection and recovery. Observe the current behavior before editing. Test ordinary purchase, merge into a full bench, no eligible merge, close/reopen, phase expiry, focus restoration and save/resume. Inspect 1280×720, 1600×1000 and 1920×1080 plus required text scales, long Indonesian strings, color-independent information and reduced effects. Compare physical controls with handler tests; both have separate results. Study participants must not need implementation terminology.

**Failure/recovery:** modal closes after rejection and loses selection: preserve a reproduction and pre-fix capture; revise that state transition, rerun cutoff/focus/resume regressions and then retest the affected first-use task with eligible users. Pram approves product scope; human-study evidence controls comprehension claims. Reuse: generic journey/validation contract with Unreal interface adapter and product task policy.

## SP-05 — human-study

**Purpose/trigger:** qualify comprehension, pacing, accessibility or repeated use on an identified build. Inputs: existing B0/B1/B2/M5 protocol, eligibility, participant/device availability, consent/data minimization, task rubric and stop conditions. Outputs: preregistered session kit, assistance-aware raw observations, anonymized analysis and recommendation. Reuse tools/vnext/human_study.py where suitable; avoid a second scoring database.

**Invocation:** `human-study prepare gate=B2 candidate=development-r3 participant_target=5`. Input example: `{first_use_required:true, task_set:"existing nine tasks", record_assistance:true, contact_authorized:false}`. Output example: `{recruitment:"NOT_RUN", sessions:0, acceptance:"OPEN", kit:"<artifact>"}`. Preparing a kit grants no permission to contact people.

**Procedure/verification:** freeze protocol/build, separate returning B1 users from new B2 users, capture task success, cause explanations, errors, help, personal elimination and final-winner/spectating endpoints. Apply the existing four-of-five formative criteria without silently replacing them. Record normal-speed full duration, pauses and eliminated-player time separately. M5 repeat-day evidence uses its existing requirements. Dry-run scoring against fixtures with assistance, missing rows and withdrawal.

**Failure/recovery:** an assisted success counted as independent is a scoring defect: correct raw classification transparently, rerun scoring and preserve original export. Insufficient eligible people yields BLOCKED participant logistics, while independent engineering continues. Five people provide formative signals, not a population success rate. Pram authorizes recruitment and design decisions; participants provide the observations. Reuse: research kit/operators with project gate policy.

## SP-06 — creature-delivery

**Purpose/trigger:** repair and qualify the current wc-creature-production/rigging route for one animation-ready creature, without regenerating unchanged accepted work. Inputs: asset ID, accepted four-view hashes, current source/candidate, anatomy recipe, geometry/maps, supported provider surface, allowed credits and scoped approvals. Outputs: preserved source/receipts, Unreal skeleton/skin/editable controls, actual deformation/contact evidence, cold-reopen check and combined G3/G4 presentation.

**Invocation:** `creature-delivery resume asset=wc_vn_cragstoat candidate=SageTail_r003 contract=animation-ready`. Input example: `{route:"Meshy→Unreal", new_generation:false, anatomy:"quadruped plus flexible tail", credit_cap:0}`. Output example: `{source_preserved:true, local_contact:"<measured result>", visual_review:"NOT_RUN", owner_acceptance:"OPEN"}` until each dimension is inspected.

**Procedure/verification:** capability-probe API/web separately; unsupported quadruped API rigging routes to the authorized local Unreal completion/manual surface. Identify semantic root/spine/head/limb/bend/contact/tail roles and assert anatomy cardinalities. Do not use Bellback numeric bone indices or fixed foot offsets. Derive contact surfaces from this mesh/rest pose; stress actual skinned vertices, not control locators. Preserve maps, UVs, rigid attachments and tolerated reference alignment; review four anatomical slots and asymmetry. Save/cold reopen/reimport and present one combined forms/color/rig review while retaining intermediate technical records.

**Failure/recovery:** a control-only contact pass hides floor penetration: classify evidence invalid, preserve the candidate, correct weights/control mapping on an isolated revision and rerun actual surface cases. After two ineffective revisions of a critical defect, change method or stop that stage. Unchanged approval scope persists. Reuse: generic anatomy contract, Unreal adapter and family recipes; human art acceptance cannot be automated.

## SP-07 — motion-events

**Purpose/trigger:** repair wca-motion for the selected Unreal route and synchronize animation, effects and sound with authoritative combat. Inputs: accepted animation-ready candidate, semantic controls, event schema/timing, required clips and original sound rights. Outputs: editable clips/transitions, event mapping, cancellable/poolable cue behavior, continuous-motion/listening evidence and timing regressions. It does not redesign abilities or emit authoritative damage.

**Invocation:** `motion-events plan asset=wc_vn_cragstoat behavior=charge candidate=<exact-rig>`. Input example: `{events:["commit","release","impact","cancel","death"], timing_source:"C++ event stream", reduced_effects:true}`. Output example: `{clips:"NOT_RUN", synchronization:"NOT_RUN", listening:"NOT_RUN", acceptance:"OPEN"}`.

**Procedure/verification:** first review continuous normal-speed locomotion/contact/turn and relevant attack/cast/hit/death, then inspect difficult frames. Verify interruption, source defeat after release, target movement, simultaneous cues, pooling/expiry and reduced-effects grammar. Listen to repeated overlap in the packaged mix with volume buses; verify rights separately. Controls must reset and reopen. Changing a rest pose invalidates affected clips; changing release timing invalidates affected animation/VFX/audio sync without erasing an unchanged appearance approval.

**Failure/recovery:** a charge cue shows impact before the event: isolate the cue version, fix event binding and test commit/cancel/impact/death alongside normal-speed review. A valid animation file without a reviewed transition is incomplete. Pram approves creative motion/audio; runtime validators enforce event identity. Reuse: event validator and Unreal adapters with creature-family locomotion recipes.

## SP-08 — exact-build

**Purpose/trigger:** repair wc-release-evidence routing and produce a traceable package for the requested study/release contract. Inputs: accepted scope or study scope, source/runtime digest, toolchain, final content/flags, dependencies and target hardware. Outputs: exact source/payload/executable manifest, build/install/control/performance results, defects, rollback location and explicit remaining gates. wca-release still owns accepted asset promotion, not whole-game release.

**Invocation:** `exact-build plan candidate=studio-slice-001 contract=playtest-build profile=wonder_vnext`. Input example: `{overwrite_existing:false, freeze_content:true, install_target:"independent device pending", release_authorized:false}`. Output example: `{package:"NOT_RUN", clean_checkout:"NOT_RUN", clean_machine:"BLOCKED", game_release:"NOT_ACCEPTED"}` with the device limitation reason.

**Procedure/verification:** build into a new candidate directory, bind executable/config/content to the freeze, rerun affected regressions and applicable large final gates at promotion. Distinguish same-machine clean checkout from independent clean-machine install. Verify new/load, input, full lifecycle, settings, crash diagnostics and rollback. Measure named-hardware mixed content including twenty deployed units, entities/effects and actual off-screen fights; do not transfer Bellback-only timings to the full game. Remote checks belong to M6 and remain mandatory for that scope.

**Failure/recovery:** an import changes after freeze: fail identity, preserve existing build/evidence, refreeze and repeat affected checks; never edit a manifest to match an unexplained output. Independent hardware absent leaves that gate open. Pram alone accepts/releases the final product. Reuse: generic build/evidence operators with Unreal packaging and Wonder Chess gates.
