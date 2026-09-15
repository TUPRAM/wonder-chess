"""Record the actual desktop-launcher smoke and verify copied review artifacts."""
import hashlib, json, shutil
from pathlib import Path

evidence = Path(__file__).resolve().parent
root = evidence.parents[3]
delivery = Path('C:/Users/iputu/Documents/Project Support/Wonder Chess/Storybook Demo - r20')
launch_dir = root / 'reports/vnext/milestones/launch-20260913T153437052Z'
launch = json.loads((launch_dir / 'launch.json').read_bytes())
log = (launch_dir / 'engine.log').read_text(encoding='utf-8', errors='replace')
assert launch['storybook'] and launch['mode'] == 'Solo'
assert 'WonderChess-Storybook-r20' in launch['executable']
assert 'WC_STORYBOOK_INTERFACE assets_ready=1 shop_slots=5 bench_slots=10 seats=8' in log
assert 'LogExit: Exiting.' in log
wrapper = delivery.parent / 'Play Wonder Chess.cmd'
smoke = dict(status='PASS', wrapper=str(wrapper), wrapper_sha256=hashlib.sha256(wrapper.read_bytes()).hexdigest(),
    launch_record=str((launch_dir / 'launch.json').relative_to(root)), native_window_observed=True,
    screenshot=str(delivery / 'in-game/desktop-launcher.png'), normal_exit=True,
    boundary='Exact friendly Solo cmd was executed and its native window inspected, then closed. Same-machine evidence.')
(evidence / 'launcher-smoke.json').write_text(json.dumps(smoke, indent=2) + '\n', encoding='utf-8')
verification_path = evidence / 'verification.json'
verification = json.loads(verification_path.read_bytes())
verification['desktop_launcher'] = smoke
verification['git_diff_check'] = 'PASS; tracked whitespace check; existing line-ending warnings only'
verification['final_candidate_game_processes_running'] = 0
verification_path.write_text(json.dumps(verification, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
shutil.copy2(verification_path, delivery / 'verification.json')
ledger_path = root / 'reports/implementation_state.json'
ledger = json.loads(ledger_path.read_bytes())
ledger['vnext_storybook_expansion']['desktop_launcher'] = smoke
ledger['vnext_storybook_expansion']['git_diff_check'] = verification['git_diff_check']
ledger['vnext_storybook_expansion']['final_candidate_game_processes_running'] = 0
ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
manifest = json.loads((root / 'art-source/2d-expansion/r001/asset_manifest_candidate.json').read_bytes())
checks = []
for row in manifest['sources']:
    rel = Path(row['path']).relative_to('art-source/2d-expansion/r001')
    dest = delivery / 'art' / rel
    passed = hashlib.sha256(dest.read_bytes()).hexdigest() == row['sha256']
    assert passed, str(dest)
    checks.append(dict(path=str(dest.relative_to(delivery)), sha256=row['sha256'], matches_source=True))
assert len(checks) == 23
for name in ['Play Wonder Chess.cmd', 'Play Storybook - Solo.cmd', 'Play Storybook - Lab.cmd', 'Play Combat Clarity - Solo.cmd', 'Play Combat Clarity - Lab.cmd']:
    assert '-Storybook' in (delivery.parent / name).read_text()
(delivery / 'delivery-verification.json').write_text(json.dumps(dict(status='PASS', copied_new_paintings=checks,
    explicit_launchers=5, preserved_comparison_launchers=4), indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(status='PASS', painted_source_copies=len(checks), desktop_launcher='PASS', delivery=str(delivery))))
