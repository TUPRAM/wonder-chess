import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
summary = json.loads((OUT / 'summary.json').read_text())
record = {
    'date': '2026-09-17',
    'status': 'ALL_709_ORIGINALLY_MISSING_PAYLOADS_RECOVERED',
    'report': 'reports/github-check-20260917/README.md',
    'original_missing_count': 709,
    'cumulative_exact_recoveries': 709,
    'original_missing_payloads_unrecovered': 0,
    'final_ten_archive_hashes': 'ALL_MATCH_ORIGINAL_TRANSFER_MANIFEST',
    'downloads_guide_matches_published_text': True,
    'remote_revision': summary['remote_revision'],
    'local_head': summary['local_head'],
    'remote_ahead_by': summary['remote_ahead_by'],
    'branch_reconciled': False,
    'working_changes_preserved': True,
    'full_original_manifest_equivalence_claimed': False,
    'remaining_setup': ['Matching Unreal 5.7.4 and actual project build unverified', 'One Windows PowerShell policy-dependent test failure'],
    'product_acceptance_changed': False,
}
(OUT / 'verification.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
path = ROOT / 'reports/implementation_state.json'
ledger = json.loads(path.read_text(encoding='utf-8'))
ledger['github_recovery_20260917'] = record
path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('Recorded complete missing-file recovery; setup limitations retained.')
