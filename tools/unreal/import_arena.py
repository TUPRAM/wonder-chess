"""Import original modular courtyard and create a compact surface material."""
from pathlib import Path
import runpy
import json
import math
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
helpers = runpy.run_path(str(ROOT/'tools/unreal/import_alpha_assets.py'))
task, settings = helpers['task'], helpers['fbx_settings']
folder='/Game/WonderChess/Arena'
material=helpers['hero_material']('wc_seven_lantern_courtyard',folder,ROOT/'exports/arena')
records=[]
for path in (ROOT/'exports/arena').glob('SM_*.fbx'):
    options=settings('static')
    options.static_mesh_import_data.combine_meshes=True
    meshes=task(path,folder,path.stem,options,unreal.FbxFactory())
    for mesh in meshes:
        if not isinstance(mesh,unreal.StaticMesh): continue
        mesh.set_material(0,material)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        bounds=mesh.get_bounding_box()
        size=bounds.max-bounds.min
        records.append({'path':mesh.get_path_name(),'size_cm':[size.x,size.y,size.z]})

assets=unreal.AssetToolsHelpers.get_asset_tools()
surface=unreal.load_asset('/Game/WonderChess/Materials/M_WC_Surface')
if not surface:
    surface=assets.create_asset('M_WC_Surface','/Game/WonderChess/Materials',unreal.Material,unreal.MaterialFactoryNew())
    color=unreal.MaterialEditingLibrary.create_material_expression(surface,unreal.MaterialExpressionVectorParameter,-300,0)
    color.set_editor_property('parameter_name','Color')
    color.set_editor_property('default_value',unreal.LinearColor(.5,.5,.5,1))
    unreal.MaterialEditingLibrary.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(surface)
    unreal.EditorAssetLibrary.save_loaded_asset(surface)
out=ROOT/'reports/WC-330/arena-import.json'
out.write_text(json.dumps({'engine':unreal.SystemLibrary.get_engine_version(),'modules':records,'status':'imported_needs_visual_review'},indent=2)+'\n')
if len(records)!=13: raise RuntimeError('Expected 13 actual imported courtyard modules')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
layout=json.loads((ROOT/'exports/arena/courtyard_layout.json').read_text())
for map_path in ['/Game/WonderChess/Maps/L_WC_Menu','/Game/WonderChess/Maps/L_WC_Courtyard']:
    if not levels.load_level(map_path): raise RuntimeError('Cannot open '+map_path)
    for actor in actors.get_all_level_actors():
        if 'WCArena' in [str(t) for t in actor.tags]: actors.destroy_actor(actor)
    for record in layout['instances']:
        name=record['module']
        mesh=unreal.load_asset(folder+'/'+name)
        p=record['location_m']; e=record['rotation_euler_radians']; s=record['scale']
        actor=actors.spawn_actor_from_object(mesh,unreal.Vector(p[1]*100,p[0]*100,p[2]*100),unreal.Rotator(pitch=math.degrees(e[0]),yaw=-math.degrees(e[2]),roll=-math.degrees(e[1])))
        actor.set_actor_scale3d(unreal.Vector(s[1],s[0],s[2]))
        actor.set_actor_label(record['instance'])
        actor.tags=['WCArena']
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if not levels.save_current_level(): raise RuntimeError('Cannot save '+map_path)
unreal.log('WC_ARENA_IMPORT_PASS modules='+str(len(records)))
