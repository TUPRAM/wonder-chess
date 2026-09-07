"""Original Pippa pilot source production on the explicit small-family rig.

Only Pippa's source/export folders are writable. Shared authoring helpers and
other family rigs remain read-only. Render/export execution is separately logged.
"""
from __future__ import annotations
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import re
import runpy
import shutil
import sys

import bpy
import bmesh
from mathutils import Euler, Matrix, Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_alpha import Geometry, make_mesh, preserve_source_parts, export_fbx, export_lods, setup_render, rgb
from hand_contacts import oriented_matrix, place_hand
from halfling_production_profile import PROFILES, rig_spec, clip_spec, motion_pose, face_sections, palm_sections, finger_paths, RIG_REVISION

UID='wc_u_halfling_warrior'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def material(unit,out):
    p=PROFILES[UID]
    colors=re.findall(r'#[0-9A-Fa-f]{6}',unit['art']['palette'])+['#A6834B','#664332',p['skin'],p['hair'],'#EDE1CD','#352A25','#BC9652',p['iris'],'#AD7860','#465141',p['skin_accent'],'#D5C59B']
    buffers=[array.array('f',[0])*(1024*1024*4) for _ in range(3)]
    for y in range(1024):
        for x in range(1024):
            index=(y//256)*4+x//256;k=(y*1024+x)*4
            color=rgb(colors[index]);shade=.94+.06*(y%256)/255
            if index in (0,1,2):shade+=.008 if (x+y)%11<3 else 0
            buffers[0][k:k+4]=array.array('f',[*(v*shade for v in color),1])
            buffers[1][k:k+4]=array.array('f',[.5,.5,1,1])
            metal=index in (4,10)
            buffers[2][k:k+4]=array.array('f',[1,.4 if metal else .76,int(metal),1])
    textures=[]
    for suffix,pixels in zip(('BaseColor','Normal','ORM'),buffers):
        name=f'T_{UID}_{suffix}';im=bpy.data.images.new(name,width=1024,height=1024)
        if suffix!='BaseColor':im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(pixels);im.filepath_raw=str(out/f'{name}.png');im.file_format='PNG';im.save()
        path=im.filepath_raw;bpy.data.images.remove(im)
        im=bpy.data.images.load(path,check_existing=False);im.name=name
        im.colorspace_settings.name='sRGB' if suffix=='BaseColor' else 'Non-Color';textures.append(im)
    mat=bpy.data.materials.new('M_'+UID);mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF')
    for index,im in enumerate(textures):
        node=nodes.new('ShaderNodeTexImage');node.image=im
        if index==0:links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
        elif index==1:
            normal=nodes.new('ShaderNodeNormalMap');links.new(node.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
        else:
            separate=nodes.new('ShaderNodeSeparateColor');links.new(node.outputs['Color'],separate.inputs['Color'])
            links.new(separate.outputs['Green'],bsdf.inputs['Roughness']);links.new(separate.outputs['Blue'],bsdf.inputs['Metallic'])
    return mat


def create_rig(height):
    specifications,points=rig_spec()
    data=bpy.data.armatures.new(RIG_REVISION);arm=bpy.data.objects.new('Armature',data)
    bpy.context.collection.objects.link(arm);bpy.context.view_layer.objects.active=arm;arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name,start,end,parent in specifications:
        bone=data.edit_bones.new(name);bone.head=Vector(start)*height;bone.tail=Vector(end)*height;bone.align_roll(Vector((0,1,0)))
        if parent:bone.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in arm.pose.bones:bone.rotation_mode='QUATERNION'
    return arm,points


def tube(g,points,radius,color,bone,sides=8):
    g.tube(points,[radius]*len(points),color,bone,sides)


def face(g):
    g.loft(face_sections(UID),6,'head',20)
    # Jaw-connected ears, an adult nasal bridge and compact almond eyes.
    for sign in (-1,1):
        g.ellipsoid((sign*.080,-.005,.899),(.012,.020,.025),6,'head',6,10)
        g.ellipsoid((sign*.086,.006,.899),(.006,.013,.014),14,'head',5,8)
        x=sign*.034
        g.ellipsoid((x,.069,.909),(.022,.011,.009),8,'head',6,12)
        g.ellipsoid((x,.080,.908),(.0067,.0024,.0070),11,'head',5,10)
        g.ellipsoid((x,.083,.908),(.0032,.0012,.0047),9,'head',5,8)
        g.ellipsoid((x-sign*.0018,.084,.911),(.0017,.001,.0018),8,'head',4,6)
        tube(g,[(x-.021,.077,.908),(x-.010,.079,.917),(x+.004,.080,.918),(x+.020,.077,.911)],.0028,7,'head',6)
        tube(g,[(x-.020,.076,.907),(x,.078,.902),(x+.020,.076,.910)],.0020,14,'head',6)
        tube(g,[(x-.023,.069,.929),(x,.077,.934),(x+.022,.069,.929)],.0030,7,'head',7)
        for dx,dz in ((-.009,.002),(.003,.006),(.015,0),(.010,-.007)):
            fx=x+dx*.8
            surface=.002+.071*math.sqrt(max(0,1-(fx/.079)**2))
            g.ellipsoid((fx,surface+.0006,.884+dz),(.0017,.00035,.0013),7,'head',4,6)
    g.loft([((0,.060,.932),.007,.008),((0,.072,.910),.009,.012),((0,.084,.889),.014,.012),((0,.078,.882),.012,.008)],14,'head',10)
    for sign in (-1,1):g.ellipsoid((sign*.008,.083,.883),(.003,.002,.0022),9,'head',4,6)
    tube(g,[(-.023,.065,.865),(-.011,.073,.861),(0,.075,.860),(.014,.071,.864),(.024,.064,.869)],.0017,12,'head',7)
    tube(g,[(-.012,.070,.858),(0,.075,.856),(.010,.071,.859)],.0018,14,'head',7)
    # A fitted hair cap with connected short curl strands, rather than a pile of spheres.
    g.loft([((0,-.014,.927),.077,.069),((0,-.015,.955),.083,.076),((0,-.016,.977),.064,.061),((0,-.015,.990),.028,.032)],7,'head',18)
    for index in range(11):
        angle=math.pi*index/10
        x=.076*math.cos(angle);y=.010+.060*math.sin(angle);z=.948+.005*math.sin(angle*3)
        points=[(x+.006*math.cos(t),y+.005*math.sin(t),z+.015*t/math.tau) for t in [i*math.tau/8 for i in range(9)]]
        tube(g,points,.0062,7,'head',7)
    for sign in (-1,1):
        tube(g,[(sign*.077,-.008,.937),(sign*.084,-.003,.922),(sign*.076,.012,.915)],.008,7,'head',8)
    for x in (-.048,-.020,.013,.044):
        tube(g,[(x,-.031,.978),(x+.010,-.014,.987),(x+.016,.012,.980),(x+.011,.024,.973)],.006,7,'head',7)
    for x in (-.060,-.030,0,.030,.060):
        for y in (-.056,-.027,.002,.031,.054):
            radius=(x/.080)**2+(y/.077)**2
            if radius>.94:continue
            z=.944+.048*math.sqrt(1-radius)
            points=[(x+.009*math.cos(a),y-.015+.008*math.sin(a),z+.004*math.sin(a)) for a in [i*math.tau/7 for i in range(8)]]
            tube(g,points,.0052,7,'head',6)


def body(unit,points):
    g=Geometry()
    g.loft([((0,0,.450),.140,.090),((0,0,.492),.144,.092),((0,0,.546),.121,.077),
            ((0,0,.635),.137,.085),((0,0,.712),.153,.085),((0,0,.751),.153,.080),((0,0,.778),.075,.056)],
           0,'spine_02',16,weights=[{'pelvis':1},{'pelvis':.85,'spine_01':.15},{'pelvis':.3,'spine_01':.7},
                                  {'spine_01':.25,'spine_02':.75},{'spine_02':.4,'spine_03':.6},{'spine_03':1},{'spine_03':1}])
    g.loft([((0,0,.776),.044,.040),((0,0,.848),.039,.035)],6,'neck',12)
    for side,sign in (('l',1),('r',-1)):
        p=points[side]
        g.tube([p['hip'],(sign*.086,.004,.36),p['knee'],p['ankle']], [.068,.063,.051,.039],1,'thigh_'+side,12,
               weights=[{'pelvis':.25,'thigh_'+side:.75},{'thigh_'+side:1},{'thigh_'+side:.4,'calf_'+side:.6},{'calf_'+side:1}],depth=1.02)
        # Full walking soles and continuous shaped boot uppers, planted by foot IK.
        g.loft([((sign*.082,.044,0),.067,.101),((sign*.082,.048,.025),.068,.104),
                ((sign*.082,.046,.055),.066,.100),((sign*.082,.018,.098),.047,.057),((sign*.082,0,.135),.044,.044)],5,'foot_'+side,12)
        g.loft([((sign*.082,.044,0),.068,.102),((sign*.082,.046,.020),.070,.105)],3,'foot_'+side,12)
        for y,z in ((.067,.078),(.039,.094)):
            tube(g,[(sign*.082-.035,y,z),(sign*.082,y+.006,z+.003),(sign*.082+.035,y,z)],.003,1,'foot_'+side,6)
        sh,el,wr=Vector(p['shoulder']),Vector(p['elbow']),Vector(p['wrist'])
        g.tube([tuple(sh+Vector((-sign*.088,0,-.028))),tuple(sh),tuple(sh.lerp(el,.3)),tuple(sh.lerp(el,.8)),tuple(el),tuple(el.lerp(wr,.2)),tuple(el.lerp(wr,.72)),tuple(wr)],
               [.038,.052,.054,.051,.049,.047,.039,.030],0,'upperarm_'+side,12,
               weights=[{'spine_03':1},{'clavicle_'+side:.65,'upperarm_'+side:.35},{'upperarm_'+side:1},{'upperarm_'+side:.9,'lowerarm_'+side:.1},
                        {'upperarm_'+side:.5,'lowerarm_'+side:.5},{'lowerarm_'+side:.9,'upperarm_'+side:.1},{'lowerarm_'+side:1},{'lowerarm_'+side:1}],depth=.97)
        g.ellipsoid(tuple(el),(.047,.046,.048),0,'lowerarm_'+side,6,12)
        g.tube([tuple(Vector(p['wrist'])+Vector((0,0,.013))),p['wrist']], [.036,.035],1,'lowerarm_'+side,10)
        g.loft(palm_sections(side),6,'hand_'+side,10)
        for i,path in enumerate(finger_paths(side)):tube(g,path,.0050 if i<4 else .0062,6,'hand_'+side,7)
    # Broad scarf forms a different silhouette from shoulder armour.
    g.loft([((0,.002,.765),.101,.067),((0,.002,.790),.119,.071),((0,0,.808),.082,.058)],2,'spine_03',16)
    g.plate([(-.10,.786),(-.178,.788),(-.195,.76),(-.161,.751),(-.102,.768)],-.061,.016,2,'spine_03',.07)
    g.plate([(-.086,.769),(-.154,.752),(-.178,.688),(-.122,.708)],-.09,.016,2,'spine_03',.08)
    # Raised restrained seam lattice follows the curved jacket, with real hem/cuffs.
    for z in (.525,.585,.645,.705):
        width=.123 if z<.60 else .14
        for x in (-.07,0,.07):
            y=.074*math.sqrt(max(.2,1-(x/width)**2))+.013
            tube(g,[(x-.026,y-.004,z),(x,y+.003,z+.026),(x+.026,y-.004,z),(x,y+.003,z-.026),(x-.026,y-.004,z)],.0015,1,'spine_01' if z<.62 else 'spine_02',5)
    g.plate([(-.022,.555),(.022,.555),(.023,.513),(-.022,.513)],.093,.012,4,'pelvis',.13)
    g.plate([(-.048,.679),(.048,.679),(.048,.589),(-.048,.589)],-.091,.010,1,'spine_02',.12)
    tube(g,[(-.036,-.100,.659),(.036,-.100,.659),(.036,-.100,.603),(-.036,-.100,.603),(-.036,-.100,.659)],.002,3,'spine_02',5)
    face(g)
    return g


def gear(g,points):
    palm=Vector(points['r']['hand']);x,y,z=palm
    tube(g,[(x,y,z-.06),(x,y,z+.165)],.016,3,'weapon_r',10)
    g.plate([(x-.034,z+.14),(x-.068,z+.22),(x-.056,z+.29),(x,z+.37),(x+.056,z+.29),(x+.066,z+.22),(x+.033,z+.14)],y,.032,3,'weapon_r',.11)
    tube(g,[(x,y+.019,z+.155),(x,y+.022,z+.345)],.005,1,'weapon_r',6)
    for offset in (.095,.155,.235):
        tube(g,[(x-.032,y-.002,z+offset),(x,y+.020,z+offset),(x+.032,y-.002,z+offset)],.006,4,'weapon_r',7)
    # Round buckler is carried ahead of the hand, with a curved rear grip.
    x,y,z=points['l']['hand'];center=(x,y+.064,z+.027)
    outline=[(x+.112*math.cos(a),z+.027+.112*math.sin(a)) for a in [i*math.tau/20 for i in range(20)]]
    g.plate(outline,center[1],.028,3,'weapon_l',.075)
    g.ring((x,center[1]+.018,z+.027),.109,.008,4,'weapon_l',steps=24)
    for dx in (-.048,0,.048):
        extent=math.sqrt(.099**2-dx**2)
        tube(g,[(x+dx,center[1]+.019,z+.027-extent),(x+dx,center[1]+.019,z+.027+extent)],.0023,1,'weapon_l',5)
    # Orchard tree emblem: one trunk, three broad leaves, no copied insignia.
    g.plate([(x-.009,z-.014),(x+.009,z-.014),(x+.012,z+.040),(x-.010,z+.046)],center[1]+.023,.010,0,'weapon_l',.10)
    for dx,dz in ((-.031,.054),(0,.073),(.031,.054)):
        g.plate([(x+dx-.030,z+dz),(x+dx,z+dz+.027),(x+dx+.030,z+dz),(x+dx,z+dz-.019)],center[1]+.025,.010,0,'weapon_l',.12)
    tube(g,[(x-.031,y+.040,z+.033),(x-.020,y+.006,z+.011),(x+.020,y+.006,z+.011),(x+.031,y+.040,z+.033)],.007,5,'weapon_l',8)


def place_foot(arm,side,target,height):
    upper=arm.pose.bones['thigh_'+side];lower=arm.pose.bones['calf_'+side];foot=arm.pose.bones['foot_'+side]
    bpy.context.view_layer.update();start=upper.head.copy();line=Vector(target)*height-start
    distance=line.length;a=upper.bone.length;b=lower.bone.length
    reach=min(max(distance,abs(a-b)+.001),a+b-.001);direction=line.normalized()
    along=(a*a-b*b+reach*reach)/(2*reach);across=math.sqrt(max(0,a*a-along*along))
    bend=Vector((0,1,0));bend=(bend-direction*bend.dot(direction)).normalized()
    knee=start+direction*along+bend*across;ankle=start+direction*reach
    upper.matrix=oriented_matrix(start,knee-start);upper.scale=(1,1,1);bpy.context.view_layer.update()
    lower.matrix=oriented_matrix(knee,ankle-knee);lower.scale=(1,1,1);bpy.context.view_layer.update()
    matrix=foot.bone.matrix_local.copy();matrix.translation=ankle;foot.matrix=matrix;foot.scale=(1,1,1)
    bpy.context.view_layer.update()
    return abs(distance-reach)


def clean_lods(unit,mesh,arm,out):
    """Triangulate reduced sources before export to avoid FBX ngon divergence."""
    records=export_lods(unit,mesh,arm,out)
    for record in records:
        lod=bpy.data.objects[f'SK_{UID}_LOD{record["lod"]}']
        bm=bmesh.new();bm.from_mesh(lod.data)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        degenerate=[face for face in bm.faces if face.calc_area()<1e-12]
        if degenerate:bmesh.ops.delete(bm,geom=degenerate,context='FACES_ONLY')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(lod.data);bm.free();lod.data.update()
        lod.data.calc_loop_triangles();before_validation=len(lod.data.loop_triangles)
        # The installed FBX importer calls Mesh.validate. Apply the same source
        # validity rule now; decimation can otherwise leave duplicate faces.
        record['mesh_validation_changed']=lod.data.validate(verbose=True,clean_customdata=False)
        lod.data.calc_loop_triangles();record['triangles']=len(lod.data.loop_triangles);record['removed_invalid_triangles']=before_validation-record['triangles']
        record['explicit_triangulation']=True;record['removed_degenerate_faces']=len(degenerate)
        export_fbx(out/f'{lod.name}.fbx',[arm,lod],False)
    return records


def animate(unit,arm,out):
    h=unit['height_m'];clips=clip_spec(unit);audit=[]
    for clip,spec in clips.items():
        arm.animation_data_clear();maximum_hand=maximum_foot=0;previous={}
        for frame in range(1,spec['frames'][1]+1):
            for bone in arm.pose.bones:bone.rotation_quaternion=(1,0,0,0);bone.location=(0,0,0);bone.scale=(1,1,1)
            pose=motion_pose(unit,clip,frame)
            if clip=='Defeat':pose['head_euler']=(-pose['head_euler'][0],pose['head_euler'][1],pose['head_euler'][2])
            pelvis=arm.pose.bones['pelvis'];pelvis.location=pelvis.bone.matrix_local.to_3x3().inverted()@(Vector(pose['body'])*h)
            head=arm.pose.bones['head'];basis=head.bone.matrix_local.to_quaternion()
            head.rotation_quaternion=basis.inverted()@Euler(tuple(math.radians(v) for v in pose['head_euler']),'XYZ').to_quaternion()@basis
            bpy.context.view_layer.update()
            for side in ('l','r'):
                rotation=Euler(tuple(math.radians(v) for v in pose['hand_euler'][side]),'XYZ').to_matrix()
                maximum_hand=max(maximum_hand,place_hand(arm,side,Vector(pose['palms'][side])*h,rotation,h))
                maximum_foot=max(maximum_foot,place_foot(arm,side,pose['feet'][side],h))
            for bone in arm.pose.bones:
                if bone.name in previous and bone.rotation_quaternion.dot(previous[bone.name])<0:bone.rotation_quaternion.negate()
                previous[bone.name]=bone.rotation_quaternion.copy()
                bone.keyframe_insert('rotation_quaternion',frame=frame,group=bone.name);bone.keyframe_insert('location',frame=frame,group=bone.name)
        action=arm.animation_data.action;action.name=f'AN_{UID}_{clip}';action.use_fake_user=True;spec['action']=action.name
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
        bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=spec['frames'][1];bpy.context.scene.frame_set(1)
        export_fbx(out/f'{action.name}.fbx',[arm],True)
        audit.append(dict(clip=clip,frames=spec['frames'][1],maximum_hand_ik_clamp_m=maximum_hand,maximum_foot_ik_clamp_m=maximum_foot))
    return clips,audit


def use_clip(arm,spec,frame=1):
    action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_start=spec['frames'][0];bpy.context.scene.frame_end=spec['frames'][1];bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()


def audit_frames(arm,mesh,clips,report):
    rows=[];errors=[]
    for clip,spec in clips.items():
        minimum=999;root_drift=scale_error=0
        for frame in range(1,spec['frames'][1]+1):
            use_clip(arm,spec,frame);obj=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=obj.to_mesh()
            minimum=min(minimum,min((obj.matrix_world@v.co).z for v in data.vertices));obj.to_mesh_clear()
            root_drift=max(root_drift,arm.pose.bones['root'].location.length)
            scale_error=max(scale_error,max(abs(v-1) for bone in arm.pose.bones for v in bone.scale))
        if minimum<-.025 or root_drift>1e-6 or scale_error>1e-6:errors.append(clip)
        rows.append(dict(clip=clip,frames=spec['frames'][1],minimum_geometry_z_m=minimum,root_translation_max_m=root_drift,scale_error_max=scale_error))
    result=dict(status='FAIL' if errors else 'PASS',evidence_kind='ALL_FRAME_DEFORMED_GEOMETRY_INVARIANTS',clips=rows,errors=errors,
                boundary='Not continuous visual, equipment collision or engine approval')
    write(report/'all-frame-invariants.json',result)
    if errors:raise RuntimeError('Deformation invariant failures: '+','.join(errors))


def camera_view(unit,view):
    h=unit['height_m'];camera=bpy.context.scene.camera
    target=Vector((0,0,h*(.91 if view=='face' else .54)))
    positions={'front':(0,4,h*.6),'side':(4,0,h*.6),'back':(0,-4,h*.6),'three-quarter':(h*1.7,h*3.1,h*1.8),'face':(.2,4,h*.93),'game-angle':(0,h*2.4,h*4.2)}
    camera.location=positions[view];camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=h*(.43 if view=='face' else 1.45)


def render_views(unit,arm,clips,report,out):
    scene=bpy.context.scene;use_clip(arm,clips['Idle'])
    scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.cycles.samples=16
    for view in ('front','side','back','three-quarter','face','game-angle'):
        camera_view(unit,view);scene.render.resolution_x=scene.render.resolution_y=768
        scene.render.filepath=str(report/f'{view}.png');bpy.ops.render.render(write_still=True)
    camera_view(unit,'three-quarter');scene.render.resolution_x=scene.render.resolution_y=640
    scene.render.filepath=str(out/'portrait.png');bpy.ops.render.render(write_still=True)
    scene.render.resolution_x=scene.render.resolution_y=320;scene.cycles.samples=8
    for clip,spec in clips.items():
        for label,frame in [('start',1),('release',spec['release_frame'] or round(spec['frames'][1]/2)),('end',spec['frames'][1])]:
            use_clip(arm,spec,frame);scene.render.filepath=str(report/f'{clip}-{label}.png');bpy.ops.render.render(write_still=True)


def render_movies(unit,arm,clips,report):
    scene=bpy.context.scene;camera_view(unit,'three-quarter')
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.render.resolution_x=scene.render.resolution_y=384;scene.render.image_settings.media_type='VIDEO'
    scene.render.image_settings.file_format='FFMPEG';scene.render.image_settings.color_mode='RGB'
    scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='MEDIUM'
    for clip,spec in clips.items():
        use_clip(arm,spec);scene.render.filepath=str(report/f'continuous-{clip}.mp4');bpy.ops.render.render(animation=True)
    scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.engine='CYCLES'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True);parser.add_argument('--revision',type=int,default=1)
    parser.add_argument('--movies',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    report=args.report.resolve()
    if not report.is_relative_to((ROOT/'reports').resolve()) or report.exists():raise ValueError('Use a new reports directory')
    report.mkdir(parents=True)
    unit=next(row for row in json.loads((ROOT/'data/units.json').read_text(encoding='utf-8'))['units'] if row['id']==UID)
    out=ROOT/'exports/heroes'/UID;source=ROOT/'art-source/heroes'/UID
    for label,folder in (('exports',out),('source',source)):
        if folder.exists():
            shutil.copytree(folder,report/('before-'+label))
        folder.mkdir(parents=True,exist_ok=True)
    write(report/'input.json',dict(unit_id=UID,revision=args.revision,blender_version=bpy.app.version_string,author_sha256=sha(__file__),
                                  family_helper_sha256=sha(ROOT/'tools/blender/halfling_production_profile.py'),units_sha256=sha(ROOT/'data/units.json')))
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.fps=60
    for name in ('BODY','COSTUME','EQUIPMENT','RIG','PRESENTATION_HELPERS','EXPORT'):
        collection=bpy.data.collections.new(name);scene.collection.children.link(collection)
    mat=material(unit,out);arm,points=create_rig(unit['height_m']);geo=body(unit,points);equipment_start=len(geo.faces);gear(geo,points)
    mesh=make_mesh(geo,unit,arm,mat)
    for polygon,color in zip(mesh.data.polygons,geo.colors):
        if color in (0,1):polygon.use_smooth=True
    for obj in (arm,mesh):
        for collection in list(obj.users_collection):collection.objects.unlink(obj)
        bpy.data.collections['EXPORT'].objects.link(obj)
    bpy.data.collections['RIG'].objects.link(arm);preserve_source_parts(mesh,geo,equipment_start)
    export_fbx(out/f'SK_{UID}.fbx',[arm,mesh],False);lods=clean_lods(unit,mesh,arm,out)
    clips,ik=animate(unit,arm,out);write(report/'executed-ik-reach.json',ik)
    audit_frames(arm,mesh,clips,report)
    setup_render(unit['height_m']);render_views(unit,arm,clips,report,out)
    if args.movies:render_movies(unit,arm,clips,report)
    use_clip(arm,clips['Idle']);camera_view(unit,'three-quarter');scene.render.resolution_x=scene.render.resolution_y=768
    source_file=source/f'{UID}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source_file))
    mesh.data.calc_loop_triangles()
    manifest=dict(status='AUTHORED_EXPORTED_BLENDER_EXECUTED_ENGINE_AND_VISUAL_ACCEPTANCE_OPEN',unit_id=UID,name=unit['name'],
                  blender_version=bpy.app.version_string,source_revision=args.revision,geometry_revision=args.revision,geometry_source_revision=args.revision,animation_revision=args.revision,
                  source_sha256=sha(source_file),author_script_sha256=sha(__file__),family_helper_sha256=sha(ROOT/'tools/blender/halfling_production_profile.py'),
                  units_source_sha256=sha(ROOT/'data/units.json'),height_m=unit['height_m'],rig_family=unit['rig_family'],rig_revision=RIG_REVISION,
                  bones=len(arm.data.bones),triangles=len(mesh.data.loop_triangles),materials=1,fps=60,source_forward='+Y',source_up='+Z',unit_scale_m=1,
                  fbx_profile='tools/blender/profiles/fbx_skeletal_cm_v1.json',normalized_export_revision=1,
                  normalized_exporter_sha256=sha(ROOT/'tools/blender/normalized_fbx.py'),exported_coordinate_units='centimeters in independent temporary copies; source metres',
                  engine_calibration=['reports/WC-330/import-probe/forward_cm-results.json','reports/WC-330/import-probe/all7-comparison.json'],
                  textures={'BaseColor':'sRGB','Normal':'linear flat tangent +Y; geometric bevels','ORM':'linear R occlusion, G roughness, B metallic'},
                  clips=clips,lods=lods,source_brief=unit['art'],equipment='Visual only; fully authored wooden club and buckler weighted to weapon bones',
                  files={path.name:sha(path) for path in sorted(out.iterdir()) if path.is_file() and path.name!='export_manifest.json'},
                  report_directory=str(report.relative_to(ROOT)),open_reviews=['continuous seven-clip visual quality','hands and weapon contact','crowded game-camera identity','actual Unreal import/reimport','LOD silhouettes','effects/audio synchronization'])
    write(out/'export_manifest.json',manifest)
    saved=sys.argv
    try:
        sys.argv=['inspect_scene.py','--','--collection','EXPORT','--output',str(report/'structural.json'),'--require-skin']
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
        sys.argv=['audit_motion.py','--','--unit',UID,'--output',str(report/'sampled-motion.json')]
        runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved
    write(report/'completed.json',dict(status='BLENDER_EXECUTED_REVIEW_REQUIRED',unit_id=UID,source_sha256=manifest['source_sha256'],export_manifest_sha256=sha(out/'export_manifest.json'),triangles=manifest['triangles'],clips=len(clips)))
    print('WC_PIPPA_EXPORTED '+json.dumps({'unit':UID,'report':str(report),'triangles':manifest['triangles']}),flush=True)


if __name__=='__main__':main()
