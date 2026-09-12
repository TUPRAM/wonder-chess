import bpy,json
from mathutils import Vector
assert bpy.context.scene.name=='MR1_FACE_PROOF'
scene=bpy.context.scene;col=bpy.data.collections['MR1_FACE_CANDIDATE_ALLOWLIST']
skin=bpy.data.objects['MR1_Right_Orbital_Cage'];globe=bpy.data.objects['MR1_Right_Eye_Globe']
key=bpy.data.objects['MR1_FACE_Key'];fill=bpy.data.objects['MR1_FACE_Fill'];key.data.energy=1.3;fill.data.energy=.32
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
wire=skin.copy();wire.name='MR1_FACE_Control_Cage_Wire';wire.modifiers.clear();wire.data=skin.data.copy()
wire.data.materials.clear();wire.data.materials.append(bpy.data.materials['MR1_Cage_Dark'])
col.objects.link(wire);w=wire.modifiers.new('Actual control edges','WIREFRAME');w.thickness=.00018;w.offset=1;w.use_replace=True
wire.hide_render=True;wire.hide_set(True)
base=bpy.data.scenes.new('MR1_FACE_BASELINE_REVIEW');bc=bpy.data.collections.new('MR1_FACE_BASELINE_ALLOWLIST');base.collection.children.link(bc)
for name in ['ADA_Head_Continuous','ADA_Fitted_Eye_R','ADA_Fitted_Brow_R']:
    src=bpy.data.objects[name];o=src.copy();o.data=src.data.copy();o.name='MR1_BASE_'+name;bc.objects.link(o)
    o.hide_render=False
for o in col.objects:
    if o.type in ['CAMERA','LIGHT']:bc.objects.link(o)
base.render.engine=scene.render.engine;base.cycles.samples=16;base.cycles.use_denoising=True
base.render.resolution_x=900;base.render.resolution_y=900;base.render.resolution_percentage=100
base.world=scene.world;base.view_settings.view_transform='Standard';base.view_settings.look='None'
base.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
target=Vector((.039,.025,1.687))
def light(reverse=False):
    key.location=(.328 if reverse else -.25,.35,1.95)
    fill.location=(-.202 if reverse else .28,.23,1.77)
    for o in [key,fill]:o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
def render(sc,name,view):
    sc.camera=bpy.data.objects['MR1_FACE_'+view];sc.render.filepath=root+'/captures/'+name+'_'+view+'.png'
    bpy.ops.render.render(write_still=True,scene=sc.name)
for view in ['front','profile','three_quarter','opposite']:
    render(scene,'face_r001_gaze',view)
    scene.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
    render(scene,'face_r001_clay',view)
    scene.view_layers[0].material_override=None
    render(base,'face_baseline_clay',view)
scene.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay'];globe.hide_render=True
render(scene,'face_r001_opening','three_quarter');globe.hide_render=False
scene.view_layers[0].material_override=None
wire.hide_render=False
skin.modifiers[0].show_render=False
render(scene,'face_r001_cage','three_quarter')
skin.modifiers[0].show_render=True
render(scene,'face_r001_cage_surface','three_quarter')
wire.hide_render=True
light(True);scene.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
for view in ['front','three_quarter']:
    render(scene,'face_r001_reverse',view);render(base,'face_baseline_reverse',view)
light(False);scene.view_layers[0].material_override=None
scene.camera=bpy.data.objects['MR1_FACE_three_quarter']
scene['mr1_render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
base['mr1_render_allowlist']=json.dumps([o.name for o in base.objects])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.ops.wm.save_as_mainfile(filepath=root+'/face_proof_r001.blend',copy=True)
print(json.dumps({'capture_sets':'initial gaze/clay/cage/opening/reverse + matched baseline','source_vertices':len(skin.data.vertices),'old_skin_in_proof':False,'proof_saved':'face_proof_r001.blend'}))

