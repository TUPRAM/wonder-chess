import bpy,bmesh,json,math
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/head-polish/HP1/r001'
scene=bpy.data.scenes['HP1_HEAD_POLISH'];bpy.context.window.scene=scene
old=bpy.data.objects['HP1_HEAD_POLISH_Head_r001'];head=old.copy();head.data=old.data.copy();head.name='HP1_HEAD_POLISH_Head_r002';scene.collection.objects.link(head)
old.hide_render=True;old.hide_set(True)
features=json.loads(head['feature_indices']);edges={v.index:[] for v in head.data.vertices}
for e in head.data.edges:
    a,b=e.vertices;edges[a].append(b);edges[b].append(a)
all_orbits=[]
for side,sign in [('R',1),('L',-1)]:
    ids=features['orbit_'+side];rootset=set(features['orbit_root_'+side]);outer=[]
    for i in ids[60:80]:
        match=[j for j in edges[i] if j in rootset];assert len(match)==1;outer.append(match[0])
    all_orbits.append(ids+outer)
    outside=[head.data.vertices[i].co.copy() for i in outer]
    # Redistribute the entire opening into four balanced quadrants. The
    # failed cage crowded five controls into one tiny medial corner, pulling
    # long darts into the brow. This rebuilds the feature parameterization.
    for layer in range(4):
        for j in range(20):
            a=math.radians(225+j*18);q=math.cos(a);s=math.sin(a)
            x=.034+.0187*q
            z=1.6894+.0012*q+(.0068 if s>=0 else .0054)*s
            if layer==1:
                x=.034+(x-.034)*1.026;z=1.6894+(z-1.6894)*1.10
            elif layer==2:
                x=.034+(x-.034)*1.13;z=1.6894+(z-1.6894)*1.48
            if layer<3:
                y=.032+math.sqrt(max(.000001,.023**2-(x-.034)**2-(z-1.690)**2))+[.00065,.00145,.00225][layer]
                point=Vector((sign*x,y,z))
            else:
                body=head.data.vertices[ids[40+j]].co
                point=body*.48+outside[j]*.52
                # A broad anatomical socket plane; it is not globe-shaped.
                upper=point.z>1.694
                medial=abs(point.x)<.025
                point.y=(.059 if upper else .054) if medial else point.y+.001
            head.data.vertices[ids[layer*20+j]].co=point
head['orbital_rings']=json.dumps(all_orbits)
# A short philtrum with continuous volume between nasal base and upper lip.
mouth_ids=features['mouth']
for local,i in enumerate(mouth_ids):
    layer=local//34;p=head.data.vertices[i].co
    if layer>=6 and p.z>1.630 and abs(p.x)<.022:
        influence=max(0,1-(abs(p.x)/.022)**2)
        p.y+=.006*influence
# Explicit upper-nasal sections. The bridge meets a broad nasion and ends in
# a compact rounded tip; it is not an endlessly smoothed vertical ridge.
nose_ids=features['nose']
sections={3:(.014,.080,.066),4:(.012,.075,.062),5:(.0115,.070,.060),6:(.013,.066,.059),7:(.016,.062,.059),8:(.019,.060,.0585)}
for row,(width,center_y,edge_y) in sections.items():
    for j in range(9):
        q=(j-4)/4;i=nose_ids[row*9+j];p=head.data.vertices[i].co
        p.x=width*q;p.y=edge_y+(center_y-edge_y)*(1-abs(q)**1.65)
# Preserve the lower nasal aperture geometry; round the tip's transverse
# shoulders instead of extending the dorsal ridge into a sharp end.
for j in [2,3,4,5,6]:
    p=head.data.vertices[nose_ids[18+j]].co
    p.y+=.0018*(1-abs(j-4)/3)
head.data.update();head['method']='Balanced orbital quadrants with separately authored socket planes, nasal cross-sections and upper-muzzle volume; no hair-family geometry.'
bm=bmesh.new();bm.from_mesh(head.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(head.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','portrait']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/r002_'+label+'.png';bpy.ops.render.render(write_still=True)
print('HP1 orbital construction changed and evaluated in four matched cameras.')
