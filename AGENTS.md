# Wonder Chess project instructions

## Adopted successor programme — 2026-09-10

- The user adopted the full **Wonder Chess — A New Gameplay, Roster, and Production Blueprint** for implementation. `docs/vnext/README.md` is the successor contract; the v3/24-hero documents below remain authority for the preserved `alpha_24` baseline only.
- Implement `wonder_vnext` in this existing Unreal project: a new mythic-storybook roster, asymmetric race/class ecosystems with no fixed final hero count, independent shops, preparation-only player decisions, ten-unit deployment/ten-slot bench, five costs, twelve starting relic designs, and a 35–45-minute full-match target requiring measurement.
- Preserve legacy canonical data, imported assets, packages, Ada/AQ1/AS1 studies, and unrelated working-tree changes. New heroes receive new stable IDs. A six-hero laboratory is an explicitly labeled prototype, not the complete new roster or a release.
- Successor canonical source is `data/vnext/catalog.json`; generate its runtime and dossier outputs through `tools/vnext/catalog.py`. Never describe an authored mechanic, trait, relic, or hero as executed until its actual runtime tests pass.
- M0–M7 acceptance remains evidence-gated. Human reference/forms/release approval, external-player studies, remote hardware, and online operational prerequisites are separate from local code and package checks. Continue independent authorized work when one gate is blocked.
- Use a new art pilot for the successor. The previous Ada correction gates are not dependencies of the new art direction. AS1 ownership, immutable evidence, and human approvals still apply to new assets.

- New independent project. Never modify or reuse VEILMARK code/assets/lore/configuration. Preserve unrelated user files and genuine Wonder Chess progress.
- Active product contract: `docs/MASTER_IMPLEMENTATION_v3.md` with the user-adopted 24-hero amendments in `docs/updates/2026-09-auto-chess-inspired/MASTER_UPDATE.md`. First release is a playable eight-seat Unreal bot alpha, NOT a website. Read the relevant focused contract/task before editing.
- Canonical source: `data/units.json`, `data/rules.alpha.json`, `data/traits.json`, `data/world.json`, `data/bots.json`. Do not independently hard-code stats into dossiers, widgets or Blueprints. Edit source, regenerate, validate.
- Runtime/art set: exactly all 24 authored heroes in `alpha_unit_ids`, plus seven original neutral archetypes for monster rounds. The user adopted the update on 2026-09-06; execute WC-U400–460. Preserve existing twelve-hero progress while completing the full roster. Equipment remains visual only.
- Tests: `python tools/validate_kit.py`; `python -m unittest discover -s tests -v`; `python tools/build_documents.py --check`; `python tools/compile_catalog.py --check`.
- Runtime: Unreal C++ rules plus Blueprint/presentation where useful. Python is authoring/editor/reference tooling only. Off-screen bot-versus-bot fights must use actual combat, not strength-score outcomes.
- Evidence: distinguish authored, executed, imported, visually reviewed, packaged and verified. Never invent results. Missing tools block the corresponding gate, not unrelated work.
- One owner per canonical file/binary. No concurrent edits to `.blend`, `.uasset`, `.umap`, shared schema or generated manifests. Use checkpoints and bounded tasks.
- No paid services, unlicensed media, public deployment, secret exposure or security bypass. No hidden bot stat/economy advantages or runtime LLM dependency.
- Record actual state in `reports/implementation_state.json`. Continue unblocked implementation within the authorized task; leave a precise handoff on real limits. Do not promise asynchronous work.
- Use installed versions and official docs; do not assume a model name or third-party bridge grants editor access. Local Windows launch wrappers are candidates until actually run.

## Asset Studio AS1 art workflow

For art production or substantial likeness correction, use `$wca-orchestrate` and the active asset manifest under `art-source/asset-studio/<asset_id>/`. Read only the relevant stage manual and direct dependencies.

Treat `production/asset-studio/` as an art workflow package, not a new game master. Preserve stable gameplay IDs, abilities, stats, runtime behavior and existing canonical assets unless a reviewed art change explicitly requires a compatible integration update. Never restart the repository or silently reduce an already implemented roster.

Source art, tool execution, technical acceptance and human art acceptance are distinct. Do not claim quality from file count, polygon count, a successful script, or an image path not actually viewed. Do not self-issue human approval. Keep candidate outputs separate until approval and measured Unreal review. Never fake model sheets, measured profile results, source hashes, imports or capture metadata.

One writer per `.blend`/rig family and one queue per Blender session. Inspect before retry after timeout. Do not execute remote scripts, expose MCP on public interfaces, upload private art, purchase services or change broad permissions without authorization.

If two bounded revisions do not improve a critical visual defect, change the modeling method or escalate; do not keep smoothing the same failed design. Stop the affected stage at a hard gate while continuing independent authorized work. A tool not present is blocked, not passed.
