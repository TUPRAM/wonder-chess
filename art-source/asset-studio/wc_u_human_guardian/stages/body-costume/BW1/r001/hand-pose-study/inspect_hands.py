import bpy, json
from pathlib import Path
out=Path(__file__).parent
rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
report={'scenes':[s.name for s in bpy.data.scenes], 'objects':[{'name':o.name,'type':o.type,'hide_render':o.hide_render} for o in bpy.context.scene.objects], 'rig_matrix':[list(r) for r in rig.matrix_world], 'bones':{}}
for b in rig.data.bones:
    if any(t in b.name for t in ('finger','wrist','metacarpal')):
        report['bones'][b.name]={'head':list(rig.matrix_world@b.head_local),'tail':list(rig.matrix_world@b.tail_local),'matrix':[list(r) for r in b.matrix_local],'parent':b.parent.name if b.parent else None}
glove=bpy.data.objects['BW1_Glove_Pair_SourceFit']
report['glove']={'matrix':[list(r) for r in glove.matrix_world],'vertices':len(glove.data.vertices),'modifiers':[(m.name,m.type) for m in glove.modifiers]}
(out/'inspection.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
