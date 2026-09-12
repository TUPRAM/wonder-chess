"""Reopen the separate proposal and compare its geometry to the explicit source record."""
import bpy
import hashlib
import json
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent
source=json.loads((OUT/'actual_hilt_and_bind.json').read_text())
proposal=json.loads((OUT/'hilt_proposal_geometry.json').read_text())
parts={p['identified_part']:p for p in source['sword_components']}
checks={}
for variant in ['Actual','Proposal']:
    for name,p in parts.items():
        expected=proposal['proposed']['world_vertices_m'] if variant=='Proposal' and name=='handle' else p['world_vertices_m']
        obj=bpy.data.objects[variant+'_'+name.title()]
        error=max((v.co-Vector(e)).length for v,e in zip(obj.data.vertices,expected))
        checks[obj.name]={'vertex_count':len(obj.data.vertices),'max_raw_coordinate_error_m':error,
          'independent_mesh':obj.data.users==1,'pass':error<1e-7 and len(obj.data.vertices)==len(expected)}
        assert checks[obj.name]['pass']
assert hashlib.sha256(Path(source['source']).read_bytes()).hexdigest()==source['source_sha256']
record={'status':'REOPENED_UNSELECTED_PROPOSAL_GEOMETRY_VERIFIED', 'blender_version':bpy.app.version_string,
 'reopened_file':bpy.data.filepath,'checks':checks,'canonical_source_preserved':True,
 'human_approval':False,'hand_fitting_executed':False,'source_saved':False}
(OUT/'hilt_proposal_reopen.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
