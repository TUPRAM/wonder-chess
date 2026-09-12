"""Fixed-camera AQ1 evidence; operates only on explicitly opened candidate copies."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,use_clip

def material(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m

def setup():
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    for o in scene.objects:
        if o.type=='LIGHT' or o.name.startswith('PRESENTATION_'):o.hide_render=True
    world=bpy.data.worlds.new('AQ1_NeutralWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.15,.19,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;scene.world=world
    for name,loc,power,size in [('Key',(-3,4,5),420,3),('Fill',(3,2,3),240,3),('Rim',(1,-3,4),480,2.5)]:
        d=bpy.data.lights.new('AQ1_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size
        ob=bpy.data.objects.new(d.name,d);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.025));ground=bpy.context.object;ground.name='AQ1_ReviewGround';ground.data.materials.append(material('AQ1_Ground',(.22,.235,.26),.85))
    cam=bpy.data.cameras.new('AQ1_FixedCamera');cam.type='ORTHO';ob=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(ob);scene.camera=ob
    return scene

VIEWS={
 'front':((0,5,1.1),(0,0,.95),2.3),
 'side':((5,0,1.1),(0,0,.95),2.3),
 'back':((0,-5,1.1),(0,0,.95),2.3),
 'three_quarter':((-3,5,2.4),(0,0,.95),2.3),
 'board':((0,5,6.96),(0,0,.95),2.45),
 'face':((-.3,4,1.76),(0,.025,1.65),.48),
 'grip':((-2.5,4,1.1),(-.60,.15,.75),.42),
 'shoulder':((-2,4,1.95),(-.33,0,1.38),.58),
 'shield_back':((2,-4,1.4),(.58,.25,1.01),1.1),
 'blade_edge':((-2,4,1.3),(-.6,.17,1.02),.72),
}

def render_view(scene,path,view,size=900):
    loc,target,scale=VIEWS[view];cam=scene.camera;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    scene.render.resolution_x=size;scene.render.resolution_y=size;scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)

def metadata():
    arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    result={'blender':bpy.app.version_string,'source':bpy.data.filepath,'skeleton_and_curves':invariants(arm),'rest_bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(r) for r in b.matrix_local],'parent':b.parent.name if b.parent else None} for b in arm.data.bones},'meshes':[],'actions':{a.name:list(a.frame_range) for a in bpy.data.actions}}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        o.data.calc_loop_triangles()
        result['meshes'].append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'materials':[m.name for m in o.data.materials if m],'uv_layers':[u.name for u in o.data.uv_layers],'hide_render':o.hide_render,'bounds_local':[list(c) for c in o.bound_box]})
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--views',default='front,side,back,three_quarter,board,face,grip,shoulder,shield_back,blade_edge');p.add_argument('--clay',action='store_true');p.add_argument('--save',action='store_true');p.add_argument('--size',type=int,default=900);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    relinks=[]
    for image in bpy.data.images:
        if image.source=='FILE' and image.filepath.startswith('//'):
            original=(ROOT/'art-source/heroes/wc_u_human_guardian'/image.filepath[2:]).resolve()
            if original.is_file():
                relinks.append({'image':image.name,'original_relative':image.filepath,'resolved':str(original),'sha256':hashlib.sha256(original.read_bytes()).hexdigest()})
                image.filepath=str(original);image.reload()
    (out/'texture_relinks.json').write_text(json.dumps(relinks,indent=2))
    (out/'loaded_metadata.json').write_text(json.dumps(metadata(),indent=2))
    arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');use_clip(arm,'Idle');scene=setup()
    for view in a.views.split(','):
        render_view(scene,out/('material_'+view+'.png'),view,a.size)
    render_view(scene,out/'material_thumbnail96.png','board',96)
    if a.clay:
        scene.view_layers[0].material_override=material('AQ1_Clay',(.43,.45,.47),.7)
        for view in ['front','side','back','three_quarter','board','face','grip']:
            render_view(scene,out/('clay_'+view+'.png'),view,a.size)
        scene.view_layers[0].material_override=None
    (out/'camera_contract.json').write_text(json.dumps({'views':VIEWS,'resolution':a.size,'engine':'CYCLES','samples':24,'view_transform':'AgX','exposure':0},indent=2))
    if a.save:bpy.ops.wm.save_as_mainfile(filepath=str(out/'review_scene.blend'))
    print('AQ1_CAPTURE_COMPLETE',str(out),flush=True)

if __name__=='__main__':main()
