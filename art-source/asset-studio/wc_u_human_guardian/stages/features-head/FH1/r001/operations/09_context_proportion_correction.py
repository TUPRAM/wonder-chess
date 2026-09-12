import bpy,bmesh,json,math
from mathutils import Vector
scene=bpy.data.scenes['FH1_COMBINED_HEAD'];bpy.context.window.scene=scene
old=bpy.data.objects['FH1_Combined_Head_Control_Cage']
assert bpy.data.objects.get('FH1_Combined_Head_Control_Cage_r002') is None
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/combined_initial_checkpoint.blend',copy=True)
head=old.copy();head.data=old.data.copy();head.name='FH1_Combined_Head_Control_Cage_r002';scene.collection.objects.link(head)
old.hide_render=True;old.hide_set(True)
original=[v.co.copy() for v in head.data.vertices]
lookup={tuple(round(c,6) for c in p):i for i,p in enumerate(original)}

def original_match(points):
    return [lookup[tuple(round(c,6) for c in p)] for p in points]

def group_ids(obj,name):
    g=obj.vertex_groups[name].index
    return [v.index for v in obj.data.vertices if any(w.group==g for w in v.groups)]

ears=set(group_ids(head,'Ear_R')+group_ids(head,'Ear_L'))
# Broaden the facial planes across the cheek and forehead. The old parabolic
# frontal arc receded too early at the lateral orbit, exposing the globe.
# This changes original anatomical stations, without projecting a cheek.
for i,p in enumerate(original):
    if i in ears:continue
    x,y,z=p
    if y>-.020 and 1.586<z<1.746:
        u=min(1,abs(x)/.084)
        weight=min(1,(z-1.586)/.017,(1.746-z)/.012,max(0,(y+.020)/.020))
        head.data.vertices[i].co.y+=.078*(u*u-u**4)*weight

# Restrain the nasal projection with the border retained as a shared seam.
nose_source=bpy.data.objects['FH1_Nose_Control_Cage_r002']
nose_ids=original_match([v.co for v in nose_source.data.vertices])
rootset=set(json.loads(nose_source['interface_indices']))
for local,i in enumerate(nose_ids):
    p=head.data.vertices[i].co
    if local not in rootset:p.y=.060+(p.y-.060)*.61
    if p.z<1.652 and local not in rootset:p.z+=.0008

# Raise and advance the subnasal/lip transition gently; preserve contact.
mouth_source=bpy.data.objects['FH1_Mouth_Control_Cage_r002']
mouth_ids=original_match([v.co for v in mouth_source.data.vertices])
for local,i in enumerate(mouth_ids):
    layer=local//34;factor=1 if layer<=5 else .72 if layer==6 else .36 if layer==7 else 0
    p=head.data.vertices[i].co;p.z+=.003*factor;p.y+=.0025*factor

# Reposition the eye opening and guide sphere coherently. Margin/body are
# guide-constrained; outer socket and cheek retain independent geometry.
orbital=orbital_data()
for side,label in [(1,'R'),(-1,'L')]:
    points=[(side*p[0],p[1],p[2]) for p in orbital['vertices']]
    ids=original_match(points)
    for local,i in enumerate(ids):
        layer=local//20;j=local%20;p=head.data.vertices[i].co
        if layer<=2:
            p.x=side*(.034+(abs(original[i].x)-.038)*.91)
            dx=abs(p.x)-.034;dz=p.z-1.690
            clearance=[.0007,.0016,.0027][layer]
            p.y=.032+math.sqrt(max(.000001,.023**2-dx*dx-dz*dz))+clearance
    for j in range(20):
        body=head.data.vertices[ids[40+j]].co;outer=head.data.vertices[ids[80+j]].co
        p=body*.48+outer*.52;p.y+=.001
        head.data.vertices[ids[60+j]].co=p
    globe=bpy.data.objects['FH1_Diagnostic_Eye_'+label]
    globe.location=(side*.034,.032,1.690);globe.scale=(.023/.0245,)*3

# Round the exposed crown/back with explicit cranium depth stations and keep
# the lower mandibular angle distinct from the rear cranium.
for i,p in enumerate(original):
    if p.z>=1.750:
        q=head.data.vertices[i].co
        a=(p.z-1.750)/.0475
        q.y+=.013*max(0,1-a)*max(0,(p.y+.100)/.125)
        if p.z>1.779:q.z-=.003*max(0,(p.z-1.779)/.019)
    if i not in ears and p.y<-.035 and p.z<1.644:
        q=head.data.vertices[i].co;q.y+=.010*max(0,(1.644-p.z)/.065)
head.data.update();head['correction']='Assembly pass 1: independent wider face planes, smaller nasal projection, eased philtrum, coherent eye guides, and rounded crown/occiput.'
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/combined_r002_'+label+'.png';bpy.ops.render.render(write_still=True)
print('Combined pass 1 executed. Topology and all shared interfaces preserved; actual pixel review required.')
