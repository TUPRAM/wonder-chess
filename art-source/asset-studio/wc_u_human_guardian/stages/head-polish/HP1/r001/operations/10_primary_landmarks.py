import bpy,bmesh,json,math
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
s=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=s
assert '/head-polish/HP1/r001/' in bpy.data.filepath.replace('\\','/')
assert bpy.data.objects.get('HP1_HEAD_POLISH_Head_r010') is None
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r009'];h=old.copy();h.data=old.data.copy();h.name='HP1_HEAD_POLISH_Head_r010';s.collection.objects.link(h);old.hide_render=True;old.hide_set(True)
f=json.loads(h['feature_indices']);source=bpy.data.objects['HP1_HEAD_POLISH_Head_r006']
# Restore semantic cage groups after the topology additions. These are edit
# selections, not skinning weights or a runtime rig.
for g in source.vertex_groups:
    target=h.vertex_groups.get(g.name)
    if target is None:target=h.vertex_groups.new(name=g.name)
    ids=[v.index for v in source.data.vertices if any(a.group==g.index for a in v.groups)]
    if ids:target.add(ids,1,'REPLACE')
orbits=json.loads(h['orbital_rings'])
for side,ring in zip(['R','L'],orbits):h.vertex_groups['Orbital_'+side].add(ring,1,'REPLACE')
h.vertex_groups['Nose'].add(json.loads(h['nasal_bulb_section']),1,'REPLACE')
# Primary-reference registration reveals a high ear. Lower the whole ear
# and distribute the junction displacement through neighboring surface flow.
ears=set()
for side in ['R','L']:
    g=source.vertex_groups['Ear_'+side]
    ids=[v.index for v in source.data.vertices if any(a.group==g.index for a in v.groups)]
    f['ear_'+side]=ids;ears.update(ids)
adj={v.index:set() for v in h.data.vertices}
for edge in h.data.edges:
    a,b=edge.vertices;adj[a].add(b);adj[b].add(a)
weight={i:1.0 for i in ears};frontier=set(ears)
for w in [.7,.35,.10]:
    new=set()
    for i in frontier:
        for j in adj[i]:
            if j not in weight:new.add(j)
    for i in new:weight[i]=w
    frontier=new
for i,w in weight.items():h.data.vertices[i].co.z-=.0105*w
# Lift and slightly recess the closed mouth toward the primary portrait's
# placement. The perioral rings taper the displacement into nose and chin.
for local,i in enumerate(f['mouth']):
    layer=local//34;p=h.data.vertices[i].co
    weight=[1,1,1,1,1,.94,.76,.35,0][layer]
    p.z+=.0048*weight;p.y-=.0035*weight
h['feature_indices']=json.dumps(f)
h['revision_notes']='Primary portrait comparison: lower ear with propagated junction, slightly higher/recessed mouth and restored semantic edit selections. Neutral cameras unchanged.'
h.data.update();bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
s['render_allowlist']=json.dumps([o.name for o in s.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','primary_fit']:
    s.camera=bpy.data.objects[s.name+'_'+label]
    s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900
    s.render.filepath=ROOT+'/captures/r010_'+label+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=900;s.render.resolution_y=900
print('HP1 r010 registered-mouth and ear placement executed.')
