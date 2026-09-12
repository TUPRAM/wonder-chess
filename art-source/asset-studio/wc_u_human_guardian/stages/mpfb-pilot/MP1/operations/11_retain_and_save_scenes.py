import bpy,json
s=bpy.data.scenes['MP1_ADA_HEAD']
for sc in bpy.data.scenes:sc.use_fake_user=True
bpy.context.window.scene=s
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1/ada_mpfb_work.blend')
bpy.ops.wm.save_as_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1/ada_mpfb_checkpoint_r002_verified.blend',copy=True)
print(json.dumps({'scenes':[(sc.name,sc.users,sc.use_fake_user) for sc in bpy.data.scenes],'work':bpy.data.filepath,'checkpoint':'ada_mpfb_checkpoint_r002_verified.blend','geometry_modified':False},indent=2))
