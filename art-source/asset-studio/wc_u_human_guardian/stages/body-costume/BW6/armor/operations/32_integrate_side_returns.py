import bpy,bmesh,json,importlib.util
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_upper_integrated_r002.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig']
path=R.parent/'sideclosure/append_side_return.py';spec=importlib.util.spec_from_file_location('bw6_side',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);added=m.append_side_return(rig,s)
oldnames=added['old_context_to_review']+['BW6_SideEnclosure_-1','BW6_Side_LeatherClosure_-1_0','BW6_Side_LeatherClosure_-1_1']
for n in oldnames:
 o=bpy.data.objects[n];o.hide_render=True;o.hide_set(True)
newleft=[]
for n in added['objects']:
 o=bpy.data.objects[n]
 assert not o.parent and max(abs(o.matrix_world[i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4))<1e-6
 assert all(g.name=='spine01' for g in o.vertex_groups)
 cp=o.copy();cp.data=o.data.copy();cp.name=n.replace('_R_','_L_');assert cp.name!=n
 o.users_collection[0].objects.link(cp)
 bm=bmesh.new();bm.from_mesh(cp.data)
 for v in bm.verts:v.co.x=-v.co.x
 bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(cp.data);bm.free()
 cp['BW6_side_extension']='Independent mirrored world geometry and reversed winding; same verified central spine owner. No limb Euler mirroring. Candidate left fit awaits whole-assembly queries.';newleft.append(cp.name)
for n in added['objects']+newleft:
 o=bpy.data.objects[n];o.hide_render=False;o.hide_set(False);o.data.materials.clear();o.data.materials.append(bpy.data.materials['BW6_ColorLayout_Leather' if 'Strap' in n else 'BW6_ColorLayout_Steel'])
owned=[n for n in json.loads(s['BW6_owned_visible_parts']) if n not in oldnames];s['BW6_owned_visible_parts']=json.dumps(owned+added['objects']+newleft)
s['BW6_side_append']=json.dumps({'right':added,'left':newleft,'hidden':oldnames});s['BW6_bracer_fit_status']='INVALIDATED_SOURCE_COAT_TRANSFORM; corrected-context refit pending. Current bracers are failed contextual fit.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_upper_side_integrated_r003.blend'))
s.cycles.samples=20;s.render.threads=4
for view in ['three_quarter','profile','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('side_integrated_'+view+'.png'));bpy.ops.render.render(write_still=True)
(R/'records/side_integration.json').write_text(json.dumps({'right':added,'left':newleft,'hidden':oldnames,'scope':'Left extension uses central spine, not mirrored limb controls; full candidate clearance pending.'},indent=2));print('BW6_SIDE_INTEGRATION_COMPLETE')
