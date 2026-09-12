import bpy,json
assert bpy.data.filepath.replace('\\','/').endswith('/live/ada_clay_study_r002.blend')
assert bpy.context.scene.get('as1_operation_id')=='clay-r002-temporal-coverage'
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian'
out=root+'/live/ada_clay_study_r003.blend'
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.wm.save_as_mainfile(filepath=root+'/stages/clay-study/r003/before_region_proof.blend',copy=True)
bpy.context.scene['as1_operation_id']='clay-r003-initialize'
print(json.dumps({'new_live':bpy.data.filepath,'scope':'one eye/socket method mirrored after construction; skull-fitting hair masses','preserved':'r002 disk and r003 before_region_proof include pre-edit session state'}))
