# Ada — Method Recovery MR1
**Focused continuation of Asset Studio AS1. Not a new production pipeline.**

## Deliverable
One improved eye/socket/cheek construction proof and one asymmetric scalp-supported hair-mass proof, followed by a contextual head study only if those methods visibly work. All results remain candidates until the required human review. This package does not contain a repaired model.

## Use
1. Extract this folder under `production/asset-studio/method-recovery/MR1/` in the existing Wonder Chess repository. Do not overwrite existing files.
2. Give Codex `FIRST_MESSAGE_TO_CODEX.md`. It references the local AS1 skills rather than replacing them.
3. Use the actual current r003 source and frozen checkpoint. The upload hash in `evidence/source_files.json` identifies the inspected upload, not all future local revisions. Compare; never overwrite newer local work merely to match the upload.
4. The optional `wca-ada-method-recovery` skill can be copied into the repository's `.agents/skills/` if the name is unused. The task works by directly reading the documents without installing that skill.
5. Start the face proof, not another framework rewrite. Reuse existing MCP, review cameras, reference approvals and reporting tools after a short relevant health check.

## Read order
- `FIRST_MESSAGE_TO_CODEX.md`: the assignment.
- `docs/01_SOURCE_DIAGNOSIS.md`: evidence and preservation boundary.
- `docs/02_EYE_SOCKET_PROOF.md`: specific face modeling procedure.
- `docs/03_HAIR_MASS_PROOF.md`: specific hair modeling procedure.
- `docs/04_REVIEW_AND_HANDOFF.md`: camera controls, scope, pass/revise decisions, fallback.

## What is authorized
A documented change from the failed formula-driven method to deliberate low-density control-cage editing and/or focused sculpting. Work in new revisions. A successful agent review may permit another internal method-proof stage; it is not human approval of Ada. Preserve the AS1 two-no-improvement limit for each genuinely different method. Changing a seed, raising mesh resolution or tweaking the same patch formula does not reset the limit.

## What is not authorized
Changing gameplay, changing the approved identity, resetting the project, exporting this bust as a finished hero, uploading art to external services, acquiring paid assets, replacing root instructions, altering safety settings, forcing mouse/keyboard access while Pram is using the machine, or manufacturing human approval.

## Helper
`tools/prepare_study.py` is an optional standalone Python staging helper. It is dry-run by default. With `--execute`, it creates a new directory containing immutable-intent baseline and work copies plus a source-hash record. It does not start Blender, inspect geometry, enforce an ACL, or approve art. Review Blender's unsaved changes before operating on a disk copy.

## Evidence limits
The attached review is the source for the reported 53 visible meshes, 189,972 evaluated triangles and prior tests. Those results were not rerun for this handoff. A separate read-only binary inventory of the supplied .blend found 106 saved Object records and 88 Mesh records including experimental/hidden data. These totals describe different scopes and must not be substituted for each other. No Blender/bpy runtime was installed here; no new render, sculpt, deformation test or Unreal import was performed.

Keep the original `.blend`, `.blend1` and frozen checkpoint. The `.blend1` upload is not automatically the intended rollback target.

## Optional local staging command
Let Codex resolve `$Source` to the verified current disk file and `$StudyRoot` to a new, nonexistent revision directory. In PowerShell, from the repository root:

```powershell
python production/asset-studio/method-recovery/MR1/tools/prepare_study.py --source "$Source" --output "$StudyRoot"
```

Inspect the dry-run result, then add `--execute` only after checking unsaved Blender work. An `--expected-sha256` argument can enforce a known baseline; a mismatch requires inspecting the difference, not overwriting newer work. The helper produces **source copies only**. It does not repair a mesh or substitute for the modeling tasks.
