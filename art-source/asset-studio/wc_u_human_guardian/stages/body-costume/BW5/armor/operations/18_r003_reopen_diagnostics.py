import bpy,json,hashlib,ast,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];frozen=R/'ada_bw5_armor_checkpoint_r003_ART_REVISE.blend';work=R/'ada_bw5_armor_work.blend'
def signature(o):
    h=hashlib.sha256();me=o.data;a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(str([tuple(p.vertices) for p in me.polygons]).encode());h.update(str([[(g.group,round(g.weight,8)) for g in v.groups] for v in me.vertices]).encode())
    if me.shape_keys:
        for key in me.shape_keys.key_blocks:key.data.foreach_get('co',a);h.update(key.name.encode());h.update(a.tobytes())
    return h.hexdigest()
def allmesh():return {o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
def pose_samples():
    s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;r=bpy.data.objects['BW4_Armor_Independent_Rig'];out=[]
    for fr in [1,25,49,73,97]:
        s.frame_set(fr);bpy.context.view_layer.update();out.append([[list(x) for x in pb.matrix] for pb in r.pose.bones])
    return np.array(out)
bpy.ops.wm.open_mainfile(filepath=str(R.parents[1]/'BW4/r001/armor/ada_armor_checkpoint_FINAL_ART_REVISE.blend'),use_scripts=False)
baseline=allmesh();poses=pose_samples();cam0={o.name:[list(r) for r in o.matrix_world] for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('BW4_Camera_')}
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw5_armor_correction2.blend'),use_scripts=False);c2=allmesh()
bpy.ops.wm.open_mainfile(filepath=str(work),use_scripts=False);ws=allmesh()
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False);fs=allmesh();assert ws==fs
changed=set(['BW4_Breastplate_ControlSurface','BW4_Backplate_ControlSurface','BW4_Front_Side_L_Return','BW4_Front_Side_R_Return','BW4_Back_Side_L_Return','BW4_Back_Side_R_Return'])
assert all(fs[n]==v for n,v in c2.items() if n not in changed)
preserve=[n for n in baseline if n.startswith('BW1_') or n.startswith('BW4_CONTEXT_')]
assert all(fs[n]==baseline[n] for n in preserve)
poseerr=float(np.max(np.abs(pose_samples()-poses)));assert poseerr<1e-6
cam={o.name:[list(r) for r in o.matrix_world] for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('BW4_Camera_')};assert cam==cam0
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
sol=[]
for n,th in [('BW4_CONTEXT_BW1_CoatUpper_Continuous',.006),('BW4_CONTEXT_BW1_Leggings',.002)]:
    m=next(m for m in bpy.data.objects[n].modifiers if m.type=='SOLIDIFY');assert abs(m.thickness-th)<1e-7 and m.offset==-1 and not m.use_even_offset;sol.append({'name':n,'thickness_m':m.thickness,'offset':m.offset,'even_offset':m.use_even_offset})
active=json.loads(s['BW5_owned_visible_parts']);allow=[o.name for o in s.objects if o.type=='MESH' and not o.hide_render]
(R/'records/render_allowlist.json').write_text(json.dumps({'scene':s.name,'visible_meshes':allow,'owned_visible_parts':active,'rejected_new_collar_hidden':bpy.data.objects['BW5_Tailored_Collar'].hide_render,'old_collar_and_shoulders':'Unchanged context, ART_REVISE'},indent=2))
struct=[]
for name in active:
    o=bpy.data.objects[name];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();struct.append({'name':name,'cage_vertices':len(o.data.vertices),'evaluated_vertices':len(me.vertices),'triangles':len(me.loop_triangles),'degenerate_polygons':sum(p.area<1e-12 for p in me.polygons),'finite':all(math.isfinite(x) for v in me.vertices for x in v.co),'owner_bone':o.get('owner_bone'),'modifiers':[m.type for m in o.modifiers]});ev.to_mesh_clear()
old=R.parents[1]/'BW4/r001/armor/operations/08_verify_and_motion.py';t=ast.parse(old.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['geom','crossing']],type_ignores=[]),str(old),'exec'),globals())
q=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';t=ast.parse(q.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='segment_triangle'],type_ignores=[]),str(q),'exec'),globals())
checks=['BW4_Breastplate_ControlSurface','BW4_Backplate_ControlSurface','BW5_Navy_Waist_Enclosure','BW4_Thorax_SideReturn_1','BW4_Thorax_SideReturn_-1']
extra=[]
for fr in [19.75,20.25,27.75,28.25,28.75,29.25,53.75,54.25]:
    s.frame_set(int(fr),subframe=fr-int(fr));bpy.context.view_layer.update();coat=geom(bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']);extra.append({'frame':fr,'vs_coat':{n:crossing(geom(bpy.data.objects[n]),coat) for n in checks}})
(R/'records/r003_critical_subframes.json').write_text(json.dumps({'source':str(frozen),'sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'frames':extra,'scope':'Eight additional quarter-frame transverse crossing checks, not continuous collision certification'},indent=2))
report={'source_work':str(work),'work_sha256':hashlib.sha256(work.read_bytes()).hexdigest(),'frozen':str(frozen),'frozen_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'work_frozen_mesh_signatures_match':True,'c2_geometry_signatures_match_except_six_recorded_neckline_parts':True,'all97_current_source_audit':'records/r003_all97_crossings.json','unchanged_original_and_context_mesh_key_records':len(preserve),'historical_cameras_exactly_unchanged':True,'five_sampled_authoring_pose_matrix_max_difference':poseerr,'solidify_preserved':sol,'parts':struct,'reference_scene_has_independent_rig_data':bpy.data.objects['BW5_ReferencePose_Rig'].data!=bpy.data.objects['BW4_Armor_Independent_Rig'].data,'status':'ART_REVISE','not_run':['Canonical seven game clips','Unreal import/reimport','Packaged game','Human approval','Recipe promotion']}
(R/'verification_r003.json').write_text(json.dumps(report,indent=2))
# Supplementary torso bend/twist on the independent posing context. The original
# 97-frame action remains unchanged and contains arm tests, not torso bends.
rs=bpy.data.scenes['BW5_REFERENCE_POSE_APPROXIMATE'];bpy.context.window.scene=rs;rr=bpy.data.objects['BW5_ReferencePose_Rig'];rs.frame_set(1)
pb=rr.pose.bones['spine02'];basis=pb.matrix_basis.copy();tests=[]
for label,axis,deg in [('forward_bend','X',-10),('torso_twist','Z',15)]:
    pb.matrix_basis=basis;bpy.context.view_layer.update();world=rr.matrix_world@pb.matrix;head=world.translation.copy();turn=Matrix.Translation(head)@Matrix.Rotation(math.radians(deg),4,axis)@Matrix.Translation(-head);pb.matrix=rr.matrix_world.inverted()@turn@world;bpy.context.view_layer.update()
    row={'label':label,'bone':'spine02','world_axis':axis,'degrees':deg,'basis':[list(x) for x in pb.matrix_basis],'vs_coat':{}}
    g=geom(bpy.data.objects['BW5_REF_BW4_CONTEXT_BW1_CoatUpper_Continuous'])
    for n in checks:row['vs_coat'][n]=crossing(geom(bpy.data.objects['BW5_REF_'+n]),g)
    tests.append(row)
    for view in ['front','right','back']:
        rs.camera=bpy.data.objects['BW5_Reference_'+view];rs.render.filepath=str(R/'captures'/f'r003_diagnostic_{label}_{view}.png');bpy.ops.render.render(write_still=True)
pb.matrix_basis=basis
(R/'records/r003_supplementary_bending.json').write_text(json.dumps({'source':str(frozen),'scope':'Two static deliberate world-axis pose tests on independent reference rig. Not original authoring action, not actual game clips or validated anatomical range. No source save.','tests':tests},indent=2))
assert hashlib.sha256(frozen.read_bytes()).hexdigest()==report['frozen_sha256']
print('REOPEN_AND_SUPPLEMENTARY_DIAGNOSTICS_COMPLETE',flush=True)
