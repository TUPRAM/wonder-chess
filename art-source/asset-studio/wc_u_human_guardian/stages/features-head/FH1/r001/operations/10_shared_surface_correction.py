import bpy,bmesh,json,math
from mathutils import Vector
scene=bpy.data.scenes['FH1_COMBINED_HEAD'];bpy.context.window.scene=scene
old=bpy.data.objects['FH1_Combined_Head_Control_Cage_r002'];initial=bpy.data.objects['FH1_Combined_Head_Control_Cage']
assert bpy.data.objects.get('FH1_Combined_Head_Control_Cage_r003') is None
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/combined_r002_checkpoint.blend',copy=True)
head=old.copy();head.data=old.data.copy();head.name='FH1_Combined_Head_Control_Cage_r003';scene.collection.objects.link(head)
old.hide_render=True;old.hide_set(True)
lookup={tuple(round(c,6) for c in v.co):v.index for v in initial.data.vertices}

def mapped(points):return [lookup[tuple(round(c,6) for c in p)] for p in points]
def group_ids(name):
    g=head.vertex_groups[name].index
    return {v.index for v in head.data.vertices if any(w.group==g for w in v.groups)}
ears=group_ids('Ear_L')|group_ids('Ear_R');mouth=group_ids('Mouth');nose=group_ids('Nose')
# Cheek crest is independent of the globe. Reduce the swollen horizontal
# under-eye shelf with a compact broad cheek plane, preserving lid margins.
orbit_inner=set()
orbital=orbital_data();orbit_lists=[]
for side in [1,-1]:
    ids=mapped([(side*p[0],p[1],p[2]) for p in orbital['vertices']]);orbit_lists.append(ids);orbit_inner.update(ids[:60])
for v in head.data.vertices:
    x,y,z=v.co
    if v.index not in ears|nose|mouth|orbit_inner and y>-.005 and .022<abs(x)<.071 and 1.652<z<1.693:
        tz=max(0,1-abs(z-1.671)/.022);tx=min(1,(abs(x)-.022)/.013,(.071-abs(x))/.013)
        v.co.y-=.009*tz*tx
# Set medial socket transition controls deliberately toward the nasal root;
# no globe projection or smoothing of the surrounding cheek.
for ids in orbit_lists:
    for j in range(20):
        v=head.data.vertices[ids[60+j]];p=v.co
        if abs(p.x)<.030:
            p.y+=.0055
        elif p.z>1.699:
            p.y+=.002
        elif p.z<1.681:
            p.y-=.002
    # The outer medial seam follows a gentle root plane across its height.
    for j in range(15,20):
        v=head.data.vertices[ids[80+j]]
        v.co.y=.0605 if v.co.z>1.69 else .059

# Use a smooth ellipsoidal cranium above the forehead station; feature and
# facial geometry are excluded. The section matches the existing brow-level
# envelope and removes the angular peak/back break in diagnostic profile.
for v in head.data.vertices:
    x,y,z=v.co
    if z>1.732:
        z0=min(z,1.7945)
        a=math.atan2((y+.025)/.090,x/.086)
        radius=math.sqrt(max(.00001,1-((z0-1.690)/.105)**2))
        v.co.x=.086*radius*math.cos(a);v.co.y=-.025+.090*radius*math.sin(a);v.co.z=z0
    if v.index not in ears|mouth and 1.575<z<1.640:
        taper=.09*max(0,1-abs(z-1.603)/.040)
        v.co.x*=1-taper

# Non-faceted diagnostic gaze, produced by a shader on the smooth globe.
gaze=bpy.data.materials.new('FH1_Diagnostic_Gaze');gaze.use_nodes=True
n=gaze.node_tree.nodes;n.clear();links=gaze.node_tree.links
out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.55
tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');links.new(tex.outputs['Generated'],sep.inputs[0])
dx=n.new('ShaderNodeMath');dx.operation='SUBTRACT';dx.inputs[1].default_value=.5;links.new(sep.outputs['X'],dx.inputs[0])
dz=n.new('ShaderNodeMath');dz.operation='SUBTRACT';dz.inputs[1].default_value=.5;links.new(sep.outputs['Z'],dz.inputs[0])
x2=n.new('ShaderNodeMath');x2.operation='MULTIPLY';links.new(dx.outputs[0],x2.inputs[0]);links.new(dx.outputs[0],x2.inputs[1])
z2=n.new('ShaderNodeMath');z2.operation='MULTIPLY';links.new(dz.outputs[0],z2.inputs[0]);links.new(dz.outputs[0],z2.inputs[1])
add=n.new('ShaderNodeMath');add.operation='ADD';links.new(x2.outputs[0],add.inputs[0]);links.new(z2.outputs[0],add.inputs[1])
iris=n.new('ShaderNodeMath');iris.operation='LESS_THAN';iris.inputs[1].default_value=(.0082/.049)**2;links.new(add.outputs[0],iris.inputs[0])
pupil=n.new('ShaderNodeMath');pupil.operation='LESS_THAN';pupil.inputs[1].default_value=(.0035/.049)**2;links.new(add.outputs[0],pupil.inputs[0])
mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.55,.55,.52,1);mix.inputs[2].default_value=(.09,.045,.015,1);links.new(iris.outputs[0],mix.inputs[0])
pm=n.new('ShaderNodeMixRGB');pm.inputs[2].default_value=(.006,.006,.006,1);links.new(pupil.outputs[0],pm.inputs[0]);links.new(mix.outputs[0],pm.inputs[1]);links.new(pm.outputs[0],bs.inputs['Base Color']);links.new(bs.outputs[0],out.inputs[0])
for label in ['R','L']:
    eye=bpy.data.objects['FH1_Diagnostic_Eye_'+label];eye.data.materials.clear();eye.data.materials.append(gaze)
    for p in eye.data.polygons:p.material_index=0
head.data.update();head['correction']='Assembly pass 2: medial socket/root transition controls, independent lower cheek planes, tapered lower jaw, and smooth crown sections. Shared topology retained.'
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render])
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter','underside']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/combined_r003_'+label+'.png';bpy.ops.render.render(write_still=True)
print('Shared surface correction pass 2 executed; source remains editable. Review required.')
