"""Native read-only reopen and preserved interface/source checks."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];STAGE=OUT.parents[1];BW4=STAGE/'BW4/r001';BW5=STAGE/'BW5/hand'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def geo(o):return {'matrix_world':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons]}
def geohash(o):return hashlib.sha256(json.dumps(geo(o),sort_keys=True).encode()).hexdigest()
protected={str(BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend'):'f85003358791c8346f4432a0fbdfc797047abca19ca9dc33c9d66428b411ffa3',str(BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend'):'bbd06c025af7ab848bd5e52e001e62b25d7a13edecd9bd70e75fd7650dd5d563',str(BW5/'ada_bw5_hand_work.blend'):'edf436f59dc54255db650decd9994fb9b693ffc1f53462498bc3578edf82ac41'}
for p,h in protected.items():assert sha(p)==h,(p,sha(p))
baseline=BW5/'ada_bw5_hand_checkpoint_ART_REVISE.blend';bpy.ops.wm.open_mainfile(filepath=str(baseline),load_ui=False,use_scripts=False)
equipment={n:geo(bpy.data.objects['BW4_SelectedSword_'+n]) for n in ('handle','guard','blade')}
cameras={n:{'matrix':[list(r) for r in bpy.data.objects['BW4_'+n].matrix_world],'ortho':bpy.data.objects['BW4_'+n].data.ortho_scale} for n in ('palm','dorsal','side','underside','oblique','axial')}
src=json.loads((BW4/'records/open_glove_geometry.json').read_text());co=Counter(tuple(sorted((a,b))) for f in src['faces'] for a,b in zip(f,f[1:]+f[:1]));source_wrist=[Vector(src['vertices_m'][i]) for i in sorted({i for e,c in co.items() if c==1 for i in e})]
report={'protected_baseline_sha256':protected,'native_reopen':[],'runtime':'NOT_RUN_LOCAL_ART_AND_CONTACT_GATES_NOT_MET','preservation_boundary':'Listed BW4/BW5 sources checked against baseline hashes; no unrelated project source writes in this lane'}
for file in ('ada_bw6_hand_work.blend','ada_bw6_hand_checkpoint_ART_REVISE.blend'):
 path=OUT/file;digest=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);o=bpy.data.objects['BW6_ClosedGlove_Retained'];bm=bmesh.new();bm.from_mesh(o.data)
 boundary=[v.co.copy() for v in bm.verts if any(e.is_boundary for e in v.link_edges)];bm.free();worst=max(min((p-q).length for q in boundary) for p in source_wrist)
 eq={n:geo(bpy.data.objects['BW4_SelectedSword_'+n])==expected for n,expected in equipment.items()}
 cam={n:{'matrix':[list(r) for r in bpy.data.objects['BW4_'+n].matrix_world],'ortho':bpy.data.objects['BW4_'+n].data.ortho_scale}==expected for n,expected in cameras.items()}
 item={'file':str(path),'sha256':digest,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'mesh_hash':geohash(o),'mesh_data_users':o.data.users,'mesh_independent_from_every_hidden_source':all(other==o or other.type!='MESH' or other.data!=o.data for other in bpy.data.objects),'local_data_not_linked':o.library is None and o.data.library is None,'shape_keys':None if o.data.shape_keys is None else len(o.data.shape_keys.key_blocks),'modifiers':[{'name':m.name,'type':m.type,'levels':m.levels if m.type=='SUBSURF' else None} for m in o.modifiers],'wrist_boundary_vertices':len(boundary),'source_wrist_vertex_max_error_m':worst,'equipment_exact_geometry_and_transform_equal_BW5':eq,'historical_cameras_exact_equal_BW5':cam,'status':bpy.context.scene['BW6_status']}
 assert worst<1e-7 and len(boundary)==20 and all(eq.values()) and all(cam.values()) and item['mesh_independent_from_every_hidden_source'] and item['local_data_not_linked']
 item['sha256_after']=sha(path);assert item['sha256_after']==digest;report['native_reopen'].append(item)
assert len({p['mesh_hash'] for p in report['native_reopen']})==1
for p,h in protected.items():assert sha(p)==h
handle=equipment['handle']['vertices'];report['selected_equipment']={'local_axis_guard_to_end':[-1,0,0],'handle_bounds_m':[[min(v[i] for v in handle),max(v[i] for v in handle)] for i in range(3)],'handle_dimension_m':[max(v[i] for v in handle)-min(v[i] for v in handle) for i in range(3)],'selected_exposed_length_m':.110,'guard_begin_x_m':.059,'registration_changed':False,'handedness':'Index/thumb positive X toward guard; little negative X toward hilt end. No mirrored matrix or hand scaling.'}
(OUT/'records/reopen_and_preservation.json').write_text(json.dumps(report,indent=2));print('BW6_REOPEN_PRESERVATION_OK',flush=True)
