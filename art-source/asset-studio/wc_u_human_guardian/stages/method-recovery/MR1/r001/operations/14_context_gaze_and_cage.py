import bpy,json
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
sc=bpy.data.scenes['MR1_CONTEXT_HEAD_CANDIDATE'];bpy.context.window.scene=sc;col=bpy.data.collections['MR1_CONTEXT_CANDIDATE_ALLOWLIST'];clay=bpy.data.materials['MR1_Uniform_Clay']
for o in sc.objects:
    if o.type=='MESH' and 'Globe_' not in o.name:
        o.data.materials.clear();o.data.materials.append(clay)
sc.view_layers[0].material_override=None
def cap(name,view):
    sc.camera=bpy.data.objects['MR1_CONTEXT_'+view];sc.render.filepath=root+'/captures/'+name+'_'+view+'.png';bpy.ops.render.render(write_still=True)
for v in ['front','profile','three_quarter','opposite']:cap('context_final_gaze',v)
joined=bpy.data.objects['MR1_CONTEXT_Joined_Head_Diagnostic'];cage=bpy.data.objects['MR1_CONTEXT_Two_Eye_Source_Cage'];retained=bpy.data.objects['MR1_CONTEXT_Retained_Head_Outside_Orbital_Regions']
# Actual unsmoothed authoring cage before the derived interface bridge.
wire=bpy.data.objects.new('MR1_CONTEXT_Source_Cage_Wire',cage.data.copy());col.objects.link(wire);wire.data.materials.clear();wire.data.materials.append(bpy.data.materials['MR1_Cage_Dark'])
mod=wire.modifiers.new('Source cage edges','WIREFRAME');mod.thickness=.0003;mod.offset=1
joined.hide_render=True;cage.hide_render=False;cage.modifiers[0].show_render=False;retained.hide_render=False
cap('context_source_cage','three_quarter')
wire.hide_render=True;wire.hide_set(True);joined.hide_render=False;cage.hide_render=True;cage.modifiers[0].show_render=True;retained.hide_render=True
# Derived bridge-only wire identifies the rejected contextual connection explicitly.
audit=json.loads(joined['mr1_join_audit']);n=audit['bridge_faces'];me=bpy.data.meshes.new('MR1_Context_Join_Wire_Mesh')
me.from_pydata([tuple(v.co) for v in joined.data.vertices],[],[tuple(f.vertices) for f in list(joined.data.polygons)[-n:]]);me.update()
w=bpy.data.objects.new('MR1_CONTEXT_Join_Diagnostic_Wire',me);col.objects.link(w);me.materials.append(bpy.data.materials['MR1_Cage_Dark'])
m=w.modifiers.new('Context bridge edges','WIREFRAME');m.thickness=.00022;m.offset=1
cap('context_join_wire','three_quarter');w.hide_render=True;w.hide_set(True)
sc.view_layers[0].material_override=clay;sc.camera=bpy.data.objects['MR1_CONTEXT_three_quarter']
sc['mr1_render_allowlist']=json.dumps([o.name for o in sc.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Four context gaze views, raw cage and actual join-wire evidence captured')
