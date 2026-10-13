"""Read-only batch entry point, launched by run_unreal_checks.ps1 inside Unreal."""
import json
import os
import sys
from pathlib import Path
import unreal as u

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/production'))
import unreal_asset_validator as validator

source = Path(os.environ['WC_ASSET_CONTRACT_FILE'])
output = Path(os.environ['WC_ASSET_VALIDATION_OUTPUT'])
document = json.loads(source.read_text(encoding='utf-8-sig'))
contracts = document.get('contracts')
if not isinstance(contracts, dict) or not contracts:
    raise ValueError('Supply a nonempty contracts map; unfilled templates cannot pass')
results = []
for path, contract in contracts.items():
    if not path.startswith('/Game/') or not isinstance(contract, dict) or not contract:
        raise ValueError('Each contract needs a /Game/ object path and explicit requirements')
    asset = u.load_asset(path)
    if not asset:
        results.append({'asset': path, 'errors': ['Missing primary asset'], 'callback_executed': False})
        continue
    observed = validator.validate(asset, contract)
    results.append({'asset': path, 'errors': [e for row in observed for e in row['errors']],
                    'callback_executed': True})
result = {'status': 'fail' if any(row['errors'] for row in results) else 'pass',
          'source_contract': str(source), 'engine': u.SystemLibrary.get_engine_version(),
          'scope': 'declared_editor_contracts_only', 'human_acceptance': False, 'results': results}
output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
if result['status'] != 'pass':
    raise RuntimeError('Creature asset contract validation failed; see ' + str(output))
