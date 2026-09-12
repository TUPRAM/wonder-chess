"""Static correspondence/rest-state inspection of the immutable BW1 snapshot. No blend save."""
import bpy, json, math, hashlib, re
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001')
body=bpy.data.objects['BW1_IndexedBody']; master=bpy.data.objects['MP1_MpfbFoundation_Source']
rig=bpy.data.objects['BW1_Temporary_Pose_Rig']; scene=bpy.data.scenes['BW1_BODY_COSTUME']
def coords(data):
    a=np.empty(len(data)*3,dtype=np.float32);data.foreach_get('co',a);return a.reshape(-1,3)
def mix(o):
    k=o.data.shape_keys
    if not k:return coords(o.data.vertices)
    out=coords(k.reference_key.data).astype(np.float64)
    for key in k.key_blocks:
        if key==k.reference_key or key.mute or key.value==0:continue
        out+=(coords(key.data)-coords(key.relative_key.data))*key.value
    return out
def world(o,p):
    mat=np.array(o.matrix_world,dtype=float);return p@mat[:3,:3].T+mat[:3,3]
def bounds(p):return {'min_m':p.min(axis=0).tolist(),'max_m':p.max(axis=0).tolist(),'extent_m':np.ptp(p,axis=0).tolist()}
def membership(o,name,minimum=0):
    idx=o.vertex_groups[name].index;return [v.index for v in o.data.vertices if any(g.group==idx and g.weight>minimum for g in v.groups)]
def weights(o):
    names={g.index:g.name for g in o.vertex_groups}
    return [{names[g.group]:float(g.weight) for g in v.groups if names[g.group] in rig.data.bones and g.weight>1e-8} for v in o.data.vertices]
def matrixlists(m):return [list(row) for row in m]
def key_hash(k):return hashlib.sha256(coords(k.data).tobytes()).hexdigest()
key_checks=[]
for k in master.data.shape_keys.key_blocks:
    other=body.data.shape_keys.key_blocks.get(k.name)
    key_checks.append({'name':k.name,'present':other is not None,'master_sha256':key_hash(k),'candidate_sha256':key_hash(other) if other else None,'coordinates_exact_equal':bool(np.array_equal(coords(k.data),coords(other.data))) if other else False,'value_unchanged':other.value==k.value if other else False,'master_value':k.value,'candidate_value':other.value if other else None})
same_faces=len(body.data.polygons)==len(master.data.polygons) and all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(body.data.polygons,master.data.polygons))
same_edges=len(body.data.edges)==len(master.data.edges) and all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(body.data.edges,master.data.edges))
out={'source_file':bpy.data.filepath,'snapshot_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'source_saved':False,'live_session_accessed':False,'measurement_space':'Body current shape-key mix, pre-armature rest-state world meters; no evaluated posed mesh used for anthropometric values.',
 'preservation':{'body_vertices':len(body.data.vertices),'master_vertices':len(master.data.vertices),'body_mesh_is_independent':body.data!=master.data,'body_keys_are_independent':body.data.shape_keys!=master.data.shape_keys,'mesh_datablock_names':[body.data.name,master.data.name],'key_datablock_names':[body.data.shape_keys.name,master.data.shape_keys.name],'base_mesh_coords_exact_equal':bool(np.array_equal(coords(body.data.vertices),coords(master.data.vertices))),'indexed_face_lists_exact_equal':same_faces,'indexed_edge_lists_exact_equal':same_edges,'master_key_count':len(master.data.shape_keys.key_blocks),'body_key_count':len(body.data.shape_keys.key_blocks),'original_key_checks':key_checks,'added_keys':[{'name':k.name,'value':k.value} for k in body.data.shape_keys.key_blocks if k.name not in master.data.shape_keys.key_blocks]},
 'scene_settings':{k:scene[k] for k in ('body_height_target_m','fitting_scale','rest_pose','body_landmarks_initial','body_target_settings','BW1_leg_pose_spec') if k in scene}}
out['contextual_head_preservation']={}
# Objects outside the active scene can have unevaluated cached world matrices.
# Evaluate each scene explicitly before comparing contextual placement.
bpy.context.window.scene=bpy.data.scenes['MP1_ADA_HEAD']
bpy.context.view_layer.update()
original_world_matrices={n:bpy.data.objects[n].matrix_world.copy() for n in ('MP1_Head_r002','MP1_Eye_R','MP1_Eye_L')}
bpy.context.window.scene=scene
bpy.context.view_layer.update()
for n,original in [('BW1_Context_Head_ART_REVISE','MP1_Head_r002'),('BW1_Context_Eye_R','MP1_Eye_R'),('BW1_Context_Eye_L','MP1_Eye_L')]:
    a=bpy.data.objects[n]; b=bpy.data.objects[original];p=coords(a.data.vertices);q=coords(b.data.vertices)
    aw=world(a,p); bm=np.array(original_world_matrices[original]);bw=q@bm[:3,:3].T+bm[:3,3]
    out['contextual_head_preservation'][n]={'original':original,'vertices':len(p),'mesh_independent':a.data!=b.data,'local_coordinates_exact_equal':bool(np.array_equal(p,q)),'maximum_local_coordinate_distance_m':float(np.linalg.norm(p-q,axis=1).max()),'maximum_world_coordinate_distance_m':float(np.linalg.norm(aw-bw,axis=1).max()),'face_lists_exact_equal':len(a.data.polygons)==len(b.data.polygons) and all(tuple(x.vertices)==tuple(y.vertices) for x,y in zip(a.data.polygons,b.data.polygons)),'candidate_matrix_world':matrixlists(a.matrix_world),'original_matrix_world':matrixlists(original_world_matrices[original]),'world_matrices_evaluated_in_respective_scenes':True,'candidate_unmodified_world_bounds':bounds(aw),'original_unmodified_world_bounds':bounds(bw)}
bp=world(body,mix(body));sp=world(master,mix(master));ids=membership(body,'body'); sid=membership(master,'body'); bw=weights(body)
def head(n):return np.array(rig.matrix_world@rig.data.bones[n].head_local)
def tail(n):return np.array(rig.matrix_world@rig.data.bones[n].tail_local)
def length(a,b):return float(np.linalg.norm(a-b))
restbones={n:{'head_world_m':head(n).tolist(),'tail_world_m':tail(n).tolist(),'rest_matrix_world':matrixlists(rig.matrix_world@rig.data.bones[n].matrix_local),'parent':rig.data.bones[n].parent.name if rig.data.bones[n].parent else None} for n in rig.data.bones.keys()}
out['rig_rest']={'name':rig.name,'bone_count':len(rig.data.bones),'matrix_world':matrixlists(rig.matrix_world),'bones':restbones}
measure={'complete_source_skin_rest_bounds_world':bounds(bp[ids]),'original_MP1_untransformed_skin_mix_bounds':bounds(sp[sid]),'display_below_neck_skin_bounds_world':bounds(bp[sorted(set(ids)&set(membership(body,'BW1_Display_Body_Below_Neck')))]),'shoulder_joint_center_span_m':length(head('upperarm01.R'),head('upperarm01.L')),'hip_joint_center_span_m':length(head('upperleg01.R'),head('upperleg01.L')),'sides':{}}
for side in ('R','L'):
    shoulder=head('upperarm01.'+side);elbow=head('lowerarm01.'+side);wrist=head('wrist.'+side);hip=head('upperleg01.'+side);knee=head('lowerleg01.'+side);ankle=head('foot.'+side)
    footids=[i for i in ids if sum(v for k,v in bw[i].items() if k=='foot.'+side or k.startswith('toe') and k.endswith('.'+side))>0.01 and bp[i,2]<ankle[2]+0.015]
    forward=tail('toe2-3.'+side)-ankle;forward[2]=0;forward/=np.linalg.norm(forward)
    sideaxis=np.array([forward[1],-forward[0],0])
    palm1=head('finger2-1.'+side);palm2=head('finger5-1.'+side)
    measure['sides'][side]={'shoulder_m':shoulder.tolist(),'elbow_m':elbow.tolist(),'wrist_m':wrist.tolist(),'hip_m':hip.tolist(),'knee_m':knee.tolist(),'ankle_m':ankle.tolist(),'upperarm_joint_length_m':length(shoulder,elbow),'forearm_joint_length_m':length(elbow,wrist),'shoulder_to_wrist_chain_length_m':length(shoulder,elbow)+length(elbow,wrist),'palm_index_to_pinky_MCP_joint_span_m':length(palm1,palm2),'palm_span_definition':'Joint-center distance finger2-1 head to finger5-1 head, excludes soft-surface margins and thumb.','upperleg_joint_length_m':length(hip,knee),'lowerleg_joint_length_m':length(knee,ankle),'hip_to_ankle_chain_length_m':length(hip,knee)+length(knee,ankle),'foot_skin_selection_count':len(footids),'foot_length_horizontal_projection_m':float(np.ptp(bp[footids]@forward)),'foot_width_horizontal_projection_m':float(np.ptp(bp[footids]@sideaxis)),'foot_selection_definition':'Skin vertices with foot or toe weights >0.01, below ankle center plus15mm; length along horizontal ankle-to-toe2 tip direction.','foot_skin_bounds_world':bounds(bp[footids])}
    palm_normal=head('finger3-1.'+side)-wrist; palm_plane=wrist+0.60*palm_normal; palm_normal/=np.linalg.norm(palm_normal)
    width_axis=palm2-palm1;width_axis-=palm_normal*np.dot(width_axis,palm_normal);width_axis/=np.linalg.norm(width_axis)
    palm_ids=set(i for i in ids if sum(v for k,v in bw[i].items() if k.endswith('.'+side) and ('finger' in k or 'metacarpal' in k or 'wrist' in k))>0.20 and sum(v for k,v in bw[i].items() if k.startswith('finger1-'))<0.20)
    points=[]
    for e in body.data.edges:
        a,b=e.vertices
        if a not in palm_ids or b not in palm_ids:continue
        da=np.dot(bp[a]-palm_plane,palm_normal);db=np.dot(bp[b]-palm_plane,palm_normal)
        if da*db<0:points.append(bp[a]+da/(da-db)*(bp[b]-bp[a]))
    measure['sides'][side]['palm_skin_midsection']={'definition':'Skin edge intersection with plane60% from wrist joint to middle MCP; thumb-heavy edges excluded; width perpendicular to palm long axis toward index-pinky MCP span. Diagnostic measure, not clinical anthropometry.','intersections':len(points),'width_m':float(np.ptp(np.array(points)@width_axis)) if points else None,'plane_point_m':palm_plane.tolist(),'plane_normal':palm_normal.tolist()}
# Horizontal torso cross sections use actual mesh edges, excluding arm-weighted endpoints.
torso_set=set(i for i in ids if sum(w for k,w in bw[i].items() if any(t in k for t in ('arm','wrist','finger','metacarpal')))<0.05)
sections={}
for name,fraction in [('ribcage_section',0.70),('waist_section',0.61),('pelvis_section',0.54)]:
    z=float(scene['body_height_target_m'])*fraction;points=[]
    for e in body.data.edges:
        a,b=e.vertices
        if a not in torso_set or b not in torso_set:continue
        if (bp[a,2]-z)*(bp[b,2]-z)<0:
            t=(z-bp[a,2])/(bp[b,2]-bp[a,2]);points.append(bp[a]+t*(bp[b]-bp[a]))
    points=np.array(points);sections[name]={'height_m':z,'height_choice':'Fixed diagnostic plane at '+str(fraction)+' times chosen source height; not a recovered 2D reference measurement.','intersected_edges':len(points),'width_m':float(np.ptp(points[:,0])),'depth_m':float(np.ptp(points[:,1]))}
measure['torso_diagnostic_sections']=sections
measure['ribcage_to_pelvis_width_ratio']=sections['ribcage_section']['width_m']/sections['pelvis_section']['width_m']
ctx=world(bpy.data.objects['BW1_Context_Head_ART_REVISE'],coords(bpy.data.objects['BW1_Context_Head_ART_REVISE'].data.vertices))
measure['assembled_context_skin_height_m']=float(ctx[:,2].max()-bp[ids,2].min())
measure['assembled_context_note']='Undivided cage coordinate bounds for retained contextual head + body feet; excludes hair, armor, soles and subdivision. This is distinct from full MPFB source height.'
out['measurements']=measure
def weight_audit(o):
    w=weights(o);p=world(o,coords(o.data.vertices));sums=[sum(x.values()) for x in w]
    result={'vertices':len(w),'unweighted_vertices':sum(s<1e-6 for s in sums),'maximum_weight_sum_error':max(abs(s-1) for s in sums),'minimum_sum':min(sums),'maximum_sum':max(sums),'maximum_deform_influences':max(len(x) for x in w),'negative_weight_count':sum(v<0 for x in w for v in x.values()),'opposite_side_weight_vertices':0,'maximum_opposite_side_weight':0,'deform_group_names':sorted(set(k for x in w for k in x)),'point_integer_attributes':[a.name for a in o.data.attributes if a.domain=='POINT' and a.data_type=='INT']}
    for i,x in enumerate(w):
        if abs(p[i,0])<.01:continue
        wrong='.L' if p[i,0]>0 else '.R';v=sum(v for k,v in x.items() if k.endswith(wrong));result['opposite_side_weight_vertices']+=v>1e-5;result['maximum_opposite_side_weight']=max(v,result['maximum_opposite_side_weight'])
    if 'mpfb_source_index' in o.data.attributes:
        ix=[d.value for d in o.data.attributes['mpfb_source_index'].data]
        errs=[]
        for i,j in enumerate(ix):
            if not 0<=j<len(bw):continue
            errs.append(max([abs(w[i].get(k,0)-bw[j].get(k,0)) for k in set(w[i])|set(bw[j])],default=0))
        result['source_index_audit']={'count':len(ix),'unique':len(set(ix)),'min':min(ix),'max':max(ix),'out_of_range':sum(not 0<=j<len(bw) for j in ix),'maximum_deform_weight_difference_from_named_source_vertex':max(errs),'vertices_with_difference_over_1e_6':sum(e>1e-6 for e in errs)}
    if 'Glove' in o.name:
        # Only distal-segment proximity candidates; web/palm blends are not judged as defects.
        flags=[];tested=0
        for i,x in enumerate(w):
            side='R' if p[i,0]>0 else 'L'; choices=[]
            for digit in range(1,6):
                for segment in (2,3):
                    n=f'finger{digit}-{segment}.{side}';a=head(n);b=tail(n);ab=b-a;t=float(np.dot(p[i]-a,ab)/np.dot(ab,ab));clamped=max(0,min(1,t));dist=length(p[i],a+ab*clamped)
                    choices.append((dist,digit,segment,t))
            dist,digit,segment,t=min(choices)
            if dist>.014 or t<.1 or t>.9:continue
            tested+=1
            foreign=sum(v for k,v in x.items() if k.startswith('finger') and int(k[6])!=digit)
            if foreign>.1:flags.append({'vertex':i,'nearest_digit':digit,'nearest_segment':segment,'distance_m':dist,'foreign_digit_weight':foreign,'weights':x})
        result['distal_finger_leakage_screen']={'definition':'Nearest second/third finger bone segment, interior10%-90%, distance<14mm; foreign-digit weight>0.1 is a heuristic flag, not proof of a defect.','vertices_tested':tested,'flagged_count':len(flags),'flags':flags}
    if o.name=='BW1_Leggings':
        suspects=[{'vertex':i,'world_m':p[i].tolist(),'arm_hand_weight':sum(v for k,v in x.items() if any(t in k for t in ('arm','wrist','finger','metacarpal'))),'weights':x} for i,x in enumerate(w) if sum(v for k,v in x.items() if any(t in k for t in ('arm','wrist','finger','metacarpal')))>0.01]
        result['arm_hand_influence_screen']={'threshold':0.01,'flagged_count':len(suspects),'maximum':max([r['arm_hand_weight'] for r in suspects],default=0),'flags':suspects}
        adjacency=[set() for _ in w]
        for edge in o.data.edges:
            a,b=edge.vertices;adjacency[a].add(b);adjacency[b].add(a)
        unseen=set(range(len(w)));components=[]
        while unseen:
            todo=[next(iter(unseen))]; component=set()
            while todo:
                i=todo.pop()
                if i in component:continue
                component.add(i);todo.extend(adjacency[i]-component)
            unseen-=component
            components.append({'vertices':len(component),'indices':sorted(component) if len(component)<50 else None,'bounds_world':bounds(p[sorted(component)]),'maximum_arm_hand_weight':max(sum(v for k,v in w[i].items() if any(t in k for t in ('arm','wrist','finger','metacarpal'))) for i in component)})
        result['connected_components']=components
    return result
out['weight_and_correspondence_audits']={n:weight_audit(bpy.data.objects[n]) for n in ('BW1_CoatUpper_Continuous','BW1_Glove_Pair_SourceFit','BW1_Boot_Pair_SourceFit','BW1_Leggings')}
out['preservation']['new_garment_masks']=[{'name':m.name,'viewport':m.show_viewport,'render':m.show_render} for m in body.modifiers if m.type=='MASK' and m.name.startswith('Delete.')]
(ROOT/'reviews/body_measurements.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'preservation':{k:v for k,v in out['preservation'].items() if k!='original_key_checks'},'all_original_keys_unchanged':all(k['coordinates_exact_equal'] and k['value_unchanged'] for k in key_checks),'head':out['contextual_head_preservation'],'measurements':measure,'weights':out['weight_and_correspondence_audits']},indent=2))
