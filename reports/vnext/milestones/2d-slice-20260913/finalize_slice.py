"""Record actual first-slice results and prepare the owner-facing launcher handoff."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
from PIL import Image
root=Path(__file__).resolve().parents[4]
ev=root/'reports/vnext/milestones/2d-slice-20260913'
art=root/'art-source/2d-slice/r001'
support=Path('C:/Users/iputu/Documents/Project Support/Wonder Chess')
load=lambda p:json.loads(Path(p).read_bytes())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
graphics=load(ev/'r15-graphics-a1.json')
assert len(graphics)==6 and all(x['passed'] for x in graphics)
package=load(ev/'package-verify.json'); assert package['status']=='PASS'
automation=load(ev/'r15-engine-contracts/automation/index.json')
assert automation['succeeded']==2 and automation['failed']==0
rules=load(ev/'rules-preserved.json');assert rules['all_unchanged']
authoring=load(ev/'authoring-checks-r2.json');assert all(x['exit_code']==0 for x in authoring)
exe=root/'builds/WonderChess-2DSlice-r15/Windows/WonderChess/Binaries/Win64/WonderChess.exe'
runtime_log=(ev/'r15-lab-720-a1/engine.log').read_text(errors='replace')
assert 'portrait_size=1024x1024' in runtime_log and 'heavy_bloom_size=512x512' in runtime_log
assert 'size=1024x1024 material=1' in runtime_log
staged=[]
for name,size in [('bellback_portrait.png',1024),('heavy_bloom.png',512),('quiet_stone.png',1024)]:
 p=art/'sources'/name
 with Image.open(p) as im:
  staged.append(dict(path=p.relative_to(root).as_posix(),sha256=sha(p),bytes=p.stat().st_size,
                     source_size=list(im.size),source_mode=im.mode,cooked_size=[size,size],opaque=True))
refs=[
 'art-source/2d-style/r001/ref01_materials_and_shape_language.png',
 'art-source/2d-style/r001/ref03_icons_portraits_and_relic_language.png',
 'art-source/asset-studio/wc_vn_bellback/inputs/references/r001/bellback_reference_candidate.png',
 'art-source/asset-studio/wc_vn_bellback/inputs/references/r004_construction/construction_spec.json',
]
sources=[
 'game/Source/WonderChessRuntime/Public/WCVNextArtStyle.h',
 'game/Source/WonderChessRuntime/Private/WCVNextArtStyle.cpp',
 'game/Source/WonderChessRuntime/Public/WCVNextLab.h',
 'game/Source/WonderChessRuntime/Private/WCVNextLab.cpp',
 'game/Source/WonderChessRuntime/Private/WCVNextSolo.cpp',
 'game/Source/WonderChessRuntime/Private/WCVNextCombatPresentation.cpp',
 'tools/unreal/import_art_slice.py','tools/unreal/launch_milestones.ps1',
]
manifest=dict(schema='wonder_vnext.2d_slice_candidate.1',asset_id='wc_vn_2d_slice_r001',
 status='PACKAGED_STUDY_PENDING_OWNER_REVIEW',owner_authorization='Execute the bounded first integrated slice; larger set remains conditional on its review.',
 formal_gate_acceptance='NONE_SELF_ISSUED',kind='ui_environment_vfx_study',
 generated_with='built_in_image_gen',external_paid_service=False,third_party_assets_downloaded=False,
 sources=staged,references=[dict(path=p,sha256=sha(root/p)) for p in refs],
 prompts=[dict(path=p.relative_to(root).as_posix(),sha256=sha(p)) for p in sorted((art/'inputs').glob('*.txt'))],
 native_authored_sources=[dict(path=p,sha256=sha(root/p)) for p in sources],
 rejected=[dict(path='sources/heavy_bloom_rejected_checkerboard.png',reason='RGB painted checkerboard; no transparency. Never imported.',sha256=sha(art/'sources/heavy_bloom_rejected_checkerboard.png'))],
 limitations=['Bellback portrait is a cropped identity study; modeled forms remain ART_REVISE.',
              'Sources are opaque RGB; no transparent or layered export is claimed.',
              'Exact seamless texture production and final-content performance are not certified.',
              'World effect components are native geometry, not authored sprite animation frames.'])
(art/'asset_manifest_candidate.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
verify=dict(schema='wonder_vnext.2d_slice_verification.1',utc=datetime.now(timezone.utc).isoformat(),
 status='PASS_SCOPED_PACKAGE_OWNER_ART_REVIEW_OPEN',candidate='WonderChess-2DSlice-r15',
 package=str(exe),game_binary_sha256=sha(exe),baseline='Preserved WonderChess-CombatClarity-r13',
 artwork=staged,graphics=[dict(case=x['case'],passed=x['passed'],boolean_checks=len(x['checks'])) for x in graphics],
 python_tests=230,authoring_checks=400,required_generation_checks='PASS',package_identity=package,
 engine_contracts=dict(succeeded=2,failed=0,combat_clarity_assertions=2929,mana_assertions=581),
 gameplay_code_and_data_preserved=rules,
 manual_input=dict(r14='Actual pointer pause, three Bellback purchases, live owned/merge feedback, gold 10 to 7 and automatic 2-star bench merge observed. Found and preserved focus overlay defect.',
 r15='Source fix compiled and packaged; final actual pointer/keyboard focus recheck NOT_RUN after user stopped Computer Use with Escape.',
 r15_launch='Launcher invoked; engine log confirms READY, all artwork loaded, and correct combat-clarity digest. Screen control stopped before capture.'),
 visual_review=dict(r15='Root and separate reviewer inspected packaged Lab720 and status1080 captures. Contrast revision resolves pale semantic cues; no further new screenshot defect found requiring another revision before owner review.',
 limit='Screenshot review does not certify continuous animation, human enjoyment or final modeled identity.'),
 remaining=['Owner review of integrated style at actual play size.','Final r15 physical keyboard-focus/purchase visual recheck interrupted.',
 'Existing thin grid-line speckling in combat predates slice.','Final character forms, full artwork production, pacing acceptance and release gates remain open.'],
 failed_attempts=['Heavy Bloom first output painted checkerboard; rejected and revised to opaque ink.',
 'Initial compile name-shadowing and narrowing errors fixed.',
 'Initial Python child invocation selected Unreal Python without Pillow; rerun with exact authoring interpreter passed.',
 'r14 Lab HUD check ran before first presentation update; moved identical check after settled capture.',
 'r14 manual focus overlay white fill fixed with explicit transparent tint in r15; physical r15 recheck interrupted.'])
(ev/'verification.json').write_text(json.dumps(verify,indent=2)+'\n',encoding='utf-8')
(art/'state.json').write_text(json.dumps(dict(status=verify['status'],candidate=verify['candidate'],human_art_approval='PENDING',larger_batch='NOT_STARTED',verification='../../../reports/vnext/milestones/2d-slice-20260913/verification.json'),indent=2)+'\n',encoding='utf-8')
# Keep prior launch paths usable and expose the comparison without changing r13.
script=str(root/'tools/unreal/launch_milestones.ps1')
for mode in ['Lab','Solo']:
 live=support/f'Play Combat Clarity - {mode}.cmd'
 comparison=support/f'Play Combat Clarity r13 - {mode}.cmd'
 if not comparison.exists() and live.exists():shutil.copy2(live,comparison)
 body='@echo off\r\npowershell -NoProfile -ExecutionPolicy Bypass -File "'+script+'" -Mode '+mode+' -ArtSlice\r\nif errorlevel 1 pause\r\n'
 live.write_bytes(body.encode('utf-8'))
 (support/f'Play 2D Art Slice - {mode}.cmd').write_bytes(body.encode('utf-8'))
 for p in [live,support/f'Play 2D Art Slice - {mode}.cmd']:
  assert '-ArtSlice' in p.read_text() and script in p.read_text()
verify['launchers']=[dict(path=str(support/f'Play Combat Clarity - {mode}.cmd'),sha256=sha(support/f'Play Combat Clarity - {mode}.cmd')) for mode in ['Lab','Solo']]
(ev/'verification.json').write_text(json.dumps(verify,indent=2)+'\n',encoding='utf-8')
ledger=root/'reports/implementation_state.json'
state=load(ledger);state['vnext_2d_asset_slice']=verify
ledger.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(status=verify['status'],game_binary_sha256=verify['game_binary_sha256'],graphics=verify['graphics'],launchers=verify['launchers']),indent=2))

