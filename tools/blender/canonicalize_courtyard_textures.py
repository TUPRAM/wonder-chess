"""Correct existing-scene image name collisions without changing geometry."""
import bpy
from pathlib import Path
import shutil
import json
import hashlib
root=Path(__file__).resolve().parents[2];out=root/'exports/arena'
for suffix in ('BaseColor','Normal','ORM'):
    name=f'T_wc_seven_lantern_courtyard_{suffix}'
    corrected=out/(name+'.001.png');canonical=out/(name+'.png')
    if not corrected.is_file():raise FileNotFoundError(corrected)
    shutil.copy2(corrected,canonical)
    for image in bpy.data.images:
        if Path(bpy.path.abspath(image.filepath)).name in (corrected.name,canonical.name):
            image.filepath=str(canonical);image.reload()
    for folder in out.glob('*.fbm'):shutil.copy2(canonical,folder/canonical.name)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
manifest=out/'arena_manifest.json';record=json.loads(manifest.read_text())
record['canonical_texture_files']=[f'T_wc_seven_lantern_courtyard_{suffix}.png' for suffix in ('BaseColor','Normal','ORM')]
record['source_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
record['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='arena_manifest.json'}
manifest.write_text(json.dumps(record,indent=2)+'\n')
print('WC_CANONICAL_ARENA_TEXTURES_STABLE',flush=True)
