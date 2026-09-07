"""Restore the canonical LOD source collection without changing any asset bytes."""
import argparse,json,shutil,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from author_update_pippa import sha,write
from refine_update_ada import invariants,mesh_geometry_digest
UID='wc_u_dragonkin_guardian'
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve()
if report.exists() or not report.is_relative_to((ROOT/'reports').resolve()):raise ValueError('Fresh report required')
report.mkdir(parents=True);out=ROOT/'exports/heroes'/UID;source=ROOT/'art-source/heroes'/UID/(UID+'.blend')
m=json.loads((out/'export_manifest.json').read_text());assert m['source_revision']==6 and sha(source)==m['source_sha256']
shutil.copy2(source,report/'before-source.blend');shutil.copy2(out/'export_manifest.json',report/'before-manifest.json')
(report/'executed-repair.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];before=invariants(arm);geometry=mesh_geometry_digest()
collection=bpy.data.collections['LOD_SOURCE'];moved=[]
for level in (1,2):
    obj=bpy.data.objects[f'SK_{UID}_LOD{level}'];previous=[c.name for c in obj.users_collection]
    if obj.name not in collection.objects:collection.objects.link(obj)
    for other in list(obj.users_collection):
        if other!=collection:other.objects.unlink(obj)
    moved.append(dict(object=obj.name,old_collections=previous,new_collection=collection.name))
assert len([o for o in collection.objects if o.type=='MESH'])==2
assert invariants(arm)==before and mesh_geometry_digest()==geometry
bpy.ops.wm.save_as_mainfile(filepath=str(source))
assert all(sha(out/name)==value for name,value in m['files'].items())
updated=dict(m);updated.update(source_revision=7,source_sha256=sha(source),
    source_organization_script_sha256=sha(__file__),source_organization_evidence=str(report.relative_to(ROOT)))
write(out/'export_manifest.json',updated)
write(report/'repair.json',dict(status='SOURCE_COLLECTION_REPAIR_EXECUTED',source_before_sha256=m['source_sha256'],
    source_after_sha256=updated['source_sha256'],moved=moved,exact_geometry_digest=geometry,
    preserved_invariants=before,verified_candidate_invariants=invariants(arm),all_14_export_bytes_unchanged=True,
    visual_evidence_directory=m['report_directory'],boundary='Source collection organization only; geometry, rig, actions and export bytes unchanged'))
print('WC_SORA_LOD_COLLECTION_REPAIRED '+updated['source_sha256'],flush=True)
