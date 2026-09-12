import bpy,bmesh,json,hashlib,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];BW4=OUT.parents[1]/'BW4/r001'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def geo(o):return {'matrix_world':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons]}
def geohash(o):return hashlib.sha256(json.dumps(geo(o),sort_keys=True).encode()).hexdigest()
baseline=BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend';before=sha(baseline)
assert before==json.loads((OUT/'records/root_inspection.json').read_text())['sha256']
bpy.ops.wm.open_mainfile(filepath=str(baseline),load_ui=False,use_scripts=False)
equipment={n:geo(bpy.data.objects['BW4_SelectedSword_'+n]) for n in ('handle','guard','blade')}
cameras={n:[list(r) for r in bpy.data.objects['BW4_'+n].matrix_world] for n in ('palm','dorsal','side','underside','oblique','axial')}
src=json.loads((BW4/'records/open_glove_geometry.json').read_text());co=Counter(tuple(sorted((a,b))) for f in src['faces'] for a,b in zip(f,f[1:]+f[:1]));source_wrist=[Vector(src['vertices_m'][i]) for i in sorted({i for e,c in co.items() if c==1 for i in e})]
report={'BW4_source':str(baseline),'BW4_sha256_before':before,'native_reopen':[],'runtime':'NOT_RUN_LOCAL_VISUAL_GATE_NOT_MET','source_data_were_not_written':True}
for file in ('ada_bw5_hand_work.blend','ada_bw5_hand_checkpoint_ART_REVISE.blend'):
 path=OUT/file;digest=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);o=bpy.data.objects['BW5_ClosedGlove_Retained'];bm=bmesh.new();bm.from_mesh(o.data)
 boundary=[v.co.copy() for v in bm.verts if any(e.is_boundary for e in v.link_edges)];bm.free()
 worst=max(min((p-q).length for q in boundary) for p in source_wrist)
 eq={n:geo(bpy.data.objects['BW4_SelectedSword_'+n])==expected for n,expected in equipment.items()}
 cam={n:[list(r) for r in bpy.data.objects['BW4_'+n].matrix_world]==matrix for n,matrix in cameras.items()}
 item={'file':str(path),'sha256':digest,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'mesh_hash':geohash(o),'mesh_data_users':o.data.users,'mesh_independent_from_hidden_BW4':o.data!=bpy.data.objects['BW5_Retained_BW4_FAILURE_HIDDEN'].data,'local_data_not_linked':o.library is None and o.data.library is None,'shape_keys':None if o.data.shape_keys is None else len(o.data.shape_keys.key_blocks),'modifiers':[{'name':m.name,'type':m.type,'levels':m.levels if m.type=='SUBSURF' else None} for m in o.modifiers],'wrist_boundary_vertices':len(boundary),'source_wrist_vertex_max_error_m':worst,'equipment_exact_geometry_and_transform_equal_BW4':eq,'historical_cameras_exact_equal_BW4':cam,'status':bpy.context.scene['BW5_status']}
 assert worst<1e-7 and len(boundary)==20 and all(eq.values()) and all(cam.values()) and item['mesh_independent_from_hidden_BW4'] and item['local_data_not_linked']
 item['sha256_after']=sha(path);assert item['sha256_after']==digest;report['native_reopen'].append(item)
assert len({p['mesh_hash'] for p in report['native_reopen']})==1
report['BW4_sha256_after']=sha(baseline);assert report['BW4_sha256_after']==before
handle=equipment['handle']['vertices'];report['selected_equipment']={'local_axis_guard_to_end':[-1,0,0],'handle_bounds_m':[[min(v[i] for v in handle),max(v[i] for v in handle)] for i in range(3)],'handle_dimension_m':[max(v[i] for v in handle)-min(v[i] for v in handle) for i in range(3)],'selected_exposed_length_m':.110,'guard_begin_x_m':.059,'registration_changed':False,'new_hand_registration_review':'Index and thumb are positive X, toward the guard. Little is negative X, toward the exposed hilt end. No mirrored matrix or hand scale applied.'}
(OUT/'records/reopen_and_preservation.json').write_text(json.dumps(report,indent=2))
# Decode the actual newly encoded MP4 in a separate native movie scene.
bpy.ops.wm.read_factory_settings(use_empty=True)
motion=OUT/'motion';video=motion/'BW5_HAND_ART_REVISE_STATIC_INSPECTION_NOT_GAME_CLIPS.mp4';expected=json.loads((OUT/'records/capture_manifest.json').read_text())['motion']['sha256'];assert sha(video)==expected
sc=bpy.context.scene;ed=sc.sequence_editor_create();strip=ed.strips.new_movie('Actual MP4 reopen',str(video),channel=1,frame_start=1);decoded=motion/'decoded';decoded.mkdir(exist_ok=True)
data={'file':str(video),'sha256':sha(video),'frames':strip.frame_duration,'fps':strip.fps,'dimensions':[strip.elements[0].orig_width,strip.elements[0].orig_height],'scope':'STATIC CAMERA TURNTABLE; NO GAME ANIMATION OR HOLDING MOTION CLAIM','source_saved':False}
assert data['frames']==48 and abs(data['fps']-24)<.001 and data['dimensions']==[800,800]
sc.frame_start=1;sc.frame_end=48;sc.render.fps=24;sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.filepath=str(decoded/'frame_');sc.render.use_file_extension=True;sc.render.use_sequencer=True;sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
bpy.ops.render.render(animation=True,scene=sc.name)
files=[decoded/f'frame_{f:04}.png' for f in range(1,49)];assert all(p.is_file() for p in files);data['decoded_frames']=48;data['frame_hashes']=[{'frame':i,'sha256':sha(p)} for i,p in enumerate(files,1)];data['sha256_after']=sha(video);assert data['sha256_after']==expected
(motion/'video_verification.json').write_text(json.dumps(data,indent=2));print('BW5_REOPEN_AND_DECODE_OK',flush=True)
