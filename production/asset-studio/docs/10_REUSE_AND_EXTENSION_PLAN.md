# Reusable foundations, change control and tool-extension priorities

## 1. Promote a successful recipe, not an unsuccessful generator

After the Ada reference succeeds, preserve a **golden asset**: accepted source, construction references, topology, rig, UV/bake recipe, materials, camera setup, animations, engine import settings and review evidence. This asset proves one production path. It does not prove the same body will suit every race or costume.

Build a small versioned library: body-family bases, rest/export skeletons, hands and grip poses, armor-construction examples, material masters, shared animation foundations, terrain/architecture modules, collision conventions and effect-timing templates. Record license and allowed modification/export for each external foundation. Do not distribute unlicensed source.

Each reused component declares ID, version/hash, dimensional contract, compatible skeleton, UV/material dependencies and the character-specific deviations. Reuse does not automatically carry its parent's artistic approval to the new hero. The new face, silhouette, equipment and all intended clips still require review.

The next proof after Ada should contrast her: a slender cloth-led hero and a stocky body-family hero. Validate those before broad roster production. Keep environment and UI production parallel only where source ownership and shared dependencies are stable.

## 2. Pilot versus complete-asset approval

Ada's head-and-torso study is an early **pilot checkpoint** inside the forms work. It is not permission to mark the whole hero's forms gate complete. Before that full gate, the complete body and every required costume/equipment part must exist, agree with the approved identity and pass the complete multi-view check. A bust-only study cannot satisfy the downstream hero topology, skin, motion or release gates.

The included Ada part inventory is explicitly partial and must be completed before a whole-hero gate. Never relabel an incomplete inventory as complete to satisfy a check.

## 3. Changes and targeted regression

| Change | Required rechecks |
|---|---|
| New facial/armor proportions | Likeness, geometry, rest contacts, affected weights, poses, portraits and engine scale |
| Topology/vertex order | UV/bakes, skin, morph data, tangents, mesh export and affected engine integration |
| Skeleton rest transforms | Skin, all dependent clips/sockets, retargeting and imports; do not silently update shared skeletons |
| Texture/roughness changes | Material and mip review, engine material comparison, portrait and relevant performance |
| Import profile | Calibration asset, skeleton/material interpretation, reference reimport and packaged regression |
| Shared material/skeleton change | Every dependent asset, not only the one currently open |
| New lower-detail mesh | Actual screen-size silhouette, animation/attachment and transition checks |
| UI portrait redraw | Character identity, crop, alpha edges, readability and actual widget |

AS1's local ledger is conservatively invalidating; it does not implement a full cross-asset build graph. Maintain cross-asset dependencies in the manifest and have the orchestrator schedule dependent checks. A future content build service can implement finer invalidation, but do not claim it is already supplied.

## 4. Extend tools only when a testable gap justifies it

Prioritize these additions after installing and verifying the current helpers:

1. **Live MCP operation wrapper.** Map real schemas, session ownership, source hash, operation IDs, status and non-destructive timeout handling. It must not expose arbitrary execution to a public endpoint. Tests: duplicate calls do not repeat destructive edits; timeout triggers inspection; wrong scene revision blocks mutation.
2. **Registered review capture.** Store target camera/pose plus genuine image responses that Codex can inspect. Tests: source hash changes, camera mismatch, unavailable images and stale paths are clearly reported. No automatic image-similarity approval.
3. **Specialized geometry/UV checks.** Add overlap islands, texel-density analysis, self-intersection candidates and cage diagnostics. Distinguish intended overlaps and layered assemblies from defects. Tests use deliberately clean/broken fixtures; a detector result is not final visual truth.
4. **Pose/contact harness.** Evaluate actual deform geometry across sampled clips, socket trajectories and bounds. Record thresholds per asset and intended use. Validate the detector against known collisions/sliding; do not confuse bone movement with vertex deformation.
5. **Unreal candidate importer/review runner.** Reuse the project's measured profile. Validate normals, reference skeleton, clips, materials, real screenshots and packaged loading. Keep candidate promotion explicit.
6. **Protected approval/promotion service, only if needed.** Real human identity, append-only review and CI-owned publication. This is an optional infrastructure project—not functionality of the bundled local ledger.

None of these recommended new adapters is represented as already deployed. Codex must verify API/tool availability and use actual outputs. Do not let tool-building become an excuse to postpone the Ada form study indefinitely.

## 5. Portfolio-level quality

After individual acceptance, show the accepted roster together in neutral lighting and the actual arena. Check body-family consistency, contrast, scale, material language, faction similarities without cloned silhouettes, and how effects overlap. Include names/stars/selection treatments at gameplay scale. A group review can reveal clashes that individual portraits conceal.

Only then promote the shared recipe as the default for the next batch. A successful single pilot is a useful evidence point, not a guarantee for all future assets.
