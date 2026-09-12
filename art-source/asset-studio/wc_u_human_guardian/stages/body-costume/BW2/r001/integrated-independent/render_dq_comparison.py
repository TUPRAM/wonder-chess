import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
out=Path(__file__).parent;source=out.parent/'grip_integrated_contact_r001.blend';s=bpy.context.scene;sha=hashlib.sha256(source.read_bytes()).hexdigest();rec=json.loads(s['BW2_hand_contract']);F=Matrix(rec['frame_world']);X=F.col[0].xyz;Y=F.col[1].xyz;Z=F.col[2].xyz
body=bpy.data.objects['BW1_IndexedBody'];glove=bpy.data.objects['BW1_Glove_Pair_SourceFit'];armmods=[next(m for m in o.modifiers if m.type=='ARMATURE') for o in [body,glove]];prior=[m.use_deform_preserve_volume for m in armmods]
for o in s.objects:
    if o.type=='MESH':o.hide_render=True
camdata=bpy.data.cameras.new('BW2_AUDIT_back_temp');cam=bpy.data.objects.new('BW2_AUDIT_back_temp',camdata);s.collection.objects.link(cam);camdata.type='ORTHO';camdata.ortho_scale=.235;target=F.translation+Y*.083;loc=target-Z*.45
cam.matrix_world=Matrix(((-X.x,Y.x,-Z.x,loc.x),(-X.y,Y.y,-Z.y,loc.y),(-X.z,Y.z,-Z.z,loc.z),(0,0,0,1)))
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.6,.6,.6);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='Standard'
record={'source_sha256':sha,'original_preserve_volume':dict(zip([body.name,glove.name],prior)),'only_change':'Unsaved Armature use_deform_preserve_volume flags; same pose/weights/mesh/patches/handle','renders':[]}
for mode in ['linear','dq']:
    for m in armmods:m.use_deform_preserve_volume=mode=='dq'
    bpy.context.view_layer.update()
    for name,ob in [('body',body),('glove',glove)]:
        body.hide_render=ob!=body;glove.hide_render=ob!=glove
        for view in (['back'] if mode=='linear' else ['palm','axial','back']):
            s.camera=cam if view=='back' else bpy.data.objects['BW2_cam_'+view];s.render.filepath=str(out/(name+'_'+mode+'_'+view+'.png'));bpy.ops.render.render(write_still=True);record['renders'].append(s.render.filepath)
for m,p in zip(armmods,prior):m.use_deform_preserve_volume=p
record['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert record['source_sha256_after']==sha;(out/'dq_render_metadata.json').write_text(json.dumps(record,indent=2))
