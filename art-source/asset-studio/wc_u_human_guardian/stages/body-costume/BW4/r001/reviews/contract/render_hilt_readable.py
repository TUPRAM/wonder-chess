"""Correct only diagnostic illumination and label readability; preserve proposal geometry."""
import bpy
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
scene=bpy.context.scene
for name,power in [('Key',5),('Fill',2)]:bpy.data.lights[name].energy=power
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.25
ink=bpy.data.materials['Annotation']
nodes=ink.node_tree.nodes;nodes.clear()
em=nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.018,.025,.03,1);em.inputs['Strength'].default_value=1
out=nodes.new('ShaderNodeOutputMaterial');ink.node_tree.links.new(em.outputs[0],out.inputs[0])
for name in ['Actual_Blade','Proposal_Blade']:bpy.data.objects[name].hide_render=True
for obj in bpy.data.objects:
    if obj.type=='FONT' and 'same scale' in obj.data.body:
        obj.data.body='UNSELECTED | same scale | blade omitted from closeup; blade and guard geometry unchanged'
scene.render.filepath=str(OUT/'actual_vs_unselected_hilt_proposal_review.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_bw4_hilt_proposal_UNSELECTED_REVIEW.blend'))
bpy.ops.render.render(write_still=True)
paths=[OUT/'ada_bw4_hilt_proposal_UNSELECTED_REVIEW.blend',OUT/'actual_vs_unselected_hilt_proposal_review.png',OUT/'hilt_proposal_geometry.json']
(OUT/'hilt_proposal_review_manifest.json').write_text(json.dumps({'status':'UNSELECTED_PROPOSAL',
    'geometry_unchanged_from_initial_proposal':True,'blade_hidden_in_closeup':True,
    'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},indent=2)+'\n',encoding='utf-8')
