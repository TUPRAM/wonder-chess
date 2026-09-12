"""Read-only native Blender reopen and exact data binding for BW3; never saves a blend."""
import bpy, hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
ROOT=Path(r"C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/r001")
BW2=ROOT.parents[1]/'BW2/r001'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('bw2_readonly_helpers',BW2/'reviews/audit_bw2_checkpoint.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
base=json.loads((ROOT/'reviews/preflight/saved_baseline_semantic_snapshot.json').read_text())
paths=[ROOT/'thumb_route_C_final_method_input.blend',ROOT/'ada_bw3_grip_work.blend',ROOT/'ada_bw3_grip_checkpoint_r001_ART_REVISE.blend']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def mat(m):return [list(v) for v in m]
def snapshot(p):
    before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
    s=bpy.data.scenes['BW3_COLLISION_FIRST'];bpy.context.window.scene=s;bpy.context.view_layer.update()
    r=bpy.data.objects['BW3_Derived_Rig'];g=bpy.data.objects['BW3_Derived_Glove'];b=bpy.data.objects['BW3_Derived_Body']
    checks={}
    for field in ['mesh_sources','modifiers','rigs','actions']:
        mismatches=[]
        for nm,record in base[field].items():
            if field=='mesh_sources':actual=h.mesh_source(bpy.data.objects[nm])
            elif field=='modifiers':actual=[h.modifier_record(m) for m in bpy.data.objects[nm].modifiers]
            elif field=='rigs':actual={'bones':h.rigid_rest(bpy.data.objects[nm])['bones'],'object_basis':mat(bpy.data.objects[nm].matrix_basis)}
            else:
                a=bpy.data.actions[nm];actual={'payload':h.action_source(a),'fake_user':a.use_fake_user,'slots':[v.identifier for v in a.slots]}
            if actual!=record:mismatches.append(nm)
        checks[field]={'compared':len(base[field]),'equal':not mismatches,'mismatches':mismatches}
    # Match master hierarchy, original camera optics, and scene membership; new candidate adds only its own scene/collections.
    mismatches=[]
    for nm,record in base['object_structures'].items():
        o=bpy.data.objects[nm]
        actual={'parent':o.parent.name if o.parent else None,'parent_type':o.parent_type,'parent_bone':o.parent_bone,'parent_inverse':mat(o.matrix_parent_inverse),'constraints':h.hierarchy(o)['constraints'],'data_name':o.data.name if o.data else None,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None}
        if actual!=record:mismatches.append(nm)
    checks['master_hierarchy']={'compared':len(base['object_structures']),'equal':not mismatches,'mismatches':mismatches}
    independence={'rig_data':r.data!=bpy.data.objects['BW1_Temporary_Pose_Rig'].data,
      'body_mesh':b.data!=bpy.data.objects['BW1_IndexedBody'].data,
      'body_shape_key_id':b.data.shape_keys!=bpy.data.objects['BW1_IndexedBody'].data.shape_keys,
      'glove_mesh':g.data!=bpy.data.objects['BW1_Glove_Pair_SourceFit'].data,
      'rig_action':r.animation_data.action!=bpy.data.objects['BW1_Temporary_Pose_Rig'].animation_data.action,
      'armature_targets':all(m.object==r for o in [g,b] for m in o.modifiers if m.type=='ARMATURE'),
      'fixture_parent':bpy.data.objects['BW3_Locked_Handle_28mm'].parent==bpy.data.objects['BW3_FixedHandFrame_R'],
      'holder_parent':bpy.data.objects['BW3_FixedHandFrame_R'].parent==r and bpy.data.objects['BW3_FixedHandFrame_R'].parent_bone=='wrist.R',
      'camera_data':all(o.data!=bpy.data.objects[o.name.replace('BW3_','BW2_',1)].data for o in s.objects if o.type=='CAMERA')}
    rigrest=h.rigid_rest(r);rigrest.pop('matrix_world')
    core={'meshes':{o.name:h.mesh_source(o) for o in [g,b,bpy.data.objects['BW3_Locked_Handle_28mm']]},
      'modifiers':{o.name:[h.modifier_record(m) for m in o.modifiers] for o in [g,b]},'rig_rest':rigrest,
      'actions':{a.name:h.action_source(a) for a in [r.animation_data.action,bpy.data.objects['BW3_cam_carry_close'].animation_data.action]},
      'hierarchy':{o.name:{k:v for k,v in h.hierarchy(o).items() if k not in ['matrix_world','properties']} for o in [r,g,b,bpy.data.objects['BW3_FixedHandFrame_R'],bpy.data.objects['BW3_Locked_Handle_28mm']]},
      'contract':{k:s[k] for k in ['BW2_frame_world','BW2_hand_contract','BW2_contact_patches_open','BW2_hand_frame_in_posebone']},
      'camera_optics':{o.name:{'matrix_basis':mat(o.matrix_basis),'lens':o.data.lens,'ortho_scale':o.data.ortho_scale,'type':o.data.type} for o in s.objects if o.type=='CAMERA' and o.animation_data is None}}
    saved={'frame':s.frame_current,'camera':s.camera.name,'action':r.animation_data.action.name,
      'scene':s.name,'objects':sorted(o.name for o in s.objects),'body_vertices':len(b.data.vertices),'body_keys':len(b.data.shape_keys.key_blocks),
      'glove_vertices':len(g.data.vertices),'rig_bones':len(r.data.bones),'properties':h.properties(s)}
    g.hide_set(False);b.hide_set(False)
    posed={}
    for f in [1,7,15,20,25,49,85,109,121,145]:
        s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
        for o in [g,b]:
            e=o.evaluated_get(dg);m=e.to_mesh()
            rows[o.name]={'verts':len(m.vertices),'vertices_hash':h.array_hash(m.vertices,'co',3,np.float32),'corners_hash':h.array_hash(m.loops,'vertex_index',1,np.int32),'world':mat(e.matrix_world)}
            e.to_mesh_clear()
        rows['fixture_world']=mat(bpy.data.objects['BW3_Locked_Handle_28mm'].matrix_world)
        posed[str(f)]=rows
    return {'path':str(p),'sha256':before,'sha_after':sha(p),'master_checks':checks,'independence':independence,'saved':saved,'core_hash':digest(core),'core':core,'posed_signature':posed}
assert bpy.app.background
snapshots=[snapshot(p) for p in paths]
protected=json.loads((ROOT/'records/BW2_complete_before.json').read_text())['files']
old62=json.loads((BW2/'preservation_before.json').read_text())
if isinstance(old62,dict):old62=old62.get('files',old62.get('artifacts',old62.get('records',[])))
pres=[]
for row in protected+old62:
    p=Path(row['path']);expected=row.get('sha256',row.get('hash'))
    pres.append({'path':str(p),'expected':expected,'actual':sha(p) if p.exists() else None})
result={'blender':bpy.app.version_string,'method':'Native reopen of work, frozen result and C evidence input. Exact masters and independent candidate data; action/mesh/modifier/hierarchy binding plus10 posed geometry samples. No source saves.',
 'files':[{k:v for k,v in row.items() if k not in ['core','posed_signature']} for row in snapshots],
 'binding':{'all_core_data_equal':len({r['core_hash'] for r in snapshots})==1,'all10_pose_samples_equal':all(r['posed_signature']==snapshots[0]['posed_signature'] for r in snapshots[1:]),'frames':[1,7,15,20,25,49,85,109,121,145]},
 'protected_file_count':len(pres),'protected_all_unchanged':all(r['expected']==r['actual'] for r in pres),'protected':pres,
 'all_source_files_unchanged_after_reopen':all(r['sha256']==r['sha_after'] for r in snapshots)}
result['reopen_pass']=all(all(v['equal'] for v in r['master_checks'].values()) and all(r['independence'].values()) for r in snapshots) and all(result['binding'][k] for k in ['all_core_data_equal','all10_pose_samples_equal']) and result['protected_all_unchanged'] and result['all_source_files_unchanged_after_reopen']
(ROOT/'records/reopen_and_preservation.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'records/reopen_data_signatures.json').write_text(json.dumps(snapshots,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['files','protected']},indent=2))

