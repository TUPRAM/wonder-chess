import bpy, json, hashlib, ast, math, re, sys
from pathlib import Path
from collections import Counter
import numpy as np
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

out=Path(__file__).parent
bw2=out.parents[3]/'BW2/r001'
source=bw2/'ada_bw2_grip_checkpoint_r001_ART_REVISE.blend'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf'
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig']
g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];body=bpy.data.objects['BW1_IndexedBody']
rec=json.loads(s['BW2_hand_contract']);relative=Matrix(rec['frame_relative_to_wrist'])
C=np.array(rec['handle_center_hand_m']);axis=np.array(rec['handle_axis_hand']);R=rec['radius_m'];half=rec['endpoint_span_m']/2
U=np.array([0.,0.,1.]);V=np.cross(axis,U);V/=np.linalg.norm(V)
defs=[]
for file,names in [(bw2/'integrated-independent/audit_integrated_geometry.py',('segment_triangle','self_audit')),(bw2/'middle-independent/audit_triangle_interiors.py',('clip','closest_projected','has_depth'))]:
    tree=ast.parse(file.read_text());defs.extend(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names)
exec(compile(ast.Module(body=defs,type_ignores=[]),str(__file__),'exec'),globals())
deform={b.name for b in r.data.bones if b.use_deform}
mods={ob.name:[(m,m.show_viewport) for m in ob.modifiers] for ob in [g,body]}
s.frame_set(1);bpy.context.view_layer.update()
open_basis={p.name:p.matrix_basis.copy() for p in r.pose.bones if p.name.endswith('.R') and re.match(r'finger[2-5]-',p.name)}
original_action=r.animation_data.action;action=original_action.name

def set_frame(frame,isolate):
    r.animation_data.action=original_action
    n=math.floor(frame);s.frame_set(n,subframe=frame-n);bpy.context.view_layer.update()
    if isolate:
        pose={p.name:p.matrix_basis.copy() for p in r.pose.bones};pose.update(open_basis);r.animation_data.action=None
        for name,matrix in pose.items():r.pose.bones[name].matrix_basis=matrix
    bpy.context.view_layer.update()
    if isolate:
        ev=r.evaluated_get(bpy.context.evaluated_depsgraph_get())
        assert max(abs(ev.pose.bones[n].matrix_basis[i][j]-m[i][j]) for n,m in open_basis.items() for i in range(4) for j in range(4))<1e-6

def groupweights(ob,v):
    return {ob.vertex_groups[a.group].name:float(a.weight) for a in v.groups if ob.vertex_groups[a.group].name in deform and a.weight>1e-7}

def label(w):
    sums={'thumb':0.,'index':0.,'middle':0.,'ring':0.,'little':0.,'palm':0.}
    for name,value in w.items():
        mt=re.match(r'finger([1-5])-',name)
        sums[['thumb','index','middle','ring','little'][int(mt.group(1))-1] if mt else 'palm']+=value
    return max(sums,key=sums.get)

def geometry(ob,raw):
    for m,flag in mods[ob.name]:m.show_viewport=flag and not(raw and m.type!='ARMATURE')
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg)
    rr=r.evaluated_get(dg);F=rr.matrix_world@rr.pose.bones['wrist.R'].matrix@relative;Fi=F.inverted()
    me=ev.to_mesh();me.calc_loop_triangles();transform=np.array(Fi@ev.matrix_world)
    coords=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3);q=coords@transform[:3,:3].T+transform[:3,3]
    w=[groupweights(ob,v) for v in me.vertices]
    selected={i for i,p in enumerate(q) if -.025<p[1]<.25 and abs(p[0])<.14 and abs(p[2])<.15}
    if ob==body and raw:
        index=ob.vertex_groups['body'].index;selected &= {v.index for v in me.vertices if any(a.group==index and a.weight>.5 for a in v.groups)}
    tris=[(t.index,tuple(t.vertices)) for t in me.loop_triangles if all(i in selected for i in t.vertices)]
    ev.to_mesh_clear()
    for m,flag in mods[ob.name]:m.show_viewport=flag
    return q,w,tris

def cylinder(q,tris):
    shifted=q-C;ax=shifted@axis;rad=np.linalg.norm(shifted-np.outer(ax,axis),axis=1)-R
    dd=np.stack([rad,np.abs(ax)-half],axis=1);sd=np.minimum(np.max(dd,axis=1),0)+np.linalg.norm(np.maximum(dd,0),axis=1)
    ids=sorted({i for _,vs in tris for i in vs});vmin=min(ids,key=lambda i:sd[i])
    # Conservative rectangular broadphase; exact reused triangle/slab query confirms entry.
    x=shifted@U;y=shifted@V;candidates=[]
    for index,vs in tris:
        ix=list(vs)
        if min(ax[ix])>half or max(ax[ix])<-half or min(x[ix])>R or max(x[ix])<-R or min(y[ix])>R or max(y[ix])<-R:continue
        candidates.append((index,vs,shifted[ix]))
    first={}
    for depth,key in [(0.,'entry'),(.0005,'deeper_than_0_5mm')]:
        hit=None
        for index,vs,triangle in candidates:
            if has_depth(triangle,depth)[0]:hit={'triangle':index,'vertices':vs};break
        first[key]=hit
    return {'minimum_vertex_sdf_mm':float(sd[vmin]*1000),'minimum_vertex':vmin,**first}

def measure(ob,raw,frame,isolate):
    set_frame(frame,isolate);q,w,tris=geometry(ob,raw);cross=self_audit(q,tris);counts=Counter();examples={}
    for p in cross['pairs']:
        names=[]
        for vs in p['vertices']:
            avg={}
            for i in vs:
                for n,v in w[i].items():avg[n]=avg.get(n,0.)+v/3
            names.append(label(avg))
        names=sorted(names);category='/'.join(names);counts[category]+=1;examples.setdefault(category,p)
    entry={'frame':frame,'vertex_count':len(q),'triangle_count':len(tris),'crossing_pair_count':cross['confirmed_nonadjacent_transverse_pairs'],'categories':dict(counts),'first_examples':examples}
    if ob==g:
        entry['cylinder']=cylinder(q,tris)
        if frame==14 and not raw and not isolate:
            entry['vertex6670']={'hand_m':q[6670].tolist(),'deform_weights':w[6670],'dominant_region':label(w[6670]),'incident_triangle_ids':[i for i,vs in tris if 6670 in vs]}
    return entry

events={'thumb_palm':lambda a:a['categories'].get('palm/thumb',0)>0,'thumb_index_middle':lambda a:sum(a['categories'].get(k,0) for k in ['index/thumb','middle/thumb'])>0,'middle_ring':lambda a:a['categories'].get('middle/ring',0)>0,'any_crossing':lambda a:a['crossing_pair_count']>0,'handle_entry':lambda a:bool(a.get('cylinder',{}).get('entry')),'handle_deeper_0_5mm':lambda a:bool(a.get('cylinder',{}).get('deeper_than_0_5mm'))}
report={'source':str(source),'source_sha256':sha,'action':action,'method':'BW2 triangle code reused. Every integer frame 1..25 plus quarterframes in first onset intervals. Fixed fixture follows original wrist-relative frame. Thumb-only repeats source thumb keys with all other right digits fixed at recorded frame1 OPEN. No pose optimization, weights, topology or source saves. Region names use dominant deform groups, not exact anatomical segmentation.','variants':[]}
isolation_only='--isolation-only' in sys.argv
if isolation_only:
    previous=json.loads((out/'onset_results.json').read_text())
    (out/'onset_results_before_action_detach_verification.json').write_text(json.dumps(previous,indent=2))
    report['variants']=[v for v in previous['variants'] if v['trajectory']=='integrated_source']
    report['isolation_verification']='Source action sampled then detached in memory; all basis matrices explicitly assigned; non-thumb evaluated bases asserted OPEN at each sample.'
for isolate in ([True] if isolation_only else [False,True]):
    for ob,raw in [(g,False),(g,True),(body,False),(body,True)]:
        variant={'trajectory':'thumb_only_others_open' if isolate else 'integrated_source','object':ob.name,'surface':'raw_posed_cage' if raw else 'evaluated_level1','integer_frames':[],'quarterframes':[],'first_onsets':{}}
        for frame in range(1,26):
            row=measure(ob,raw,frame,isolate);variant['integer_frames'].append(row)
            if not raw and ob==g:print('FRAME',variant['trajectory'],frame,row['categories'],row.get('cylinder'),flush=True)
        refine=set()
        for name,test in events.items():
            first=next((a['frame'] for a in variant['integer_frames'] if test(a)),None)
            if first and first>1:refine.update([first-.75,first-.5,first-.25])
        for frame in sorted(refine):variant['quarterframes'].append(measure(ob,raw,frame,isolate))
        samples=sorted(variant['integer_frames']+variant['quarterframes'],key=lambda a:a['frame'])
        for name,test in events.items():
            first=next((a for a in samples if test(a)),None)
            if first:
                prior=next((a for a in reversed(samples) if a['frame']<first['frame']),None)
                variant['first_onsets'][name]={'first_positive_frame':first['frame'],'last_preceding_sample_frame':prior['frame'] if prior else None,'already_present_at_frame1':first['frame']==1}
            else:variant['first_onsets'][name]=None
        report['variants'].append(variant);(out/'onset_results.json').write_text(json.dumps(report,indent=2));print('ONSET',variant['trajectory'],ob.name,variant['surface'],variant['first_onsets'],flush=True)
report['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert report['source_sha256_after']==sha
(out/'onset_results.json').write_text(json.dumps(report,indent=2))
print('COMPLETE',flush=True)
