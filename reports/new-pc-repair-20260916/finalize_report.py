import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
record = {
    'date': '2026-09-16',
    'status': 'CONNECTIONS_VERIFIED_RECOVERY_AND_BUILD_SETUP_PARTIAL',
    'report': 'reports/new-pc-repair-20260916/README.md',
    'recovery': {'exact_originals_restored': 424, 'initial_missing': 709, 'unrecovered_original_payloads': 285, 'missing_source_files_remaining': 9, 'git_fsck': 'PASS_EXIT_0', 'complete': False, 'evidence': 'reports/new-pc-repair-20260916/recovery/README.md'},
    'python_environment': '.venv',
    'authoring_checks': 'PASS_ALL_FOUR_COMMANDS',
    'python_tests': {'attempted': 221, 'passed': 219, 'failures': 1, 'import_errors': 1, 'full_suite_pass': False, 'causes': ['Windows PowerShell execution policy Restricted blocks launcher test', 'verify_milestone_package.py is still missing']},
    'blender': {'version': '5.2.1 LTS', 'configured_mcp_protocol': 5, 'all_five_configured_tools': 'PASS', 'create_read_remove_marker': 'PASS', 'viewport_captured_and_viewed': True, 'source_unchanged_in_read_only_verification': True, 'loopback': '127.0.0.1:9876', 'safe_mode': True, 'telemetry': False, 'evidence': 'reports/new-pc-repair-20260916/blender/live-verification/verification.json'},
    'unreal': {'version': '5.8.2', 'python_commandlet': 'PASS', 'blender_fbx_import_save_reload': 'PASS', 'dimensions_cm': [100.000008, 100.000008, 100.0], 'isolated_diagnostic_project': True, 'actual_game_converted': False, 'actual_game_57_build': 'BLOCKED_57_ENGINE_AND_CPP_TOOLS_ABSENT', 'evidence': 'reports/new-pc-repair-20260916/unreal/README.md'},
    'build_tools': {'status': 'SIGNED_INSTALLER_PREPARED_USER_ADMIN_ACTION_REQUIRED', 'automatic_review_rejection': 'blocked by policy', 'installed': False, 'engine_57_installed': False, 'evidence': 'reports/new-pc-repair-20260916/build-tools/README.md'},
    'product_acceptance_changed': False,
}
(out / 'verification.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
ledger_path = root / 'reports/implementation_state.json'
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
ledger['new_pc_repair_20260916'] = record
ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('Recorded partial repair and verified connections; historical evidence retained.')
