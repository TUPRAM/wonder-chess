import bpy
s=bpy.data.scenes['MP1_ADA_HEAD'];bpy.context.window.scene=s
for side in ['R','L']:
    eye=bpy.data.objects['MP1_Eye_'+side];eye.data.materials.clear();eye.data.materials.append(bpy.data.materials['MP1_Uniform_Clay'])
for label in ['front','profile','three_quarter','primary_fit']:
    s.camera=bpy.data.objects['HP1_HEAD_POLISH_'+label];s.render.resolution_x=840 if label=='primary_fit' else 900;s.render.resolution_y=788 if label=='primary_fit' else 900;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/mpfb-pilot/MP1/captures/final_clay_'+label+'.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['HP1_HEAD_POLISH_three_quarter'];s.render.resolution_x=900;s.render.resolution_y=900
