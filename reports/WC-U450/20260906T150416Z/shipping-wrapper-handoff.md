# Shipping wrappers and evidence auditors

Frozen handoff, 6 September 2026. No game process was launched by this task.

## Implemented

- `tests/runtime/packaged_payload.ps1` extracts the previously passed solo function without changing its acceptance logic. Solo, routed network, disconnect and packaged regression all call it immediately before creating launch evidence. Every manifested packaged file is hashed with size/stamp checks; missing/extra/duplicate/outside-root files and executable-only legacy manifests fail. Runtime Saved directories remain excluded. Preflight results are retained in launch/trial JSON.
- Routed network and disconnect accept `-OutputDirectory` under this workspace's reports directory and refuse existing evidence paths. Their legacy default directory layout remains usable. Routed defaults are 720 seconds for host and 750 for client at 5x simulation, with a 810-second supervisor deadline after client launch; `-Seconds`, `-SimulationSpeed`, `-Port` are explicit overrides. Both tracked inner/launcher lifecycles are observed.
- Disconnect defaults now reserve more startup and survivor time; explicit `-HostSeconds`, `-ClientSeconds`, `-SimulationSpeed` support measured fixture timing. A sampled comparable resource transition is checked without falsely asserting that every timed departure was PvP combat. The report records actual phase and replicated neutralRound kind, and separately declares neutral/PvP combat coverage. Existing late-join refusal/privacy/takeover checks remain.
- Packaged regression uses a configurable `-TimeoutSeconds` default900. Timeout writes an explicit retained-process state rather than pretending completion.
- Shared Python shipping auditor rehashes all current payload bytes/file membership, checks the launch preflight and manifest digest, and requires actual received schema3.1.0/protocol4/catalog digest agreement. Routed audits separately check observed rounds1/2/3/every5 neutral coverage. Earlier logs and build evidence remain separate.

## Executed checks

- Six PowerShell files parsed with the installed PowerShell AST parser: `powershell-parse.json`.
- Three shipping Python auditors passed `python -m py_compile`.
- `git diff --check -- tests/runtime` passed (line-ending warnings only).
- Eight actual file-preflight fixtures passed: valid payload; changed UCAS; extra file; missing file; duplicate entry; outside-root path; legacy executable-only group; allowed runtime Saved file.
- Fifteen Python auditor fixtures passed: those eight payload cases, four neutral/PvP/unknown/preparation cases, protocol4 success, old-protocol rejection and digest-mismatch rejection.

Fixture evidence is in `payload-preflight-fixtures/`. These are labelled file/JSON fixtures, not game executables, network evidence or completed-match results.

## Commands after the integrator releases a fresh immutable package

```powershell
./tests/runtime/run_shipping_network_routed.ps1 -ProvenancePath '<fresh-provenance.json>' -OutputDirectory '<fresh reports path>/routed-2H6B' -Seconds 720 -SimulationSpeed 5
python tests/runtime/audit_shipping_network.py '<fresh reports path>/routed-2H6B'
./tests/runtime/run_shipping_disconnect.ps1 -Mode client-loss -ProvenancePath '<fresh-provenance.json>' -OutputDirectory '<fresh reports path>/client-loss'
python tests/runtime/audit_shipping_disconnect.py '<fresh reports path>/client-loss'
./tests/runtime/run_shipping_disconnect.ps1 -Mode host-loss -ProvenancePath '<fresh-provenance.json>' -OutputDirectory '<fresh reports path>/host-loss'
python tests/runtime/audit_shipping_disconnect.py '<fresh reports path>/host-loss'
./tests/runtime/run_packaged_regression.ps1 -ProvenancePath '<fresh-provenance.json>' -EvidenceName 'update24-regression' -OutputDirectory '<fresh reports path>/regression100' -TimeoutSeconds 900
```

The routed and disconnect wrappers run two real processes on this computer's loopback address. They do not establish the required two-physical-machine LAN check. Timed-exit overrides need actual observation before claiming a selected departure phase. Current scripts do not terminate unrelated processes or change security policy.

The legacy `audit_packaged_regression.py` still compares hardcoded candidate6/candidate4 evidence; use the root agent's current update regression analysis, not that legacy auditor, for this release. No runtime source, hero source/export, rig, map or binary was changed in this wrapper task.
