import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_understrap_prebent.blend');names=json.loads(s['BW6_SHOULDER_SUPPORT_STUDY']);s['BW6_SHOULDER_STRAP_STATUS']='ART_REVISE_NOT_FOR_APPEND';s['BW6_SHOULDER_STRAP_FAILURE']='Initial plus2 bounded routing revisions. Full119-pose analysis retains cloth and first-lame crossings. No body or tested self-crossings. No allowed terminal overlap exclusions were used.';freeze=R/'ada_bw6_shoulder_understrap_checkpoint_ART_REVISE.blend';assert not freeze.exists();s.frame_set(56);bpy.context.view_layer.update();before={n:ck.geom(bpy.data.objects[n])[0] for n in names};s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(freeze));s=ck.load(freeze);s.frame_set(56);bpy.context.view_layer.update();errs={n:float(np.max(np.abs(ck.geom(bpy.data.objects[n])[0]-before[n]))) for n in names};assert max(errs.values())<2e-6
for pose,cage in [(56,False),('lowered',False),(56,True)]:
 s=ck.load(freeze)
 if pose=='lowered':ck.lowered(s)
 else:s.frame_set(pose)
 for o in s.objects:
  if o.type=='MESH':o.hide_render=o.name not in names+['BW6_PaddedCoat_Tailored']
 camera=bpy.data.objects['BW4_Camera_shoulder'];camera.location=(3,.8,1.02);camera.rotation_euler=(Vector((.26,-.01,1.42))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.37
 if cage:
  for name in names:
   o=bpy.data.objects[name]
   for m in o.modifiers:
    if m.type!='HOOK':m.show_render=False
   w=o.modifiers.new('Actual posed support cage','WIREFRAME');w.thickness=.0008;w.use_replace=False;w.use_even_offset=False
 ck.render(s,'strap_failed_exposed_'+str(pose)+('_cage' if cage else ''),pose=pose)
(R/'records/strap_failure_reopen.json').write_text(json.dumps({'source':str(freeze),'sha256':hashlib.sha256(freeze.read_bytes()).hexdigest(),'reopen_frame':56,'evaluated_error_m':errs,'captures':'Steel hidden only for exposed strap diagnostics. Hooks remain active. Source immutable.','status':'ART_REVISE_NOT_FOR_APPEND'},indent=2));print('FAILED_STRAP_SAVED_REOPENED')
