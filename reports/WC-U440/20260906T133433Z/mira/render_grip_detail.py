import sys
from pathlib import Path
import bpy
from mathutils import Vector
root=Path.cwd();out=Path(__file__).resolve().parent/'refinement-v7'
sys.path.insert(0,str(root/'tools/blender'))
from refine_update_ada import components
bpy.ops.wm.open_mainfile(filepath=str(out/'mira-update24-revision7.blend'))
uid='wc_u_human_priest';arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid]
action=bpy.data.actions['AN_'+uid+'_Idle'];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
part=next(p for p in components(mesh) if p['groups']==['hand_r'] and p['count']==70)
evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());deformed=evaluated.to_mesh()
target=sum((evaluated.matrix_world@deformed.vertices[i].co for i in part['indices']),Vector())/len(part['indices'])
evaluated.to_mesh_clear();scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=512
scene.render.resolution_percentage=100;scene.cycles.samples=16;scene.camera.data.ortho_scale=.45
for name,offset in (('front',(0,3,.8)),('side',(3,1,.8))):
    path=out/f'grip-{name}.png';assert not path.exists()
    scene.camera.location=target+Vector(offset)
    scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
print('WC_MIRA_GRIP_DETAIL_RENDERED',flush=True)
