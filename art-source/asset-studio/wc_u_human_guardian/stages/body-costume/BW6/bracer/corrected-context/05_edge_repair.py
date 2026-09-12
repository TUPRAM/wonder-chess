import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;SOURCE=R/'ada_bw6_bracers_actual_sleeve_correction1.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
o=bpy.data.objects['BW6_Fit_R_Bracer_ClosureStrap_1'];m=next(m for m in o.modifiers if m.type=='BEVEL');before={'width':m.width,'segments':m.segments,'angle_limit':m.angle_limit};m.show_viewport=False;m.show_render=False
o['edge_repair']='Disable optional bevel creating one finite self-crossing pair at its narrow return; physical wall and smooth control surface retained.'
out=R/'ada_bw6_bracers_actual_sleeve_correction2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));(R/'records/correction2.json').write_text(json.dumps({'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'candidate':str(out),'object':o.name,'before':before,'after':'optional bevel disabled; no geometry, weights, body or coat edits'},indent=2))
s.cycles.samples=12;s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=960
for side in ['R','L']:
 rec=next(r for r in json.loads(s['BW6_correct_context_bracer_record']) if r['side']==side);f=rec['frame'];W=Vector(f['wrist']);A=Vector(f['proximal']);D=Vector(f['dorsal']);T=Vector(f['transverse']);target=W+A*.095
 for name,offset in [('dorsal',D*.45+A*.03),('volar',-D*.32+A*.01),('side',T*.4)]:
  cd=bpy.data.cameras.new('BW6_CorrectFit_'+side+'_'+name);cd.type='ORTHO';cd.ortho_scale=.35;c=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(c);c.location=target+offset;c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c;s.render.filepath=str(R/'captures'/('r002_'+side+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('EDGE_REPAIR_DONE')
