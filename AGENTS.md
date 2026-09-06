# Wonder Chess project instructions

- New independent project. Never modify or reuse VEILMARK code/assets/lore/configuration. Preserve unrelated user files and genuine Wonder Chess progress.
- Active product contract: `docs/MASTER_IMPLEMENTATION_v3.md`. First release is a playable eight-seat Unreal bot alpha, NOT a website. Read the relevant focused contract/task before editing.
- Canonical source: `data/units.json`, `data/rules.alpha.json`, `data/traits.json`, `data/world.json`, `data/bots.json`. Do not independently hard-code stats into dossiers, widgets or Blueprints. Edit source, regenerate, validate.
- Initial runtime/art set: exactly `alpha_unit_ids`. Other heroes are complete expansion designs, not alpha asset obligations.
- Tests: `python tools/validate_kit.py`; `python -m unittest discover -s tests -v`; `python tools/build_documents.py --check`; `python tools/compile_catalog.py --check`.
- Runtime: Unreal C++ rules plus Blueprint/presentation where useful. Python is authoring/editor/reference tooling only. Off-screen bot-versus-bot fights must use actual combat, not strength-score outcomes.
- Evidence: distinguish authored, executed, imported, visually reviewed, packaged and verified. Never invent results. Missing tools block the corresponding gate, not unrelated work.
- One owner per canonical file/binary. No concurrent edits to `.blend`, `.uasset`, `.umap`, shared schema or generated manifests. Use checkpoints and bounded tasks.
- No paid services, unlicensed media, public deployment, secret exposure or security bypass. No hidden bot stat/economy advantages or runtime LLM dependency.
- Record actual state in `reports/implementation_state.json`. Continue unblocked implementation within the authorized task; leave a precise handoff on real limits. Do not promise asynchronous work.
- Use installed versions and official docs; do not assume a model name or third-party bridge grants editor access. Local Windows launch wrappers are candidates until actually run.
