import bpy,json
from mathutils import Vector
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
sc=bpy.data.scenes['MR1_HAIR_PROOF'];bpy.context.window.scene=sc
assert sc['mr1_hair_corrections']==0
bpy.ops.wm.save_as_mainfile(filepath=root+'/hair_before_correction_01.blend',copy=True)
o=bpy.data.objects['MR1_HAIR_CONTEXT_ADA_Hair_Foundation']
# Recess the inherited front-temple foundation lip under the unchanged sweep.
# Four existing scalp rows share a graded contact correction, not a hair projection.
deltas=[]
weights={3469:.2,3470:.5,3471:.8,3472:1,3473:1,3474:.9,3475:.7,3476:.5,3477:.3,3478:.1}
for end,w in weights.items():
    for row,fade in [(0,1),(1,.75),(2,.40),(3,.12)]:
        idx=end-row*96;v=o.data.vertices[idx];before=list(v.co);v.co+=Vector((-.002,-.007,.001))*w*fade;deltas.append({'i':idx,'before':before,'after':list(v.co)})
o.data.update();o['mr1_contact_correction']=json.dumps(deltas)
sc['mr1_hair_corrections']=1;sc['mr1_operation']='hair_correction_01_candidate_foundation_temple_contact'
for v in ['front','profile','three_quarter','rear','top','root']:
    sc.camera=bpy.data.objects['MR1_HAIR_'+v];sc.render.filepath=root+'/captures/hair_r002_clay_'+v+'.png';bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['MR1_HAIR_three_quarter']
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.wm.save_as_mainfile(filepath=root+'/hair_mass_proof_r002.blend',copy=True)
print(json.dumps({'changed_object':o.name,'changed_vertices':len(deltas),'hair_clump_geometry_changed':False,'correction_pass':1}))
