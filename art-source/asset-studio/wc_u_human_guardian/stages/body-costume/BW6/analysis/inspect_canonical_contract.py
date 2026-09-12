"""Read current alpha_24 source, sample its authored clips, never save a blend."""
from pathlib import Path
import bpy, json, hashlib, datetime, re

ROOT = Path(__file__).resolve().parents[7]
SOURCE = ROOT / 'art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend'
OUT = Path(__file__).resolve().parent / 'canonical_seven_clip_contract.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), use_scripts=False)
scene=bpy.context.scene
rigs=[o for o in scene.objects if o.type=='ARMATURE']
assert len(rigs)==1
rig=rigs[0]
rig.animation_data_create()
for t in rig.animation_data.nla_tracks: t.mute=True
mat=lambda m: [list(r) for r in m]
report={'status':'READ_ONLY_CANONICAL_AUTHORED_SOURCE_NOT_BW6_CANDIDATE_VERIFICATION',
        'source':str(SOURCE),'sha256_before':before,'blender':bpy.app.version_string,
        'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'fps':scene.render.fps,'fps_base':scene.render.fps_base,'rig':rig.name,
        'rig_world':mat(rig.matrix_world), 'bones':[], 'actions':[],
        'source_saved':False,'new_candidate_tested':False,'unreal_executed':False}
for b in rig.data.bones:
    report['bones'].append({'name':b.name,'parent':b.parent.name if b.parent else None,
      'deform':b.use_deform,'matrix_local':mat(b.matrix_local),
      'head_world':list(rig.matrix_world@b.head_local),'tail_world':list(rig.matrix_world@b.tail_local)})
report['digit_bones']=[b.name for b in rig.data.bones if re.search('finger|thumb|digit',b.name,re.I)]
report['constraints']={p.name:[{'name':c.name,'type':c.type} for c in p.constraints] for p in rig.pose.bones if p.constraints}
for clip in ('Idle','Move','Attack','Active','Hit','Defeat','Victory'):
    a=bpy.data.actions['AN_wc_u_human_guardian_'+clip]
    rig.animation_data.action=a
    if a.slots: rig.animation_data.action_slot=a.slots[0]
    curves=[c for l in a.layers for s in l.strips for bag in s.channelbags for c in bag.fcurves]
    rec={'name':a.name,'range':list(a.frame_range),'curve_count':len(curves),
         'animated_bones':sorted({re.search(r'pose.bones\["([^"]+)"\]',c.data_path).group(1) for c in curves if re.search(r'pose.bones\["([^"]+)"\]',c.data_path)}),
         'non_bone_paths':sorted({c.data_path for c in curves if not c.data_path.startswith('pose.bones[')}),
         'sample_interval_frames':0.5,'samples':0,'equipment_hand_relative_max_matrix_delta':0.0}
    first={}
    start,end=a.frame_range
    for step in range(round((end-start)*2)+1):
        f=start+step/2; scene.frame_set(int(f),subframe=f-int(f))
        ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for side in ('r','l'):
            rel=ev.pose.bones['hand_'+side].matrix.inverted()@ev.pose.bones['weapon_'+side].matrix
            if side not in first: first[side]=rel.copy()
            delta=max(abs(rel[i][j]-first[side][i][j]) for i in range(4) for j in range(4))
            rec['equipment_hand_relative_max_matrix_delta']=max(delta,rec['equipment_hand_relative_max_matrix_delta'])
        rec['samples']+=1
    report['actions'].append(rec)
report['sha256_after']=sha(SOURCE)
assert report['sha256_after']==before
OUT.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'output':str(OUT),'rig':rig.name,'bones':len(report['bones']),'actions':[{k:r[k] for k in ('name','range','curve_count','samples','equipment_hand_relative_max_matrix_delta')} for r in report['actions']],'sha256':before}))
