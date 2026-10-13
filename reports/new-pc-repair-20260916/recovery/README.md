# Exact missing-file recovery — 16 September 2026

Recovered **424 of 709 original missing files**, using only exact size and SHA-256 matches to the unchanged `TRANSFER_MANIFEST.jsonl`. **285 original payloads remain unrecovered**, including **9 active source files**.

## Verified result

- Recovery never overwrote existing files, reset/checked out/staged Git content, changed gameplay, or replaced older sources under current names.
- Each recovery records its source and verifies the written bytes in [restored.jsonl](restored.jsonl).
- Final rehash statuses: `{'restored_exact': 423, 'missing': 284, 'restored_then_intentionally_updated_by_main_agent': 1, 'newly_generated_cache_not_recovered': 1}`.
- The main agent intentionally updated the restored `tools/blender/Start-Mcp.ps1` for the installed Blender path; its original matching bytes and restoration source remain recorded.
- A cache produced by running Python is classified separately from an exact historical recovery.
- `git fsck --full` after recovery exited **0**. The recovered capture ref points to the existing tree object; index and branch refs remain untouched by recovery.

## Active source files still requiring original backup

| Path | Original bytes |
|---|---:|
| `tests/runtime/run_vnext_balance_experiment.ps1` | 3536 |
| `tests/runtime/vnext_balance_experiment.cpp` | 29604 |
| `tools/verify_transfer.py` | 5942 |
| `tools/unreal/create_combat_cue_material.py` | 1462 |
| `tools/unreal/import_art_slice.py` | 5004 |
| `tools/unreal/import_storybook.py` | 4602 |
| `tools/unreal/launch_milestones.ps1` | 4316 |
| `tools/vnext/analyze_mana_experiment.py` | 5766 |
| `tools/vnext/verify_milestone_package.py` | 16787 |

## Search performed

- Existing manifest-identical copies, including preserved older checkouts.
- All available Git object metadata and eligible blobs, including dangling objects; original, LF, and CRLF representations.
- 302,360 bounded newline/BOM/ref representations across 5,005 distinct normalized text blobs. This recovered the mixed-newline `tests/test_vnext_catalog.py` and the missing capture tree ref.
- Unreachable Git trees indexed by missing source filenames; some retained versions predate the missing current files.
- Size-matched files across this project, Downloads and Desktop; 16 local ZIP archives. No additional matches.

## Remaining payload and boundaries

- [Full unresolved inventory with expected sizes/hashes](unresolved.json)
- [Final audit of all 709 original missing paths](final-path-audit.json)
- [Machine-readable summary](summary.json)
- [Post-recovery Git integrity output](git-fsck-after.txt)

The remainder includes historical Python caches/dependencies, migration evidence, download archives, validation evidence, and two files in the preserved r6 clean-study package. They are not declared disposable or recovered. A complete original folder or backup is required to finish exact recovery. The retained playable candidate packages were not changed. This report does not claim complete transfer integrity or a complete authoring/test pass.
