import bpy,bmesh,json,math
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert '/head-polish/HP1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r011') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r010'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r011';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
f=json.loads(h['feature_indices']);rings=json.loads(h['orbital_rings'])
# Fair the connecting skin as one constrained surface on the new topology.
# Feature loops and frontal landmark positions are pinned; only depth of the
# intervening skin is solved. No rectangular selection and no old-face or
# whole-cheek sphere projection is used.
fixed=set(f['mouth'][:204]+f['ear_R']+f['ear_L'])
for ring in rings:fixed.update(ring[:80])
fixed.update(json.loads(h['nasal_bulb_section']))
fixed.update(f['nose'][9:36]);fixed.update(f['nose'][81:])
initial=[v.co.copy() for v in h.data.vertices];adj={v.index:[] for v in h.data.vertices}
for edge in h.data.edges:
    a,b=edge.vertices
    dist=max(.001,(initial[a]-initial[b]).length)
    adj[a].append((b,1/dist));adj[b].append((a,1/dist))
movable=[v.index for v in h.data.vertices if v.index not in fixed and v.co.y>.008 and abs(v.co.x)<.069 and 1.604<v.co.z<1.744]
depth=[p.y for p in initial]
for iteration in range(36):
    nextdepth=depth[:]
    for i in movable:
        neighbors=adj[i];avg=sum(depth[j]*w for j,w in neighbors)/sum(w for j,w in neighbors)
        target=.10*initial[i].y+.90*avg
        nextdepth[i]=depth[i]*.25+target*.75
    depth=nextdepth
for i in movable:
    p=h.data.vertices[i].co
    p.y=max(initial[i].y-.006,min(initial[i].y+.006,depth[i]))
    # A local collision floor only for the outer orbital skin.
    for ring in rings:
        if i in ring[80:120]:
            rr=.0207**2-(abs(p.x)-.034)**2-(p.z-1.690)**2
            if rr>0:p.y=max(p.y,.039+math.sqrt(rr)+.0015)
h['revision_notes']='Feature-constrained fairing of connecting skin on rebuilt topology; x/z and meaningful lid/lip/nose/ear loops pinned. No rectangular smoothing patch.'
h['fairing_edited_vertices']=len(movable)
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','primary_fit']:
    s.camera=bpy.data.objects[s.name+'_'+label];s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900
    s.render.filepath=ROOT+'/captures/r011_'+label+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=900;s.render.resolution_y=900
print('HP1 r011 constrained connecting surface: '+str(len(movable))+' controls, feature loops pinned.')
