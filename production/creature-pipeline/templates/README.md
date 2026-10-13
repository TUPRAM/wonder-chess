# Candidate records: copy only what the current operation needs

These templates contain **no approvals, measured results, provider tasks or spending
authorization**. Copy them into the versioned candidate folder when production is
authorized; do not edit the templates to track a live hero.

| Template | Populate when | Notes |
|---|---|---|
| [candidate.json](candidate.json) | G0 intake | Identity, dependencies, intended use, ownership, actual stage state and evidence |
| [lighting-profile.json](lighting-profile.json) | G1 comparison | Values are null until measured; do not infer a preset from this file |
| [view-set.json](view-set.json) | G2 four-view preparation | Main/front, anatomical Left, Back and anatomical Right; origin, hashes, consistency review and exact decision |
| [generation-receipt.json](generation-receipt.json) | Before/after each external or local generation | Permissions, actual request/task, source/output hashes, cost and rights |
| [material-map.csv](material-map.csv) | G3/G4 import | One row per actual texture binding/channel; retain original colors |
| [animation-cue-sheet.csv](animation-cue-sheet.csv) | G4/G5 | Runtime event ownership, clip/transition/cancel behavior; no duplicate stat authority |
| [audio-cue-sheet.csv](audio-cue-sheet.csv) | G6 | Cue identity, variants, event, rights, processing and actual review |
| [review.md](review.md) | Any review gate | Exact inputs, measured checks, visible/audible observations and actual decision |
| [handoff.md](handoff.md) | End of work or handoff | First incomplete stage, pending job, next bounded operation and exact blockers |
| [camera-set.json](camera-set.json) | G2 camera setup | Fixed pose, anatomical axes, four transforms, framing and output hashes |
| [construction-parts.csv](construction-parts.csv) | G2/G3A | Parts, attachment, rigid/flexible/contact decisions and source |
| [uv-bake.json](uv-bake.json) | G3C | High/low source, UVs, tangents, bake settings and original/derivative maps |
| [budget-profile.json](budget-profile.json) | G0/G7 | Explicit limits, hardware and measured crowd scenarios |
| [source-preflight.json](source-preflight.json) | Before import/reimport | Bundle-relative files, hashes and numeric requirements |
| [unreal-contracts.json](unreal-contracts.json) | G4/G7 | Opt-in Unreal object requirements; empty maps fail |
| [revision-recovery.json](revision-recovery.json) | G7 delivery | Controlled edit, rebuild, cold reopen and independent recovery |

## Filling rules

- Use repository-relative paths, forward slashes and real SHA-256 values. Paths in
  JSON are project-relative, not relative to wherever the shell happens to run.
  Exception: paths inside a source preflight manifest are relative to its explicitly
  selected bundle root, as required by the source checker CLI.
- Use ISO 8601 timestamps with timezone. If a source event time is unknown, write
  null and state when the record was made. Never invent a user's approval timestamp.
- `null` means unknown/not supplied; `0` means measured zero. Empty lists mean no
  recorded items, not a passed check. `not_run` means unexecuted, not successful.
- Stage states: `not_started`, `working`, `awaiting_review`, `accepted_current`,
  `rejected`, `blocked`, `stale`. These are operational records, not automatic AS1
  ledger promotion. Attach technical/visual/human evidence separately.
- Check states: `not_run`, `pass`, `fail`, `not_applicable_with_reason`, `stale`.
- Record unresolved anatomy, budget and hardware facts explicitly with the stage
  that needs the decision. Do not hide an unresolved choice inside a confident prompt.
- An approval record needs exact user words, scope and the manifest of the candidate
  actually reviewed. Provider success and an agent's opinion cannot fill that field.
- Keep original provider response/settings when safe, but redact keys, bearer tokens,
  signed download credentials, billing details and unrelated private account data.
- Save meaningful versioned records. Never overwrite an approval snapshot or raw
  download to make it match a revised candidate.

## Hash commands — read-only examples from the repository root

For four-view sets, follow [FOUR_VIEW.md](../FOUR_VIEW.md). `origin_kind` should name
the actual source, such as `original_reference`, `exact_crop`, `authored_view`,
`ai_inferred_view` or `existing_model_render`; record parent files and transformations.
The template's slot labels are defaults, not evidence that images exist. Keep
`ready_for_submission` false until the exact set is reviewed and actual preflight
passes; view readiness does not grant credits or replace the G1 dependency. Geometry
and texture receipts record their actual sets separately, even when the files match.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'data/vnext/catalog.json'
Get-FileHash -Algorithm SHA256 -LiteralPath 'path/to/actual/source.glb'
```

Replace the second path with an existing file before running. Hash all dependencies
named in the candidate, including relevant Unreal `.uasset`/`.umap`, recipes, audio,
textures and package files. A hash is evidence of identity, not evidence of quality.

For the handbook dependency, save the documentation validator's `file_hashes` into
the candidate's `recipes/handbook-manifest.json` and hash that file too. Record its
path/hash in `handbook.manifest_path` and `handbook.manifest_sha256`. This binds the
candidate to every stage manual and template, not just the entry page. Preserve
that snapshot when the shared handbook changes.

## AS1 report helper — real CLI semantics

From the project root, using an existing asset workspace and a supported stage:

```powershell
& .venv/Scripts/python.exe production/asset-studio/tools/asset_studio/assetctl.py report-template --workspace art-source/asset-studio/wc_vn_cragstoat --stage forms --output reports/FORMS_REVIEW_r001.json
```

This is an example, not an instruction to initialize or accept Cragstoat now.
`--output` is relative to the selected asset workspace: do not repeat the workspace
prefix or it will create a nested path. Read `--help` for the installed CLI before
prepare/approve. Prepare only a completed report with actual observations; never
invoke an agent-generated human approval. See the handbook's AS1 correspondence
for the Blender-free route amendment and older route limitations.
