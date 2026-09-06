"""UE 5.7 editor script: import and round-trip the two compiled alpha DataTables."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

import unreal


def main() -> None:
    project = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()
    root = project.parent
    source = project / 'Content/WonderChess/SourceData'
    reports = root / 'reports/WC-300'
    reports.mkdir(parents=True, exist_ok=True)
    report = {
        'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'engine_version': unreal.SystemLibrary.get_engine_version(),
        'status': 'STARTED',
        'scope': 'compiled reflected alpha DataTable import, saved asset and JSON round-trip parity',
        'tables': [],
        'runtime_gameplay_verified': False,
    }
    report_path = reports / 'data-table-import.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assets = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    try:
        stage = json.loads((source / 'runtime_stage_manifest.json').read_text(encoding='utf-8'))
        for table_name, struct_name in (('DT_Units_Alpha', 'WCUnitRow'), ('DT_Abilities_Alpha', 'WCAbilityRow')):
            source_name = f'generated/unreal/{table_name}.json'
            input_path = source / source_name
            raw = input_path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest != stage['files'][source_name]['sha256']:
                raise RuntimeError(f'Staged source hash mismatch: {source_name}')
            expected = json.loads(raw)
            expected_by_id = {row['Name']: row for row in expected}
            if len(expected) != 12 or len(expected_by_id) != 12:
                raise RuntimeError(f'{table_name} must contain twelve unique alpha rows')
            row_struct = unreal.find_object(None, f'/Script/WonderChessRuntime.{struct_name}')
            if row_struct is None:
                raise RuntimeError(f'Compiled row structure unavailable: {struct_name}; compile the editor target first')
            asset_path = f'/Game/WonderChess/Data/{table_name}'
            if assets.does_asset_exist(asset_path):
                table = assets.load_asset(asset_path)
                if not isinstance(table, unreal.DataTable):
                    raise RuntimeError(f'Existing asset has wrong class; preserving {asset_path}')
                if table.get_editor_property('row_struct') != row_struct:
                    raise RuntimeError(f'Existing table has wrong row struct; preserving {asset_path}')
            else:
                factory = unreal.DataTableFactory()
                factory.set_editor_property('struct', row_struct)
                table = asset_tools.create_asset(table_name, '/Game/WonderChess/Data', unreal.DataTable, factory)
                if table is None:
                    raise RuntimeError(f'Could not create {asset_path}')
            if not unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(table, str(input_path), row_struct):
                raise RuntimeError(f'Unreal rejected {table_name}; inspect editor log for import warnings/errors')
            exported_path = reports / f'imported_{table_name}.json'
            if not unreal.DataTableFunctionLibrary.export_data_table_to_json_file(table, str(exported_path)):
                raise RuntimeError(f'Could not export imported {table_name} for parity verification')
            actual = json.loads(exported_path.read_text(encoding='utf-8-sig'))
            actual_by_id = {row['Name']: row for row in actual}
            if len(actual) != len(actual_by_id) or expected_by_id != actual_by_id:
                differences = []
                for row_id in sorted(expected_by_id.keys() | actual_by_id.keys()):
                    left, right = expected_by_id.get(row_id), actual_by_id.get(row_id)
                    if left != right:
                        differences.append({'row_id': row_id, 'expected': left, 'actual': right})
                raise RuntimeError(f'{table_name} field parity failure: {json.dumps(differences, ensure_ascii=False)}')
            if not assets.save_loaded_asset(table, only_if_is_dirty=False):
                raise RuntimeError(f'Could not save verified table {asset_path}')
            row_count = len(unreal.DataTableFunctionLibrary.get_data_table_row_names(table))
            if row_count != 12:
                raise RuntimeError(f'Saved row count mismatch: {asset_path}')
            report['tables'].append({
                'asset': asset_path,
                'row_struct': row_struct.get_path_name(),
                'row_count': row_count,
                'source_sha256': digest,
                'export_sha256': hashlib.sha256(exported_path.read_bytes()).hexdigest(),
                'field_parity': 'PASS',
                'saved': True,
            })
            unreal.log(f'WC_DATA_TABLE_VERIFIED {asset_path} rows={row_count} all_fields_match=true')
        report['status'] = 'PASS'
    except Exception as error:
        report['status'] = 'FAIL'
        report['error'] = str(error)
        raise
    finally:
        report['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


main()
