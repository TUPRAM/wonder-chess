import bpy,json,math,hashlib,bmesh
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];src=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];bone=rig.data.bones['upperarm01.R'];anchor=rig.matrix_world@bone.head_local
axis=(rig.matrix_world@rig.data.bones['upperarm02.R'].tail_local-anchor).normalized();front=(Vector((0,1,0))-axis*axis.y).normalized();out=axis.cross(front).normalized()
col=bpy.data.collections.new('BW6_SHOULDER_SUPPORTED_PANELS_AUTHORING_ONLY');s.collection.children.link(col)
for o in s.objects:
 if o.name.startswith('BW4_Pauldron_R'):o.hide_render=True;o.hide_set(True)
def delta(name,bone_name):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.empty_display_size=.04
 c=o.constraints.new('CHILD_OF');c.name='Rest-relative world bone delta';c.target=rig;c.subtarget=bone_name;c.inverse_matrix=(rig.matrix_world@rig.data.bones[bone_name].matrix_local).inverted();c.set_inverse_pending=False
 return o
armdelta=delta('BW6_R_Arm_RestDelta','upperarm01.R');supportdelta=delta('BW6_R_Shoulder_RestDelta','shoulder01.R')
names=[];helpers=[]
def helper(name,amount):
 h=bpy.data.objects.new(name,None);col.objects.link(h);h.location=anchor;h.rotation_mode='QUATERNION';h.empty_display_type='ARROWS';h.empty_display_size=.04
 c=h.constraints.new('COPY_LOCATION');c.target=rig;c.subtarget='upperarm01.R';c.target_space='WORLD';c.owner_space='WORLD';c.head_tail=0
 c=h.constraints.new('COPY_ROTATION');c.name='Full shoulder-support rest-relative rotation';c.target=supportdelta;c.mix_mode='REPLACE';c.target_space='WORLD';c.owner_space='WORLD'
 c=h.constraints.new('COPY_ROTATION');c.name='Partial arm roll, rigid plate suspension';c.target=armdelta;c.mix_mode='REPLACE';c.target_space='WORLD';c.owner_space='WORLD';c.influence=amount
 h['motion_contract']='Joint-anchored world rest-delta rotation interpolation. Candidate authoring constraint, not runtime verified.';h['arm_rotation_influence']=amount;helpers.append(h.name)
 return h
mat=bpy.data.materials.new('BW6_Steel_Form_Study');mat.diffuse_color=(.42,.45,.50,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.36,.39,.44,1);bs.inputs['Metallic'].default_value=.3;bs.inputs['Roughness'].default_value=.38
def panel(name,rows,amount):
 h=helper(name+'_Suspension',amount);vs=[];faces=[];N=13
 for u,rw,rv,theta in rows:
  for j in range(N):
   t=(j/(N-1)*2-1)*math.radians(theta)
   # Noncircular front/back section, a broad crown and deliberately open underside.
   v=rv*math.sin(t)*(1.04 if t<0 else .96);w=rw*math.cos(t)
   p=axis*u+front*v+out*w;vs.append(tuple(p))
 for i in range(len(rows)-1):
  for j in range(N-1):a=i*N+j;faces.append((a,a+1,a+N+1,a+N))
 me=bpy.data.meshes.new(name+'_EditableControlCage');me.from_pydata(vs,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 # Require outward normals at the broad crown before thickness.
 if sum(p.normal.dot(out) for p in me.polygons)<0:
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=h;o.matrix_parent_inverse=Matrix.Identity(4);o.location=(0,0,0);me.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 m=o.modifiers.new('Editable surface level 1','SUBSURF');m.levels=1;m.render_levels=1
 m=o.modifiers.new('3mm inward steel shell','SOLIDIFY');m.thickness=.003;m.offset=-1;m.use_even_offset=False
 m=o.modifiers.new('0.4mm physical edge highlight','BEVEL');m.width=.0004;m.segments=2;m.limit_method='ANGLE';m.angle_limit=.6
 o['BW6_owned']=True;o['authoring_only']=True;names.append(name);return o
panel('BW6_Pauldron_R_Cap',[(-.067,.067,.110,38),(-.06,.073,.112,40),(-.035,.110,.120,55),(0,.123,.122,75),(.045,.120,.115,83),(.083,.113,.108,85),(.11,.110,.104,85)],.42)
panel('BW6_Pauldron_R_Lame1',[(.083,.098,.101,83),(.092,.099,.099,83),(.119,.096,.093,83),(.150,.091,.087,83)],.70)
panel('BW6_Pauldron_R_Lame2',[(.139,.081,.087,81),(.149,.082,.085,81),(.17,.078,.081,81),(.191,.073,.076,81)],1.0)
s['BW6_SHOULDER_ACTIVE']=json.dumps(names);s['BW6_SHOULDER_HELPERS']=json.dumps(helpers+[armdelta.name,supportdelta.name]);s['BW6_SHOULDER_STATUS']='INITIAL_UNREVIEWED'
bpy.context.view_layer.update();record={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'anchor_world_m':list(anchor),'basis':{'axis':list(axis),'front':list(front),'out':list(out)},'objects':{}}
for name in names:
 o=bpy.data.objects[name];q=[o.matrix_world@v.co for v in o.data.vertices];record['objects'][name]={'bounds_world_m':[[min(p[i] for p in q),max(p[i] for p in q)] for i in range(3)],'vertices':len(q),'faces':len(o.data.polygons),'helper':o.parent.name,'arm_rotation_influence':o.parent['arm_rotation_influence']}
record['rest_delta_matrix']=[list(x) for x in armdelta.matrix_world];(R/'records/initial_construction.json').write_text(json.dumps(record,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_initial.blend'));print(json.dumps(record,indent=2))
