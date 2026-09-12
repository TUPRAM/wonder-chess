"""Compare source arrays in r002 with data loaded read-only from frozen r001; never save blends."""
import bpy, json, hashlib
from pathlib import Path
import numpy as np
ROOT=Path(r'C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001')
prior=ROOT/'ada_body_costume_checkpoint_r001_ART_REVISE.blend'
def h(data):return hashlib.sha256(data).hexdigest()
def floats(data,field,width):
    a=np.empty(len(data)*width,dtype=np.float32);data.foreach_get(field,a);return h(a.tobytes())
def ints(data,field,width):
    a=np.empty(len(data)*width,dtype=np.int32);data.foreach_get(field,a);return h(a.tobytes())
def mesh(o):
    d=o.data; names={g.index:g.name for g in o.vertex_groups}
    weights=[sorted((names[g.group],float(g.weight)) for g in v.groups) for v in d.vertices]
    r={'vertices':len(d.vertices),'coordinate_hash':floats(d.vertices,'co',3),'edges_hash':ints(d.edges,'vertices',2),'corner_vertex_hash':ints(d.loops,'vertex_index',1),'polygon_sizes_hash':ints(d.polygons,'loop_total',1),'polygon_material_hash':ints(d.polygons,'material_index',1),'weights_hash':h(json.dumps(weights,separators=(',',':')).encode()),'uv_hashes':{a.name:floats(a.data,'uv',2) for a in d.uv_layers},'point_source_indices':{a.name:ints(a.data,'value',1) for a in d.attributes if a.domain=='POINT' and a.data_type=='INT' and 'source' in a.name}}
    r['shape_keys']=[{'name':k.name,'value':k.value,'coordinate_hash':floats(k.data,'co',3),'relative_key':k.relative_key.name} for k in d.shape_keys.key_blocks] if d.shape_keys else []
    return r
scene=bpy.data.scenes['BW1_BODY_COSTUME']; names=[o.name for o in scene.objects if o.type=='MESH']
current={n:mesh(bpy.data.objects[n]) for n in names}
def action_content(action):
    curves=[]
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    curves.append({'path':curve.data_path,'array_index':curve.array_index,'extrapolation':curve.extrapolation,'keyframes':[{'co':list(k.co),'left':list(k.handle_left),'right':list(k.handle_right),'interpolation':k.interpolation,'easing':k.easing,'handle_left_type':k.handle_left_type,'handle_right_type':k.handle_right_type} for k in curve.keyframe_points]})
    return {'frame_range':list(action.frame_range),'curves':curves}
action_name='BW1_DIAGNOSTIC_RANGE_ART_REVISE'
current_action=action_content(bpy.data.actions[action_name])
with bpy.data.libraries.load(str(prior),link=False) as (source,target):
    assert set(names)<=set(source.objects)
    target.objects=list(names)
    target.actions=[action_name]
old={n:mesh(o) for n,o in zip(names,target.objects)}
old_action=action_content(target.actions[0])
checks={n:{'exact_source_data_equal':current[n]==old[n],'changed_fields':[k for k in current[n] if current[n][k]!=old[n][k]],'current':current[n],'r001':old[n]} for n in names}
out={'status':'EXACT_SOURCE_ARRAY_COMPARISON','new_file':bpy.data.filepath,'new_sha256':h(Path(bpy.data.filepath).read_bytes()),'r001_file':str(prior),'r001_sha256':h(prior.read_bytes()),'mesh_count':len(names),'all_mesh_source_arrays_equal':all(x['exact_source_data_equal'] for x in checks.values()),'mesh_checks':checks,'comparison_scope':'All active-scene mesh raw coordinates, indexed topology, polygon material assignments, UV coordinates, every vertex-group weight, source-index attributes and every shape-key coordinate/value/relative-name. Evaluated coordinates may differ as intended from Solidify settings.','source_saved':False}
out['action_curves_and_keys_exact_equal']=current_action==old_action
out['action_curve_count']=len(current_action['curves'])
out['action_source_content_sha256']=h(json.dumps(current_action,separators=(',',':')).encode())
(ROOT/'reviews/r002_exact_source_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='mesh_checks'},indent=2));print('changed',[(n,x['changed_fields']) for n,x in checks.items() if not x['exact_source_data_equal']])
