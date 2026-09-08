import bpy,json
s=bpy.context.scene
ed=s.sequence_editor_create()
print('WC_ENCODER_PROBE '+json.dumps({'blender':bpy.app.version_string,'has_strips':hasattr(ed,'strips'),'has_sequences':hasattr(ed,'sequences'),'strip_properties':list(ed.bl_rna.properties.keys()),'ffmpeg_formats':[x.identifier for x in s.render.ffmpeg.bl_rna.properties['format'].enum_items]}))
