import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_upper_integrated_r002.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];source=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']
original={tuple(round(float(c),6) for c in v.co) for v in source.data.vertices}
bm=bmesh.new();bm.from_mesh(coat.data)
extra=[v for v in bm.verts if abs(v.co.x)>.235 and tuple(round(float(c),6) for c in v.co) not in original]
record={'source':source.name,'before_vertices':len(bm.verts),'removed_new_cut_vertices':[list(v.co) for v in extra],'scope':'Only nonoriginal world-horizontal cut vertices beyond absolute X .235m; original sleeve vertex coordinates retained. Restores source sleeve control topology, not armor inflation or body scaling.'}
bmesh.ops.dissolve_verts(bm,verts=extra,use_face_split=False,use_boundary_tear=False)
record['after_vertices']=len(bm.verts);bm.to_mesh(coat.data);bm.free()
coat['BW6_sleeve_restoration']=record['scope'];coat.data.update()
out=R/'ada_bw6_sleeve_topology_restored.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
s.cycles.samples=20;s.render.threads=4
for layer in s.view_layers:layer.material_override=None
for view in ['three_quarter','front']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('restored_sleeve_'+view+'.png'));bpy.ops.render.render(write_still=True)
(R/'records/sleeve_restoration.json').write_text(json.dumps(record,indent=2));print('BW6_SLEEVE_TOPOLOGY_RESTORE_COMPLETE',len(extra))
