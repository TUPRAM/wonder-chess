import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SOURCE=R.parent/'armor/ada_bw6_upper_integrated_r002.blend'
PARTS=R/'ada_bw6_side_return_correction1.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
rig=bpy.data.objects['BW4_Armor_Independent_Rig']
names=['BW6_R_FittedSideReturn','BW6_R_FittedSideStrap_1','BW6_R_FittedSideStrap_2']
assert not any(bpy.data.objects.get(n) for n in names)
protected={n:hashlib.sha256(str([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in bpy.data.objects[n].data.vertices]).encode()).hexdigest() for n in ['BW6_FrontPlate','BW6_BackPlate','BW6_PaddedCoat_Tailored','BW4_CONTEXT_BW1_IndexedBody']}
with bpy.data.libraries.load(str(PARTS),link=False) as (src,dst):dst.objects=names.copy()
col=bpy.data.collections.new('BW6_R_SIDE_RETURN_REPLAY');s.collection.children.link(col)
for o in dst.objects:
 arm=next(m for m in o.modifiers if m.type=='ARMATURE');source_rig=arm.object
 assert not source_rig.parent and not source_rig.constraints
 a=source_rig.matrix_basis@source_rig.data.bones['spine01'].matrix_local;b=rig.matrix_world@rig.data.bones['spine01'].matrix_local
 assert max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))<2e-5
 arm.object=rig;col.objects.link(o);o.hide_render=False;o.hide_set(False)
hidden=['BW6_SideEnclosure_1','BW6_Side_LeatherClosure_1_0','BW6_Side_LeatherClosure_1_1']
for n in hidden:bpy.data.objects[n].hide_render=True;bpy.data.objects[n].hide_set(True)
s['BW6_side_return_owned']=json.dumps(names);s['BW6_side_return_replaced_context']=json.dumps(hidden)
assert protected=={n:hashlib.sha256(str([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in bpy.data.objects[n].data.vertices]).encode()).hexdigest() for n in protected}
out=R/'ada_bw6_side_return_r002_context.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/r002_context_replay.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'parts_source':str(PARTS),'parts_sha256':hashlib.sha256(PARTS.read_bytes()).hexdigest(),'protected_geometry_weights':protected,'candidate':str(out),'owned':names,'old_hidden':hidden},indent=2))
s.cycles.samples=12;s.render.threads=3
for view in ['three_quarter','profile','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('r002_context_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('R002_CONTEXT_DONE')
