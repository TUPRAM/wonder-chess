import bpy,json,hashlib,ast,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];SOURCE=R/'ada_bw6_left_bracer_initial.blend'
p=R.parent/'operations/11_freeze_and_capture.py';tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='sig'],type_ignores=[]),str(p),'exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW6_LEFT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_owned'])];ctx=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])];rig=bpy.data.objects['BW6_LeftBracer_Independent_Rig'];F=json.loads(s['BW6_bracer_frame']);W=Vector(F['wrist']);A=Vector(F['proximal']);D=Vector(F['dorsal']);T=Vector(F['transverse'])
signature={o.name:sig(o) for o in owned+ctx};s['review_status']='LOCAL_REVIEW_CANDIDATE_NOT_HUMAN_APPROVED';s['runtime_status']='LEFT_AUTHORING_ADAPTATION_NOT_GAME_CLIPS'
work=R/'ada_bw6_left_bracer_work.blend';frozen=R/'ada_bw6_left_bracer_checkpoint_r001_REVIEW_CANDIDATE.blend';bpy.ops.wm.save_as_mainfile(filepath=str(work));bpy.ops.wm.save_as_mainfile(filepath=str(frozen))
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False);s=bpy.data.scenes['BW6_LEFT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);assert signature=={n:sig(bpy.data.objects[n]) for n in signature}
owned=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_owned'])];ctx=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])];rig=bpy.data.objects['BW6_LeftBracer_Independent_Rig'];sha=hashlib.sha256(frozen.read_bytes()).hexdigest()
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'work':str(work),'checkpoint':str(frozen),'sha256':sha,'mesh_weight_records_match_reopen':True,'signatures':signature,'captures':[]}
for o in ctx:
 vg=o.vertex_groups.new(name='LEFT_RENDER_ONLY_FOREARM_CROP')
 for v in o.data.vertices:
  q=o.matrix_world@v.co-W;t=q.dot(A);r=(q-A*t).length
  if -.22<t<.29 and r<.145:vg.add([v.index],1,'REPLACE')
 m=o.modifiers.new('Temporary image isolation; not saved','MASK');m.vertex_group=vg.name
def shot(label,cam):
 s.camera=bpy.data.objects['BW6_LeftBracer_Camera_'+cam];s.render.filepath=str(R/'captures'/(label+'.png'));bpy.ops.render.render(write_still=True);report['captures'].append({'path':s.render.filepath,'frame':s.frame_current,'camera':s.camera.name,'sha256_source':sha,'render_context':'Temporary forearm isolation on unchanged body/glove/coat copies; source file retains complete geometry'})
for label,cam in [('left_r001_dorsal','Dorsal'),('left_r001_volar','Volar'),('left_r001_three_quarter','ThreeQuarter'),('left_r001_axial','Axial')]:shot(label,cam)
wrist=rig.pose.bones['wrist.L'];basis=wrist.matrix_basis.copy();act=rig.animation_data.action;rig.animation_data.action=None;wrist.matrix_basis=basis@Matrix.Rotation(math.radians(25),4,'X');bpy.context.view_layer.update();shot('left_r001_wrist_Xplus25','ThreeQuarter');wrist.matrix_basis=basis;rig.animation_data.action=act;s.frame_set(1)
# Representative moved-arm image with tracked camera and actual world-delta authoring pose.
cam=bpy.data.objects['BW6_LeftBracer_Camera_ThreeQuarter'];restcam=cam.matrix_world.copy();restbone=(rig.matrix_world@rig.pose.bones['lowerarm02.L'].matrix).copy();s.frame_set(49);bpy.context.view_layer.update();cam.matrix_world=(rig.matrix_world@rig.pose.bones['lowerarm02.L'].matrix)@restbone.inverted()@restcam;shot('left_r001_authoring49_tracked','ThreeQuarter')
assert hashlib.sha256(frozen.read_bytes()).hexdigest()==sha;(R/'records/verification.json').write_text(json.dumps(report,indent=2));print('LEFT_REOPEN_AND_CAPTURES_DONE')
