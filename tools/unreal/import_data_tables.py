"""UE 5.7 editor script: import and round-trip the two compiled alpha DataTables."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import unreal


def expand_exported_effects(rows):
    """Read UE's nested struct text through its own reflected struct importer."""
    for row in rows:
        if 'Effects' not in row:
            continue
        effects = []
        for encoded in row['Effects']:
            if not isinstance(encoded, str):
                raise RuntimeError('Unexpected legacy nested effect representation')
            value = unreal.WCAbilityEffect()
            if not value.import_text(encoded):
                raise RuntimeError('Unreal rejected its exported effect struct')
            effect = {}
            for json_name, property_name in (
                ('EffectId', 'effect_id'), ('DamageType', 'damage_type'),
                ('MagnitudeUnit', 'magnitude_unit'), ('StatId', 'stat_id'),
            ):
                name = str(value.get_editor_property(property_name))
                effect[json_name] = 'none' if not name or name.lower() == 'none' else name
            for json_name, property_name in (
                ('Magnitude1', 'magnitude1'), ('Magnitude2', 'magnitude2'),
                ('Magnitude3', 'magnitude3'), ('DurationMs', 'duration_ms'),
            ):
                effect[json_name] = value.get_editor_property(property_name)
            effects.append(effect)
        row['Effects'] = effects
    return rows


def main() -> None:
    project = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()
    root = project.parent
    source = project / 'Content/WonderChess/SourceData'
    reports = Path(os.environ.get('WC_EDITOR_REPORT_DIR', str(root / 'reports/WC-300'))).resolve()
    reports.mkdir(parents=True, exist_ok=True)
    # UE 5.7.4's property-visitor exporter asserts on TArray<FWCAbilityEffect>.
    # The installed DataTableJSON.cpp exposes this supported legacy export path.
    unreal.SystemLibrary.execute_console_command(None, 'DataTableJSON.ExportUsingPropertyVisitor 0')
    report = {
        'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'engine_version': unreal.SystemLibrary.get_engine_version(),
        'status': 'STARTED',
        'scope': 'compiled reflected alpha DataTable import, saved asset and JSON round-trip parity',
        'tables': [],
        'runtime_gameplay_verified': False,
        'exporter': 'DataTableJSON.ExportUsingPropertyVisitor=0 (process-local UE 5.7.4 nested-array workaround)',
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
            if len(expected) != 24 or len(expected_by_id) != 24:
                raise RuntimeError(f'{table_name} must contain twenty-four unique alpha rows')
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
            actual = expand_exported_effects(json.loads(exported_path.read_text(encoding='utf-8-sig')))
            (reports / f'normalized_{table_name}.json').write_text(json.dumps(actual, indent=2) + '\n', encoding='utf-8')
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
            if row_count != 24:
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
