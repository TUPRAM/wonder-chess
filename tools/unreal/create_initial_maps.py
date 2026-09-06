"""Executed in the UE 5.7 editor commandlet after the project module compiles."""
import unreal

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for path in ["/Game/WonderChess/Maps/L_WC_Menu", "/Game/WonderChess/Maps/L_WC_Courtyard"]:
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.log("Preserving existing map: " + path)
        continue
    if not levels.new_level(path):
        raise RuntimeError("Cannot create map " + path)
    if not levels.save_current_level():
        raise RuntimeError("Cannot save map " + path)
    unreal.log("WC_MAP_SAVED " + path)
