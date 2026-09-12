import bpy,json
assert bpy.context.scene.name=='MR1_FACE_PROOF'
bpy.data.objects['MR1_FACE_Key'].data.energy=.65
bpy.data.objects['MR1_FACE_Fill'].data.energy=.16
globe=bpy.data.objects['MR1_Right_Eye_Globe']
mat=bpy.data.materials.new('MR1_Gaze_Diagnostic_Shader');mat.use_nodes=True
nt=mat.node_tree;n=nt.nodes;l=nt.links;bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.5
tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Generated'],sep.inputs[0])
def mathnode(op,a,b=None):
    o=n.new('ShaderNodeMath');o.operation=op
    if hasattr(a,'node'):l.new(a,o.inputs[0])
    else:o.inputs[0].default_value=a
    if b is not None:
        if hasattr(b,'node'):l.new(b,o.inputs[1])
        else:o.inputs[1].default_value=b
    return o.outputs[0]
x=mathnode('SUBTRACT',sep.outputs['X'],.5);z=mathnode('SUBTRACT',sep.outputs['Z'],.5)
r2=mathnode('ADD',mathnode('MULTIPLY',x,x),mathnode('MULTIPLY',z,z))
front=mathnode('GREATER_THAN',sep.outputs['Y'],.5)
im=mathnode('MULTIPLY',mathnode('LESS_THAN',r2,.0308),front)
pm=mathnode('MULTIPLY',mathnode('LESS_THAN',r2,.0049),front)
mix=n.new('ShaderNodeMixRGB');l.new(im,mix.inputs[0]);mix.inputs[1].default_value=(.67,.67,.64,1);mix.inputs[2].default_value=(.09,.045,.015,1)
mix2=n.new('ShaderNodeMixRGB');l.new(pm,mix2.inputs[0]);l.new(mix.outputs[0],mix2.inputs[1]);mix2.inputs[2].default_value=(.006,.006,.006,1)
l.new(mix2.outputs[0],bs.inputs['Base Color'])
globe.data.materials.clear();globe.data.materials.append(mat)
for f in globe.data.polygons:f.material_index=0
scene=bpy.context.scene;scene.camera=bpy.data.objects['MR1_FACE_three_quarter']
scene.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001/captures/face_calibrated_three_quarter.png'
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Review light calibration and unembossed diagnostic shader executed; cage geometry unchanged.')

