import bpy,json,ast
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_layers_work.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];body=bpy.data.objects['BW6_BodyFit_Candidate']
collision=body.modifiers.new('BW6 Animated body cloth collider','COLLISION');body.collision.thickness_outer=.003;body.collision.thickness_inner=.001
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
g=coat.vertex_groups.new(name='BW6_Cloth_Authored_Pin')
for v in coat.data.vertices:
 p=v.co;release=smooth((abs(p.x)-.14)/.035)*smooth((.485-abs(p.x))/.045)*smooth((1.49-p.z)/.05)
 g.add([v.index],1-release,'REPLACE')
cloth=coat.modifiers.new('BW6 Sleeve collision experiment AUTHORING_ONLY','CLOTH');bpy.context.view_layer.objects.active=coat
bpy.ops.object.modifier_move_to_index(modifier=cloth.name,index=1)
st=cloth.settings;st.quality=12;st.mass=.3;st.air_damping=3;st.tension_stiffness=35;st.compression_stiffness=35;st.shear_stiffness=25;st.bending_stiffness=.5;st.vertex_group_mass=g.name;st.pin_stiffness=1;st.use_dynamic_mesh=True
cs=cloth.collision_settings;cs.use_collision=True;cs.use_self_collision=True;cs.distance_min=.004;cs.self_distance_min=.002;cs.collision_quality=8
cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=97;cloth.point_cache.use_disk_cache=True
coat['BW6_cloth_scope']='Native cloth after Armature, before subdivision and wall; pins preserve torso/collar/cuffs. Actual animated body collider, self collision. Diagnostic with no pre-roll, not runtime physics or baked game animation.'
out=R/'ada_bw6_cloth_collision_study.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
base=R.parents[1]
for p,names in [(base/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
record={'source':str(out),'settings':{'quality':st.quality,'collision_quality':cs.collision_quality,'cloth_distance_m':cs.distance_min,'self_distance_m':cs.self_distance_min,'pin_group':g.name,'use_dynamic_mesh':st.use_dynamic_mesh},'poses':{}}
for fr in range(1,50):
 s.frame_set(fr);bpy.context.view_layer.update();e=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();coords=np.array([e.matrix_world@v.co for v in m.vertices]);e.to_mesh_clear()
 assert np.isfinite(coords).all() and abs(coords).max()<3,('unstable',fr)
 if fr in [1,20,49]:
  a=geom(coat);b=geom(body);row={'self':screen(a,a,True),'body':screen(a,b)};record['poses'][str(fr)]=row;print('CLOTH',fr,{k:v['pairs'] for k,v in row.items()},flush=True)
  s.cycles.samples=8;s.render.threads=4;s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.filepath=str(R/'captures'/('cloth_'+str(fr)+'.png'));bpy.ops.render.render(write_still=True)
 if fr%5==0:print('SIM_FRAME',fr,flush=True)
(R/'records/cloth_collision_study.json').write_text(json.dumps(record,indent=2));s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_cloth_collision_sampled49.blend'))
print('BW6_CLOTH_STUDY_COMPLETE')
