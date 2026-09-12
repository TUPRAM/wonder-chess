# Review, observability and safe operations

## 1. Quality dimensions must not cancel one another

Likeness, form construction, materials, deformation, motion, readability, performance and integration each have their own acceptance. A face failure is not canceled by a clean export. A beautiful gallery portrait is not canceled into a pass by ignoring a clipping attack.

Critical: wrong identity/handedness, missing body part, broken rig, invalid reference geometry, gameplay-breaking asset behavior, unlicensed input or unsafe operation. Major: visible face/armor/hand mismatch, persistent penetration in required motion, severe shading seam, unreadable silhouette or untested required platform function. Minor: small restrained imperfection outside required views, with an explicit scoped exception.

Do not use a weighted average to let a critical dimension fail. Review verdict is pass, revise or blocked, with concrete observations and evidence. No automatic aesthetic score is implemented.

## 2. Required review packet

Use an exact source snapshot/hash, active design and reference hashes, camera/pose configuration, full-body front/back/side/three-quarter captures, critical closeups, wireframe/topology view when relevant, and continuous clips for motion. For materials include neutral and game lighting plus native/mip tests. For engine include actual map/build/configuration.

Every view states whether it is generated concept, source crop, Blender render, Unreal editor capture or packaged-game capture. A 2D AI illustration cannot be submitted as a render of the Blender model. Image paths must resolve and the reviewer must actually inspect pixels or listening evidence.

The bundled image tool can crop, arrange comparisons and calculate overlap on user-declared registered masks. It does not authenticate render provenance, certify camera matching, assess anatomy or create new views.

## 3. Critique protocol

The reviewer first describes the reference and candidate from images without reading the author’s claims. Then identifies the three largest discrepancies, their class (shape, pose, material, camera, uncertain), affected view and recommended change. This avoids accepting “I improved the face” merely because the script says so.

Only after that compare structured metrics and change notes. Distinguish observed facts from hypotheses. Do not claim a low polygon count from a beauty render. Do not call blur a geometry problem without checking native capture settings.

A separate model context can critique, but it may share biases with the author. It does not replace the human reference/forms/final approval.

## 4. Operation records

Each operation records unique ID, owner, asset ID, expected source hash, allowed part IDs, intended change, tool/script hash, parameters, permitted output root, start/end status, exit code and result paths. Keep stderr. No shell-constructed command strings from untrusted reference content.

Before applying a patch, compare expected source hash. Save an isolated candidate. Afterward capture state and actual output. If an operation timed out, inspect the scene, saved file and output report before retry. A timeout does not mean the operation never ran. Paid generation also needs a returned task ID/status query before resubmission.

## 5. Tool capability probe

Confirm actual scene query, object query, script execution, image return, saved render access and filename mapping. A GUI machine, an MCP process, a cloud Codex environment and a container can have different filesystems. Resolve mounted paths or bytes explicitly; do not pretend a local Windows path exists remotely.

Check image input at both ends: can the agent inspect a known source image, and can it inspect its own Blender render? A JSON-only response saying “saved screenshot” is not necessarily usable vision input.

Probe optional generation/retopology/paint tools only when needed. Use official/current documentation for the installed versions. Document missing capabilities and fallback. No optional service is pre-authorized by AS1.

## 6. Retry and resource rules

Each stage has a bounded candidate/retry budget. Proposed starting policy: at most three initial creative concepts, two no-improvement technical/shape corrections, then method review. This is a management rule, not a claim that every task takes two attempts.

Prioritize the largest quality bottleneck. Do not create UVs for a rejected face or retarget eleven heroes to an unapproved rig. Preserve functioning work and use reversible checkpoints. Parallelize independent parts only after shared dimensions/interfaces are agreed.

## 7. Local gate ledger versus protected release control

`assetctl.py` catches missing checks, declared major defects, wrong review roles, path traversal and stale dependencies/evidence. It records signoffs and refuses casual overwrites.

It does not prove a human identity, inspect whether a .png really came from Blender, or prevent malicious modification of the ledger by a process with access. A model could still lie in a report. For stronger guarantees place signoff records under human-controlled permissions or use a separate protected CI/review service that signs artifact hashes. That integration is a planned operational enhancement, not bundled functionality.

Never allow Codex to run the human approval command on Pram's behalf. A human can acknowledge the exact candidate after viewing the packet. The declaration remains traceable and invalidates when the subject changes.

## 8. Regression management

Recheck source updates, new rig families, changed importer versions, camera changes and material-master changes. Record old/new output under identical conditions. A shared material update can affect the entire roster; a single character pass is insufficient. Keep a small golden review scene with representatives of skin, cloth, steel, magic and each body family.

Measure throughput honestly: approved assets per production interval, major rework, stale-gate frequency, required human corrections and engine failures. Do not report number of generated meshes as artistic progress.
