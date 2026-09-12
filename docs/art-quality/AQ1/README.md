# Wonder Chess — Art Quality Upgrade AQ1

**Prepared:** 2026-09-08  
**Type:** Source-grounded design and execution supplement. Not a mesh, a patched repository, or a verified Blender/Unreal implementation.  
**Inspected repository:** `TUPRAM/wonder-chess`, commit `9623fd82f98ff80a90985b9f552d8851ccece30f`.

## Decision

Keep the existing Wonder Chess game and its current content scope. Improve the art workflow instead of restarting development. Suspend **bulk visual polishing/regeneration** until one redesigned Ada establishes a convincing reference. Runtime work can continue independently.

The immediate deliverable is **one visually approved, animated, in-engine Ada candidate**, not a higher triangle count, a new character bible, or another complete roster of similarly coarse characters.

## Read in this order

1. `01_REPOSITORY_FINDINGS.md`: what the inspected code and supplied images actually show.
2. `02_ADA_VISUAL_DIRECTION.md`: a specific proposed redesign that preserves her identity and gameplay.
3. `03_MCP_ART_WORKFLOW.md`: bounded modeling, actual visual feedback, snapshots, and approval.
4. `04_GEOMETRY_MATERIAL_UNREAL_CONTRACT.md`: source geometry, game topology, materials, rig compatibility, and import checks.
5. `FIRST_TASK_TO_CODEX.md`: the next assignment to paste into Codex.

`review_template.json` records evidence and approvals. It is intentionally empty/pending. `skill_template/SKILL.md` is an optional skill to install after reviewing the existing project instructions. `SOURCE_INDEX.json` records the inspected sources and technical references. `MCP_ARCHIVE_AUDIT.md` distinguishes uploaded bridge capabilities from a verified live connection.

## Integration into the existing repository

Place this folder under `docs/art-quality/AQ1/` after checking for an existing directory with that name. Do not replace the root `AGENTS.md`, existing skills, canonical assets, or game code automatically. Review/merge a short pointer into the existing instructions so this becomes the active **art experiment**, not a competing game specification.

Create candidate work under `art-source/heroes/wc_u_human_guardian/candidates/AQ1/` only after checking that directory is safe. Use a separate Unreal candidate location. Preserve the accepted source, exports, and runtime references until a candidate passes review.

Read current HEAD and the local working tree before beginning. The repository may have changed since this audit. Use differences to update the task, not overwrite newer work with the inspected snapshot.

## Scope boundaries

- Preserve unit IDs, balance, skills, tournament behavior, and current roster scope.
- Preserve the existing skeleton/animation contract when it genuinely supports the new form. An incompatible proportion change requires an explicit rig/retarget migration, not concealed compensating scales.
- Source/modeling changes are permitted; the old coarse head, armor, sword, and shield are **not** sacred compatibility boundaries.
- No competitor asset extraction, undocumented external uploads, purchases, public publishing, or project-wide regeneration.
- No requirement to create a new website, backend, lore system, or asset-management platform.
- A passing structural report is not visual acceptance. Pram's approval of the actual reference character is required before bulk rollout.

## What this package does not contain

No concept images were generated here. No `.blend` or `.uasset` was edited or executed here. No local MCP session was opened. No source code was pushed to GitHub. Technical findings come from a targeted source inspection; numerical asset properties are identified as manifest-reported rather than independently measured.
