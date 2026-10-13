import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
archive = Path('D:/Wonder Chess/support/archives/downloads/blender-mcp-main (1).zip')
archive_result = {'path': str(archive), 'bytes': archive.stat().st_size, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
try:
    with zipfile.ZipFile(archive) as z:
        archive_result['zip_crc_failure'] = z.testzip()
except zipfile.BadZipFile as exc:
    archive_result['zip_error'] = str(exc)
(OUT / 'nonmatching-archive.json').write_text(json.dumps(archive_result, indent=2), encoding='utf-8')
summary = json.loads((OUT / 'recovery-summary.json').read_text())
record = {
    'date': '2026-09-17',
    'status': 'ALL_MISSING_SOURCE_RECOVERED_TEN_HISTORICAL_ARCHIVES_UNRESOLVED',
    'report': 'reports/backup-recovery-20260917/README.md',
    'backup': 'D:/Wonder Chess',
    'backup_modified': False,
    'this_recovery': summary,
    'original_missing_files': 709,
    'cumulative_exact_recoveries': 699,
    'remaining_original_archives': 10,
    'missing_source_files_remaining': 0,
    'authoring_checks': 'PASS_ALL_FOUR_400_DATA_CHECKS',
    'python_tests': {'attempted': 230, 'passed': 229, 'failures': 1, 'errors': 0, 'remaining_failure': 'Windows PowerShell Restricted execution policy blocks launcher fixture'},
    'storybook_launcher': 'VALIDATE_ONLY_PASS_NOT_LAUNCHED',
    'compiler_sdk_smoke': json.loads((OUT / 'compiler-smoke/result.json').read_text(encoding='utf-8-sig')),
    'unreal_57_installed': False,
    'actual_game_build': 'NOT_RUN_MATCHING_ENGINE_UNAVAILABLE',
    'product_acceptance_changed': False,
}
(OUT / 'verification.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
ledger_path = ROOT / 'reports/implementation_state.json'
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
ledger['backup_recovery_20260917'] = record
ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('Recorded recovery and compiler verification.')
