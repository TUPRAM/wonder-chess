"""Compare the saved Cass source revisions outside the explicitly replaced face layers."""
import hashlib,json,sys
from pathlib import Path
import bpy

ROOT=Path('C:/Users/iputu/Documents/Wonder Chess')
OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants

def signature(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    ob=bpy.data.objects['SK_wc_u_human_warrior']
    colors={}
    for p in ob.data.polygons:
        uv=ob.data.uv_layers.active.data[p.loop_start].uv
        for i in p.vertices:colors[i]=int(uv.x*4)+4*int(uv.y*4)
    # These are the intentionally replaced eye/lid/brow surfaces only.
    replaced=set()
    for c in components(ob):
        if c['groups']==['head']:
            palette=colors[c['indices'][0]]
            if (palette in (8,9,15) and 1.66<c['center_m'][2]<1.71) or (palette in (7,1) and 1.72<c['center_m'][2]<1.75) or (palette==6 and c['count']<60 and 1.66<c['center_m'][2]<1.71):
                replaced.update(c['indices'])
    verts=[]
    for v in ob.data.vertices:
        if v.index in replaced:continue
        weights=sorted((ob.vertex_groups[g.group].name,round(g.weight,7)) for g in v.groups)
        verts.append((tuple(round(x,7) for x in v.co),colors[v.index],weights))
    payload=json.dumps(sorted(verts),sort_keys=True)
    return {'retained_vertex_count':len(verts),'retained_vertices_coordinates_colors_weights_sha256':hashlib.sha256(payload.encode()).hexdigest(),'invariants':invariants(bpy.data.objects['Armature'])}

before=signature(OUT/'candidate5-v2/before.blend')
after=signature(ROOT/'art-source/heroes/wc_u_human_warrior/wc_u_human_warrior.blend')
report={'status':'PASS' if before==after else 'FAIL','before':before,'after':after,'boundary':'All retained vertex coordinates, UV swatch identities and bone weights; skeleton and seven action curves. Eye/lid/brow layers explicitly excluded.'}
(OUT/'preserved-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
assert before==after,report
print(json.dumps(report))
