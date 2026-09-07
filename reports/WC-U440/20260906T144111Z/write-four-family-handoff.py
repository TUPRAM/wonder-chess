"""Consolidate already executed evidence; never promote it to Unreal/art acceptance."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
HEROES = [
    ('Cass', 'wc_u_human_warrior', 'candidate-v3', 'refinement-v3', 'verified-v4',
     'Broad low diagonal blade with two baked hand contacts; crimson split coat, cream trim, single silver shoulder guard, supported back banner and brow streak.',
     'Protruding eye plates, unsupported shoulder edge and duplicate LOD faces were corrected. Some armor-cap creasing and the stylized face remain art-review concerns. Basic slash is compact; assess game-camera readability.'),
    ('Neris', 'wc_u_elf_mage', 'candidate-v1', 'refinement-v3', 'verified-v4',
     'Slender violet layered robe, pale-blue trim, curved broken-arc headpiece with temple supports, rear braided knot, held star lens and chart case.',
     'Floating arc, downward grip fingers and overlapping sleeve pieces were corrected. Stiff projecting lapels and low-detail facial planes remain art-review concerns. The focus-hand/pointing-hand action needs release-effect readability in Unreal.'),
    ('Orla', 'wc_u_dwarf_priest', 'candidate-v1', 'refinement-v2', 'verified-v3',
     'Stocky adult silhouette, rust wool, oatmeal apron, paired silver braids, closed padded travel hood, supported octagonal lantern with eight posts and travel pouch.',
     'Intersecting sleeves, open rear hood and opaque lantern side panels were corrected; accidentally removed lantern posts were restored in a fresh revision. Basic lantern attack is subtle; assess at game camera with VFX. Small cuff openings and stylized face remain art-review concerns.'),
    ('Tala', 'wc_u_orc_guardian', 'candidate-v1', 'refinement-v2', 'verified-v3',
     'Broad moss-green Orc with small tusks and braided rear knot; bronze shoulder guards, leather coat, blue sash, curved road-mark tower shield, short mace and flat backpack.',
     'Overlapping sleeve pieces were replaced with continuous skinned sleeves. Shoulder armor remains deliberately faceted; shield partly occludes torso and must be assessed at combat camera. Low-detail face and material finish remain art-review concerns.'),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

records = []
for name, uid, before, after, verify, work, concerns in HEROES:
    source = ROOT / 'art-source/heroes' / uid / (uid + '.blend')
    exports = ROOT / 'exports/heroes' / uid
    manifest_path = exports / 'export_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    evidence = OUT / uid / verify
    checks = json.loads((evidence / 'published-verification.json').read_text())
    encoded = json.loads((evidence / 'normal-speed-evidence.json').read_text())
    assert sha(source) == checks['source_sha256'] == manifest['source_sha256']
    assert sha(manifest_path) == checks['manifest_sha256']
    assert len(manifest['files']) == 14
    assert all(sha(exports / f) == digest for f, digest in manifest['files'].items())
    assert len(encoded['clips']) == 7 and encoded['speed_multiplier'] == 1
    assert all(Path(c['gif']).is_file() and Path(c['contact_sheet']).is_file() for c in encoded['clips'])
    records.append({
        'name': name, 'unit_id': uid, 'source': str(source), 'exports': str(exports),
        'manifest': str(manifest_path), 'source_sha256': sha(source), 'manifest_sha256': sha(manifest_path),
        'source_revision': checks['source_revision'], 'geometry_revision': checks['geometry_revision'],
        'animation_revision': checks['animation_revision'], 'triangles': [r['triangles'] for r in checks['mesh_fbx_readbacks']],
        'bone_count': 27, 'source_clip_count': 7, 'exported_files_hash_verified': 14,
        'rig_family': manifest['rig_family'], 'authoring_units_source_sha256': manifest['units_source_sha256'],
        'authored_work': work, 'remaining_review_concerns': concerns,
        'before_front': str(OUT / uid / before / 'front.png'),
        'after_views': {view: str(OUT / uid / after / (view + '.png')) for view in ('front', 'side', 'back', 'three-quarter')},
        'source_and_mesh_fbx_evidence': str(evidence / 'published-verification.json'),
        'motion_numeric_evidence': str(evidence / 'motion-invariants.json'),
        'rendered_sequence_evidence': str(evidence / 'motion-sequences.json'),
        'encoded_review_evidence': str(evidence / 'normal-speed-evidence.json'),
        'source_20hz_clip_contact_sheets_inspected': ['Idle', 'Move', 'Attack', 'Active', 'Hit', 'Defeat', 'Victory'],
        'source_and_exports_frozen_for_unreal_owner': True,
        'this_lane_verified_animation_fbx_import': False,
        'this_lane_verified_unreal_import': False,
        'continuous_unreal_visual_review': 'NOT_RUN_IN_THIS_LANE',
        'final_art_accepted': False,
    })

report = {
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'SOURCE_EXPORT_AND_SAMPLED_BLENDER_REVIEW_HANDOFF',
    'owner': '/root/update_data', 'blender_version': '5.1.1',
    'total_heroes': 4, 'source_clips': 28, 'independent_mesh_fbx_readbacks': 12,
    'exported_files_hash_verified': 56,
    'source_pose_sampling': 'Every 3 frames of authored 60 FPS; in-place root, bone scale and support sole checks.',
    'visual_evidence': 'Actual Blender Cycles stills plus 20 Hz pose frames encoded at 1x and inspected as all-sample contact sheets. This is not a claim of continuous playback review.',
    'limits': [
        'No new UE binaries were edited or imported in this lane; root owns actual UE import, continuous playback, VFX/audio integration and packaging.',
        'Skin/root/floor and mesh-FBX checks are technical gates, not finished-art approval.',
        'Normal textures use a flat tangent normal; modeled bevels carry form. High-detail surface finish remains an art-review concern.',
        'Runtime target selection, skills, damage/reward behavior, performance and complete matches are outside this source asset evidence.',
    ],
    'retained_failures': [
        'Cass initial authoring failed hand-contact reach checks before successful bounded contact repair; earlier logs and unanimated source are retained.',
        'Cass verified-v3 failed LOD2 triangle readback (1238 source versus 1229 FBX); source4 removes duplicate faces and verified-v4 passes.',
        'Orla refinement-v1 removed lantern side posts with opaque side panels; refinement-v2 restores eight posts and closes the rear hood.',
        'Neris source3 and Tala source2 numeric checks passed but actual back-view inspection found sleeve overlaps; fresh source4/source3 repairs and fresh evidence are retained.',
    ],
    'heroes': records,
}
json_path = OUT / 'four-family-source-handoff.json'
md_path = OUT / 'four-family-source-handoff.md'
assert not json_path.exists() and not md_path.exists(), 'Preserve published handoff; use a fresh name for corrections.'
json_path.write_text(json.dumps(report, indent=2) + '\n')
lines = [
    '# WC-U440: Cass, Neris, Orla and Tala source handoff', '',
    'Four frozen Blender source candidates now have 28 authored clips, 12 independent mesh-FBX readbacks and 56 verified exported file hashes. This handoff does not certify finished art or Unreal playback.', '',
    '| Hero | Stable ID | Source / geometry / animation | LOD triangles | Evidence |',
    '|---|---|---|---|---|',
]
for r in records:
    lines.append(f"| {r['name']} | `{r['unit_id']}` | {r['source_revision']} / {r['geometry_revision']} / {r['animation_revision']} | {' / '.join(map(str, r['triangles']))} | [{Path(r['source_and_mesh_fbx_evidence']).parent.name}](<{r['source_and_mesh_fbx_evidence']}>) |")
lines += ['', 'Each hero retains editable source collections, 27 bones, one UV/material palette, 1024 BaseColor/Normal/ORM, an actual 768px model portrait, normalized centimetre mesh/clip FBXs and two reduced LODs. Stable IDs and canonical ability timings are preserved.', '',
          'The actual front, side, back and three-quarter views were inspected, followed by all seven sampled clip sheets for each final revision. GIF encoding was decoded and checked at 20 Hz / 1x. Continuous Unreal playback, complete-match readability, effects, audio, animation-FBX import and final visual acceptance remain the integration owner’s checks.', '']
for r in records:
    lines += [f"## {r['name']}", '', r['authored_work'], '',
              f"[Source](<{r['source']}>) · [Export manifest](<{r['manifest']}>) · [Before](<{r['before_front']}>) · [After front](<{r['after_views']['front']}>) · [After back](<{r['after_views']['back']}>) · [All seven review clips](<{r['encoded_review_evidence']}>)", '',
              f"Source SHA-256: `{r['source_sha256']}`", '', f"Manifest SHA-256: `{r['manifest_sha256']}`", '', r['remaining_review_concerns'], '']
lines += ['## Retained failures and limits', ''] + ['- ' + s for s in report['retained_failures']] + [''] + ['- ' + s for s in report['limits']]
md_path.write_text('\n'.join(lines) + '\n')
print(json.dumps({'status': report['status'], 'json': str(json_path), 'markdown': str(md_path), 'heroes': 4, 'clips': 28, 'mesh_readbacks': 12, 'files': 56}))
