import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_upper_integrated_r002.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
materials=list(bpy.data.objects['BW6_PaddedCoat_Tailored'].data.materials)
# Replay only the actual retained coat construction, restricting the torso
# section cuts to torso faces. Source forearm cages must not gain those cuts.
code=(R/'operations/18_fitted_section_and_collar.py').read_text()
code=code[code.index("old=bpy.data.objects['BW6_PaddedCoat_Tailored']"):code.index("out=R/'ada_bw6_torso_fitted_coat.blend'")]
code=code.replace("bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces)","faces=[f for f in bm.faces if all(abs(v.co.x)<.235 for v in f.verts)];edges={e for f in faces for e in f.edges};vs={v for f in faces for v in f.verts}\n bmesh.ops.bisect_plane(bm,geom=list(vs)+list(edges)+faces")
exec(compile(code,'BW6_scoped_torso_section_replay','exec'),globals())
code=(R/'operations/19_oriented_padded_interface.py').read_text();code=code[code.index("coat=bpy.data.objects['BW6_PaddedCoat_Tailored']"):code.index("out=R/'ada_bw6_torso_oriented_work.blend'")];exec(compile(code,'BW6_retained_wall_replay','exec'),globals())
code=(R/'operations/22_cut_and_sew_neckline.py').read_text();code=code[code.index("coat=bpy.data.objects['BW6_PaddedCoat_Tailored']"):code.index('bpy.ops.wm.save_as_mainfile')];exec(compile(code,'BW6_retained_neck_aperture_replay','exec'),globals())
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');solid.thickness_clamp=.5;solid.use_thickness_angle_clamp=True
coat.data.materials.clear()
for m in materials:coat.data.materials.append(m)
for f in coat.data.polygons:
 p=f.center;in_collar=(p.x/.14)**2+((p.y+.05)/.13)**2<1.24;f.material_index=int((p.z<1.245 and abs(p.x)<.21) or (p.z>1.465 and in_collar and p.x>0))
coat['BW6_sleeve_scope']='Torso construction replayed with section cuts limited to faces whose every vertex lies inside absolute X .235m. Original source sleeves copied, without newly inserted forearm horizontal cuts.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_torso_scoped_sections.blend'))
s.cycles.samples=20;s.render.threads=4
for layer in s.view_layers:layer.material_override=None
for view in ['three_quarter','front']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('scoped_sections_'+view+'.png'));bpy.ops.render.render(write_still=True)
(R/'records/scoped_sections_replay.json').write_text(json.dumps({'scope':coat['BW6_sleeve_scope'],'retained_procedures':['18 torso fit with restricted cuts','19 oriented wall','22 cut/sew aperture'],'rejected':'30 blind inserted-vertex dissolution produced broken sleeves and is not adopted','vertices':len(coat.data.vertices)},indent=2));print('BW6_SCOPED_SECTION_REPLAY_COMPLETE')
