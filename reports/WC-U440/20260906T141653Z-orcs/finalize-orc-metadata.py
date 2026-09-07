import hashlib,json
from pathlib import Path
root=Path.cwd();base=root/'reports/WC-U440/20260906T141653Z-orcs'
entries={'wc_u_orc_warrior':base/'rok-candidate02/workbench-review','wc_u_orc_mage':base/'zura-candidate02/workbench-fitted','wc_u_orc_rogue':base/'kesh-contact03/workbench-review'}
for uid,out in entries.items():
    path=root/f'exports/heroes/{uid}/export_manifest.json';manifest=json.loads(path.read_text());refined=json.loads((out/'refinement.json').read_text());result=json.loads((out/'export-result.json').read_text())
    manifest['open_reviews']=['Current Unreal source revision and reimport','Continuous in-engine seven-clip review','Crowded-board weapon and costume readability','LOD silhouette review','Skill release and audio alignment','Final facial and costume art acceptance']
    manifest['geometry_review_evidence']=out.relative_to(root).as_posix()
    manifest['animation_update_changes']=refined.get('animation_changes',[])
    if manifest['animation_update_changes']:
        manifest['animation_revision']=7
        manifest['animation_update_script_sha256']=refined['contact_correction_script_sha256']
        manifest['clips']['Move']['measured_support_correction']=manifest['animation_update_changes'][0]
    if (out/'portrait-framing.json').is_file():manifest['portrait_framing']=json.loads((out/'portrait-framing.json').read_text())
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    result['manifest_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();result['animations_modified_by_refinement']=[x['clip'] for x in manifest['animation_update_changes']]
    (out/'export-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(uid,manifest['source_revision'],manifest['animation_revision'],manifest['triangles'],result['manifest_sha256'])
