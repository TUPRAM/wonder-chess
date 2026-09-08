import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
BUILD = ROOT / 'reports/WC-U430/20260907T171400Z-protocol-fix'
ART = ROOT / 'reports/WC-U440/20260907T165200Z-closeout'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def relative(path):
    return Path(path).relative_to(ROOT).as_posix()

def link(path, title=None):
    return f'[{title or Path(path).name}](<{Path(path).as_posix()}>)'

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
provenance = read(BUILD / 'provenance.json')
regression = read(RUN / 'regression-audit-complete/regression-analysis.json')
restart = read(RUN / 'restart/functional-audit/audit.json')
network = read(RUN / 'loopback/audit/network-analysis.json')
gallery_path = next((BUILD / 'gallery1080').glob('*frontend-audit.json'))
gallery = read(gallery_path)
frames = read(RUN / 'normal1080-opening/frame-summary.json')
launch = read(RUN / 'normal1080-opening/launch.json')
matrix = read(ART / 'asset-matrix-complete-inputs/asset-readiness.json')
movies = read(ART / 'engine-movies168/encoding-report.json')
assert all(x['status'] == 'PASS' for x in (regression, restart, network, gallery))
assert launch['exit_code'] == 0 and launch['simulation_speed'] == 1
assert frames['viewport_1080p_observed'] and frames['eight_neutral_encounters_status'] == 'OBSERVED'
assert movies['status'] == 'ENCODING_PASS_REVIEW_PENDING' and len(movies['encoded']['clips']) == 168
binary = Path(provenance['packaged_game_executable'])
binary_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
assert next(x['sha256'] for x in provenance['files'] if x['path'] == str(binary)) == binary_hash
rules = read(ROOT / 'data/rules.alpha.json')
units = read(ROOT / 'data/units.json')['units']
source_commit = '7f50c6c'
paths = {
    'provenance': relative(BUILD / 'provenance.json'),
    'asset_matrix': relative(ART / 'asset-matrix-complete-inputs/asset-readiness.json'),
    'hero_clip_matrix': relative(ART / 'asset-matrix-complete-inputs/hero-clips-168.csv'),
    'regression_audit': relative(RUN / 'regression-audit-complete/regression-analysis.json'),
    'restart_audit': relative(RUN / 'restart/functional-audit/audit.json'),
    'network_audit': relative(RUN / 'loopback/audit/network-analysis.json'),
    'gallery_audit': relative(gallery_path),
    'frame_times': relative(RUN / 'normal1080-opening/frame-summary.json'),
    'movies': relative(ART / 'engine-movies168/encoding-report.json'),
}
delivery = dict(package_launcher=relative(Path(provenance['packaged_executable'])),
    inner_executable_sha256=binary_hash, source_commit=source_commit,
    schema=rules['schema_version'], balance_version=rules['balance_version'], protocol=6,
    catalog_digest=provenance['catalog_digest'], acceptance='VERIFIED_IMPLEMENTATION_CHECKPOINT_NOT_FULL_RELEASE_ACCEPTANCE',
    launch='Run WonderChess.exe from the intact Windows package folder. Play > Solo starts one human and seven bots. Heroes opens the gallery.',
    manual_1H7B='NOT_RUN_NATIVE_COMPUTER_USE_DISABLED', physical_2H6B='BLOCKED_SECOND_PHYSICAL_MACHINE_NOT_SUPPLIED',
    continuous_art_audio_acceptance='NOT_RUN', **paths)
state_path = ROOT / 'reports/implementation_state.json'
state = read(state_path)
old = state.get('update_delivery')
if old and old.get('package_launcher') != delivery['package_launcher']:
    state.setdefault('historical_update_deliveries', []).append(old)
state['update_delivery'] = delivery
state['actual_game_status'] = '24_HERO_PACKAGED_IMPLEMENTATION_CHECKPOINT_FULL_ART_MANUAL_LAN_ACCEPTANCE_OPEN'
state['updated_utc'] = state['last_updated_utc'] = now
state['current_data']['integration_status'] = 'PROTOCOL6_SHARED_CONSTANT_EDITOR_SHIPPING_BUILT_CURRENT_PACKAGE_AUDITS_PASS'
state['update_performance'] = dict(report=paths['frame_times'], boundary='150-second normal-speed opening sample; not full-match/busy-PvP/lobby/gallery acceptance',
    eight_neutral_encounters=frames['eight_neutral_encounters_status'], required_busy_load=frames['required_busy_load_status'])
statuses = {
    'WC-U400': 'PASS_SCHEMA3_1_PROTOCOL6_400_BASELINE_CHECKS_147_TESTS_28_DOCS_6_CATALOG',
    'WC-U410': 'PASS_CURRENT_PACKAGED100_ACTUAL_COMBAT_581951_AUDIT_CHECKS',
    'WC-U420': 'PASS_CURRENT_PVE_TOURNAMENT_RESTART_AND_LOOPBACK_FUNCTIONAL_CHECKS',
    'WC-U430': 'PASS_CURRENT_PACKAGED_GALLERY531_CHECKS_24_MESHES_168_CLIPS_MANUAL_USABILITY_OPEN',
    'WC-U440': '24_HERO_7_NEUTRAL_ASSETS_IMPORTED_COLD_PASS_168_MOVIES_RECORDED_FINISHED_ART_NOT_ACCEPTED',
    'WC-U450': 'FUNCTIONAL_BOTS_UI_AUDIO_INTEGRATED_BALANCE_AND_CONTINUOUS_AV_REVIEW_OPEN',
    'WC-U460': 'CHECKPOINT_TECHNICAL_PASSES_PHYSICAL_LAN_MANUAL_PLAY_FULL_PERFORMANCE_AND_ART_GATES_OPEN',
}
for group in ('tasks', 'update_tasks'):
    for key, status in statuses.items():
        record = state[group].setdefault(key, {})
        record['status'] = status
        if 'reports/UPDATE24_CHECKPOINT_HANDOFF.md' not in record.setdefault('evidence', []):
            record['evidence'].append('reports/UPDATE24_CHECKPOINT_HANDOFF.md')
state['warnings'] = [
    'This is a tested implementation checkpoint, not full user-requested release acceptance.',
    'All24 source/export/import records exist; finished anatomy/material/motion/FX/audio quality is not accepted.',
    '168 engine movies are captured and encoded; continuous visual and audio review NOT_RUN.',
    '1H7B evidence uses scripted legal controller commands at20x; complete manual normal-speed play NOT_RUN.',
    'Actual2H6B is same-machine loopback only. Two physical LAN machines NOT_RUN.',
    'Final timing is a150-second normal-speed opening sample; full-match/busy-PvP/lobby/gallery performance NOT_RUN.',
    'Real-time MCP bridge setup explicitly deferred by user; enabled add-on screenshot is not connection proof.',
]
save(state_path, state)
save(RUN / 'closeout-summary.json', dict(utc=now, delivery=delivery, baseline_checks=400, baseline_tests=147,
    gallery_checks=gallery['checks_executed'], packaged_tournaments=100, regression_checks=regression['checks_passed'],
    restart_checks=len(restart['checks']), loopback_checks=56, asset_totals=matrix['totals'],
    frame_rows=frames['source']['rows'], full_release_accepted=False, pending=state['warnings']))

lines = ['# Wonder Chess 24-hero implementation checkpoint', '',
    f'Updated {now}. Source checkpoint `{source_commit}`. The user requested a fast closeout and deferred real-time MCP bridge discussion.', '',
    '**The Windows Unreal package is produced and exercised. Full release acceptance remains open. The models are authored, imported and animated; they are not certified finished artwork.**', '',
    '## Launch and source', '',
    f'- Launcher: {link(provenance["packaged_executable"])}. Keep the entire Windows folder together.',
    '- Double-click WonderChess.exe, choose **Play > Solo** for one human and seven persistent bots. Choose **Heroes** for the gallery. The LAN menu prepares real local sessions; it is not an online matchmaking service.',
    f'- Inner Shipping executable SHA-256: `{binary_hash}`.',
    f'- Source project: {link(ROOT / "game/WonderChess.uproject")}; C++: {link(ROOT / "game/Source/WonderChessRuntime")}.',
    f'- Canonical data: {link(ROOT / "data")}; generated data: {link(ROOT / "generated")}. Schema `{rules["schema_version"]}`, profile `alpha_24`, balance `{rules["balance_version"]}`, protocol `6`.',
    f'- Catalog digest: `{provenance["catalog_digest"]}`.',
    f'- Full input/build/payload identity: {link(BUILD / "provenance.json")}. Git HEAD in that record is historical capture context; per-file hashes are authoritative. The source was then committed as `{source_commit}`.', '',
    '## Implemented and verified boundary', '',
    'All24 stable hero IDs are in actual combat. The update includes short display names, six races/six classes and reachable2/4 tiers, individual skills, visual-only weapons/armor, monster rounds1/2/3/every positive multiple of5, original Brighthaven lobby, Solo/LAN preparation and entry transition, animated gallery and star-dependent details, and the existing shop/bench/deployment/upgrades/leveling/scouting/elimination/spectating/results/restart loop. No item inventory or equipment drops were added.', '',
    'Closeout completed Varek/Iri/Oren source and imports, finalized Rok/Kesh/Nella alternating attack windows, forced Unreal marker persistence after an actual cold-load failure, and centralized protocol6 after an actual network audit found stale protocol5 public metadata. Existing rigs, sources and retained failures were preserved.', '',
    '| Check | Actual result |', '|---|---|',
    '| Fresh baseline |400 specification/data checks;147 Python tests;28 generated documents;6 catalog artifacts passed |',
    '| Native current combat |100 tournaments;3,379,152 assertions passed |',
    '| Actual Unreal cold reload |5 tests passed;24 hero meshes,168 unique clips and24,138 sampled bone transforms; neutral/data/window checks passed |',
    '| Final Editor + Shipping build/cook/archive |PASS; corrected qualified-constant run. Initial C2065 failure retained |',
    f'| Final packaged gallery |PASS {gallery["checks_executed"]} checks;24 models,24 portraits,168 clips;72 star-stat and75 effect-star rows |',
    f'| Final packaged0H8B |PASS100 actual-combat tournaments;{regression["checks_passed"]:,} audit checks,0 failures |',
    f'| Final packaged1H7B/restart |PASS {len(restart["checks"])} checks;3 complete scripted matches,2 restarts, elimination and spectating |',
    '| Final packaged2H6B loopback |PASS35 paired-state +21 additional checks;both players reached round33;both received protocol6;process exits0 |',
    '| Physical two-machine2H6B |NOT_RUN: second physical machine/address/access not supplied |',
    '| Manual normal-speed complete1H7B |NOT_RUN: native computer-use APIs disabled in current session |',
    '| Continuous168-clip and audio approval |NOT_RUN;movies/PCM/PNG evidence does not establish listening or visual approval |', '',
    'The final functional runs overlapped accelerated game/regression workloads. They establish behavior, not uncontended performance. Their legal scripted player inputs are not manual play.', '',
    'Final1H7B outcomes: ' + '; '.join(f'namespace{x["namespace"]}:round{x["rounds"]}, human eliminated round{x["elimination_round"]}, placement{x["human_place"]}' for x in restart['matches']) + '.', '',
    '## Asset matrix and review media', '',
    f'All24 source/export/import hash bindings pass, with168 hero clips and7 neutral sources/exports/imports containing40 neutral clips. Detailed matrices: {link(ART / "asset-matrix-complete-inputs/asset-readiness.json")}, {link(ART / "asset-matrix-complete-inputs/hero-clips-168.csv")}, {link(ART / "asset-matrix-complete-inputs/neutral-clips.csv")}.', '',
    f'Actual Unreal capture:3,701 frames over all168 clips at20Hz, encoded into168 movies with readback. {link(ART / "engine-movies168", "Review movies")}; {link(ART / "engine-movies168/encoding-report.json")}. These were captured before the final metadata-only correction; all579 game_content provenance entries match the final inputs exactly (staged source data is verified separately): {link(BUILD / "content-continuity.json")}.', '',
    '| Hero | Stable ID | Source revision | Imported clips | Finished-art approval |', '|---|---|---:|---:|---|']
for unit in units:
    manifest = read(ROOT / 'exports/heroes' / unit['id'] / 'export_manifest.json')
    lines.append(f'| {unit.get("display_name",unit["name"])} | `{unit["id"]}` | {manifest["source_revision"]} |7|Open|')
lines += ['', '## Measured performance', '',
    'Final package,150-second normal-speed opening,1920x1080/D3D11/100% screen scale/60fps cap. Lenovo82RG/GR1ZZYLY, AMD Ryzen7 6800H,16GB RAM, active NVIDIA RTX3060 Laptop GPU6GiB. The OS also lists an AMD integrated GPU; the measured active RHI adapter is NVIDIA. Existing user Blender stayed open. No other task game, compiler or encoder was running during this final sample.', '',
    '| Sample | Frames | Frame p50 ms | Frame p95 ms | Frame p99 ms | Max ms |', '|---|---:|---:|---:|---:|---:|']
for name in ('all_profiled_frames','neutral_combat_frames','eight_live_neutral_encounters','pvp_combat_frames'):
    row = frames['subsets'][name]; values = row['frame_ms']
    def number(key):
        value = values.get(key)
        return 'not sampled' if value is None else f'{value:.3f}'
    lines.append(f'|{name}|{row["frames"]}|{number("p50_ms")}|{number("p95_ms")}|{number("p99_ms")}|{number("max_ms")}|')
lines += ['', f'Eight simultaneous neutral encounters: **{frames["eight_neutral_encounters_status"]}**. Required busy12-visible-unit load: **{frames["required_busy_load_status"]}**. Full-match, busy PvP, all-hero lobby/gallery stage profiling remain NOT_RUN. CPU/render/GPU timings, settings, memory and input hashes are in {link(RUN / "normal1080-opening/frame-summary.json")}.', '',
    '## Defects and remaining acceptance', '',
    '- Art remains prototype-quality in places: simplified facial/anatomical forms, conspicuous rounded joints, sparse costume/material detail and uneven silhouettes. Improve these against the authored dossiers; do not call current technical exports finished heroes.',
    '- Review all168 movies continuously; inspect hands, equipment contact, deformation, footsteps, attack release, effects and transitions in live Unreal. Audition all audio and verify synchronization. Encoded silent review movies do not test audio.',
    '- Balance remains initial tuning:100 tournaments had12,597 fights,1,815,540 events,1,844 combat timeouts and524 ghosts. Simulated duration median1,284.525s, p951,426.95s. Early waves were won800/800 each; round30 only32/132 wins; hero use is uneven (Neris69 unit-rounds versus Dagna12,366). Do not call balance solved.',
    '- Complete manual normal-speed1H7B, physical2H6B on two machines, actual disconnect/recovery on the final build, and full-match/lobby/gallery/busy-load profiling. Existing earlier recovery and loopback records are retained but do not close these current mandatory gates.',
    '- Current computer-use tool explicitly disables native surfaces. No callable Blender real-time bridge was found. The supplied enabled-addon screenshot is not connection proof; connection setup was deferred at the user\'s request.', '',
    '## Evidence and exact resume', '',
    *[f'- {key}: {link(ROOT / value)}' for key,value in paths.items()],
    f'- Retained r3 failures and corrections: {link(ROOT / "reports/WC-U450/20260907T170300Z-closeout/retained-failures.json")}. Earlier wrong-fixture and premature incomplete-evidence audits remain failed; fresh completed audits are separate.', '',
    'Resume this existing workspace and read AGENTS.md, START_HERE.md, this handoff and implementation_state.json. Keep source commit7f50c6c and the immutable r4 package. Begin the next user-authorized discussion by verifying the actual callable real-time MCP bridge before editing a live Blender scene. Then prioritize Ada visual quality, use the168 review movies and matrix to address each hero, and repeat affected imports/cold tests/package checks. Do not regenerate the project or overwrite retained sources/evidence.', '',
    f'For physical LAN use {link(ROOT / "docs/current/PHYSICAL_LAN_WC_U460.md")} and {link(ROOT / "tests/runtime/run_physical_lan.ps1")}; the launcher defaults to preflight and needs real machine addresses. Do not label loopback as physical LAN.', '',
    'Automatic approval review previously rejected moving/cleaning70 misplaced PNGs under C:/reports/WC-U440/20260906T162705Z-elf-shoulders, reason "blocked by policy". They remain untouched. Exact prior handoff: reports/WC-U440/20260906T162705Z-elf-shoulders/elf-source8-handoff.md.', '']
(ROOT / 'reports/UPDATE24_CHECKPOINT_HANDOFF.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'handoff':'reports/UPDATE24_CHECKPOINT_HANDOFF.md','source_commit':source_commit,'binary_sha256':binary_hash,'frame_rows':frames['source']['rows']}))
