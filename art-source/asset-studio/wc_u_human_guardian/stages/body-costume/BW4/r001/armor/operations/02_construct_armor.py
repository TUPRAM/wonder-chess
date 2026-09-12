import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW4/r001/armor')
src=bpy.data.scenes['BW1_BODY_COSTUME'];src.frame_set(1)
s=bpy.data.scenes.new('BW4_ARMOR_LOCAL_AUTHORING_ONLY');bpy.context.window.scene=s
col=bpy.data.collections.new('BW4_ARMOR_CANDIDATE');s.collection.children.link(col)
rig0=bpy.data.objects['BW1_Temporary_Pose_Rig'];rig=rig0.copy();rig.data=rig0.data.copy();rig.name='BW4_Armor_Independent_Rig';col.objects.link(rig);rig.animation_data_clear()
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
rig['scope']='Independent MPFB authoring rig. No canonical animation compatibility claim.'
clay=bpy.data.materials.new('BW4_Armor_Clay');clay.diffuse_color=(.47,.46,.43,1);clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.47,.46,.43,1);bs.inputs['Roughness'].default_value=.65
under=clay.copy();under.name='BW4_Underlayer_Clay';under.diffuse_color=(.33,.32,.30,1);under.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.33,.32,.30,1)
parts=[];context=[];baseline=[]
exclude=['BW1_Breastplate','BW1_Backplate','BW1_Pauldron_R_Cap','BW1_Pauldron_R_Lame1','BW1_Pauldron_R_Lame2']
for o in src.objects:
 if o.type!='MESH' or not o.name.startswith('BW1_') or o.hide_render or any(t in o.name for t in ['Sword','Shield']):continue
 n=o.copy();n.data=o.data.copy();n.name='BW4_CONTEXT_'+o.name;col.objects.link(n);n.hide_render=False;n.hide_viewport=False
 if n.animation_data:n.animation_data_clear()
 if n.parent==rig0:
  n.parent=rig;n.matrix_parent_inverse=o.matrix_parent_inverse.copy();n.matrix_basis=o.matrix_basis.copy()
 for m in n.modifiers:
  if m.type=='ARMATURE' and m.object==rig0:m.object=rig
 n.data.materials.clear();n.data.materials.append(under if o.name in ['BW1_CoatUpper_Continuous','BW1_PaddedCollar'] else clay)
 if o.name in exclude:baseline.append(n);n.hide_render=True
 else:context.append(n)
 if o.name=='BW1_CoatUpper_Continuous':coat=n
 if o.name=='BW1_IndexedBody':body=n
 # Every derived mesh and shape-key datablock is independent.
 assert n.data!=o.data
 if o.data.shape_keys:assert n.data.shape_keys!=o.data.shape_keys
for n in [coat,bpy.data.objects['BW4_CONTEXT_BW1_Leggings']]:
 for m in n.modifiers:
  if m.type=='SOLIDIFY':assert not m.use_even_offset
bpy.context.view_layer.update()
# A BVH of the actual undeformed padded source supplies only minimum-clearance bounds.
deps=bpy.context.evaluated_depsgraph_get();ev=coat.evaluated_get(deps);me=ev.to_mesh();co=[ev.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons];bvh=BVHTree.FromPolygons(co,faces);ev.to_mesh_clear()
def frontbound(x,z,front=True):
 origin=Vector((x,1 if front else -1,z));direction=Vector((0,-1 if front else 1,0));hit=bvh.ray_cast(origin,direction,2)
 return hit[0].y if hit[0] else None
def mesh(name,v,f,bone,thick=.003,sub=0,mat=clay):
 me=bpy.data.meshes.new(name+'_EditableCage');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 if sub:m=ob.modifiers.new('Controlled surface interpolation','SUBSURF');m.levels=sub;m.render_levels=sub
 if thick:m=ob.modifiers.new('Steel wall 3mm inward','SOLIDIFY');m.thickness=thick;m.offset=-1;m.use_even_offset=False
 if thick:m=ob.modifiers.new('Edge highlight 0.6mm','BEVEL');m.width=.0006;m.segments=2
 if bone:
  vg=ob.vertex_groups.new(name=bone);vg.add(list(range(len(me.vertices))),1,'REPLACE');m=ob.modifiers.new('Rigid authoring attachment','ARMATURE');m.object=rig
  ob['owner_bone']=bone
 ob['status']='AUTHORING_ONLY_ART_CANDIDATE';ob['new_geometry']=True;parts.append(ob)
 return ob
def strip(name,points,width,normal,bone):
 v=[]
 for i,p in enumerate(points):
  p=Vector(p);a=Vector(points[max(0,i-1)]);b=Vector(points[min(len(points)-1,i+1)]);t=(b-a).normalized();ac=t.cross(Vector(normal)).normalized()*width/2
  v.extend([p-ac,p+ac])
 f=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)]
 return mesh(name,v,f,bone,.004,1)
# Thoracic plates use nine semantic columns and ten shaped cross-sections.
U=[-1,-.97,-.8,-.51,-.16,0,.16,.51,.8,.97,1]
rows=[(1.116,.181,.160),(1.124,.179,.158),(1.155,.172,.150),(1.224,.184,.182),(1.302,.199,.211),(1.362,.201,.209),(1.410,.177,.194),(1.450,.155,.164),(1.478,.148,.142),(1.484,.148,.141)]
record=[]
for front in [True,False]:
 v=[];f=[];sign=1 if front else -1
 for j,(z,w,d) in enumerate(rows):
  for u in U:
   # U-shaped neck opening and a pointed, shallow waist return are designed in the cage.
   zz=z
   if j<2:zz-=.018*(1-abs(u))
   if j>=7:zz-=.062*(1-abs(u))**2*((j-6)/3)
   x=w*u
   depth=d if front else d*.79
   y=-.046+sign*depth*(1-.69*abs(u)**1.85)
   if front:y+=.004*(1-min(1,abs(u)/.16))
   bound=frontbound(x,zz,front)
   if bound is not None:
    y=max(y,bound+.010) if front else min(y,bound-.010)
   v.append((x,y,zz));record.append({'part':'front' if front else 'back','x':x,'z':zz,'surface_y':y,'coat_y':bound})
  if j:
   a=(j-1)*len(U)
   for i in range(len(U)-1):f.append((a+i,a+i+1,a+i+1+len(U),a+i+len(U)))
 ob=mesh('BW4_Breastplate_ControlSurface' if front else 'BW4_Backplate_ControlSurface',v,f,'spine01',.003,1)
 ob['construction']='Purpose-built transverse cage; independent convex chest, concave neck opening, armhole setbacks and waist return. Coat ray bounds constrain clearance only.'
 n=len(U)
 # Broad edge returns use shaped ribbons, not torus ornaments.
 for edge,idx in [('Neck',list(range((len(rows)-1)*n,len(rows)*n))),('Waist',list(range(n))),('Side_L',[j*n for j in range(len(rows))]),('Side_R',[j*n+n-1 for j in range(len(rows))])]:
  pts=[Vector(v[i])+Vector((0,sign*.0015,0)) for i in idx]
  strip(('BW4_Front_' if front else 'BW4_Back_')+edge+'_Return',pts,.007,(0,sign,0),'spine01')
# Side closures fill the old implied connection with two separated, fitted leather straps.
for side in [-1,1]:
 for z in [1.215,1.335]:
  pts=[]
  for i in range(11):
   t=i/10;pts.append((side*(.181+.022*math.sin(math.pi*t)),.035-.155*t,z+.004*math.sin(math.pi*t)))
  strip('BW4_SideClosure_'+str(side)+'_'+str(z),pts,.026,(side,0,0),'spine01')
 # Shoulder bridges terminate on front/back upper shoulders, leaving collar free.
 pts=[(side*.138,.028,1.473),(side*.14,-.008,1.507),(side*.137,-.069,1.518),(side*.137,-.126,1.484),(side*.14,-.151,1.471)]
 strip('BW4_ShoulderBridge_'+str(side),pts,.026,(side,0,0),'spine01')
# Purposeful flattened pauldron cross-section. It is broad across the crown,
# fuller at the rear, and cut away at the front rather than a circular cap.
a=Vector((.18184635,-.04636158,1.44498372));b=Vector((.36106092,-.04210385,1.24891078));axis=(b-a).normalized();front=Vector((0,1,0));front=(front-axis*front.dot(axis)).normalized();outer=axis.cross(front)
cross=[(-1.0,-.16),(-.97,.00),(-.82,.52),(-.52,.90),(-.23,1.02),(0,1.03),(.26,1.02),(.55,.88),(.85,.46),(1,.02)]
layouts=[('Cap',[(-.063,.052),(-.055,.067),(-.021,.105),(.020,.113),(.077,.111),(.090,.107)]),('Lame1',[(.071,.106),(.077,.107),(.117,.102),(.139,.092),(.146,.091)]),('Lame2',[(.126,.099),(.133,.100),(.174,.088),(.191,.078),(.198,.077)])]
for name,rs in layouts:
 v=[];f=[]
 for j,(u,r) in enumerate(rs):
  for t,h in cross:
   # Rear return stays fuller; front cutout clears deltoid motion.
   uu=u+(.010 if name=='Cap' else .003)*t+.010*abs(t)**2
   p=a+axis*uu+front*(t*r*(1.06 if t<0 else .94))+outer*(h*r)
   v.append(tuple(p))
  if j:
   k=(j-1)*len(cross)
   for i in range(len(cross)-1):f.append((k+i,k+i+1,k+i+len(cross)+1,k+i+len(cross)))
 ob=mesh('BW4_Pauldron_R_'+name,v,f,'upperarm01.R',.003,1)
 ob['construction']='Asymmetric flattened crown with rear fullness, shaped front clearance and subordinate lames.'
 ob['attachment_limit']='Rigid to MPFB upperarm01.R for local authoring test; canonical existing clavicle/upperarm path must be fitted separately.'
 strip('BW4_Pauldron_R_'+name+'_LowerReturn',[Vector(p)+outer*.001 for p in v[-len(cross):]],.006,axis,'upperarm01.R')
# Camera/light setup is saved once and used for every comparison state.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=960;s.render.resolution_y=960;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('BW4_ReviewWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.film_transparent=False
def camera(name,loc,target,scale):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;return o
for name,loc in [('front',(0,3,1.36)),('back',(0,-3,1.36)),('profile',(3,-.045,1.36)),('three_quarter',(2.4,3.2,1.74)),('rear_three_quarter',(2.4,-3.2,1.70))]:camera('BW4_Camera_'+name,loc,(.01,-.045,1.335),.92)
camera('BW4_Camera_context',(3,5,2.6),(0,0,.88),2.08)
camera('BW4_Camera_shoulder',(2,3,2.2),(.24,-.04,1.4),.49)
for name,loc,power,size in [('Key',(-2,3,4),500,3),('Fill',(3,1,2),200,3),('Rim',(1,-3,3),450,2)]:
 d=bpy.data.lights.new('BW4_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new('BW4_'+name,d);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler()
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s['armor_parts']=json.dumps([o.name for o in parts]);s['baseline_parts']=json.dumps([o.name for o in baseline]);s['context_parts']=json.dumps([o.name for o in context]);s['scope']='Independent breast/back and right shoulder only. Head ART_REVISE; hand/equipment omitted from diagnostic, no engine claim.'
s['iteration']='Initial construction; no corrective revisions yet';s.frame_start=1;s.frame_end=97;s.render.fps=24
(R/'records/initial_fit_bounds.json').write_text(json.dumps(record,indent=2))
(R/'records/ownership.json').write_text(json.dumps({'source':bpy.data.filepath,'parts':[{'name':o.name,'owner':o.get('owner_bone'),'vertices':len(o.data.vertices)} for o in parts],'source_rig_bones':len(rig.data.bones),'scope':s['scope']},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_armor_initial_setup_corrected.blend'))
for label,cam in [('initial_valid_front','front'),('initial_valid_three_quarter','three_quarter'),('initial_valid_back','back')]:
 s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{label}.png');bpy.ops.render.render(write_still=True)
print('ARMOR_INITIAL_COMPLETE')
