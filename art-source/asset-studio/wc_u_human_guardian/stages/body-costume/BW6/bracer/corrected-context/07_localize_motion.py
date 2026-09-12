import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;SOURCE=R/'ada_bw6_bracers_actual_sleeve_correction2.blend';report=json.loads((R/'records/correction2_surface_checks.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;rig=bpy.data.objects['BW4_Armor_Independent_Rig'];coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];rec=next(r for r in json.loads(s['BW6_correct_context_bracer_record']) if r['side']=='R');F=rec['frame'];W=Vector(F['wrist']);A=Vector(F['proximal']);D=Vector(F['dorsal']);T=Vector(F['transverse']);findings=[]
for row in report['samples']:
 if not row['sample'].startswith('frame'):continue
 total=sum(q['pairs'] for p in row['parts'].values() for q in p['context'].values())
 if not total:continue
 f=int(row['sample'][5:]);s.frame_set(f);bpy.context.view_layer.update();pw=rig.matrix_world@rig.pose.bones['lowerarm02.R'].matrix;rw=rig.matrix_world@rig.data.bones['lowerarm02.R'].matrix_local;unpose=rw@pw.inverted();ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();examples=[]
 for n,p in row['parts'].items():
  r=p['context']['BW6_PaddedCoat_Tailored']
  for ex in r['examples']:
   world=Vector(ex['point']);q=unpose@world-W;ids=list(me.loop_triangles[ex['triangles'][1]].vertices);weights={}
   for i in ids:
    for g in me.vertices[i].groups:weights[coat.vertex_groups[g.group].name]=weights.get(coat.vertex_groups[g.group].name,0)+g.weight/3
   examples.append({'part':n,'point_world':list(world),'rigid_owner_rest_t_m':q.dot(A),'angle_deg':math.degrees(math.atan2(q.dot(T),q.dot(D))),'coat_evaluated_triangle':ids,'mean_coat_weights':weights})
 ev.to_mesh_clear();findings.append({'frame':f,'total_pairs':total,'examples':examples})
(R/'records/motion_failure_localization.json').write_text(json.dumps({'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'frames':findings},indent=2));print('FAIL_FRAMES',[(r['frame'],r['total_pairs']) for r in findings],flush=True)
if findings:
 poses=[findings[0]['frame'],max(findings,key=lambda r:r['total_pairs'])['frame']]
 for f in sorted(set(poses)):
  s.frame_set(f);bpy.context.view_layer.update();delta=(rig.matrix_world@rig.pose.bones['lowerarm02.R'].matrix)@(rig.matrix_world@rig.data.bones['lowerarm02.R'].matrix_local).inverted();target=delta@(W+A*.10);direction=delta.to_3x3()@(D*.32+T*.22);cd=bpy.data.cameras.new('BW6_FIT_MOTION_'+str(f));cd.type='ORTHO';cd.ortho_scale=.36;c=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(c);c.location=target+direction;c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c;s.cycles.samples=16;s.render.threads=3;s.render.filepath=str(R/'captures'/('r002_failed_motion_'+str(f)+'.png'));bpy.ops.render.render(write_still=True)
print('LOCAL_FAILURE_DONE_NO_SAVE')
