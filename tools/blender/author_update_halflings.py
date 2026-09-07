"""Released Finn, Nella and Milo production on the frozen Pippa small rig.

Pippa source, exports and shared helpers are read-only. This script writes only
the explicitly selected remaining Halfling and a fresh execution report.
"""
from __future__ import annotations
import argparse
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
import author_update_pippa as pilot
from author_alpha import Geometry, make_mesh, preserve_source_parts, export_fbx, setup_render
from halfling_production_profile import PROFILES, face_sections, palm_sections, finger_paths, RIG_REVISION
from halfling_production_profile import motion_pose as prepared_pose, clip_spec, action_envelope

IDS = ('wc_u_halfling_ranger', 'wc_u_halfling_rogue', 'wc_u_halfling_mage')
tube, sha, write = pilot.tube, pilot.sha, pilot.write


def face(g, uid):
    profile = PROFILES[uid]
    width = profile['cheek_width']
    shell_start=len(g.faces)
    g.loft(face_sections(uid), 6, 'head', 20)
    shell=BVHTree.FromPolygons([Vector(v) for v in g.vertices],[list(f) for f in g.faces[shell_start:]])
    def surface(x,z):
        hit=shell.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0]
        if hit is None:raise RuntimeError(f'{uid}: facial detail misses actual head surface {x},{z}')
        return hit.y
    def disc(cx,cz,rx,rz,color,depth):
        n=24;vertices=[(cx,surface(cx,cz)+depth,cz)]
        for ring in range(1,5):
            r=ring/4
            for i in range(n):
                angle=i*math.tau/n;x=cx+rx*r*math.cos(angle);z=cz+rz*r*math.sin(angle)
                vertices.append((x,surface(x,z)+depth*(1-.15*r),z))
        faces=[(0,(i+1)%n+1,i+1) for i in range(n)]
        for ring in range(3):
            q=1+ring*n
            faces.extend((q+i,q+n+i,q+n+(i+1)%n,q+(i+1)%n) for i in range(n))
        g.add(vertices,faces,color,'head')
    def strip(points,color,thickness,depth):
        vertices=[]
        for x,z in points:
            for dz in (-thickness,thickness):vertices.append((x,surface(x,z+dz)+depth,z+dz))
        g.add(vertices,[(j,j+2,j+3,j+1) for j in range(0,len(vertices)-2,2)],color,'head')
    for sign in (-1, 1):
        g.ellipsoid((sign * (width + .003), -.005, .899), (.011, .019, .024), 6, 'head', 6, 10)
        g.ellipsoid((sign * (width + .007), .006, .899), (.006, .012, .014), 14, 'head', 5, 8)
        x = sign * width * .43
        disc(x,.909,.021,.0085,8,.0013)
        disc(x,.909,.0065,.0065,11,.0023)
        disc(x,.909,.0030,.0044,9,.0030)
        disc(x-sign*.002,.912,.0017,.0018,8,.0036)
        for upper in (True,False):
            strip([(x+.021*math.cos(i*math.pi/16),.909+(.0085 if upper else -.0085)*math.sin(i*math.pi/16)) for i in range(17)],
                  7 if upper else 14,.0011,.0018)
        outer = .007 if uid == IDS[1] and sign == -1 else 0
        strip([(x-.021+i*.042/16,.929+.004*math.sin(i*math.pi/16)+outer*(1-i/16)) for i in range(17)],7,.0018,.0021)
    nose = .006 if uid == IDS[2] else 0
    g.loft([((0,.060,.933),.007,.008),((0,.072,.910),.009,.012),
            ((0,.085+nose,.888),.013,.012),((0,.078+nose,.881),.011,.008)],14,'head',10)
    for sign in (-1,1):
        g.ellipsoid((sign*.007,.084+nose,.882),(.003,.002,.002),9,'head',4,6)
    tube(g,[(-.020,.065,.864),(-.010,.073,.860),(0,.075,.860),(.013,.071,.863),(.022,.064,.867)],.0016,12,'head',7)
    tube(g,[(-.011,.070,.857),(0,.074,.855),(.010,.071,.858)],.0017,14,'head',7)
    g.loft([((0,-.014,.929),width*.96,.065),((0,-.014,.955),width*1.03,.073),
            ((0,-.015,.978),width*.80,.059),((0,-.015,.990),.026,.028)],7,'head',18)
    if uid == IDS[0]:
        for sign in (-1,1):
            for offset in range(4):
                x=sign*(.052+offset*.008)
                tube(g,[(x,.013,.944),(x+sign*.004,.026,.935),(x,.031,.924),(x-sign*.006,.019,.927)],.006,7,'head',7)
        # Sculpted folded brim: front lifts above the eye line, crown stays compact.
        vertices=[]
        for radius,z in ((.82,.947),(1,.951),(1,.960),(.73,.967)):
            for i in range(24):
                angle=i*math.tau/24
                vertices.append((.149*radius*math.cos(angle),-.012+.107*radius*math.sin(angle),
                                 z+.017*max(0,math.sin(angle))+.004*math.cos(angle*2)))
        faces=[]
        for ring in range(3):
            for i in range(24):faces.append((ring*24+i,ring*24+(i+1)%24,(ring+1)*24+(i+1)%24,(ring+1)*24+i))
        faces.extend([tuple(reversed(range(24))),tuple(72+i for i in range(24))])
        g.add(vertices,faces,2,'head')
        g.loft([((0,-.014,.965),.081,.069),((0,-.022,.995),.067,.055),((.014,-.022,1.002),.046,.042)],2,'head',16)
        g.loft([((0,-.014,.964),.083,.071),((0,-.017,.975),.079,.067)],3,'head',16)
    elif uid == IDS[1]:
        # Clipped sides and one continuous asymmetric swept tuft.
        g.loft([((0,-.005,.965),.066,.058),((-.018,.005,.985),.051,.040),
                ((-.037,.015,1.011),.031,.026),((-.055,.021,1.023),.014,.016),
                ((-.065,.023,1.026),.003,.006)],7,'head',18)
        for sign in (-1,1):
            for z in (.931,.944):
                tube(g,[(sign*.074,-.015,z),(sign*.079,.005,z-.006),(sign*.070,.018,z-.009)],.0055,7,'head',7)
    else:
        for x in (-.060,-.035,-.010,.015,.040,.060):
            for y in (-.035,.000,.030):
                z=.953+.030*math.sqrt(max(.05,1-(x/.080)**2-(y/.070)**2))
                tube(g,[(x-.008,y-.021,z-.003),(x+.002,y-.010,z+.008),(x+.007,y+.006,z+.009),
                        (x-.003,y+.019,z-.002)],.007,7,'head',7)
        for sign in (-1,1):
            tube(g,[(0,.086,.875),(sign*.009,.085,.876),(sign*.020,.076,.872),
                    (sign*.029,.067,.876)],.0048,7,'head',8)


def body(unit, points):
    uid=unit['id'];profile=PROFILES[uid];g=Geometry()
    width,depth=profile['torso_width'],profile['torso_depth']
    hem=.445 if uid==IDS[2] else .515
    g.loft([((0,0,hem),width,depth),((0,0,.545),width*.98,depth*.97),((0,0,.610),width*.91,depth*.96),
            ((0,0,.705),width*1.02,depth),((0,0,.751),width*1.06,depth*.94),((0,0,.778),.065,.050)],
           0,'spine_02',16,weights=[{'pelvis':1},{'pelvis':.8,'spine_01':.2},{'spine_01':.6,'spine_02':.4},
                                  {'spine_02':.45,'spine_03':.55},{'spine_03':1},{'spine_03':1}])
    g.loft([((0,0,.776),.041,.038),((0,0,.846),.037,.033)],6,'neck',12)
    sleeve_color=1 if uid==IDS[0] else 0
    pants_color=2 if uid==IDS[0] else 3
    g.loft([((0,0,.440),width*.89,depth*.86),((0,0,.480),width*.94,depth*.93),
            ((0,0,.535),width*.96,depth*.96)],pants_color,'pelvis',16)
    for side,sign in (('l',1),('r',-1)):
        p=points[side]
        g.tube([p['hip'],(sign*.084,.004,.35),p['knee'],p['ankle']], [.058,.054,.044,.034],pants_color,'thigh_'+side,12,
               weights=[{'pelvis':.25,'thigh_'+side:.75},{'thigh_'+side:1},{'thigh_'+side:.4,'calf_'+side:.6},{'calf_'+side:1}])
        foot=profile['feet_width']
        g.loft([((sign*.082,.043,0),foot,.097),((sign*.082,.046,.025),foot+.002,.101),
                ((sign*.082,.043,.055),foot,.096),((sign*.082,.015,.095),.042,.054),((sign*.082,0,.139),.039,.040)],5,'foot_'+side,12)
        g.loft([((sign*.082,.043,0),foot+.001,.099),((sign*.082,.045,.018),foot+.003,.102)],3,'foot_'+side,12)
        for y,z in ((.064,.078),(.034,.094)):
            tube(g,[(sign*.082-.030,y,z),(sign*.082,y+.006,z+.003),(sign*.082+.030,y,z)],.0028,1,'foot_'+side,6)
        sh,el,wr=Vector(p['shoulder']),Vector(p['elbow']),Vector(p['wrist'])
        radii=[.047,.048,.048,.047,.044,.041,.036,.027]
        if uid==IDS[2]:radii=[r*1.10 for r in radii]
        g.tube([tuple(sh),tuple(sh.lerp(el,.12)),tuple(sh.lerp(el,.3)),tuple(sh.lerp(el,.8)),
                tuple(el),tuple(el.lerp(wr,.2)),tuple(el.lerp(wr,.72)),tuple(wr)],radii,sleeve_color,'upperarm_'+side,12,
               weights=[{'clavicle_'+side:.10,'upperarm_'+side:.90},{'upperarm_'+side:1},{'upperarm_'+side:1},
                        {'upperarm_'+side:.9,'lowerarm_'+side:.1},{'upperarm_'+side:.5,'lowerarm_'+side:.5},
                        {'lowerarm_'+side:.9,'upperarm_'+side:.1},{'lowerarm_'+side:1},{'lowerarm_'+side:1}],depth=.97)
        g.ellipsoid(tuple(sh),(.053,.053,.053),sleeve_color,'upperarm_'+side,8,14)
        g.ellipsoid(tuple(el),(.041,.040,.043),sleeve_color,'lowerarm_'+side,6,12)
        g.tube([tuple(wr+Vector((0,0,.013))),tuple(wr)],[.033,.032],1 if uid==IDS[2] else pants_color,'lowerarm_'+side,10)
        g.loft(palm_sections(side),6,'hand_'+side,10)
        for i,path in enumerate(finger_paths(side)):tube(g,path,.005 if i<4 else .0062,6,'hand_'+side,7)
    # The torso closures, collar and rear silhouette are individual, not recolors.
    if uid==IDS[0]:
        g.plate([(-.025,.758),(.025,.758),(.024,.645),(0,.622),(-.024,.645)],depth+.008,.016,1,'spine_02',.08)
        for sign in (-1,1):tube(g,[(sign*.055,depth-.002,.754),(sign*.035,depth+.018,.657),(sign*.020,depth+.011,.55)],.0045,3,'spine_02',7)
        g.plate([(-.133,.748),(.133,.748),(.104,.697),(0,.565),(-.104,.697)],-depth-.014,.019,0,'spine_03',.06)
        tube(g,[(-.085,-depth-.028,.710),(-.036,-depth-.028,.670),(.021,-depth-.028,.687),(.057,-depth-.028,.644)],.004,1,'spine_03',6)
        g.plate([(-.130,.548),(-.066,.548),(-.061,.476),(-.130,.480)],depth-.007,.025,5,'pelvis',.14)
        g.plate([(-.130,.548),(-.066,.548),(-.082,.517),(-.112,.516)],depth+.011,.016,3,'pelvis',.12)
    elif uid==IDS[1]:
        g.plate([(-.037,.758),(.041,.758),(.019,.647),(-.027,.680)],depth+.012,.018,2,'spine_02',.08)
        g.plate([(-.095,.756),(-.023,.734),(-.050,.647),(-.115,.718)],depth+.021,.018,1,'spine_02',.08)
        for x,z in ((-.064,.719),(-.080,.735)):
            pts=[(x+(.009 if i%2==0 else .004)*math.cos(math.pi/2+i*math.pi/5),z+(.009 if i%2==0 else .004)*math.sin(math.pi/2+i*math.pi/5)) for i in range(10)]
            g.plate(pts,depth+.034,.016,4,'spine_02',.08)
        g.plate([(0,.800),(.137,.723),(0,.558),(-.137,.723)],-depth-.019,.020,0,'spine_03',.07)
        tube(g,[(-.102,-depth-.033,.749),(.090,-depth-.034,.641)],.008,1,'spine_03',8)
        g.loft([((0,0,.545),width*1.015,depth+.008),((0,0,.558),width*1.02,depth+.009)],1,'pelvis',16)
        g.plate([(.085,.548),(.144,.548),(.148,.468),(.090,.474)],-.014,.036,5,'pelvis',.14)
    else:
        # Two visibly separated raincoat fronts and a collar clear of the jaw.
        for sign in (-1,1):
            g.plate([(sign*.012,.594),(sign*.122,.600),(sign*.151,.449),(sign*.017,.431)],depth+.009,.020,0,'pelvis',.06)
            tube(g,[(sign*.018,depth+.025,.581),(sign*.016,depth+.026,.449)],.0035,1,'pelvis',6)
            g.plate([(sign*.033,.772),(sign*.122,.788),(sign*.141,.819),(sign*.062,.805)],.010,.097,1,'spine_03',.09)
        g.loft([((0,0,.780),.083,.061),((0,-.006,.810),.094,.064)],1,'spine_03',16)
        tube(g,[(0,depth+.010,.747),(0,depth+.018,.620)],.004,1,'spine_02',7)
        for z in (.632,.684,.731):g.ellipsoid((.012,depth+.022,z),(.006,.004,.007),2,'spine_02',4,8)
        g.plate([(-.027,.601),(.027,.601),(.027,.558),(-.027,.558)],depth+.023,.018,2,'spine_01',.13)
        # Rounded folded canopy, with broad ribs, fixed to a short visible bracket.
        tube(g,[(0,-depth,.652),(0,-depth-.046,.651)],.021,2,'spine_02',10)
        disk=[(.151*math.cos(i*math.tau/12),.654+.151*math.sin(i*math.tau/12)) for i in range(12)]
        g.plate(disk,-depth-.052,.035,3,'spine_02',.10)
        for angle in [i*math.tau/8 for i in range(8)]:
            tube(g,[(0,-depth-.077,.654),(.128*math.cos(angle),-depth-.075,.654+.128*math.sin(angle))],.0045,2,'spine_02',7)
        g.ellipsoid((0,-depth-.080,.654),(.021,.008,.021),2,'spine_02',5,10)
    face(g,uid)
    return g


def gear(g,points,uid):
    if uid==IDS[0]:
        x,y,z=points['l']['hand']
        bow=[(x-.043,y+.013,z-.270),(x-.024,y+.035,z-.228),(x+.018,y+.049,z-.151),
             (x+.009,y+.007,z-.048),(x,y,z),(x+.009,y+.007,z+.048),
             (x+.018,y+.049,z+.151),(x-.024,y+.035,z+.228),(x-.043,y+.013,z+.270)]
        g.tube(bow,[.009,.012,.013,.014,.016,.014,.013,.012,.009],3,'weapon_l',10)
        for offset in (-.058,.058):
            tube(g,[(x-.013,y-.010,z+offset),(x,y+.014,z+offset),(x+.013,y-.010,z+offset)],.005,4,'weapon_l',7)
        # The string nock is skinned to the drawing hand; ends follow the bow hand.
        g.tube([bow[0],points['r']['hand'],bow[-1]],[.0028,.0028,.0028],1,'weapon_l',6,
               weights=[{'weapon_l':1},{'weapon_r':1},{'weapon_l':1}])
        g.loft([((-.13,-.017,.480),.041,.039),((-.144,-.018,.667),.036,.034)],5,'pelvis',10)
        g.loft([((-.144,-.018,.654),.040,.037),((-.144,-.018,.678),.040,.037)],3,'pelvis',10)
        for dx in (-.017,.011):
            tube(g,[(-.144+dx,-.018,.605),(-.150+dx,-.023,.740)],.004,3,'pelvis',7)
            g.plate([(-.164+dx,.706),(-.154+dx,.742),(-.146+dx,.723),(-.141+dx,.702)],-.023,.017,1,'pelvis',.06)
    elif uid==IDS[1]:
        for side,sign in (('r',-1),('l',1)):
            x,y,z=points[side]['hand'];bone='weapon_'+side
            tube(g,[(x,y,z-.058),(x,y,z+.103)],.012,5,bone,10)
            polygon=[(x-.021,z+.075),(x-.096,z+.160),(x-.080,z+.205),(x-.039,z+.235),
                     (x+.025,z+.242),(x+.080,z+.202),(x+.096,z+.160),(x+.021,z+.075)]
            g.plate(polygon,y,.029,1 if side=='l' else 0,bone,.12)
            for dx in (-.060,-.028,.025,.061):
                tube(g,[(x,y+.018,z+.094),(x+dx,y+.020,z+.196)],.0037,4,bone,6)
            g.ellipsoid((x,y+.021,z+.126),(.017,.005,.016),4,bone,5,8)
    else:
        x,y,z=points['r']['hand']
        tube(g,[(x,y,z-.059),(x+.003,y,z+.160)],.014,3,'weapon_r',10)
        for offset in (.075,.100):
            tube(g,[(x-.014,y-.004,z+offset),(x,y+.015,z+offset),(x+.014,y-.004,z+offset)],.005,2,'weapon_r',7)
        spiral=[]
        for index in range(37):
            t=index/36;angle=-math.pi/2+t*math.tau*1.5;radius=.073*(1-.70*t)
            spiral.append((x+radius*math.cos(angle),y,z+.234+radius*math.sin(angle)))
        tube(g,spiral,.012,0,'weapon_r',10)
        tube(g,[(x,y,z+.140),(x,y,z+.161)],.014,2,'weapon_r',10)


def motion_pose(unit,clip,frame):
    pose=prepared_pose(unit,clip,frame)
    if unit['id']==IDS[0] and clip in ('Idle','Move','Hit','Victory'):
        # A relaxed nock stays nearer the bow; attacks visibly pull it back.
        pose['palms']['r']=(.008,pose['palms']['r'][1]+.010,pose['palms']['r'][2])
        pose['hand_euler']['r']=(0,0,0)
    if unit['id']==IDS[0] and clip=='Active':
        load,recover=action_envelope(frame,clip_spec(unit)[clip]);aim=load*(1-recover)
        pose['palms']={side:(p[0],p[1],p[2]+.023*aim) for side,p in pose['palms'].items()}
        pose['head_euler']=(-6*aim,0,-9*aim)
    if unit['id']==IDS[1]:
        pose['body']=(pose['body'][0],pose['body'][1],pose['body'][2]-.005)
        pose['feet']['l']=(.095,pose['feet']['l'][1]+.023,pose['feet']['l'][2])
        pose['feet']['r']=(-.095,pose['feet']['r'][1]-.023,pose['feet']['r'][2])
    return pose


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--unit',choices=IDS,required=True)
    parser.add_argument('--report',type=Path,required=True);parser.add_argument('--revision',type=int,default=1)
    parser.add_argument('--movies',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    uid=args.unit;report=args.report.resolve()
    if report.exists() or not report.is_relative_to((ROOT/'reports').resolve()):raise ValueError('Use a new reports path')
    report.mkdir(parents=True)
    unit=next(u for u in json.loads((ROOT/'data/units.json').read_text())['units'] if u['id']==uid)
    out=ROOT/'exports/heroes'/uid;source=ROOT/'art-source/heroes'/uid
    for label,folder in (('source',source),('exports',out)):
        if folder.exists():shutil.copytree(folder,report/('before-'+label))
        folder.mkdir(parents=True,exist_ok=True)
    write(report/'input.json',dict(unit_id=uid,revision=args.revision,blender_version=bpy.app.version_string,
          author_sha256=sha(__file__),pilot_helper_sha256=sha(pilot.__file__),family_helper_sha256=sha(ROOT/'tools/blender/halfling_production_profile.py'),units_sha256=sha(ROOT/'data/units.json')))
    pilot.UID=uid;pilot.motion_pose=motion_pose
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.fps=60
    for name in ('BODY','COSTUME','EQUIPMENT','RIG','PRESENTATION_HELPERS','EXPORT'):
        scene.collection.children.link(bpy.data.collections.new(name))
    mat=pilot.material(unit,out);arm,points=pilot.create_rig(unit['height_m']);geo=body(unit,points)
    equipment_start=len(geo.faces);gear(geo,points,uid);mesh=make_mesh(geo,unit,arm,mat)
    for polygon,color in zip(mesh.data.polygons,geo.colors):
        if color in (0,1,2,6,7,14):polygon.use_smooth=True
    for obj in (arm,mesh):
        for collection in list(obj.users_collection):collection.objects.unlink(obj)
        bpy.data.collections['EXPORT'].objects.link(obj)
    bpy.data.collections['RIG'].objects.link(arm);preserve_source_parts(mesh,geo,equipment_start)
    export_fbx(out/f'SK_{uid}.fbx',[arm,mesh],False);lods=pilot.clean_lods(unit,mesh,arm,out)
    clips,ik=pilot.animate(unit,arm,out);write(report/'executed-ik-reach.json',ik)
    if any(row['maximum_hand_ik_clamp_m']>.0001 or row['maximum_foot_ik_clamp_m']>.0001 for row in ik):
        raise RuntimeError('Hand or foot target outside the frozen rig reach; inspect IK report')
    pilot.audit_frames(arm,mesh,clips,report);setup_render(unit['height_m'])
    pilot.render_views(unit,arm,clips,report,out)
    if args.movies:pilot.render_movies(unit,arm,clips,report)
    pilot.use_clip(arm,clips['Idle']);pilot.camera_view(unit,'three-quarter')
    scene.render.resolution_x=scene.render.resolution_y=768
    source_file=source/f'{uid}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source_file));mesh.data.calc_loop_triangles()
    manifest=dict(status='AUTHORED_EXPORTED_BLENDER_EXECUTED_ENGINE_AND_VISUAL_ACCEPTANCE_OPEN',unit_id=uid,name=unit['name'],
        blender_version=bpy.app.version_string,source_revision=args.revision,geometry_revision=args.revision,geometry_source_revision=args.revision,animation_revision=args.revision,
        source_sha256=sha(source_file),author_script_sha256=sha(__file__),pilot_helper_sha256=sha(pilot.__file__),family_helper_sha256=sha(ROOT/'tools/blender/halfling_production_profile.py'),
        units_source_sha256=sha(ROOT/'data/units.json'),height_m=unit['height_m'],rig_family=unit['rig_family'],rig_revision=RIG_REVISION,
        bones=len(arm.data.bones),triangles=len(mesh.data.loop_triangles),materials=1,fps=60,source_forward='+Y',source_up='+Z',unit_scale_m=1,
        fbx_profile='tools/blender/profiles/fbx_skeletal_cm_v1.json',normalized_export_revision=1,normalized_exporter_sha256=sha(ROOT/'tools/blender/normalized_fbx.py'),
        exported_coordinate_units='centimeters in independent temporary copies; source metres',
        engine_calibration=['reports/WC-330/import-probe/forward_cm-results.json','reports/WC-330/import-probe/all7-comparison.json'],
        textures={'BaseColor':'sRGB','Normal':'linear flat tangent +Y; geometric bevels','ORM':'linear R occlusion, G roughness, B metallic'},
        clips=clips,lods=lods,source_brief=unit['art'],equipment='Visual only; '+PROFILES[uid]['gear']+'; '+PROFILES[uid]['rear'],
        files={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='export_manifest.json'},report_directory=str(report.relative_to(ROOT)),
        open_reviews=['continuous seven-clip visual quality','hands and weapon contact','crowded game-camera identity','actual Unreal import/reimport','LOD silhouettes','effects/audio synchronization'])
    write(out/'export_manifest.json',manifest)
    saved=sys.argv
    try:
        sys.argv=['inspect_scene.py','--','--collection','EXPORT','--output',str(report/'structural.json'),'--require-skin']
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
        sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(report/'sampled-motion.json')]
        runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved
    write(report/'completed.json',dict(status='BLENDER_EXECUTED_REVIEW_REQUIRED',unit_id=uid,source_sha256=manifest['source_sha256'],
        export_manifest_sha256=sha(out/'export_manifest.json'),triangles=manifest['triangles'],clips=len(clips)))
    print('WC_HALFLING_EXPORTED '+json.dumps({'unit':uid,'report':str(report),'triangles':manifest['triangles']}),flush=True)


if __name__=='__main__':main()
