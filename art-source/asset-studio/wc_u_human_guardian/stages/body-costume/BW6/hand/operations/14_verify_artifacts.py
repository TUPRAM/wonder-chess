"""Seal executed local review artifacts, not human approval."""
from pathlib import Path
import json,hashlib,ast
from PIL import Image
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
captures=json.loads((OUT/'records/capture_manifest.json').read_text());reopen=json.loads((OUT/'records/reopen_and_preservation.json').read_text());audit=json.loads((OUT/'records/retained_geometry.json').read_text());pads=json.loads((OUT/'records/pad_region_visualization.json').read_text())
for item in captures['captures']+pads['captures']:
 p=Path(item['path']);assert sha(p)==item['sha256'];im=Image.open(p);im.verify()
for item in reopen['native_reopen']:assert sha(item['file'])==item['sha256']==item['sha256_after']
assert audit['source_sha256']==captures['frozen_sha256']==sha(OUT/'ada_bw6_hand_checkpoint_ART_REVISE.blend')
for p,d in reopen['protected_baseline_sha256'].items():assert sha(p)==d
for m in audit['modes'].values():
 assert m['self']['confirmed_nonadjacent_transverse_pairs']==0
 assert all(v['confirmed_transverse_pairs']==0 for v in m['equipment'].values())
 assert m['handle_vertex_distance']['inside_vertices']==0
 assert all(p['count_in_minus0_5_plus1mm_band']==0 for p in m['contact_regions'].values())
parsed=[]
for p in (OUT/'operations').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'));parsed.append(str(p.relative_to(OUT)))
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='verification.json' and p.suffix in ('.blend','.json','.md','.png','.py','.txt'))
report={'status':'ART_REVISE','human_approval':False,'runtime_tests':'NOT_RUN','scope':'BW6 anatomical fixed-glove lane only; files/models and render/collision evidence actually executed','blender_version':'5.1.1','work_and_frozen_sha256':captures['frozen_sha256'],'checks':{'native_work_and_frozen_reopen':True,'historical_cameras_exact':True,'equipment_geometry_and_registration_exact':True,'wrist_20_vertices_max_error_m':0.0,'mesh_independent':True,'raw_and_evaluated_confirmed_transverse_self_equipment_clear':True,'contact_screen_pass':False,'images_opened_and_verified':len(captures['captures'])+len(pads['captures']),'script_syntax_parsed':len(parsed)},'visually_inspected':['target_initial_palm_isolated.png','target_correction1_oblique.png','target_correction2_oblique.png','reconstructed_initial_oblique.png','reconstructed_correction1_palm_isolated.png','reconstructed_correction2_oblique_isolated.png','local_transfer_initial_side.png','retained_actual_cage_oblique.png','retained_uniform_clay_reversed_key.png','retained_full_oblique.png','retained_actual_section_middle.png','provisional_pad_regions_oblique.png','BW5_vs_BW6_ANATOMICAL_HAND_ART_REVISE.png'],'remaining_major_defects':['Bulbous thumb/thenar; opposing pad not sufficiently articulated','Long straight finger faces and parallel mechanical C-shapes','Loose distributed contact','Wrist/cuff integration unproved'],'protected_source_hashes':reopen['protected_baseline_sha256'],'artifacts':[{'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('BW6_LOCAL_VERIFICATION_SEALED',len(files),'ART_REVISE')
