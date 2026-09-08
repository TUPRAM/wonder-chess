"""Released Dragonkin production using the calibrated Sora family foundation.

Writes only the explicitly selected Varek/Iri/Oren source/exports and a fresh report.
Shared helpers/preparation are read-only. No existing rig family is modified.
"""
from __future__ import annotations
import argparse
import array
import json
import math
from pathlib import Path
import runpy
import shutil
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import author_update_pippa as execution
import prepare_dragonkin_family as prepared
from author_alpha import Geometry, make_mesh, preserve_source_parts, export_fbx, setup_render, rgb
from dragonkin_production_profile import RIG_REVISION, motion_pose, clip_spec

UID = 'wc_u_dragonkin_guardian'
sha, write = execution.sha, execution.write


def material(unit, out):
    colors = prepared.PROFILES[unit['id']]['palette'].split()
    buffers = [array.array('f', [0]) * (1024 * 1024 * 4) for _ in range(3)]
    for y in range(1024):
        for x in range(1024):
            index = (y // 256) * 4 + x // 256
            k = (y * 1024 + x) * 4
            color = rgb(colors[index]); shade = .95 + .05 * (y % 256) / 255
            buffers[0][k:k+4] = array.array('f', [*(v * shade for v in color), 1])
            # Very shallow broad scale pattern in the skin swatch only.
            nx = .012 * math.sin(x * math.tau / 44) if index == 6 else 0.
            ny = .012 * math.sin(y * math.tau / 38) if index == 6 else 0.
            buffers[1][k:k+4] = array.array('f', [.5 + nx, .5 + ny, 1, 1])
            metal = index in (4,10) or (unit['unit_class']=='guardian' and index in (0,2))
            buffers[2][k:k+4] = array.array('f', [1, .47 if metal else .77, .55 if metal else 0, 1])
    textures = []
    for suffix, pixels in zip(('BaseColor', 'Normal', 'ORM'), buffers):
        name = f'T_{UID}_{suffix}'
        image = bpy.data.images.new(name, width=1024, height=1024)
        image.colorspace_settings.name = 'sRGB' if suffix == 'BaseColor' else 'Non-Color'
        image.pixels.foreach_set(pixels); image.filepath_raw = str(out / f'{name}.png')
        image.file_format = 'PNG'; image.save(); path = image.filepath_raw
        bpy.data.images.remove(image); image = bpy.data.images.load(path, check_existing=False)
        image.name = name; image.colorspace_settings.name = 'sRGB' if suffix == 'BaseColor' else 'Non-Color'
        textures.append(image)
    mat = bpy.data.materials.new('M_' + UID); mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links; shader = nodes.get('Principled BSDF')
    for index, image in enumerate(textures):
        node = nodes.new('ShaderNodeTexImage'); node.image = image
        if index == 0: links.new(node.outputs['Color'], shader.inputs['Base Color'])
        elif index == 1:
            normal = nodes.new('ShaderNodeNormalMap'); normal.inputs['Strength'].default_value = .28
            links.new(node.outputs['Color'], normal.inputs['Color']); links.new(normal.outputs['Normal'], shader.inputs['Normal'])
        else:
            split = nodes.new('ShaderNodeSeparateColor'); links.new(node.outputs['Color'], split.inputs['Color'])
            links.new(split.outputs['Green'], shader.inputs['Roughness']); links.new(split.outputs['Blue'], shader.inputs['Metallic'])
    return mat


def head(g, profile, cls):
    width, front = profile['head_width'], profile['muzzle_front']
    neck=1 if cls=='guardian' else .83
    g.loft([((0, -.003, .782), .057*neck, .052), ((0, .007, .816), .053*neck, .049),
            ((0, .015, .858), .049*neck, .049)], 6, 'neck', 16)
    sections = [(.832,.50,.046,.063),(.850,.73,.055,front*.90),(.872,.98,.067,front),
                (.890,1.,.074,front*.97),(.908,1.01,.078,.104),(.935,.98,.079,.080),
                (.965,.82,.068,.057),(.987,.52,.044,.032),(.998,.08,.010,.010)]
    vertices, faces = [], []
    for z, radius, back, reach in sections:
        for i in range(24):
            angle = i * math.tau / 24; sine = math.sin(angle)
            vertices.append((width * radius * math.cos(angle), reach * max(0,sine)**.62 if sine > 0 else back*sine,z))
    faces.append(tuple(reversed(range(24))))
    for ring in range(8):
        for i in range(24):
            a = ring*24+i; b = ring*24+(i+1)%24
            faces.append((a,b,b+24,a+24))
    faces.append(tuple(192+i for i in range(24)))
    g.add(vertices, faces, 6, 'head')
    shell = BVHTree.FromPolygons([Vector(v) for v in vertices], faces)
    def surface(x,z):
        hit = shell.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0]
        if hit is None: raise RuntimeError(f'Draconic face surface miss {x},{z}')
        return hit.y
    def disc(cx,cz,rx,rz,color,depth):
        verts = [(cx,surface(cx,cz)+depth,cz)]; sides = 24
        for ring in range(1,5):
            for i in range(sides):
                a = i*math.tau/sides; r = ring/4; x = cx+rx*r*math.cos(a); z = cz+rz*r*math.sin(a)
                verts.append((x,surface(x,z)+depth*(1-.12*r),z))
        polygons = [(0,(i+1)%sides+1,i+1) for i in range(sides)]
        for ring in range(3):
            q = 1+ring*sides
            polygons.extend((q+i,q+sides+i,q+sides+(i+1)%sides,q+(i+1)%sides) for i in range(sides))
        g.add(verts,polygons,color,'head')
    def strip(points, color, thick, depth):
        verts = [(x,surface(x,z+dz)+depth,z+dz) for x,z in points for dz in (-thick,thick)]
        g.add(verts,[(i,i+2,i+3,i+1) for i in range(0,len(verts)-2,2)],color,'head')
    for sign in (-1,1):
        x = sign*width*.61
        disc(x,.919,.019,.0075,8,.00125)
        disc(x,.919,.007,.0064,9,.0022)
        disc(x,.919,.0026,.0048,15,.0031)
        disc(x-sign*.002,.9215,.0016,.0016,8,.0038)
        for upper in (True,False):
            strip([(x+.019*math.cos(i*math.pi/16),.919+(.0075 if upper else -.0075)*math.sin(i*math.pi/16)) for i in range(17)],
                  7 if upper else 14,.0013,.0017)
        strip([(x-.020+i*.040/16,.934+.004*math.sin(i*math.pi/16)) for i in range(17)],7,.0023,.0019)
        nx = sign*.034
        disc(nx,.882,.0045,.0025,14,.001)
        if cls=='guardian':
            horn=[(sign*.065,-.008,.946),(sign*.085,-.028,.958),(sign*.097,-.065,.971),
                  (sign*.095,-.10,.977),(sign*.080,-.130,.974),(sign*.068,-.145,.966)]
            radii=[.020,.019,.016,.012,.007,.003]
        elif cls=='ranger':
            horn=[(sign*.065,-.010,.949),(sign*.089,-.025,.965),(sign*.118,-.052,.972),(sign*.125,-.073,.962)]
            radii=[.019,.023,.014,.004]
        elif cls=='rogue':
            horn=[(sign*.060,-.014,.947),(sign*.074,-.045,.960),(sign*.070,-.075,.966),(sign*.060,-.095,.954)]
            radii=[.016,.014,.009,.003]
        else:
            horn=[(sign*.061,-.018,.953),(sign*.082,-.029,.981),(sign*.085,-.065,.988),
                  (sign*.069,-.097,.975),(sign*.048,-.115,.954)]
            radii=[.021,.019,.015,.009,.003]
        g.tube(horn,radii,7,'head',10,depth=.75)
    strip([(-width*.62+i*width*1.24/24,.858-.0025*math.sin(i*math.pi/24)) for i in range(25)],14,.0011,.001)
    if profile['crest']:
        for index,z in enumerate((.914,.883,.853)):
            g.tube([(0,-.057,z),(0,-.085+index*.005,z+.013),(0,-.095+index*.008,z-.009)],
                   [.012,.014-index*.002,.006],7,'neck' if index==2 else 'head',8)
    if cls=='guardian':
        for index,z in enumerate((.801,.818,.835)):
            radius=.034-index*.003
            g.plate([(-radius,z+.010),(radius,z+.010),(radius*.83,z-.004),(0,z-.008),(-radius*.83,z-.004)],
                    .066+index*.002,.004,12,'neck',.05)


def geometry(unit,points):
    # Reuse the frozen authored body/equipment plan with the new integrated face.
    # Sleeve rings rotate with the arm; rounded undersleeves bridge to the torso.
    original_head, original_tube, original_equipment = prepared.head_geometry, Geometry.tube, prepared.equipment_geometry
    starts=[]
    rig_points=points
    def sleeve(self,points,radii,color,bone,sides=8,**kwargs):
        if bone.startswith('upperarm_') and len(points)==6:
            side = bone[-1]
            kwargs['weights'] = [{bone:1},{bone:1},{bone:1},{bone:.5,'lowerarm_'+side:.5},
                                 {'lowerarm_'+side:1},{'lowerarm_'+side:1}]
            if unit['unit_class']=='guardian':radii=[r*.78 for r in radii];color=3
            else:
                sh,el,wr=(Vector(rig_points[side][key]) for key in ('sh','el','wrist'))
                radius=prepared.PROFILES[unit['id']]['limb']
                points=[tuple(sh),tuple(sh.lerp(el,.10)),tuple(sh.lerp(el,.35)),tuple(el),tuple(el.lerp(wr,.50)),tuple(wr)]
                radii=[radius*.35,radius*.85,radius*.90,radius*.70,radius*.72,radius*.51]
        if unit['unit_class']=='ranger' and bone=='weapon_l' and color==8 and sides==6 and len(points)==3:
            points=list(points);points[1]=tuple(ranger_nock)
            kwargs['weights']=[{'weapon_l':1},{'weapon_r':1},{'weapon_l':1}]
        return original_tube(self,points,radii,color,bone,sides,**kwargs)
    ranger_nock=Vector(points['r']['hand'])
    def dressed_equipment(g,u,p):
        if u['unit_class']!='guardian':
            # Tailored cloth cuffs retain a slim outline and leave joint motion visible.
            for side,sign in (('l',1),('r',-1)):
                sh,el,wr=(Vector(p[side][key]) for key in ('sh','el','wrist'))
                radius=prepared.PROFILES[u['id']]['limb']
                shoulder_color=1 if u['unit_class']=='ranger' else 0
                g.loft([((sh.x,sh.y,sh.z-.025),radius*.95,radius),
                        ((sh.x,sh.y,sh.z+.008),radius*1.12,radius*1.18),
                        ((sh.x,sh.y,sh.z+.032),radius*.72,radius*.76),
                        ((sh.x,sh.y,sh.z+.038),radius*.22,radius*.26)],shoulder_color,'clavicle_'+side,16)
                g.tube([tuple(el.lerp(wr,t)) for t in (.80,.86,.91)],
                       [radius*.58,radius*.62,radius*.52],1,'lowerarm_'+side,12)
            if u['unit_class']=='ranger':
                # Fit trim to the actual closed torso surface, including its
                # narrow collar, so a side view cannot expose floating seams.
                torso=BVHTree.FromPolygons([Vector(v) for v in g.vertices[:120]],g.faces[:102])
                def front_point(x,z,offset):
                    hit=torso.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0]
                    if hit is None:raise RuntimeError('Costume trim misses the torso surface')
                    return (x,hit.y+offset,z)
                g.loft([((0,.004,.780),.061,.062),((0,.004,.803),.055,.057)],1,'spine_03',16)
                g.tube([front_point(-.058,.778,.0065),front_point(0,.724,.0065),front_point(.058,.778,.0065)],
                       [.0065]*3,4,'spine_03',8)
                for sign in (-1,1):
                    g.tube([front_point(sign*.093,.710,.003),front_point(sign*.085,.652,.003),
                            front_point(sign*.073,.577,.003)],[.003]*3,4,'spine_02',7)
                g.ellipsoid(front_point(0,.725,.006),(.012,.006,.009),4,'spine_03',5,10)
                waist=prepared.PROFILES[u['id']]['waist']
                g.loft([((0,0,.543),waist*1.055,.104),((0,0,.558),waist*1.055,.104)],4,'pelvis',20)
            starts.append(len(g.faces));original_equipment(g,u,p);return
        # Separate rigid armor follows each limb segment, with visible soft joints.
        for side,sign in (('l',1),('r',-1)):
            sh,el,wr=(Vector(p[side][key]) for key in ('sh','el','wrist'))
            g.ellipsoid(tuple(sh),(.064,.067,.035),3,'clavicle_'+side,8,16)
            g.ellipsoid(tuple(el),(.034,.035,.035),3,'lowerarm_'+side,8,16)
            g.tube([tuple(sh.lerp(el,t)) for t in (.14,.20,.46,.65,.70)],
                   [.047,.053,.051,.041,.036],0,'upperarm_'+side,14,depth=1.04)
            g.tube([tuple(el.lerp(wr,t)) for t in (.24,.30,.57,.78,.84)],
                   [.039,.046,.047,.037,.031],0,'lowerarm_'+side,14,depth=1.02)
            for t in (.31,.76):
                g.tube([tuple(el.lerp(wr,t-.012)),tuple(el.lerp(wr,t+.012))],
                       [.047 if t<.4 else .039]*2,10,'lowerarm_'+side,14)
            g.tube([(sign*.115,.127,.700),(sign*.10,.129,.660),(sign*.079,.127,.624)], [.005]*3,10,'spine_02',7)
            g.tube([(sign*.016,.117,.520),(sign*.025,.118,.444),(sign*.032,.118,.420)], [.0035]*3,10,'pelvis',7)
        # Back armor's central seam and short royal-blue tabard stay readable.
        for sign in (-1,1):
            g.plate([(sign*.024,.700),(sign*.068,.665),(sign*.056,.574),(sign*.022,.574)],-.109,.004,1,'spine_02',.06)
        starts.append(len(g.faces));original_equipment(g,u,p)
        # Six rounded ceremonial flutes form a blunt mace crown.
        x,y,z=p['r']['hand']
        for i in range(6):
            a=i*math.tau/6
            g.ellipsoid((x+.042*math.cos(a),y+.037*math.sin(a),z+.199),(.017,.017,.029),10,'weapon_r',5,8)
        # Beacon engraving around the fixed shield gem; no idle light source.
        x,y,z=p['l']['hand']
        for sign in (-1,1):
            g.tube([(x+sign*.046,y+.081,z+.112),(x+sign*.066,y+.080,z+.171),
                    (x+sign*.030,y+.080,z+.199)], [.0045]*3,10,'weapon_l',7)
    prepared.head_geometry=head; Geometry.tube=sleeve; prepared.equipment_geometry=dressed_equipment
    try:g,_=prepared.build_geometry(unit,points)
    finally:prepared.head_geometry=original_head; Geometry.tube=original_tube; prepared.equipment_geometry=original_equipment
    return g,starts[0]


def main():
    global UID
    parser = argparse.ArgumentParser(); parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--unit',choices=('wc_u_dragonkin_ranger','wc_u_dragonkin_rogue','wc_u_dragonkin_priest'),required=True)
    parser.add_argument('--revision',type=int,required=True); parser.add_argument('--movies',action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:]); UID=args.unit;report = args.report.resolve()
    if report.exists() or not report.is_relative_to((ROOT/'reports').resolve()): raise ValueError('Fresh report path required')
    prepared.dependencies(); report.mkdir(parents=True)
    unit = prepared.source_unit(UID); out = ROOT/'exports/heroes'/UID; source = ROOT/'art-source/heroes'/UID
    for label,folder in (('source',source),('exports',out)):
        if folder.exists(): shutil.copytree(folder,report/('before-'+label))
        folder.mkdir(parents=True,exist_ok=True)
    write(report/'input.json',dict(unit_id=UID,revision=args.revision,blender_version=bpy.app.version_string,
        author_sha256=sha(__file__),prepared_sha256=sha(prepared.__file__),execution_helper_sha256=sha(execution.__file__),
        family_sha256=sha(ROOT/'tools/blender/dragonkin_production_profile.py'),units_sha256=sha(ROOT/'data/units.json')))
    (report/'executed-author.py').write_bytes(Path(__file__).read_bytes())
    (report/'executed-profile.py').write_bytes((ROOT/'tools/blender/dragonkin_production_profile.py').read_bytes())
    bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene
    scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1; scene.render.fps=60
    scene.render.threads_mode='FIXED'; scene.render.threads=4
    for name in ('BODY','COSTUME','EQUIPMENT','RIG','PRESENTATION_HELPERS','EXPORT'):
        scene.collection.children.link(bpy.data.collections.new(name))
    mat=material(unit,out); arm,points=prepared.build_rig(unit); arm.data.name=RIG_REVISION
    for bone in arm.pose.bones: bone.rotation_mode='QUATERNION'
    write(report/'rig-calibration.json',dict(status='EXECUTED_SOURCE_REST_GEOMETRY_ONLY',rig_revision=RIG_REVISION,
        height_m=unit['height_m'],bone_count=len(arm.data.bones),source_forward='+Y',source_up='+Z',source_unit_m=1,
        bones=[dict(name=b.name,parent=b.parent.name if b.parent else None,head_m=list(b.head_local),
                    tail_m=list(b.tail_local),matrix_local=[list(row) for row in b.matrix_local]) for b in arm.data.bones],
        engine_calibration='NOT_RUN',same_names_are_not_compatibility_proof=True))
    geo,equipment_start=geometry(unit,points); mesh=make_mesh(geo,unit,arm,mat)
    for polygon,color in zip(mesh.data.polygons,geo.colors):
        if color in (0,1,3,6,7,14):polygon.use_smooth=True
    for obj in (arm,mesh):
        for collection in list(obj.users_collection):collection.objects.unlink(obj)
        bpy.data.collections['EXPORT'].objects.link(obj)
    bpy.data.collections['RIG'].objects.link(arm); preserve_source_parts(mesh,geo,equipment_start)
    write(report/'rest-structure.json',prepared.inspect_family(unit,arm,mesh))
    execution.UID=UID; execution.clip_spec=clip_spec; execution.motion_pose=motion_pose
    export_fbx(out/f'SK_{UID}.fbx',[arm,mesh],False); lods=execution.clean_lods(unit,mesh,arm,out)
    clips,ik=execution.animate(unit,arm,out); write(report/'executed-ik-reach.json',ik)
    if any(row['maximum_hand_ik_clamp_m']>.0001 or row['maximum_foot_ik_clamp_m']>.0001 for row in ik):
        raise RuntimeError('Pilot contact target outside measured rig reach')
    execution.audit_frames(arm,mesh,clips,report); setup_render(unit['height_m'])
    execution.render_views(unit,arm,clips,report,out)
    if clips['Attack'].get('presentation_windows'):
        for window in clips['Attack']['presentation_windows']:
            for label,key in (('start','start_frame'),('release','release_frame'),('end','end_frame')):
                execution.use_clip(arm,clips['Attack'],window[key]);scene.render.filepath=str(report/f'Attack-{window["name"]}-{label}.png')
                bpy.ops.render.render(write_still=True)
    if args.movies:execution.render_movies(unit,arm,clips,report)
    execution.use_clip(arm,clips['Idle']); execution.camera_view(unit,'three-quarter')
    scene.render.resolution_x=scene.render.resolution_y=768
    source_file=source/f'{UID}.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(source_file)); mesh.data.calc_loop_triangles()
    manifest=dict(status='AUTHORED_EXPORTED_BLENDER_EXECUTED_ENGINE_AND_VISUAL_ACCEPTANCE_OPEN',unit_id=UID,name=unit['name'],
        blender_version=bpy.app.version_string,source_revision=args.revision,geometry_revision=args.revision,geometry_source_revision=args.revision,animation_revision=args.revision,
        source_sha256=sha(source_file),author_script_sha256=sha(__file__),family_helper_sha256=sha(ROOT/'tools/blender/dragonkin_production_profile.py'),
        prepared_helper_sha256=sha(prepared.__file__),units_source_sha256=sha(ROOT/'data/units.json'),height_m=unit['height_m'],rig_family=unit['rig_family'],rig_revision=RIG_REVISION,
        bones=len(arm.data.bones),triangles=len(mesh.data.loop_triangles),materials=1,fps=60,source_forward='+Y',source_up='+Z',unit_scale_m=1,
        fbx_profile='tools/blender/profiles/fbx_skeletal_cm_v1.json',normalized_export_revision=1,normalized_exporter_sha256=sha(ROOT/'tools/blender/normalized_fbx.py'),
        exported_coordinate_units='centimeters in independent temporary copies; source metres',engine_calibration=['reports/WC-U440/20260906T170048Z/sora-engine-pilot'],
        textures={'BaseColor':'sRGB','Normal':'linear tangent; shallow low-frequency scale swatch','ORM':'linear R occlusion, G roughness, B metallic'},
        clips=clips,lods=lods,source_brief=unit['art'],equipment='Visual only; '+prepared.PROFILES[UID]['equipment'],
        files={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='export_manifest.json'},report_directory=str(report.relative_to(ROOT)),
        open_reviews=['continuous seven-clip visual quality','muzzle crest armor and weapon clearance','crowded game-camera identity','actual Unreal family calibration/import/reimport','LOD silhouettes','effects/audio synchronization'])
    write(out/'export_manifest.json',manifest)
    saved=sys.argv
    try:
        sys.argv=['inspect_scene.py','--','--collection','EXPORT','--output',str(report/'structural.json'),'--require-skin']
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
        sys.argv=['audit_motion.py','--','--unit',UID,'--output',str(report/'sampled-motion.json')]
        runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved
    write(report/'completed.json',dict(status='BLENDER_EXECUTED_REVIEW_REQUIRED',unit_id=UID,source_sha256=manifest['source_sha256'],
        export_manifest_sha256=sha(out/'export_manifest.json'),triangles=manifest['triangles'],clips=len(clips)))
    print('WC_DRAGONKIN_EXPORTED '+json.dumps({'unit':UID,'report':str(report),'triangles':manifest['triangles']}),flush=True)


if __name__=='__main__': main()
