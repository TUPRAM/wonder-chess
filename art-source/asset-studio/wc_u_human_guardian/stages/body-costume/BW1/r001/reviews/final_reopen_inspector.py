"""Read a supplied frozen/work BW1 file in a fresh background process, write evidence only."""
import bpy, json, math, hashlib, sys, re
import numpy as np
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]; outpath=Path(args[0])
def arr(data):
    x=np.empty(len(data)*3,dtype=np.float32);data.foreach_get('co',x);return x.reshape(-1,3)
def mat(m):return [list(r) for r in m]
def props(o):
    d={}
    for k in o.keys():
        v=o[k]
        if isinstance(v,str):
            try:v=json.loads(v)
            except Exception:pass
        elif hasattr(v,'to_list'):v=v.to_list()
        elif hasattr(v,'to_dict'):v=v.to_dict()
        d[k]=v
    return d
def world(o,a,m=None):
    m=np.array(m if m is not None else o.matrix_world);return a@m[:3,:3].T+m[:3,3]
def components(o):
    adjacency=[set() for _ in o.data.vertices]
    for e in o.data.edges:
        a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
    unseen=set(range(len(adjacency)));sizes=[]
    while unseen:
        todo=[next(iter(unseen))];found=set()
        while todo:
            i=todo.pop()
            if i in found:continue
            found.add(i);todo.extend(adjacency[i]-found)
        unseen-=found;sizes.append(len(found))
    return sorted(sizes,reverse=True)
main=bpy.data.scenes['BW1_BODY_COSTUME']; body=bpy.data.objects['BW1_IndexedBody']; original=bpy.data.objects['MP1_MpfbFoundation_Source'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
bpy.context.window.scene=bpy.data.scenes['MP1_ADA_HEAD'];bpy.context.view_layer.update()
oldm={n:bpy.data.objects[n].matrix_world.copy() for n in ('MP1_Head_r002','MP1_Eye_R','MP1_Eye_L')}
bpy.context.window.scene=main;bpy.context.view_layer.update()
out={'file':bpy.data.filepath,'file_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'source_saved':False,'read_only_background_reopen':True,'scenes':[{'name':s.name,'fake_user':s.use_fake_user,'object_count':len(s.objects)} for s in bpy.data.scenes],'scene_metadata':props(main),'scene_frame':main.frame_current,'scene_frame_range':[main.frame_start,main.frame_end],'fps':main.render.fps,'fps_base':main.render.fps_base,'collections':[{'name':c.name,'hide_render':c.hide_render,'hide_viewport':c.hide_viewport,'objects':list(c.objects.keys())} for c in bpy.data.collections]}
keyrows=[]
for k in original.data.shape_keys.key_blocks:
    c=body.data.shape_keys.key_blocks.get(k.name)
    keyrows.append({'name':k.name,'present':c is not None,'coordinates_equal':c is not None and bool(np.array_equal(arr(k.data),arr(c.data))),'value_equal':c is not None and c.value==k.value,'coordinates_sha256':hashlib.sha256(arr(k.data).tobytes()).hexdigest()})
out['source_preservation']={'body_vertices':len(body.data.vertices),'retained_master_vertices':len(original.data.vertices),'independent_mesh':body.data!=original.data,'independent_keys':body.data.shape_keys!=original.data.shape_keys,'basis_mesh_coords_equal':bool(np.array_equal(arr(body.data.vertices),arr(original.data.vertices))),'edge_indices_equal':len(body.data.edges)==len(original.data.edges) and all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(body.data.edges,original.data.edges)),'face_indices_equal':len(body.data.polygons)==len(original.data.polygons) and all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(body.data.polygons,original.data.polygons)),'original_keys':keyrows,'body_keys':[{'name':k.name,'value':k.value,'finite':bool(np.isfinite(arr(k.data)).all())} for k in body.data.shape_keys.key_blocks],'new_keys':[k.name for k in body.data.shape_keys.key_blocks if k.name not in original.data.shape_keys.key_blocks]}
out['head_preservation']={}
for n,old in [('BW1_Context_Head_ART_REVISE','MP1_Head_r002'),('BW1_Context_Eye_R','MP1_Eye_R'),('BW1_Context_Eye_L','MP1_Eye_L')]:
    a=bpy.data.objects[n];b=bpy.data.objects[old];p=arr(a.data.vertices);q=arr(b.data.vertices)
    out['head_preservation'][n]={'local_coords_exact':bool(np.array_equal(p,q)),'faces_exact':len(a.data.polygons)==len(b.data.polygons) and all(tuple(x.vertices)==tuple(y.vertices) for x,y in zip(a.data.polygons,b.data.polygons)),'world_max_difference_m':float(np.linalg.norm(world(a,p)-world(b,q,oldm[old]),axis=1).max()),'context_property':a.get('context_only',False)}
def modifier(m):
    row={'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render}
    for p in m.bl_rna.properties:
        k=p.identifier
        if k in ('rna_type','name','type') or p.type=='COLLECTION':continue
        try:
            v=getattr(m,k)
            if p.type=='POINTER':v=v.name if v is not None and hasattr(v,'name') else None
            elif getattr(p,'is_array',False):v=list(v)
            if isinstance(v,(str,int,float,bool,list)) or v is None:row[k]=v
        except Exception:pass
    return row
def weights(o):
    names={g.index:g.name for g in o.vertex_groups}
    return [{names[g.group]:g.weight for g in v.groups if names[g.group] in rig.data.bones and g.weight>1e-8} for v in o.data.vertices]
bodyweights=weights(body)
def weightmetrics(o):
    w=weights(o);sums=[sum(x.values()) for x in w]
    per={}
    for group in o.vertex_groups:
        values=[a.weight for v in o.data.vertices for a in v.groups if a.group==group.index]
        if values:per[group.name]={'vertices':len(values),'min':min(values),'max':max(values),'sum':sum(values),'rig_bone':group.name in rig.data.bones}
    result={'groups':per,'deform_vertices':sum(bool(x) for x in w),'unweighted':sum(not x for x in w),'max_deform_influences':max(map(len,w),default=0),'minimum_sum':min(sums,default=0),'maximum_sum':max(sums,default=0),'max_sum_error':max([abs(s-1) for s in sums if s>0],default=0),'source_attributes':[]}
    for a in o.data.attributes:
        if a.domain=='POINT' and a.data_type=='INT' and 'source' in a.name:
            ix=[p.value for p in a.data];errors=[]
            for i,j in enumerate(ix):
                if 0<=j<len(bodyweights):errors.append(max([abs(w[i].get(k,0)-bodyweights[j].get(k,0)) for k in set(w[i])|set(bodyweights[j])],default=0))
            result['source_attributes'].append({'name':a.name,'entries':len(ix),'unique':len(set(ix)),'min':min(ix),'max':max(ix),'invalid':sum(not 0<=j<len(bodyweights) for j in ix),'max_weight_difference':max(errors,default=0)})
    if o.name=='BW1_Leggings':result['components']=components(o);result['arm_hand_weighted_vertices']=sum(sum(v for k,v in x.items() if any(t in k for t in ('arm','wrist','finger','metacarpal')))>1e-6 for x in w)
    return result
meshrows=[];deps=bpy.context.evaluated_depsgraph_get()
for o in main.objects:
    if o.type!='MESH':continue
    p=arr(o.data.vertices);ev=o.evaluated_get(deps);me=ev.to_mesh();q=arr(me.vertices)
    row={'name':o.name,'mesh':o.data.name,'vertices':len(p),'faces':len(o.data.polygons),'evaluated_vertices':len(q),'evaluated_faces':len(me.polygons),'coordinates_finite':bool(np.isfinite(p).all()),'evaluated_coordinates_finite':bool(np.isfinite(q).all()),'matrix_finite':bool(np.isfinite(np.array(o.matrix_world)).all()),'visible':o.visible_get(),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'collections':list(c.name for c in o.users_collection),'matrix_world':mat(o.matrix_world),'modifiers':[modifier(m) for m in o.modifiers],'properties':props(o),'weight_metrics':weightmetrics(o),'has_hair_family_name':bool(re.search('hair|braid|eyebrow|eyelash',o.name,re.I)),'suspected_failed_or_helper_name':bool(re.search('fail|reject|helper|proxy',o.name,re.I))}
    ev.to_mesh_clear();meshrows.append(row)
out['active_scene_meshes']=meshrows
out['active_render_mesh_names']=[o['name'] for o in meshrows if not o['hide_render'] and all(not bpy.data.collections[c].hide_render for c in o['collections'])]
out['active_visible_mesh_names']=[o['name'] for o in meshrows if o['visible']]
out['cameras']=[{'name':o.name,'matrix_world':mat(o.matrix_world),'type':o.data.type,'ortho_scale':o.data.ortho_scale,'lens_mm':o.data.lens,'sensor_width_mm':o.data.sensor_width,'shift':[o.data.shift_x,o.data.shift_y],'clip':[o.data.clip_start,o.data.clip_end],'properties':props(o)} for o in main.objects if o.type=='CAMERA']
out['lights']=[{'name':o.name,'matrix_world':mat(o.matrix_world),'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)} for o in main.objects if o.type=='LIGHT']
out['rig']={'name':rig.name,'bone_count':len(rig.data.bones),'properties':props(rig),'matrix_world':mat(rig.matrix_world),'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'deform':b.use_deform,'rest_matrix':mat(b.matrix_local),'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones],'action':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None}
out['actions']=[{'name':a.name,'frame_range':list(a.frame_range),'fake_user':a.use_fake_user,'slots':[s.identifier for s in a.slots]} for a in bpy.data.actions]
out['technical_exceptions']=['Art remains ART_REVISE; finite meshes and weight normalization are not visual or deformation acceptance.','Primitive/source/open garment boundaries may be intentional; this audit does not classify all openings or run exhaustive collision detection.','169-frame24FPS local diagnostic is not a retargeted packaged-game animation.','The local163-bone rig differs from existing27-bone runtime rig; no runtime compatibility is claimed.']
outpath.write_text(json.dumps(out,indent=2,default=str)+'\n')
print(json.dumps({'output':str(outpath),'hash':out['file_sha256'],'scenes':out['scenes'],'active_meshes':len(meshrows),'render_meshes':len(out['active_render_mesh_names']),'visible_meshes':len(out['active_visible_mesh_names']),'finite_all':all(r['coordinates_finite'] and r['evaluated_coordinates_finite'] and r['matrix_finite'] for r in meshrows),'frame_range':out['scene_frame_range'],'fps':out['fps'],'actions':out['actions'],'normalized':{r['name']:r['weight_metrics']['max_sum_error'] for r in meshrows if 'SourceFit' in r['name']},'leggings':next((r['weight_metrics'] for r in meshrows if r['name']=='BW1_Leggings'),None)},indent=2))
