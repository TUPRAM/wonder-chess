# AS1 — System architecture and operating contract

## 1. Product objective and hard limit

Deliver assets that match a chosen artistic identity, survive the required motion and render correctly in the actual Wonder Chess build. The user explicitly requested a reusable system for every asset, with separate skills/tools and a detailed concept-to-engine workflow.

The six requested phases remain visible: (1) concept/reference, (2) modeling, (3) retopology, (4) UV/texturing, (5) rigging, (6) skinning. AS1 adds intake, reference reconciliation, explicit likeness approval, animation, LOD/performance, engine validation and controlled publication. Some stages branch or run in parallel; a rigid prop does not need skinning.

Art quality is judged, not guaranteed by code. What can be enforced procedurally is refusal to advance when required evidence or signoff is missing, a recorded serious defect remains open, or the approved inputs changed. Do not advertise a beauty guarantee, a numerical likeness percentage, or an autonomous studio without measured results.

## 2. Four cooperating layers

**Orchestrator.** Chooses the applicable route, checks dependencies, assigns one owner, maintains the operation log and detects failed approaches. It does not model every component or rate its own work as human-approved.

**Skills.** Focused working procedures containing triggers, inputs, constraints, operations, output contracts and tests. A skill is not a newly installed executable capability. Only load the stage needed now. One model can execute skills sequentially; multiple workers are optional, not proof of expertise.

**Tools/adapters.** Deterministic operations such as file hashing, native crops, Blender scene queries, controlled rendering and export checks. Existing MCP provides access to Blender; it does not supply aesthetic judgement. Some helper tools are implemented here; complex modeling and Unreal adapters remain Codex/editor work.

**Review.** Technical reviewer inspects structured evidence; visual reviewer actually views images/continuous motion; Pram approves the reference, approved forms and final release. A separate critique context can reduce anchoring but is not a genuinely independent human artist.

## 3. Authority and source of truth

Preserve existing project/runtime identity. The pipeline applies to art, not roster/economy decisions. Authority by concern:

| Concern | Source of truth |
|---|---|
| Runtime ID, stats, skill/effect timing | Existing canonical game definitions |
| Artistic identity | Selected reference plus approved design decisions |
| Construction/measurements | Reconciled construction pack and approved 3D source |
| Bone names/rest transforms/sockets | Versioned export-skeleton contract |
| Geometry, UVs and skin | Editable versioned Blender source |
| Texture outputs | Saved texture sources and reproducible bake/export recipe |
| Shipping representation | Accepted export manifest and engine import result |
| Completion | Current gate records and human acceptance, not asset presence |

Do not let old instructions such as simplified armor/gold restrictions silently override a newly chosen visual design. Reconcile them explicitly. Do not alter combat to make a defective animation appear correct.

## 4. Asset record and stage graph

Every asset gets an immutable ID, kind, design revision, dimensions, coordinate convention, budget profile, rights record, dependency IDs, part inventory, reference hashes and required stage route. Keep progress in `state.json`, not by repeatedly changing the approved manifest.

Character/creature route:

```text
brief -> references -> blockout -> forms -> topology
                                           |-> uv -> materials ----|
                                           |-> rig -> skin -> motion|-> optimization -> engine -> release
```

Perform temporary pose/proxy-rig checks during topology; the formal rig and skin approvals follow the stable topology. This catches elbow/shoulder problems before final texture production. The graph is the **approval dependency**, not permission to never test rigging until late.

Static prop/equipment/environment/foliage route omits rig/skin/motion. Animated equipment uses a separately approved rigged route when needed. VFX uses timing and visual-effect motion instead of skinning. UI uses layout/scale checks. Audio uses listening evidence instead of image evidence. See `08_ASSET_CLASS_ROUTES.md`.

## 5. Gate behavior

Possible operational descriptions: not started, working, awaiting review, rejected, blocked, accepted current, stale. The ledger stores only pending/current acceptance/staleness; detailed work state lives in operation logs. A candidate report is not approval.

All declared checks must have observations and actual evidence. `not_run` is never interpreted as pass. Critical or major open defects block a gate. A minor issue can be accepted only with a reason, affected use, owner and later action in the record. This is not permission to classify likeness failure as minor.

Mandatory human gates are references, forms and release. Technical/art reviewers cover interim stages. A highly visible head/torso study belongs at the forms gate; do not spend resources completing the whole asset before that review. Trusted review can occur by conversation; record the actual conversation decision or externally recorded approval, not a made-up signature.

## 6. Hashes and invalidation

The included ledger seals the manifest/rules, each report, every listed artifact and upstream acceptance hashes. Changes make acceptance stale. Topology changes should invalidate UV/bakes, skin and dependent exports. Skeleton rest changes invalidate skin/motion and reimport evidence. Material-only changes need not invalidate geometry in a more advanced per-component build system; AS1's ledger is intentionally conservative.

Save an immutable candidate snapshot per stage. Do not approve `latest.blend` and keep editing it. Use `forms/r003.blend`, then a new `topology/r001.blend` that references the approved parent. Derived files must never be treated as independent truth.

Hashes establish file identity, not artistic truth. Same seed/provider settings do not prove generative reproducibility. Log returned IDs/settings when available, but never invent seeds or deterministic claims.

## 7. Work ownership and safety

One writer per asset file, one writer per shared skeleton/material and one queue per Blender session. Reads may run in parallel against immutable snapshots. Fine-grained asset edits can be parallelized only on separate component files with a reviewed assembly contract. Two agents editing the same binary scene is not a collaboration strategy.

Use an exclusive work lock, expected source hash, named operations, allowed output directory and checkpoint. The included ledger lock protects its own metadata only; it does not lock Blender itself. Implement editor-side session scheduling before concurrent use.

MCP/code execution has the privileges of the local editor user. Limit it to the project; inspect source; bind locally when appropriate; never expose raw code execution publicly; review telemetry; keep credentials out of logs. Do not install/upload/purchase solely because a generated instruction suggests it.

## 8. Anti-stagnation policy

For each operation identify the largest visible defect and an observable expected correction. Compare matched before/after captures. Maximum two unsuccessful bounded attempts at a critical defect before method review. Replacing an unsuitable base, changing a modeling operation or asking for a focused artist pass is a valid recovery. Adding detail, changing lights or raising resolution is not progress if the target shape remains wrong.

Budget approved image generations, candidate branches, editor time and review load separately. No live external generation is enabled by this kit. Do not download an enormous model or rerun paid jobs to avoid reporting a blocker.

## 9. Completion

An asset is complete only for an explicit use: e.g. gameplay hero plus shop portrait on the measured PC profile. A gallery render does not establish game performance. A low-detail gameplay mesh does not automatically qualify for a cinematic closeup. Release preserves editable source, reports, dependency hashes, rights, versions, exports and rollback. Game-wide quality is tested after individual acceptance, because coherent assets can still clash when placed together.
