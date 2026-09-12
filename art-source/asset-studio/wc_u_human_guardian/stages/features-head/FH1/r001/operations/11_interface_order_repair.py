import bpy,bmesh,json,math
scene=bpy.data.scenes['FH1_COMBINED_HEAD'];bpy.context.window.scene=scene
old=bpy.data.objects['FH1_Combined_Head_Control_Cage_r003'];initial=bpy.data.objects['FH1_Combined_Head_Control_Cage']
assert bpy.data.objects.get('FH1_Combined_Head_Control_Cage_r004') is None
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/combined_r003_checkpoint.blend',copy=True)
head=old.copy();head.data=old.data.copy();head.name='FH1_Combined_Head_Control_Cage_r004';scene.collection.objects.link(head)
old.hide_render=True;old.hide_set(True)
lookup={tuple(round(c,6) for c in v.co):v.index for v in initial.data.vertices}
nose_source=bpy.data.objects['FH1_Nose_Control_Cage_r002']
ids=[lookup[tuple(round(c,6) for c in v.co)] for v in nose_source.data.vertices]
# The nasal interface must be medial to the inner lid/body, not lateral to
# it. Correct the transverse section ordering, including the shared edge.
# Lower alar and nostril structure are excluded.
target_halfwidth={3:.0140,4:.0100,5:.0100,6:.0120,7:.0140,8:.0170}
for row,width in target_halfwidth.items():
    original_width=abs(nose_source.data.vertices[row*9+8].co.x)
    for j in range(9):head.data.vertices[ids[row*9+j]].co.x*=width/original_width
# The crown cap retains its interior XY parameterization; projecting every
# interior point by altitude had collapsed it onto a rim. Rebuild this small
# quad cap from its original ordered XY coordinates on a smooth upper dome.
cap_ids=[]
for v in initial.data.vertices:
    if v.co.z>=1.7939:
        q=head.data.vertices[v.index].co
        q.x=v.co.x*.94;q.y=-.025+(v.co.y+.043)*1.18
        norm=(q.x/.086)**2+((q.y+.025)/.090)**2
        q.z=1.690+.105*math.sqrt(max(0,1-norm));cap_ids.append(v.index)
head.data.update()
bm=bmesh.new();bm.from_mesh(head.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(head.data);bm.free()
head['repair']='Anatomical ordering repaired at the nasal/orbital shared boundary; lower nose preserved. Quad crown cap uses noncollapsed interior coordinates.'
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/combined_r004_'+label+'.png';bpy.ops.render.render(write_still=True)
print('Interface order and crown cap repaired. Cap vertices '+str(len(cap_ids)))
