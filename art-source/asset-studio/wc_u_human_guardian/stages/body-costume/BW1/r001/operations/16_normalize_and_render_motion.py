import bpy,json
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];s.frame_set(13)
observations={}
for name in ['BW1_Glove_Pair_SourceFit','BW1_Boot_Pair_SourceFit']:
    ob=bpy.data.objects[name];before=[v.co.copy() for v in ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    bonegroups={g.index:g for g in ob.vertex_groups if g.name in rig.data.bones}
    sums=[];adjusted=0
    for v in ob.data.vertices:
        weights=[(bonegroups[g.group],g.weight) for g in v.groups if g.group in bonegroups]
        total=sum(w for g,w in weights);sums.append(total)
        if total>0 and abs(total-1)>.00001:
            for group,w in weights:group.add([v.index],w/total,'REPLACE')
            adjusted+=1
    bpy.context.view_layer.update()
    after=[v.co.copy() for v in ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    observations[name]={'prior_max_raw_sum':max(sums),'normalized_vertices':adjusted,'posed_max_local_vertex_delta':max((a-b).length for a,b in zip(before,after))}
s['BW1_weight_normalization_observations']=json.dumps(observations);s.frame_set(1)
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG'
s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='MEDIUM'
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/BW1_motion_diagnostic_ART_REVISE.mp4'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps(observations))
bpy.ops.render.render(animation=True)
s.frame_set(1)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
s.render.engine='CYCLES';s.render.resolution_x=850;s.render.resolution_y=1100
print('169-frame diagnostic movie rendered; returned to A pose and clay still setup')
