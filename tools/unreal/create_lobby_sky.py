"""Author the original Brighthaven sky gradient using installed Unreal materials."""
from pathlib import Path
import json
import os
import unreal

folder = '/Game/WonderChess/Lobby'
name = 'M_WC_BrighthavenSky'
material = unreal.load_asset(folder + '/' + name)
if material is None:
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name, folder, unreal.Material, unreal.MaterialFactoryNew())
edit = unreal.MaterialEditingLibrary
edit.delete_all_material_expressions(material)
material.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
material.set_editor_property('two_sided', True)
material.set_editor_property('is_sky', True)

def node(kind, x, y):
    return edit.create_material_expression(material, kind, x, y)

position = node(unreal.MaterialExpressionWorldPosition, -900, 0)
height = node(unreal.MaterialExpressionComponentMask, -700, 0)
for channel in ('r', 'g', 'a'):
    height.set_editor_property(channel, False)
height.set_editor_property('b', True)
scale = node(unreal.MaterialExpressionDivide, -500, 0)
scale.set_editor_property('const_b', 4200.0)
clamp = node(unreal.MaterialExpressionClamp, -300, 0)
horizon = node(unreal.MaterialExpressionConstant3Vector, -300, 200)
horizon.set_editor_property('constant', unreal.LinearColor(.065, .18, .25))
zenith = node(unreal.MaterialExpressionConstant3Vector, -300, 350)
zenith.set_editor_property('constant', unreal.LinearColor(.015, .07, .16))
blend = node(unreal.MaterialExpressionLinearInterpolate, 0, 0)
for source, output, target, input_name in (
    (position, '', height, ''), (height, '', scale, 'A'),
    (scale, '', clamp, ''), (horizon, '', blend, 'A'),
    (zenith, '', blend, 'B'), (clamp, '', blend, 'Alpha')):
    if not edit.connect_material_expressions(source, output, target, input_name):
        raise RuntimeError('Cannot connect sky material: ' + input_name)
if not edit.connect_material_property(blend, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR):
    raise RuntimeError('Cannot connect sky output')
edit.recompile_material(material)
if not unreal.EditorAssetLibrary.save_loaded_asset(material):
    raise RuntimeError('Cannot save original sky material')
report = {'status': 'AUTHORED_REQUIRES_RENDER_CHECK', 'path': material.get_path_name(),
          'engine': unreal.SystemLibrary.get_engine_version(), 'two_sided': True,
          'shading': 'unlit', 'gradient_height_cm': 4200,
          'horizon_linear_rgb': [.065, .18, .25], 'zenith_linear_rgb': [.015, .07, .16]}
(Path(os.environ['WC_EDITOR_REPORT_DIR']) / 'lobby-sky.json').write_text(
    json.dumps(report, indent=2) + '\n', encoding='utf-8')
