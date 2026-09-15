"""Create the owned unlit combat-cue material; preserve all existing art/materials."""
import json
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir()).resolve().parent
path='/Game/WonderChess/VNext/M_CombatCue'
if unreal.EditorAssetLibrary.does_asset_exist(path):
    raise RuntimeError('Existing cue material must be inspected before replacement')
material=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_CombatCue','/Game/WonderChess/VNext',unreal.Material,unreal.MaterialFactoryNew())
material.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
color=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionVectorParameter,-300,0)
color.set_editor_property('parameter_name','Color')
color.set_editor_property('default_value',unreal.LinearColor(1,.6,.2,1))
if not unreal.MaterialEditingLibrary.connect_material_property(color,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR):raise RuntimeError('Cue color connection failed')
unreal.MaterialEditingLibrary.recompile_material(material)
if not unreal.EditorAssetLibrary.save_loaded_asset(material):raise RuntimeError('Cue material save failed')
(root/'reports/vnext/milestones/combat-clarity-20260913/cue-material.json').write_text(json.dumps({'asset':path,'saved':True,'engine':unreal.SystemLibrary.get_engine_version(),'boundary':'Authored and saved; runtime color review remains required'},indent=2))
