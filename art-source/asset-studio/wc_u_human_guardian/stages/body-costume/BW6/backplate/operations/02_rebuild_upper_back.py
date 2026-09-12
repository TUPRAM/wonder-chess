"""Local upper back/armhole reconstruction against measured posterior coat sections."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];source=R.parent/'armor/ada_bw6_torso_recut_neck.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];rig.data=rig.data.copy();rig.animation_data.action=rig.animation_data.action.copy();rig.name='BW6_Backplate_Independent_Rig'
old=bpy.data.objects['BW6_BackPlate'];N=15;u=[-1,-.985,-.88,-.7,-.46,-.22,-.055,0,.055,.22,.46,.7,.88,.985,1]
vs=[tuple(v.co) for v in old.data.vertices[:6*N]];fs=[tuple(f.vertices) for f in old.data.polygons if max(f.vertices)<6*N]
# Cut the failed upper shell off at the preserved lower-rib/upper-back interface.
# New section rings establish a concave armhole and quiet ridge over scapular
# volume. Physical wall clearance is included, rather than copied from skin.
stations=[(1.398,.174,-.176,-.162),(1.420,.153,-.178,-.167),(1.441,.137,-.177,-.169),(1.462,.126,-.177,-.167),(1.474,.123,-.176,-.165),(1.481,.122,-.175,-.164)]
for j,(z,width,center,edge) in enumerate(stations,6):
 t=(j-5)/len(stations)
 for a in u:
  aa=abs(a);y=center+(edge-center)*aa
  vs.append((width*a,y,z-.016*(1-aa)*t**2))
 for i in range(N-1):k=(j-1)*N+i;fs.append((k,k+1,k+N+1,k+N))
me=bpy.data.meshes.new('BW6_Backplate_UpperRecut_ControlSurface');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for m in old.data.materials:me.materials.append(m)
o=old.copy();o.data=me;o.name='BW6_BackPlate_Rebuilt';s.collection.objects.link(o);o.hide_render=False;o.hide_set(False);old.hide_render=True;old.hide_set(True)
o.vertex_groups.clear();g=o.vertex_groups.new(name='spine01');g.add(list(range(len(vs))),1,'REPLACE')
for f in me.polygons:f.use_smooth=True
cr=me.attributes.new('crease_edge','FLOAT','EDGE')
for e in me.edges:
 a,b=e.vertices
 if a%N==b%N==7:cr.data[e.index].value=.65
o['BW6_scope']='Upper-back and armhole reconstruction only; rows 0-5 and center-up lower hem preserved exactly'
o['BW6_method']='Failed three-row upper shell removed; six purpose-built section rows and concave lateral armhole replace it. Measured coat/body sections define local outer envelope, with independent ridge planes. No whole-backplate offset.'
o['owner_bone']='spine01'
# Rebuild the corresponding neck return so the border follows the new edge.
oldrim=bpy.data.objects['BW6_Back_Neck_TurnedBorder'];oldrim.hide_render=True;oldrim.hide_set(True)
rv=[];rf=[];points=[Vector(p) for p in vs[-N:]]
for k,p in enumerate(points):
 tang=(points[min(k+1,N-1)]-points[max(k-1,0)]).normalized();normal=Vector((0,-1,0));inside=tang.cross(normal).normalized()
 if inside.z>0:inside=-inside
 for d,depth in [(0,.0005),(.007,.0005),(.007,.003),(0,.003)]:rv.append(p+inside*d+normal*depth)
 if k:
  for q in range(4):rf.append(((k-1)*4+q,(k-1)*4+(q+1)%4,k*4+(q+1)%4,k*4+q))
rf.extend([(3,2,1,0),tuple(range(len(rv)-4,len(rv)))])
rm=bpy.data.meshes.new('BW6_BackNeck_LocalReturn');rm.from_pydata(rv,[],rf);rm.update();bm=bmesh.new();bm.from_mesh(rm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(rm);bm.free()
rim=oldrim.copy();rim.data=rm;rim.name='BW6_Back_Neck_Rebuilt';s.collection.objects.link(rim);rim.hide_render=False;rim.hide_set(False)
for mat in oldrim.data.materials:rm.materials.append(mat)
for f in rm.polygons:f.use_smooth=True
rim.vertex_groups.clear();g=rim.vertex_groups.new(name='spine01');g.add(list(range(len(rv))),1,'REPLACE')
s['BW6_backplate_owned']=json.dumps([o.name,rim.name]);s['BW6_backplate_status']='CONSTRUCTION_REVIEW_PENDING';s['BW6_backplate_human_approval']=False
out=R/'ada_bw6_backplate_initial.blend';s.camera=bpy.data.objects['BW4_Camera_back'];bpy.ops.wm.save_as_mainfile(filepath=str(out))
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='OBJECT';s.display.shading.light='STUDIO';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
for ob in s.objects:
 if ob.type=='MESH':ob.color=(.55,.55,.55,1)
for fr in [1,49]:
 s.frame_set(fr)
 for view in ['back','profile','three_quarter']:
  s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/f'initial_context_{view}_{fr}.png');bpy.ops.render.render(write_still=True)
# Pair-only views reveal padding exposures; the query always includes full geometry.
s.frame_set(1)
for ob in s.objects:
 if ob.type=='MESH' and ob.name not in [o.name,rim.name,'BW6_Back_Hem_TurnedBorder','BW6_PaddedCoat_Tailored']:ob.hide_render=True
bpy.data.objects['BW6_PaddedCoat_Tailored'].color=(.36,.17,.13,1)
for view in ['back','profile']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/f'initial_pair_{view}.png');bpy.ops.render.render(write_still=True)
(R/'records/initial_construction.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'owned':[o.name,rim.name],'replacement_of':['BW6_BackPlate','BW6_Back_Neck_TurnedBorder'],'unchanged_lower_vertices':90,'new_upper_stations_m':stations,'neck_return_rebuilt':True,'back_center_hem_up_preserved_m':.018,'main_wall_m':.0035,'source_rig_action_copied':True,'all_other_geometry_untouched':True,'human_approval':False,'canonical_changes':False},indent=2));print('BW6_BACKPLATE_INITIAL_EXECUTED')
