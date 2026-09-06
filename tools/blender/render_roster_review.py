"""Render the authored twelve-unit encounter at the candidate gameplay camera."""
import bpy
from pathlib import Path
import json
import math
root=Path(__file__).resolve().parents[2]
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids']
roster={u['id']:u for u in json.loads((root/'data/units.json').read_text())['units']}
units=[roster[uid] for uid in ids]
if len(units)!=12:raise RuntimeError('Expected exactly twelve alpha source records')
records=[]
for index,unit in enumerate(units):
    source=root/f'art-source/heroes/{unit["id"]}/{unit["id"]}.blend'
    if not source.is_file():raise FileNotFoundError(source)
    with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
        if 'EXPORT' not in available.collections:raise RuntimeError(f'{unit["id"]}: no export collection')
        loaded.collections=['EXPORT']
        loaded.actions=[f'AN_{unit["id"]}_Idle']
    collection=loaded.collections[0];bpy.context.scene.collection.children.link(collection)
    arm=next(ob for ob in collection.objects if ob.type=='ARMATURE')
    arm.animation_data_create();arm.animation_data.action=loaded.actions[0]
    arm.animation_data.action_slot=loaded.actions[0].slots[0]
    arm.location=((index%6-2.5)*2,-1 if index<6 else 1,0)
    arm.rotation_euler.z=0 if index<6 else math.pi
    records.append({'unit_id':unit['id'],'source':str(source.relative_to(root)),
                    'location_m':list(arm.location),'rotation_z_radians':arm.rotation_euler.z})
sc=bpy.context.scene;sc.frame_set(1);sc.cycles.samples=20
for w,h in ((1920,1080),(1280,720)):
    sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.filepath=str(root/f'reports/WC-330/roster/crowded_board_{w}x{h}.png')
    Path(sc.render.filepath).parent.mkdir(parents=True,exist_ok=True);bpy.ops.render.render(write_still=True)
report={'status':'actual_blender_gameplay_camera_render_not_engine_acceptance','count':len(records),'records':records,
        'camera_name':sc.camera.name,'not_proven':['real combat motion','UI overlap','Unreal appearance','frame time']}
(root/'reports/WC-330/roster/crowded_board.json').write_text(json.dumps(report,indent=2)+'\n')
print('WC_CROWDED_RENDER_COMPLETE',flush=True)
