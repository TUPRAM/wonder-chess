"""Retest actual AS1 Blender operations after factory-startup isolation fix."""
from run_verification import ROOT, RUNNER, helper, sha, write_json
import datetime
import json

source = ROOT / 'fixture.blend'
source_sha = sha(source)
commands = []
commands.append(helper(source, 'reference_setup', 'final-reference-setup.log', [
    '--workspace', ROOT, '--spec', ROOT / 'reference-calibration.json',
    '--output-blend', ROOT / 'final-fixture-with-references.blend']))
candidate = ROOT / 'final-fixture-with-references.blend'
candidate_sha = sha(candidate)
commands.append(helper(candidate, 'scene_audit', 'final-scene-audit.log', [
    '--collection', 'AS1_FIXTURE', '--output', ROOT / 'final-scene-audit.json']))
commands.append(helper(candidate, 'scene_audit', 'final-reference-audit.log', [
    '--collection', 'AS1_REFERENCES', '--output', ROOT / 'final-reference-audit.json']))
commands.append(helper(candidate, 'render_review', 'final-render-clay.log', [
    '--collection', 'AS1_FIXTURE', '--cameras', ROOT / 'review-cameras.json',
    '--out', ROOT / 'final-renders-clay', '--clay']))
commands.append(helper(candidate, 'render_review', 'final-render-material.log', [
    '--collection', 'AS1_FIXTURE', '--cameras', ROOT / 'review-cameras.json',
    '--out', ROOT / 'final-renders-material']))
audit = json.loads((ROOT / 'final-scene-audit.json').read_text())
assert audit['blender_version'] == '5.1.1'
assert len(audit['objects']) == 3
references = json.loads((ROOT / 'final-reference-audit.json').read_text())
assert len(references['objects']) == 1
assert references['objects'][0]['semantic_part_id'] == 'tool_fixture'
assert references['objects'][0]['type'] == 'EMPTY'
assert references['file_images'][0]['size'] == [320, 512]
assert sha(source) == source_sha and sha(candidate) == candidate_sha
for name in ('final-reference-setup.log', 'final-scene-audit.log', 'final-reference-audit.log', 'final-render-clay.log', 'final-render-material.log'):
    log = (ROOT / name).read_text()
    assert 'BlenderMCP' not in log, 'User addon loading recurred.'
write_json(ROOT / 'final-execution-results.json', {
    'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'PASS_local_fixture_only', 'commands': commands,
    'runner_sha256': sha(RUNNER), 'fixture_sha256': source_sha,
    'reference_candidate_sha256': candidate_sha, 'source_files_unchanged': True,
    'saved_addon_messages_absent': True,
    'visual_review': 'recorded in VISUAL_REVIEW.md after actual captures inspected',
    'ada_art_approval': False, 'unreal_executed': False})
print('Final isolated AS1 helper smoke PASS; source hashes unchanged; no BlenderMCP addon messages.')
