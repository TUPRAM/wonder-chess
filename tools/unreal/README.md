# Unreal handoff helpers

## Status
No Unreal project, imported asset, engine compilation or PowerShell execution was performed while creating this kit. `generated/unreal/WCDataRows.h` and the JSON tables are **generated import candidates**, not validated `.uasset` files. `package_game.ps1` is an unexecuted Windows wrapper.

## Local integration sequence
1. Record installed engine, C++ toolchain and Windows SDK; create the new `WonderChess` project and package a minimal map.
2. Regenerate the catalog with `python tools/compile_catalog.py`. Add the generated header to the runtime module, adapt the module export macro only if required, and compile its reflected row structures.
3. Create one DataTable of `FWCUnitRow` and one of `FWCAbilityRow` using the actual names in the header (read it; do not guess). Import the corresponding Alpha JSON files. Validate every field and ID after import, not just the record count.
4. Build explicit presentation data assets for the twelve alpha IDs. Do not generate engine soft-object paths from display names or assume a mesh exists because its planned path is in the manifest.
5. Implement combat/economy/tournament from the contracts. Port arithmetic/transaction fixtures; the Python reference is not the shipped runtime.
6. Set project default maps, asset manager/cooking references and language resources. Run the wrapper only after confirming the installed UAT options and local paths. Review actual logs and launch the archive outside the source tree.

Suggested environment names: `BLENDER_EXE`, `UE_EDITOR_EXE`, `UE_UAT_SCRIPT`, `WONDER_CHESS_ROOT`. Do not store passwords or license tokens in this kit. Do not silence import warnings or edit imported balance values independently from `data/`.

The kit intentionally does not include a speculative “one-click” Unreal Python importer that assumes a particular installed API or existing row-structure asset. Codex must implement and execute the narrow importer after the actual module and editor environment are known. Editor automation is not runtime Python gameplay.
