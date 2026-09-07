"""Remove duplicate roof-ridge faces observed in the independently imported low LOD."""
import bpy,bmesh,json,hashlib,shutil,sys
from pathlib import Path
ROOT=Path('C:/Users/iputu/Documents/Wonder Chess');OUT=ROOT/'exports/lobby';SOURCE=ROOT/'art-source/lobby/brighthaven_approach.blend'
sys.path.insert(0,str(ROOT/'tools/blender'))
from author_alpha import export_fbx_raw
from normalized_fbx import export_normalized_copy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OUT/'lobby_manifest.json').read_text());assert m['source_revision']==3 and sha(SOURCE)==m['source_sha256']
archive=OUT/'review/revision3';archive.mkdir(exist_ok=False)
for p in (SOURCE,OUT/'lobby_manifest.json',OUT/'SM_WC_BrighthavenApproach_LOD2.fbx'):shutil.copy2(p,archive/p.name)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));ob=bpy.data.objects['SM_WC_BrighthavenApproach_LOD2'];bm=bmesh.new();bm.from_mesh(ob.data);seen=set();duplicates=[]
for face in bm.faces:
    key=tuple(sorted(tuple(round(x,5) for x in v.co) for v in face.verts))
    if key in seen:duplicates.append(face)
    seen.add(key)
assert duplicates,'Expected diagnosed duplicate ridge faces'
bmesh.ops.delete(bm,geom=duplicates,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles();export_normalized_copy(OUT/(ob.name+'.fbx'),[ob],False,export_fbx_raw)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),check_existing=False);m['source_sha256']=sha(SOURCE);m['source_revision']=4;m['prior_candidate']=str(archive);m['lods'][2]['triangles']=len(ob.data.loop_triangles);m['refinement_script_sha256']=sha(Path(__file__));m['files'][ob.name+'.fbx']=sha(OUT/(ob.name+'.fbx'))
(OUT/'lobby_manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('REMOVED_DUPLICATE_LOD_FACES',len(duplicates),'TRIANGLES',len(ob.data.loop_triangles))
