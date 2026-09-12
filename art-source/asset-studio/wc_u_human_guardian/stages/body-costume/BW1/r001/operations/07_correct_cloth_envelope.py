import bpy,math,json
from mathutils import Vector
s=bpy.data.scenes['BW1_BODY_COSTUME'];body=bpy.data.objects['BW1_IndexedBody'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
assert 'BW1_CoatUpper_Continuous' not in bpy.data.objects
for name in ['BW1_PaddedTorso','BW1_Sleeve_R','BW1_Sleeve_L_Blockout']:
    ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True);ob['replaced_by']='BW1_CoatUpper_Continuous';ob['defect']='Separate spatial extraction made staggered shoulder seams. Retained for comparison.'
states=[(m,m.show_viewport) for m in body.modifiers]
for m,_ in states:m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get();dg.update();ev=body.evaluated_get(dg);points=[body.matrix_world@v.co for v in ev.data.vertices]
group=body.vertex_groups['helper-tights'].index;ids={v.index for v in body.data.vertices if any(g.group==group and g.weight>.5 for g in v.groups)}
chosen=[]
for p in body.data.polygons:
    if not all(i in ids for i in p.vertices):continue
    center=sum((points[i] for i in p.vertices),Vector())/len(p.vertices)
    if center.z>1.082 and center.z<1.525 and abs(center.x)<.459:chosen.append(list(p.vertices))
used=sorted({i for f in chosen for i in f});mapping={old:new for new,old in enumerate(used)};verts=[]
for i in used:
    co=points[i].copy();x=abs(co.x);side=1 if co.x>0 else -1
    if x>.175 and co.z>1.1:
        a=Vector((side*.18185,-.04636,1.44498));b=Vector((side*.36106,-.04210,1.24891));c=Vector((side*.48638,.11233,1.11225));best=None
        for p,q in [(a,b),(b,c)]:
            t=max(0,min(1,(co-p).dot(q-p)/(q-p).length_squared));axis=p+(q-p)*t;delta=co-axis
            if best is None or delta.length<best[0]:best=(delta.length,delta)
        if best[0]>.001:co+=best[1].normalized()*.015
    if x<.22:
        blend=max(0,min(1,(.22-x)/.07))
        if co.y>-.035 and co.z<1.46:
            desired=.142-.035*(x/.22)**2
            co.y=co.y*(1-blend)+desired*blend
        elif co.y<-.035:co.y-=.015*blend
        co.x+=side*.013*max(0,1-(x/.22))
    verts.append(tuple(co))
mesh=bpy.data.meshes.new('BW1_CoatUpper_Continuous_Cage');mesh.from_pydata(verts,[],[[mapping[i] for i in f] for f in chosen]);mesh.update()
ob=bpy.data.objects.new('BW1_CoatUpper_Continuous',mesh);bpy.data.collections['BW1_CLOTH'].objects.link(ob);mesh.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
attr=mesh.attributes.new('mpfb_source_index','INT','POINT')
for a,i in zip(attr.data,used):a.value=i
bone_names=set(rig.data.bones.keys());groups={g.index:g.name for g in body.vertex_groups}
for bn in bone_names:
    values=[(new,gw.weight) for new,old in enumerate(used) for gw in body.data.vertices[old].groups if groups[gw.group]==bn and gw.weight>.0001]
    if values:
        vg=ob.vertex_groups.new(name=bn)
        for i,w in values:vg.add([i],w,'REPLACE')
ob.parent=rig;ob.matrix_parent_inverse=rig.matrix_world.inverted();m=ob.modifiers.new('Temporary articulation','ARMATURE');m.object=rig
m=ob.modifiers.new('Editable cloth surface','SUBSURF');m.levels=1;m.render_levels=1
m=ob.modifiers.new('Padded garment thickness','SOLIDIFY');m.thickness=.006;m.offset=-1;m.use_even_offset=True
for p in mesh.polygons:p.use_smooth=True
ob['construction']='Continuous helper-tights shirt with independent chest/sleeve fullness; exact source-index weights'
for m,state in states:m.show_viewport=state
# Widen the hanging coat envelope where the first cloth capture exposed thigh intersections.
for ob in bpy.data.collections['BW1_CLOTH'].objects:
    if ob.name.startswith('BW1_CoatPanel'):
        front='Front' in ob.name;side=1 if ob.name.endswith('_R') else -1
        for v in ob.data.vertices:
            t=max(0,min(1,(1.095-v.co.z)/.43));u=(v.index%9)/8;a=math.radians(5+83*u)*side
            v.co.x=(.206+.064*t)*math.sin(a);v.co.y=-.045+(1 if front else -1)*(.174+.035*t)*math.cos(a)
        ob.data.update()
    elif ob.name.startswith('BW1_Tabard'):
        front='Front' in ob.name
        for v in ob.data.vertices:
            t=max(0,min(1,(1.105-v.co.z)/.43));v.co.y=-.045+(1 if front else -1)*(.183+.04*t)-(.012*(v.co.x/.14)**2)*(1 if front else -1)
        ob.data.update()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/cloth_blockout_r001.png';bpy.ops.render.render(write_still=True)
print('Replaced disconnected shoulder seams with a continuous cloth envelope; widened coat panels to clear thighs. Source body remains intact.')

