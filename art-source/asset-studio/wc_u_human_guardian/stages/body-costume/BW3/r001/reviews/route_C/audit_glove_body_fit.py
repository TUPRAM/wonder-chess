from pathlib import Path
script=Path(__file__).parent/'audit_route_C.py'
exec(compile(script.read_text().split('started = time.perf_counter()')[0],str(script),'exec'),globals())

def owner(indices,weights):
    average={}
    for i in indices:
        for n,v in weights[i].items():average[n]=average.get(n,0.)+v/3
    return label(average)

def check(frame):
    scene.frame_set(frame);bpy.context.view_layer.update()
    gq,gw,gt=geometry(glove,False);bq,bw,bt=geometry(body,False)
    gv=[ids for _,ids in gt];bv=[ids for _,ids in bt]
    gb=BVHTree.FromPolygons(gq.tolist(),gv,all_triangles=True,epsilon=0.)
    bb=BVHTree.FromPolygons(bq.tolist(),bv,all_triangles=True,epsilon=0.)
    broad=gb.overlap(bb)
    edgecount=Counter(tuple(sorted((ids[i-1],ids[i]))) for ids in gv for i in range(3))
    cuffids={i for edge,count in edgecount.items() if count==1 for i in edge}
    pairs=[];counts=Counter();cuffpairs=0;first={}
    for ia,ib in broad:
        ga=gv[ia];ba=bv[ib];ta=gq[list(ga)];tb=bq[list(ba)];hits=[]
        for seg,other in [(ta,tb),(tb,ta)]:
            for i in range(3):
                p=segment_triangle(seg[i],seg[(i+1)%3],other)
                if p is not None:hits.append(p)
        if not hits:continue
        zone=owner(ga,gw)+' glove / '+owner(ba,bw)+' body';counts[zone]+=1
        cuff=bool(set(ga)&cuffids);cuffpairs+=int(cuff)
        record={'glove_triangle':gt[ia][0],'body_triangle':bt[ib][0],'glove_vertices':ga,'body_vertices':ba,'point_hand_m':np.mean(hits,axis=0).tolist(),'touches_glove_boundary_vertex':cuff}
        first.setdefault(zone,record);pairs.append(record)
    degenerate={}
    for name,q,tris in [('glove',gq,gt),('body',bq,bt)]:
        xyz=np.array([q[list(ids)] for _,ids in tris]);areas=np.linalg.norm(np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]),axis=1)*.5
        degenerate[name]={'triangle_count':len(tris),'minimum_triangle_area_m2':float(areas.min()),'area_below_1e_14_m2':int(np.sum(areas<1e-14)),'nonfinite_vertices':int(np.sum(~np.isfinite(q).all(axis=1)))}
    result={'frame':frame,'confirmed_transverse_glove_body_pairs':len(pairs),'pairs_touching_open_glove_boundary_vertices':cuffpairs,'pairs_away_from_open_glove_boundary_vertices':len(pairs)-cuffpairs,'categories':dict(counts),'first_examples':first,'boundary_vertex_count_selected_hand':len(cuffids),'geometry_degeneracy_screen':degenerate}
    if frame in [1,15,20,25,145]:result['all_crossing_pairs']=pairs
    if frame<=25 or frame%20==0 or frame==145:print('FIT',frame,len(pairs),'boundary',cuffpairs,'interior',len(pairs)-cuffpairs,dict(counts),flush=True)
    return result

report={'source':str(SOURCE),'source_sha256':EXPECTED,'status':'RUNNING','method':'Actual same-pose level1 glove and body triangles in moving wrist metric frame; independent BVH broadphase plus confirmed transverse segment/triangle crossings across objects. No shared-index adjacency exclusion between different objects. Original material visibility does not filter collision surfaces.','frames':[],'limits':['Open glove wrist boundary is separately labeled by exact boundary vertices, not used to erase crossings. Boundary-adjacent does not automatically mean acceptable.','Coplanar/tangential contacts are not certified; no signed-volume containment claim for these open/self-crossing surfaces. Absence of transverse crossing alone would not prove enclosure.','Body and glove skin normals/topology are not repaired. Degeneracy screen tests finite coordinates and tiny triangle area; it does not certify no local fold or manifold suitability.','Dominant skeletal-group ownership is approximate; geometry remains authoritative.']}
for frame in range(1,146):
    report['frames'].append(check(frame))
    (OUT/'glove_body_fit_results.json').write_text(json.dumps(report,indent=2))
report['status']='COMPLETE_READ_ONLY_INTERSURFACE_SCREEN';report['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert report['source_sha256_after']==EXPECTED
(OUT/'glove_body_fit_results.json').write_text(json.dumps(report,indent=2));print('COMPLETE',flush=True)
