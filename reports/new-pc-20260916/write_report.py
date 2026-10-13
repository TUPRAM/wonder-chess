import json
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[1]
summary = json.loads((out / 'transfer-summary.json').read_text())
record = {
    'date': '2026-09-16',
    'status': 'TRANSFER_INCOMPLETE_DEVELOPMENT_SETUP_REQUIRED',
    'report': 'reports/new-pc-20260916/README.md',
    'transfer': summary,
    'git_fsck': 'PASS_EXIT_0_DANGLING_OBJECTS_PRESERVED',
    'registered_worktrees': 1,
    'blender': {'installed': '5.2.1 LTS', 'original': '5.1 series', 'background_python': 'PASS', 'mcp': 'BROKEN_OLD_USER_PATH_NO_LOOPBACK_LISTENER'},
    'unreal': {'installed': '5.8.2', 'original': '5.7.4', 'project_association': '5.7', 'standalone_initialization': 'PASS_23.34_SECONDS', 'project_build': 'NOT_RUN'},
    'cpp_toolchain': 'NOT_FOUND_IN_STANDARD_INSTALL_LOCATIONS_OR_REGISTRY',
    'authoring_tests': 'BLOCKED_MISSING_TOOLS_AND_TESTS',
    'product_acceptance_changed': False,
}
(out / 'environment-check.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
ledger_path = root / 'reports/implementation_state.json'
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
ledger = {'new_pc_integrity_20260916': record, **ledger}
ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
c = summary['counts']
report = f'''# New computer integrity and application check — 16 September 2026

## Result

**Transfer incomplete; development setup requires repair.** This is the active repository at `C:\\Users\\USER\\Documents\\Wonder Chess`. No gameplay changes, asset resaves, engine conversion, restoration, package overwrite, or release acceptance occurred.

## File integrity

- Transfer manifest completion/count/byte/digest check: **{summary['manifest_complete']}**.
- Manifest files: **{c['manifest_files']:,}**; exact size/SHA-256 matches: **{c.get('matched', 0):,}**.
- Missing: **{c.get('missing', 0):,}**; size mismatches: **{c.get('size_mismatch', 0):,}**; hash mismatches: **{c.get('hash_mismatch', 0):,}**; read errors: **{c.get('read_error', 0):,}**.
- Missing inventory: 180 tooling files, 123 test files, 405 support files, and one Codex capture ref under `.git`.
- Support omissions include 54 migration evidence files, 240 old settings files, 99 validation files, 10 archive downloads, and two study-build files.
- Git `fsck --full` exited 0. Dangling objects are retained recovery/history material; no prune was run. One registered checkout, branch `codex/milestones-b0-m7-20260912`, base `d80635f615810a93c3161c6bfd6c34c758b08260`. Existing uncommitted changes preserved.
- The root launch shortcut depends on the missing `tools/unreal/launch_milestones.ps1`, so it cannot work as supplied. Preserved packages were hash checked, not played.
- 244 missing files have candidate copies with the same recorded hash elsewhere in the manifest. This is a recovery index, not a restoration result. No files were restored from older revisions.

## Blender

`C:/Program Files/Blender Foundation/Blender 5.2/blender.exe` launched with `--background --factory-startup` and executed Python using `bpy`. It reported **5.2.1 LTS**, background mode true, and three factory scene objects, then exited 0. This proves local command/Python execution only; no project scene, external textures, rig, or export/import round trip was validated.

The project `.codex/config.toml` still references the nonexistent `C:/Users/iputu/Documents/Wonder Chess/.../.venv/Scripts/python.exe` and old working directory. No listener was found on loopback port 9876 and no Blender MCP tools were available in this session. **The interactive bridge is disconnected.** Local bridge source is present, but the transferred virtual environment is not a verified installation.

## Unreal and compiler

Installed Engine `Build.version` reports **5.8.2**, while the project associates with **5.7** and the recorded original engine was **5.7.4**. A standalone `UnrealEditor-Cmd.exe -help -unattended -nullrhi -nosplash -stdout -FullStdOutLogOutput` probe completed engine initialization in 23.34 seconds. It stayed running, so its exact owned probe process was stopped after collecting evidence. No Wonder Chess project was opened or converted.

The editor and Build/UAT scripts are present. No Visual Studio installation/compiler registration, `vswhere`, or Windows SDK include installation was found in the checked standard locations/registry. `C:/Program Files/Windows Kits/10` contains only `Catalogs`. Project compilation, Unreal Python project integration, rendering and new-machine game acceptance remain **NOT RUN**.

The shell's `python` resolves to the Windows Store alias. Audit scripts used Codex's bundled Python; a project development environment has not been established. Required authoring/test suites cannot run while `tools/` and `tests/` are absent.

## Recommended repair order

1. Recover all missing files from the original complete folder or transfer backup, retaining this original manifest. Re-run the full integrity comparison before changing sources. Avoid replacing uncommitted files with an older Git checkout.
2. Install/locate the matching Unreal 5.7.4 and original Blender 5.1 toolchain, or plan a separately verified upgrade. Do not silently convert the current project to 5.8.
3. Install/locate Visual Studio C++ build tools and Windows SDK; create fresh project Python and Blender bridge environments, update machine-specific paths and verify the loopback addon connection.
4. Run the restored authoring/tests, then compile into a new candidate output and verify actual project asset integration and packaged launch on this PC.

## Evidence

- [Full hash summary](transfer-summary.json)
- [Every transfer issue](transfer-issues.jsonl)
- [Missing files](missing-inventory.json)
- [Potential identical local recovery copies](recovery-candidates.json)
- [Git integrity output](git-fsck.txt)
- [Unreal initialization log](unreal-launch.txt)
- [Machine check record](environment-check.json)

The hash audit ran before updating the implementation ledger. New report files and the ledger update are intentional post-audit changes. Historical results do not certify this machine.
'''
(out / 'README.md').write_text(report, encoding='utf-8')
print(json.dumps(c))
