# Wonder Chess Asset Studio AS1 local integration

The supplied workflow is installed at `production/asset-studio/`, with 22 `wca-*` skills copied into `.agents/skills/`. The existing repository instructions were extended by a reviewed AS1 appendix, and `wc-blender-asset` now routes substantial asset work through `wca-orchestrate`. The current Ada meshes, gameplay and canonical data were not modified by this integration lane.

This report records local execution. The inherited `reports/VALIDATION.md`, `reports/validation.json` and original `FILE_MANIFEST.json` remain as shipped and describe their original authoring run.

## Input and installation verification

- Source ZIP: `C:/Users/iputu/Downloads/Wonder_Chess_Asset_Studio_AS1.zip`.
- ZIP SHA256: `6dd0f7752330ecf6155696ab01c939ef77ef9ff4b10e72d7da0e6c42442a61cf`.
- All 113 ZIP files passed CRC inspection. All 112 manifest-listed files matched byte counts and SHA256 hashes before extraction; the manifest excludes itself.
- Extraction removed only the single `Wonder_Chess_Asset_Studio_AS1/` archive root. Paths were checked for traversal, absolute/drive names, duplicate/case-fold names, symlinks, reparse ancestors and existing output collisions before writes.
- All 44 files for the 22 newly installed skills still match the supplied hashes. Skill files are installed and readable; fresh Codex interface auto-discovery is not proven by file presence and is not claimed here.
- The original package includes nine routes, 11 prompt templates and six helper scripts. The synthetic route test exercised all nine routes locally.

## Focused local corrections

1. The shipped ledger accepted a minor-defect waiver with only a reason, although the system contract also requires affected use, an owner and later action. `assetctl.py` now requires nonempty `reason`, `affected_use`, `owner` and `later_action`; the review schema and CLI documentation agree. Regression coverage checks valid acceptance and 16 invalid field values in both the ledger and schema. Critical and major defects remain blocked.
2. Initial Blender background smoke loaded saved user add-ons, including BlenderMCP registration, despite `--disable-autoexec`. The runner now places `--factory-startup` before the explicitly loaded source. The command regression confirms this ordering. The tool-verification lane preserved the before/final logs and independently verified five fresh Blender 5.1.1 operations: reference setup, geometry audit, reference audit, clay rendering and material rendering. All exited 0, source file hashes remained unchanged, and saved add-on registration messages were absent. The tool agent inspected four actual final captures; see `reports/AS1/tool-verification/final-execution-results.json` and `VISUAL_REVIEW.md` from repository root.

The original manifest is intentionally unchanged. Exact original and local hashes for the five modified package files are in `local-integration.json`; the other 107 manifest-listed package files remain identical. The three Blender-side scripts are unchanged from the archive.

## Actual checks

| Command / location | Local result | Evidence |
|---|---|---|
| `python -m unittest discover -s tests -v` in original package | 52 run: 51 passed, 1 skipped; exit 0 | `local-integration-as1-original.txt` |
| Same suite after local corrections | 53 run: 52 passed, 1 skipped; exit 0 | `local-integration-as1-final.txt` |
| `python tools/validate_kit.py` at repo root | 400 checks passed; exit 0 | `local-integration-root-validate-kit.txt` |
| `python -m unittest discover -s tests -v` at repo root | 147 passed; exit 0 | `local-integration-root-unit-tests.txt` |
| `python tools/build_documents.py --check` | 28 generated documents match; exit 0 | `local-integration-root-build-documents.txt` |
| `python tools/compile_catalog.py --check` | 6 catalog artifacts match; exit 0 | `local-integration-root-compile-catalog.txt` |
| `git diff --check -- AGENTS.md .agents/skills/wc-blender-asset/SKILL.md` | Passed; exit 0 | Recorded in `local-integration.json` |

Both package-suite runs skipped the symlink-escape test because this Windows process could not create the test symlink. They emitted an existing Pillow `getdata` deprecation warning. Neither is represented as an executed pass. No dependency installation was needed.

## Ownership and remaining asset gates

The parent lane owns `art-source/asset-studio/wc_u_human_guardian/` and `reports/implementation_state.json`. The tool lane owns `reports/AS1/tool-verification/`. Consult those records for the new Ada reference packet and actual Blender/Unreal capability probes. This integration did not create any human approval, sculpt Ada, rig, import, reimport or package an asset. A passing ledger fixture does not approve any real stage. Human reference, forms and release decisions remain required by the adopted workflow.

No files were staged or committed. Pre-existing working-tree changes are recorded in `local-integration.json` and were preserved.
