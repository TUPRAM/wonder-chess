"""Replace intersecting overlay trims with connected raised bands in the shell."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];source=R/'ada_bw6_backplate_initial.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
o=bpy.data.objects['BW6_BackPlate_Rebuilt'];old=o.data;N=15;rows=12
v=[p.co.copy() for p in old.vertices];f=[]
# Remove only the two narrow face bands, retaining their existing boundary
# vertices. Insert a slightly raised connected band, never a pasted trim.
for face in old.polygons:
 ids=list(face.vertices);row=min(ids)//N
 if row not in (0,1,rows-3,rows-2):f.append(ids)
newrows=[]
for first,second,depth in [(0,2,.0028),(rows-3,rows-1,.003)]:
 loops=[[first*N+i for i in range(N)]]
 for t in (.25,.5,.75):
  ids=[]
  for i in range(N):
   p=v[first*N+i].lerp(v[second*N+i],t);p.y-=depth*(1-abs(t-.5));
   if t==.5:
    idx=((first+second)//2)*N+i;v[idx]=p;ids.append(idx)
   else:ids.append(len(v));v.append(p)
  loops.append(ids);newrows.append(ids)
 loops.append([second*N+i for i in range(N)])
 for a,b in zip(loops,loops[1:]):
  for i in range(N-1):f.append([a[i],a[i+1],b[i+1],b[i]])
me=bpy.data.meshes.new('BW6_Backplate_Connected_EdgeBands');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for mat in old.materials:me.materials.append(mat)
o.data=me;o.vertex_groups.clear();g=o.vertex_groups.new(name='spine01');g.add(list(range(len(v))),1,'REPLACE')
for p in me.polygons:p.use_smooth=True
cr=me.attributes.new('crease_edge','FLOAT','EDGE')
for e in me.edges:
 a,b=e.vertices
 if a<rows*N and b<rows*N and a%N==b%N==7:cr.data[e.index].value=.65
for name in ['BW6_Back_Neck_Rebuilt','BW6_Back_Hem_TurnedBorder']:
 ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True)
s['BW6_backplate_owned']=json.dumps([o.name]);s['BW6_backplate_replaces']=json.dumps(['BW6_BackPlate','BW6_Back_Neck_TurnedBorder','BW6_Back_Hem_TurnedBorder'])
o['BW6_edge_construction']='Neck and hem overlay meshes retired. Connected raised surface bands replace two wider connected strips; original lower control points and upward center hem preserved. Same single Solidify wall continues through edge bands.'
out=R/'ada_bw6_backplate_correction2.blend';s.camera=bpy.data.objects['BW4_Camera_back'];bpy.ops.wm.save_as_mainfile(filepath=str(out))
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='OBJECT';s.display.shading.light='STUDIO';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
for ob in s.objects:
 if ob.type=='MESH':ob.color=(.55,.55,.55,1)
for fr in [1,49]:
 s.frame_set(fr)
 for view in ['back','profile','three_quarter']:
  s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/f'correction2_context_{view}_{fr}.png');bpy.ops.render.render(write_still=True)
s.frame_set(1)
for ob in s.objects:
 if ob.type=='MESH' and ob.name not in [o.name,'BW6_PaddedCoat_Tailored']:ob.hide_render=True
bpy.data.objects['BW6_PaddedCoat_Tailored'].color=(.36,.17,.13,1)
for view in ['back','profile']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/f'correction2_pair_{view}.png');bpy.ops.render.render(write_still=True)
(R/'records/correction2_construction.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'old_control_positions_preserved':len(old.vertices)-30,'repositioned_internal_band_control_points':30,'new_band_rows':newrows,'new_vertices':len(v),'faces':len(f),'removed_overlay_trims':['BW6_Back_Neck_Rebuilt','BW6_Back_Hem_TurnedBorder'],'body_coat_front_other_geometry_changed':False,'method':'Topology-connected raised edge bands; no intersection exclusion and no pasted trim'},indent=2));print('BACKPLATE_CONNECTED_BANDS_BUILT')


