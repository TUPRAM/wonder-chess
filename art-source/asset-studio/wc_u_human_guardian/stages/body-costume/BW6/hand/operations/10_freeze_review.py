"""Freeze local anatomical surface, retain failures and render actual evidence."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parents[1];BW4=OUT.parents[1]/'BW4/r001';BW5=OUT.parents[1]/'BW5/hand'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=OUT/'ada_bw6_hand_local_transfer_initial.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
s=bpy.context.scene;o=bpy.data.objects['BW6_ClosedGlove_Reconstructed'];o.name='BW6_ClosedGlove_Retained'
s.name='BW6_ANATOMICAL_FIXED_HAND_ART_REVISE'
s['BW6_status']='ART_REVISE: improved anatomical mass construction; joint shape and distributed contact unfinished'
s['BW6_visual_blockers']='Block-like distal forms and narrow knuckle transitions; thumb pad/opposition under-described; no persistent contact screen pass'
s['BW6_runtime']='NOT_RUN_LOCAL_ART_AND_CONTACT_GATES_NOT_MET';s['BW6_human_approval']='NOT_ISSUED'
s['BW6_study_allowlist']=json.dumps([o.name]+['BW4_SelectedSword_'+n for n in ('handle','guard','blade')]);s['BW6_export_allowlist']='[]'
o['status']='ART_REVISE: zero confirmed transverse self/equipment pairs does not establish art or contact approval'
o['representation']='Independent new anatomical fixed-glove control surface; exact original CC0 wrist positions. No repaired bare-hand deformation claim.'
for ob in s.objects:
 if ob.type=='MESH':
  visible=ob==o or ob.name.startswith('BW4_SelectedSword_')
  ob.hide_render=not visible;ob.hide_set(not visible)
# The previous evaluated IDs are not reused. These new anatomical patches are
# declared from distal target segment parameters and palmar normals before scoring.
targetrecord=json.loads((OUT/'records/target_local_c2.json').read_text())
gestures=targetrecord['digit_gestures_m'];declared={}
o.data.update()
for name in ('index','middle','ring','little'):
 a,b=[Vector(p) for p in gestures[name][-2:]];axis=b-a;t=axis.normalized();u=Vector((1,0,0));u=(u-t*t.dot(u)).normalized();normal=u.cross(t).normalized()
 ids=[]
 for v in o.data.vertices:
  rel=v.co-a;along=rel.dot(axis)/axis.length_squared;radial=rel-axis*along
  if .18<along<.86 and radial.length<.014 and v.normal.dot(normal)>.35:ids.append(v.index)
 vg=o.vertex_groups.new(name='BW6_CONTACT_'+name)
 if ids:vg.add(ids,1,'REPLACE')
 declared[name]={'definition':'Distal anatomical target segment, inner palmar face; no nearest hilt selection','segment_a_m':list(a),'segment_b_m':list(b),'segment_fraction':[.18,.86],'radial_limit_m':.014,'normal_axis':list(normal),'normal_dot_min':.35,'cage_ids':ids}
ids=[v.index for v in o.data.vertices if .018<v.co.x<.040 and .058<v.co.y<.075 and .022<v.co.z<.042 and v.normal.y>.35]
vg=o.vertex_groups.new(name='BW6_CONTACT_thumb')
if ids:vg.add(ids,1,'REPLACE')
declared['thumb']={'definition':'Opposing thumb distal surface from authored target bounds, positive Y facing','x_m':[.018,.040],'y_m':[.058,.075],'z_m':[.022,.042],'normal_y_min':.35,'cage_ids':ids}
(OUT/'records/retained_pad_mapping_before_scoring.json').write_text(json.dumps({'source_geometry':str(source),'source_sha256':sha(source),'declaration_before_distance_scoring':True,'old_BW5_indices_reused':False,'selection_is_provisional_pending_visual_review':True,'regions':declared},indent=2))
s.camera=bpy.data.objects['BW4_oblique'];s.render.filepath=''
work=OUT/'ada_bw6_hand_work.blend';frozen=OUT/'ada_bw6_hand_checkpoint_ART_REVISE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(work));bpy.ops.wm.save_as_mainfile(filepath=str(frozen),copy=True);frozenhash=sha(frozen)
manifest={'retained_source':str(source),'retained_source_sha256':sha(source),'work':str(work),'work_sha256':sha(work),'frozen':str(frozen),'frozen_sha256':frozenhash,'BW5_preserved':{'file':str(BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend'),'sha256':sha(BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend')},'no_geometry_change_in_capture':True,'cameras':{},'captures':[],'scope':'Static local anatomical construction; game bind/actions, wrist deformation and seven clips NOT_RUN'}
exec(compile((Path(__file__).parent/'capture_body.txt').read_text(),str(Path(__file__).parent/'capture_body.txt'),'exec'),globals())
(OUT/'records/capture_manifest.json').write_text(json.dumps(manifest,indent=2))
print('BW6_RETAINED_FROZEN',frozenhash,flush=True)
