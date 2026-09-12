import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;rig=bpy.data.objects['BW4_Armor_Independent_Rig'];col=bpy.data.collections['BW4_ARMOR_CANDIDATE'];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];parts=[bpy.data.objects[n] for n in json.loads(s['armor_parts'])]
dg=bpy.context.evaluated_depsgraph_get();ev=coat.evaluated_get(dg);me=ev.to_mesh();bvh=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
front=bpy.data.objects['BW4_Breastplate_ControlSurface'];back=bpy.data.objects['BW4_Backplate_ControlSurface'];old=[v.co.copy() for v in front.data.vertices]
U=[-1,-.97,-.8,-.51,-.16,0,.16,.51,.8,.97,1];centers=[.142,.144,.151,.182,.197,.189,.17,.145,.137,.137]
for v in front.data.vertices:
 j=v.index//11;u=U[v.index%11];p=v.co.copy();p.y=centers[j]-.053*abs(u)**1.6+.006*(1-min(1,abs(u)/.16))
 hit=bvh.ray_cast(Vector((p.x,1,p.z)),Vector((0,-1,0)),2)
 if hit[0]:p.y=max(p.y,hit[0].y+.019)
 v.co=p
front.data.update()
# Keep rim construction attached to the corrected boundary, rather than leaving ornaments at old offsets.
for name,idx in [('Neck',list(range(99,110))),('Waist',list(range(11))),('Side_L',[j*11 for j in range(10)]),('Side_R',[j*11+10 for j in range(10)])]:
 rim=bpy.data.objects['BW4_Front_'+name+'_Return']
 for k,i in enumerate(idx):
  delta=front.data.vertices[i].co-old[i]
  rim.data.vertices[k*2].co+=delta;rim.data.vertices[k*2+1].co+=delta
 rim.data.update()
def mesh(name,v,f,bone,thick=.003,sub=1):
 me=bpy.data.meshes.new(name+'_EditableCage');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(bpy.data.materials['BW4_Armor_Clay'])
 for p in me.polygons:p.use_smooth=True
 if sub:m=ob.modifiers.new('Controlled surface interpolation','SUBSURF');m.levels=sub;m.render_levels=sub
 m=ob.modifiers.new('Steel wall inward','SOLIDIFY');m.thickness=thick;m.offset=-1;m.use_even_offset=False
 m=ob.modifiers.new('Small edge radius','BEVEL');m.width=.0006;m.segments=2
 g=ob.vertex_groups.new(name=bone);g.add(list(range(len(v))),1,'REPLACE');m=ob.modifiers.new('Rigid authoring attachment','ARMATURE');m.object=rig
 ob['owner_bone']=bone;ob['status']='AUTHORING_ONLY_ART_CANDIDATE';parts.append(ob);return ob
# Plate return sidewalls now overlap beneath backplate edges. Intentional 6 mm seam clearance.
for side in [-1,1]:
 vs=[];fs=[]
 for j in range(7):
  i=j*11+(10 if side==1 else 0);p=front.data.vertices[i].co.copy();q=back.data.vertices[i].co.copy();q.x+=side*.006;q.y-=.006
  for t in [0,.08,.46,.88,1]:
   v=p.lerp(q,t);v.x+=side*.009*math.sin(math.pi*t);vs.append(v)
  if j:
   k=(j-1)*5
   for c in range(4):fs.append((k+c,k+c+1,k+c+6,k+c+5))
 ob=mesh('BW4_Thorax_SideReturn_'+str(side),vs,fs,'spine01');ob['construction']='Thoracic side closure with back overlap; arm opening kept above.'
# Local sleeve allowance at shoulder and underarm, candidate copy only, source indices preserved.
# Establish padding volume rather than cover an uncovered arm with another plate.
for v in coat.data.vertices:
 p=coat.matrix_world@v.co
 if .125<p.x<.31 and 1.305<p.z<1.52:
  a=Vector((.181846,-.046362,1.444984));b=Vector((.361061,-.042104,1.248911));axis=(b-a).normalized();u=(p-a).dot(axis);rad=(p-a)-axis*u
  fall=min(1,max(0,(p.x-.125)/.05))*min(1,max(0,(.31-p.x)/.055));amp=.009*fall
  if rad.length>.02:p+=rad.normalized()*amp
  v.co=coat.matrix_world.inverted()@p
coat.data.update();coat['BW4_change']='Anatomical-right shoulder/underarm rest allowance, max 9mm radial, source topology and weights retained; motion tests determine acceptance.'
# Explicit short authoring range: rest, elbow, elevated arm, forward reach, rest.
poses={1:{},25:{'lowerarm01.R':(65,0,0)},49:{'upperarm01.R':(20,0,-35),'lowerarm01.R':(55,0,0)},73:{'upperarm01.R':(45,0,-12),'lowerarm01.R':(38,0,0)},97:{}}
for fr,pose in poses.items():
 for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0)
 for n,xyz in pose.items():rig.pose.bones[n].rotation_euler=tuple(math.radians(x) for x in xyz)
 for n in ['upperarm01.R','lowerarm01.R']:
  rig.pose.bones[n].keyframe_insert(data_path='rotation_euler',frame=fr)
rig.animation_data.action.name='BW4_Armor_Authoring_Diagnostic_NOT_GAME_CLIPS'
s['armor_parts']=json.dumps([o.name for o in parts]);s['iteration']='Corrective revision 1: chest clearance, side returns, right sleeve allowance; rest and three local authoring poses.'
s['pose_labels']=json.dumps({1:'REST_APOSE',25:'ELBOW65',49:'ARM_RAISE20_Zminus35_ELBOW55',73:'FORWARD45_Zminus12_ELBOW38',97:'REST_APOSE'})
s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_armor_revision1.blend'))
for name,cam,fr in [('rev1_front','front',1),('rev1_three_quarter','three_quarter',1),('rev1_profile','profile',1),('rev1_raise','three_quarter',49),('rev1_reach','three_quarter',73)]:
 s.frame_set(fr);s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{name}.png');bpy.ops.render.render(write_still=True)
for o in parts:o.hide_render=True
for o in s.objects:
 if o.type=='MESH' and o not in [coat,bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody']]:o.hide_render=True
s.frame_set(49);s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.filepath=str(R/'captures/rev1_sleeve_only_raise.png');bpy.ops.render.render(write_still=True)
print('REVISION1_RENDERED')
