"""Create a temporary review scene, link explicit source objects, render, remove review scene.
Does not save or remodel the source. Uses current pose; reference-pose conversion is NOT implicit.
Unexecuted in Blender at kit authoring. Review color/normal settings against installed version.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,uuid
from pathlib import Path
import bpy
from mathutils import Vector

def main():
    p=argparse.ArgumentParser();p.add_argument('--collection',required=True);p.add_argument('--cameras',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--clay',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(a.cameras.read_text())
    c=bpy.data.collections.get(a.collection)
    if c is None:raise ValueError('Explicit candidate collection not found.')
    if a.out.exists() and any(a.out.iterdir()):raise ValueError('Use an empty/new render directory.')
    a.out.mkdir(parents=True,exist_ok=True);original_scene=bpy.context.scene;frame=original_scene.frame_current
    scene=bpy.data.scenes.new('AS1_REVIEW_'+uuid.uuid4().hex[:10]);owned=[];owned_data=[];clay=None;world=None
    try:
        for ob in c.all_objects:
            if ob.type in {'MESH','ARMATURE','EMPTY'}:scene.collection.objects.link(ob)
        scene.frame_set(frame);scene.render.engine=cfg.get('engine','CYCLES')
        if scene.render.engine=='CYCLES':scene.cycles.samples=int(cfg.get('samples',32))
        scene.render.resolution_x,scene.render.resolution_y=map(int,cfg['resolution']);scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
        scene.view_settings.view_transform=original_scene.view_settings.view_transform
        scene.view_settings.look=original_scene.view_settings.look
        scene.view_settings.exposure=original_scene.view_settings.exposure;scene.view_settings.gamma=original_scene.view_settings.gamma
        world=bpy.data.worlds.new(scene.name+'_World');world.use_nodes=True;scene.world=world
        world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0.055,0.055,0.055,1)
        world.node_tree.nodes.get('Background').inputs['Strength'].default_value=0.35
        target=Vector(cfg['center']);h=float(cfg['height_m'])
        for name,loc,energy,size in [('Key',(2*h,3*h,3*h),800,2*h),('Fill',(-2*h,2*h,1.5*h),450,2*h),('Rim',(0,-2*h,2.5*h),600,2*h)]:
            d=bpy.data.lights.new(scene.name+'_'+name,'AREA');d.energy=energy;d.size=size
            ob=bpy.data.objects.new(d.name,d);scene.collection.objects.link(ob);owned.append(ob);owned_data.append(d)
            ob.location=loc;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
        d=bpy.data.cameras.new(scene.name+'_Camera');cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam)
        owned.append(cam);owned_data.append(d);scene.camera=cam;d.type='ORTHO';d.ortho_scale=float(cfg['ortho_scale']);d.dof.use_dof=False
        if a.clay:
            clay=bpy.data.materials.new(scene.name+'_Clay');clay.use_nodes=True
            shader=clay.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.40,.40,.40,1);shader.inputs['Roughness'].default_value=.7
            scene.view_layers[0].material_override=clay
        evidence=[]
        for view in cfg['views']:
            cam.location=view['location'];cam.rotation_euler=(Vector(view.get('target',cfg['center']))-cam.location).to_track_quat('-Z','Y').to_euler()
            d.ortho_scale=float(view.get('ortho_scale',cfg['ortho_scale']))
            path=a.out/(view['id']+'.png');scene.render.filepath=str(path)
            bpy.ops.render.render(write_still=True,scene=scene.name)
            evidence.append({'view':view['id'],'image':path.name,'camera_location':list(cam.location),'target':view.get('target',cfg['center']),'ortho_scale':d.ortho_scale})
        (a.out/'render_metadata.json').write_text(json.dumps({'status':'rendered_not_visually_approved','frame':frame,'blender_version':bpy.app.version_string,'clay':a.clay,'cameras':evidence,'view_transform':scene.view_settings.view_transform,'exposure':scene.view_settings.exposure,'source_collection':a.collection,'source_blend_name':Path(bpy.data.filepath).name if bpy.data.filepath else None,'source_blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() if bpy.data.filepath and Path(bpy.data.filepath).is_file() else None},indent=2)+'\n')
    finally:
        bpy.data.scenes.remove(scene)
        for ob in owned:
            if ob.name in bpy.data.objects:bpy.data.objects.remove(ob,do_unlink=True)
        for d in owned_data:
            if d.users==0:
                if isinstance(d,bpy.types.Camera):bpy.data.cameras.remove(d)
                elif isinstance(d,bpy.types.Light):bpy.data.lights.remove(d)
        if world and world.users==0:bpy.data.worlds.remove(world)
        if clay and clay.users==0:bpy.data.materials.remove(clay)
        original_scene.frame_set(frame)
    print('AS1_REVIEW_RENDERED',str(a.out))
if __name__=='__main__':main()
