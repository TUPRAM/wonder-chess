import bpy,bmesh,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;tag=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'initial';src=R/('ada_bw6_balanced_collar_'+tag+'.blend');sha=hashlib.sha256(src.read_bytes()).hexdigest();records=[]
def load():
    bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);return s
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
def setup(s,target,loc,scale):
    s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.use_nodes=False;s.render.use_sequencer=False
    cam=bpy.data.objects['BW4_Camera_shoulder'];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.camera=cam
def capture(s,label):
    path=R/'captures'/(tag+'_'+label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);records.append({'image':str(path),'frame':s.frame_current,'camera_matrix':list(map(list,s.camera.matrix_world)),'scale':s.camera.data.ortho_scale})
for variant in ['clay','cage','cutaway','context']:
    s=load();o=bpy.data.objects['BW6_CollarBalanced_CoatCandidate']
    if variant!='context':
        for q in s.objects:
            if q.type=='MESH':q.hide_render=q!=o
    for q in s.objects:
        if q.type=='MESH' and not q.hide_render:
            q.data.materials.clear();q.data.materials.append(mat('ReviewClay',(.62,.62,.62)))
    if variant=='cage':
        for m in o.modifiers:
            if m.type in ['SUBSURF','SOLIDIFY']:m.show_render=False
        o.data.materials.append(mat('ControlEdges',(.025,.025,.025)));wire=o.modifiers.new('Actual control surface','WIREFRAME');wire.use_replace=False;wire.use_even_offset=False;wire.thickness=.00055;wire.material_offset=1
    if variant=='cutaway':
        ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(ev);q=bpy.data.objects.new('TEMP_actual_collar_cutaway',mesh);s.collection.objects.link(q);q.matrix_world=o.matrix_world.copy();o.hide_render=True
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z<1.425 or f.calc_center_median().y>-.05],context='FACES');bm.to_mesh(mesh);bm.free()
        setup(s,(0,-.08,1.50),(1.3,3,2.05),.36)
    elif variant=='context':setup(s,(0,-.02,1.40),(2.2,3.6,2.15),.65)
    else:setup(s,(0,-.015,1.47),(1.4,3,1.9),.41)
    capture(s,variant)
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
(R/'records'/('balanced_'+tag+'_captures.json')).write_text(json.dumps({'source':str(src),'sha256':sha,'source_unchanged':True,'captures':records},indent=2));print('COLLAR_CAPTURES_COMPLETE')
