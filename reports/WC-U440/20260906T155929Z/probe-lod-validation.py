import bpy,json
from pathlib import Path
root=Path(r'C:/Users/iputu/Documents/Wonder Chess')
bpy.ops.wm.open_mainfile(filepath=str(root/'art-source/heroes/wc_u_halfling_warrior/wc_u_halfling_warrior.blend'))
rows=[]
for suffix in ('','_LOD1','_LOD2'):
    mesh=bpy.data.objects['SK_wc_u_halfling_warrior'+suffix].data
    mesh.calc_loop_triangles();before=len(mesh.loop_triangles)
    changed=mesh.validate(verbose=True,clean_customdata=False)
    mesh.calc_loop_triangles()
    rows.append({'suffix':suffix,'before':before,'after':len(mesh.loop_triangles),'mesh_validate_changed':changed})
print('LOD_VALIDATION_PROBE '+json.dumps(rows),flush=True)
(Path(__file__).parent/'lod-validation-probe.json').write_text(json.dumps({'read_only_source':True,'rows':rows},indent=2))
