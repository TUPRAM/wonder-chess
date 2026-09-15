"""Assemble the verified local Storybook candidate and its review handoff."""
import hashlib, json, re, shutil
from datetime import datetime, timezone
from pathlib import Path

evidence = Path(__file__).resolve().parent
root = evidence.parents[3]
revision = 'r20'
candidate = f'WonderChess-Storybook-{revision}'
delivery = Path('C:/Users/iputu/Documents/Project Support/Wonder Chess/Storybook Demo - r20')
def read(path):
    return json.loads(path.read_bytes())
def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

graphics = read(evidence / f'{revision}-graphics-a1.json')
contracts = read(evidence / f'{revision}-engine-contracts/verification.json')
package = read(evidence / f'package-{revision}-verify.json')
manual = read(evidence / f'{revision}-manual/input-evidence.json')
assert len(graphics) == 8 and all(row['passed'] for row in graphics)
assert contracts['passed'] and package['status'] == 'PASS'
rules = read(evidence / 'rules-before.json')['files']
for row in rules:
    row['current_sha256'] = hashlib.sha256((root / row['path']).read_bytes()).hexdigest()
    row['unchanged'] = row['current_sha256'] == row['sha256']
assert all(row['unchanged'] for row in rules)
write(evidence / 'rules-preserved.json', dict(status='PASS', files=rules))
manifest = read(evidence / f'package-{revision}-manifest.json')
payload = next(row for row in manifest['package_files'] if row['path'] == manifest['roles']['game_binary'])
record = dict(schema='wonder_vnext.storybook_verification.1', recorded_utc=datetime.now(timezone.utc).isoformat(),
    status='PACKAGED_COMPONENT_VERIFIED_OWNER_REVIEW_OPEN', candidate=candidate,
    source_paintings=23, reused_paintings=3, current_portraits=6, ability_icons=6, relic_icons=12,
    package=package, game_binary=payload, graphics=graphics, engine_contracts=contracts,
    authoring=read(evidence / 'authoring-checks.json'), python_tests=230, rules_files_unchanged=len(rules),
    actual_input=manual, previous_input='r16-manual/input-evidence.json',
    failed_candidates_preserved=['package-first-console.log', 'r16 graphical and input evidence', 'r17 graphical evidence and review corrections', 'r18-review-rejection.json', 'r19-review-rejection.json'],
    boundaries=['Expanded owner visual acceptance open', 'Current three-dimensional creatures remain gameplay proxies',
        'No clean-machine installation or final-content performance acceptance', 'No new normal-speed human study or balance acceptance',
        'B0-M7 milestone acceptance remains open; this advances M2/B3 presentation'])
write(evidence / 'verification.json', record)
art_manifest_path = root / 'art-source/2d-expansion/r001/asset_manifest_candidate.json'
art_manifest = read(art_manifest_path)
art_manifest['status'] = 'PACKAGED_COMPONENT_VERIFIED_OWNER_REVIEW_OPEN'
art_manifest['human_acceptance'] = 'Expanded candidate pending owner review; final 3D forms and release remain unaccepted.'
art_manifest['verification'] = str((evidence / 'verification.json').relative_to(root)).replace('\\', '/')
art_manifest['package'] = candidate
write(art_manifest_path, art_manifest)
ledger_path = root / 'reports/implementation_state.json'
ledger = read(ledger_path)
ledger['vnext_2d_asset_slice']['owner_review'] = dict(status='OWNER_APPROVED_SCOPED_SLICE',
    date='2026-09-13', quote='I approve the slice', boundary='Approval of the preceding r15 slice, not final 3D forms or the new r20 expansion.')
ledger['vnext_storybook_expansion'] = record | {'readout': 'docs/vnext/art/STORYBOOK_READOUT.md',
    'verification_record': 'reports/vnext/milestones/storybook-20260913/verification.json'}
write(ledger_path, ledger)
tracker_path = root / 'reports/vnext/milestones/verification.json'
tracker = read(tracker_path)
tracker['latest_component_verification'] = dict(candidate=candidate, record='reports/vnext/milestones/storybook-20260913/verification.json',
    boundary='Separate current presentation component. Historical r4 results and pause metadata above remain unchanged.')
write(tracker_path, tracker)

assert not delivery.exists(), 'Preserve earlier delivery folders; choose a fresh candidate folder.'
delivery.mkdir(parents=True)
shutil.copy2(evidence / 'verification.json', delivery / 'verification.json')
readout_path = root / 'docs/vnext/art/STORYBOOK_READOUT.md'
readout = re.sub(r'\]\((\.\.?/[^)]+)\)', lambda match: '](<' +
    str((readout_path.parent / match[1]).resolve()).replace('\\', '/') + '>)', readout_path.read_text(encoding='utf-8'))
(delivery / 'DEVELOPMENT_READOUT.md').write_text(readout, encoding='utf-8')
art_dest = delivery / 'art'
for row in art_manifest['sources']:
    source = root / row['path']
    relative = source.relative_to(root / 'art-source/2d-expansion/r001')
    target = art_dest / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
for path in art_manifest['reused_sources']:
    source = root / path
    target = art_dest / 'approved-slice' / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
captures = ['solo-recruited-preparation.png', 'solo-scouting.png', 'solo-relic-draft.png', 'solo-equipped-relic.png', 'solo-results.png']
capture_dest = delivery / 'in-game'
capture_dest.mkdir()
for name in captures:
    shutil.copy2(evidence / f'{revision}-visual-1080-a1' / name, capture_dest / name)
shutil.copy2(evidence / f'{revision}-lab-1080-a1/lab-combat.png', capture_dest / 'lab-combat.png')
for path in (evidence / f'{revision}-manual').glob('*.png'):
    shutil.copy2(path, capture_dest / path.name)
support = delivery.parent
for name, mode in [('Play Wonder Chess.cmd', 'Solo'), ('Play Storybook - Solo.cmd', 'Solo'), ('Play Storybook - Lab.cmd', 'Lab'),
                   ('Play Combat Clarity - Solo.cmd', 'Solo'), ('Play Combat Clarity - Lab.cmd', 'Lab')]:
    body = '@echo off\npowershell -NoProfile -ExecutionPolicy Bypass -File "' + str(root / 'tools/unreal/launch_milestones.ps1') + f'" -Mode {mode} -Storybook\nif errorlevel 1 pause\n'
    (support / name).write_text(body, encoding='ascii')
(delivery / 'START_HERE.md').write_text('''# Wonder Chess — Storybook demo r20

Open **Play Wonder Chess.cmd** in the parent Wonder Chess folder for the actual shop, bench, scouting, relics and eight-seat solo tournament. **Play Storybook - Lab.cmd** opens the formation and combat workbench.

In Solo, click **Pause** to hold preparation while reviewing. Click a shop portrait to buy; select its bench card, then a near-half board cell to deploy. Select a creature and use Rotate or arrow keys/Enter while the board has focus. Three matching copies merge. Click a captain on the right to scout, then You to return. Hover cards for details and scroll the side panels for more content. Select a creature before equipping a compatible owned relic.

Use **Menu → Creature & relic collection** to review all six portraits, six ability icons and twelve relics together, including smaller icon examples. **Ready for battle** advances when all captains are ready; combat is automatic. A relic draft requires one real choice. Menu provides save/load and exit. Close an older r16/r17 test window if it is still open before launching this candidate.

The in-game folder contains actual packaged captures. The art folder contains the 23 new paintings and three reused approved-slice paintings. The reference-inspired interface has live native controls and text, a perspective 3D board and a separate painted sanctuary background. All hero gameplay models are still proxies; the expanded art needs owner review and is not public-release acceptance.

The previous explicit Play 2D Art Slice aliases still open r15; Play Combat Clarity r13 aliases preserve the earlier comparison. No canonical combat rules, prices, effects or mana charging changed in this art expansion.
''', encoding='utf-8')
print(json.dumps(dict(status=record['status'], candidate=candidate, delivery=str(delivery), rules_preserved=len(rules),
                      game_sha256=payload['sha256'], graphical_cases=len(graphics)), indent=2))
