import bpy,bmesh,json,math
from mathutils import Vector
from math import sqrt
assert bpy.data.filepath.replace('\\','/').endswith('/method-recovery/MR1/r001/ada_method_proof_work.blend')
assert bpy.data.scenes.get('MR1_FACE_PROOF') is None
baseline=bpy.context.scene
def record_scene(sc):
    return {'name':sc.name,'objects':[{'name':o.name,'type':o.type,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'visible_get':o.visible_get(),'collections':[c.name for c in o.users_collection],'modifiers':[(m.name,m.type,m.show_viewport,m.show_render) for m in o.modifiers],'matrix':[list(r) for r in o.matrix_world]} for o in sc.objects],'cameras':[{'name':o.name,'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'ortho_scale':o.data.ortho_scale} for o in sc.objects if o.type=='CAMERA'],'layer_exclusions':[(c.name,c.exclude,c.hide_viewport) for c in sc.view_layers[0].layer_collection.children]}
print('BASELINE_INVENTORY '+json.dumps(record_scene(baseline)))
scene=bpy.data.scenes.new('MR1_FACE_PROOF');bpy.context.window.scene=scene
col=bpy.data.collections.new('MR1_FACE_CANDIDATE_ALLOWLIST');scene.collection.children.link(col)
def mat(name,color,rough=.6):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
    return m
clay=mat('MR1_Uniform_Clay',(.48,.48,.48))
iris=mat('MR1_Diagnostic_Iris',(.09,.045,.015));pupil=mat('MR1_Diagnostic_Pupil',(.006,.006,.006))
white=mat('MR1_Diagnostic_Sclera',(.67,.67,.64));wiremat=mat('MR1_Cage_Dark',(.025,.025,.025))
def mesh(name,verts,faces,collection=col):
    m=bpy.data.meshes.new(name+'_ControlMesh');m.from_pydata(verts,[],faces);m.update()
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    o=bpy.data.objects.new(name,m);collection.objects.link(o)
    for f in m.polygons:f.use_smooth=True
    m.materials.append(clay);return o
# Anatomical right +X. Hand-authored aperture points in millimeters: inner corner,
# upper arc with medial peak, finite lateral turn, lower arc with a different peak.
ap=[(14,1686),(16,1689),(20,1693),(25,1696),(31,1698),(38,1698),(45,1696.5),(51,1693.5),(56,1690.5),(58,1688.5),(58,1687),(55,1685),(50,1682.5),(44,1681),(37,1680.2),(30,1680.5),(24,1682),(19,1684),(16,1685),(14.5,1685.3)]
cx=.035;cy=.026;cz=1.689;rad=.0265
margin=[];margin_outer=[]
for x,z in ap:
    x/=1000;z/=1000
    y=cy+sqrt(max(0,rad*rad-(x-cx)**2-(z-cz)**2))
    margin.append((x,y+.00025,z))
    ox=x+(x-cx)*.035;oz=z+(z-cz)*.085
    oy=cy+sqrt(max(0,rad*rad-(ox-cx)**2-(oz-cz)**2))
    margin_outer.append((ox,oy+.0015,oz))
# Explicit editable lid body, brow/socket, and cheek/temple stations.
body=[(11,52,1687),(14,53,1693),(19,54,1699),(25,55,1703),(31,54,1705),(40,52,1705),(48,47,1702),(55,41,1698),(61,34,1694),(64,30,1689),(64,30,1685),(59,37,1680),(53,44,1676),(46,52,1674),(37,58,1674),(28,61,1675),(20,61,1678),(14,61,1681),(11,58,1684),(10.5,54,1686)]
socket=[(6,63,1689),(9,64,1700),(15,65,1709),(24,65,1716),(33,63,1720),(44,59,1719),(57,49,1714),(69,32,1706),(77,19,1697),(80,12,1688),(81,10,1679),(75,23,1668),(63,45,1660),(51,62,1655),(38,68,1656),(26,70,1659),(15,70,1665),(8,70,1674),(6,68,1681),(5.5,65,1686)]
outer=[(0,70,1691),(0,72,1705),(8,71,1723),(22,67,1734),(38,61,1738),(56,48,1735),(72,30,1723),(84,8,1709),(90,-8,1696),(92,-15,1680),(89,-16,1664),(79,4,1649),(64,37,1636),(49,58,1629),(36,66,1633),(23,69,1643),(10,73,1655),(1,78,1670),(0,76,1681),(0,72,1687)]
rows=[margin,margin_outer]+[[(x/1000,y/1000,z/1000) for x,y,z in row] for row in [body,socket,outer]]
verts=[v for row in rows for v in row]
faces=[(k*20+j,k*20+(j+1)%20,(k+1)*20+(j+1)%20,(k+1)*20+j) for k in range(4) for j in range(20)]
skin=mesh('MR1_Right_Orbital_Cage',verts,faces)
skin['method']='100 deliberately located cage vertices; aperture, thickness, lid body, socket and independent cheek; no dense grid or skin projection'
skin['scope']='Isolated open shell; NOT integrated head';skin['anatomical_side']='right +X'
sub=skin.modifiers.new('One subdivision level proof','SUBSURF');sub.levels=1;sub.render_levels=1
vg=skin.vertex_groups.new(name='Lid_Margin_Only');vg.add(list(range(20)),1,'REPLACE')
# Smooth globe guide; iris/pupil are face material assignments, without raised geometry.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=rad,location=(cx,cy,cz))
globe=bpy.context.object;globe.name='MR1_Right_Eye_Globe'
for c in list(globe.users_collection):c.objects.unlink(globe)
col.objects.link(globe)
for f in globe.data.polygons:f.use_smooth=True
for m in [white,iris,pupil]:globe.data.materials.append(m)
for f in globe.data.polygons:
    p=f.center
    r=sqrt(p.x*p.x+p.z*p.z)
    f.material_index=2 if p.y>0 and r<.0037 else 1 if p.y>0 and r<.0093 else 0
globe['diagnostic_only']='Material iris/pupil for gaze; no relief displacement'
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('MR1_Neutral_World');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.17,.17,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
target=Vector((.039,.025,1.687))
def camera(name,pos,scale=.135):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);col.objects.link(o)
    o.location=pos;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=20;d.dof.use_dof=False
    return o
for name,pos in [('front',(.039,.55,1.687)),('profile',(.55,.025,1.687)),('three_quarter',(.32,.44,1.707)),('opposite',(-.25,.44,1.707))]:
    camera('MR1_FACE_'+name,pos)
def area(name,pos,energy,size):
    d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);col.objects.link(o)
    o.location=pos;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.energy=energy;d.shape='DISK';d.size=size;return o
area('MR1_FACE_Key',(-.25,.35,1.95),12,.28);area('MR1_FACE_Fill',(.28,.23,1.77),3,.3)
scene.camera=bpy.data.objects['MR1_FACE_three_quarter']
scene['mr1_operation']='face_initial_cage'
scene['mr1_render_allowlist']=json.dumps([o.name for o in col.objects])
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        s=a.spaces.active;s.region_3d.view_location=target;s.region_3d.view_distance=.20
        s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO'
        s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.overlay.show_extras=False;s.overlay.show_floor=False
bpy.context.view_layer.objects.active=skin;skin.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
for name in ['front','profile','three_quarter','opposite']:
    scene.camera=bpy.data.objects['MR1_FACE_'+name];scene.render.filepath=root+'/captures/face_initial_'+name+'.png'
    bpy.ops.render.render(write_still=True)
print('FACE_INITIAL '+json.dumps({'vertices':len(skin.data.vertices),'faces':len(skin.data.polygons),'subdivision':1,'scene':scene.name,'allowlist':[o.name for o in col.objects]}))

