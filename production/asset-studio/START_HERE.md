# Wonder Chess Asset Studio — AS1
## A likeness-first production system, not an automatic character generator

**Version:** 1.0.0 · **Prepared:** 2026-09-08 · **Scope:** art workflow for the existing Wonder Chess repository.

Start with `FIRST_MESSAGE_TO_CODEX.md` and `docs/00_SYSTEM.md`. This package replaces the broad art-task routing only after integration review. It does not replace game rules, roster data, the repository, working rigs or validated exports. The previously supplied game master is background, not authority to restart the project.

## What is included

- Specialized Codex `SKILL.md` procedures for orchestration, references, organic and hard-surface modeling, costume/hair, likeness review, retopology, UV/baking, materials, rigging, skinning, animation, optimization, Unreal validation, environment, FX/UI, audio and release.
- Focused production manuals, class-specific routes, evidence contracts, an Ada pilot and prompt templates.
- A runnable standard-library gate ledger, image crop/comparison utility and explicit Blender process runner.
- Three Blender-side helper scripts: reference setup, scene observations and fixed-camera renders. They require local Blender validation; they are not finished model generators.
- Real native-pixel crops of the user-supplied Ada concept, plus the user-supplied rejected render, labeled as references rather than new art.
- Tests and a validation report describing what actually ran here.

## Install without overwriting the project

1. Put this directory at `<wonder-chess>/production/asset-studio/`.
2. Inspect the existing repository's `AGENTS.md`, nested instructions and working tree. Do not overwrite them.
3. Copy only the new `wca-*` skill directories from this package's `.agents/skills/` into the repository's `.agents/skills/`. Stop on any name collision and review differences. No bundled command performs this installation automatically.
4. Merge the small `AGENTS_APPENDIX.md` guidance by review. Existing `wc-blender-asset` should route substantial art work through `wca-orchestrate`; do not let two conflicting workflows compete.
5. Run the self-tests from this package directory: `python -m unittest discover -s tests -v`.
6. Confirm skill discovery in the installed Codex interface. File presence alone does not prove discovery or tool access.

Use Python 3.10+ for standalone helpers. `assetctl.py` is standard-library only. `image_review.py` needs Pillow; optional schema tests need jsonschema. Install dependencies into a project environment, not global Python. No paid or external service is required for the ledger.

## First asset workspace

From repository root:

```powershell
python production/asset-studio/tools/asset_studio/assetctl.py init --workspace art-source/asset-studio/wc_u_human_guardian --asset-id wc_u_human_guardian --kind hero --name "Ada Brightshield"
python production/asset-studio/tools/asset_studio/assetctl.py status --workspace art-source/asset-studio/wc_u_human_guardian
```

The initializer refuses a populated directory. It does not touch the current canonical Ada. Copy relevant references into this new workspace and fill the contract before review. Do not copy the synthetic test ledger into an actual asset workspace.

## Assurance boundary

No prompt or script guarantees subjective artistic quality or an error-free game asset. This system makes stages explicit, blocks declared unresolved defects, and invalidates stale evidence. Human approval at references, forms and release is required. The local signoff ledger records who was declared to approve; it **does not authenticate that person** or prevent an agent with filesystem permissions from bypassing it. A protected review service or human-owned approval directory is the stronger operational option.

The package does not contain a new sculpted Ada, executable game, rig or deployed MCP server. No Blender/Unreal runtime test was performed while authoring it. See `reports/VALIDATION.md` for exact results.
