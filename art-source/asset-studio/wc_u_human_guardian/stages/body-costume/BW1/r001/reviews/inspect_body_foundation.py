"""Read immutable BW1 audit snapshot; all writes are JSON evidence only."""
import bpy, json, math, hashlib
from pathlib import Path
import numpy as np
OUT=Path(r'C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/reviews/body_snapshot_inventory.json')
def custom(o):
    result={}
    for k in o.keys():
        try: result[k]=o[k].to_list() if hasattr(o[k],'to_list') else o[k]
        except Exception: result[k]=str(o[k])
    return result
out={'file':bpy.data.filepath,'scenes':[{'name':s.name,'properties':custom(s),'objects':list(s.objects.keys())} for s in bpy.data.scenes], 'objects':[]}
for o in bpy.data.objects:
    if o.type not in ('MESH','ARMATURE'): continue
    r={'name':o.name,'type':o.type,'data':o.data.name,'properties':custom(o),'matrix_world':[list(row) for row in o.matrix_world],'dimensions':list(o.dimensions)}
    if o.type=='MESH':
        r.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),groups=list(o.vertex_groups.keys()),attributes=[{'name':a.name,'type':a.data_type,'domain':a.domain} for a in o.data.attributes], modifiers=[{'name':m.name,'type':m.type,'visible':m.show_viewport,'render':m.show_render,'group':m.vertex_group if m.type=='MASK' else None} for m in o.modifiers],shape_keys=[{'name':k.name,'value':k.value} for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [])
    else:
        r['bones']=[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None,'matrix':[list(row) for row in b.matrix_local]} for b in o.data.bones]
    out['objects'].append(r)
OUT.write_text(json.dumps(out,indent=2,default=str)+'\n')
print(json.dumps({'file':out['file'],'scene_names':[s['name'] for s in out['scenes']],'meshes':[(o['name'],o.get('vertices'),len(o.get('shape_keys',[]))) for o in out['objects'] if o['type']=='MESH'],'rigs':[(o['name'],len(o['bones'])) for o in out['objects'] if o['type']=='ARMATURE'],'scene_props':[{s['name']:s['properties']} for s in out['scenes'] if s['name'].startswith('BW1')]},indent=2,default=str))
