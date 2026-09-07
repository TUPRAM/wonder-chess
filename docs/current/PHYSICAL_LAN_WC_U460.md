# Physical LAN capture handoff — WC-U460

Prepared 2026-09-06. **Physical LAN acceptance is NOT_RUN.** This handoff does not claim access to a second PC, a connection attempt, a transfer, a firewall change, a game launch, or a completed two-PC match.

Use `tests/runtime/run_physical_lan.ps1` with its sibling `tests/runtime/packaged_payload.ps1`. The new launcher defaults to a read-only package/network-configuration preflight and writes a fresh record; it launches only with explicit `-Launch`. It performs no installation, service control, firewall modification, transfer, DNS lookup or connectivity probe. Its optional launch starts exactly one game on the current machine. Keep the existing loopback wrappers and their historical reports separate.

## Inputs that must be supplied for the actual run

- The final selected **Shipping package**, and its unchanged provenance JSON produced after successful packaging. The final package selection remains the release owner's responsibility; this document does not nominate an earlier candidate as final.
- Two independently operated **physical Windows PCs**, called PC-A and PC-B below. A second process, VM, container, remote view of PC-A, or changed computer name does not satisfy this requirement.
- PC-A's assigned private IPv4 address and an unused UDP port from 1024 through 65535. The game supports literal IPv4 addresses. This launcher intentionally accepts only private 10/8, 172.16/12 or 192.168/16 addresses.
- An ordinary local copy of the complete package on each PC. Package relocation is supported. Preserve its relative file layout, immutable provenance, and the two launcher/helper scripts. Obtain/copy these using an already authorized local mechanism; no copy or network change was performed during this preparation.
- Separate new local evidence directories, outside the package, on both PCs. Use a shared run label plus different machine/role labels. Do not reuse an old directory.

The launcher compares every copied payload file's relative path, size and SHA256 against the original provenance. It does not rewrite captured paths in the JSON. Only an in-memory mapping points the existing payload checker at the local copy. Unexpected files, missing files, duplicate entries, altered bytes, unstable provenance, path escapes and reparse points fail the preflight. Runtime `Saved` directories are excluded consistently with the package provenance contract. No source workspace, Unreal installation or Python is needed on PC-B to run the PowerShell launcher; the packaged game must already have its normal Windows prerequisites available. If prerequisites or access are absent, retain the failure and stop this gate without installing or changing permissions.

## Preflight on each PC

The following paths and address are **examples**, not observed machines or an invented delivery path. Replace them with the actual selected local package, copied provenance, IP and role. In PowerShell, verify each path explicitly before executing. Do not use a network/UNC path.

```powershell
# On PC-A. Example local paths; replace them with the selected release inputs.
$Tool = 'C:\WC-LAN\tools\run_physical_lan.ps1'
$Package = 'C:\WC-LAN\Windows'
$Provenance = 'C:\WC-LAN\release-provenance.json'
$HostIP = '192.168.1.20'
$Run = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
& $Tool -Role host -HostAddress $HostIP -Port 7780 `
  -PackageRoot $Package -ProvenancePath $Provenance `
  -MachineLabel PC-A -OutputDirectory "C:\WC-LAN\evidence\$Run-host-preflight"
```

```powershell
# On PC-B, use its own local paths and the actual PC-A address.
$Tool = 'D:\WC-LAN\tools\run_physical_lan.ps1'
$Package = 'D:\WC-LAN\Windows'
$Provenance = 'D:\WC-LAN\release-provenance.json'
$HostIP = '192.168.1.20'
$Run = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
& $Tool -Role client -HostAddress $HostIP -Port 7780 `
  -PackageRoot $Package -ProvenancePath $Provenance `
  -MachineLabel PC-B -OutputDirectory "D:\WC-LAN\evidence\$Run-client-preflight"
```

Both records must say `PREFLIGHT_ONLY`, with identical `provenance_sha256`, catalog digest and complete payload-relative hash/size lists. The local paths and hardware records should differ as expected. A host address absent from PC-A's active local addresses fails. A client address that points back to a local PC-B address fails. These checks prevent the obvious same-machine setup; they do not establish physical separation. The launcher records hostname, OS, CPU, graphics driver, RAM, local IPv4 interfaces and a hashed SMBIOS UUID, with the explicit boundary that these are OS-reported facts. A missing/unusable UUID stays null; do not manufacture one.

Keep console errors from a rejected preflight alongside its run notes. Preflight rejection happens before launching anything. An exit code 0 from preflight verifies only this byte/input check.

## One complete 2H6B match

Use a new directory for the actual capture. The initial functional run uses `-InputMode scripted`: there are two authenticated human-controller seats and six persistent bots, while the installed game verification driver issues legal player commands and deliberate authority probes. This proves an actual networked controller path only after both exports are audited; it is **not manual play or human usability evidence**.

Start PC-A first. The command prints an observed game PID owning the selected UDP port. Then start PC-B. The host's scripted driver waits for two connected controllers before requesting entry. Both clients send the selected package's protocol/schema/digest readiness, the introduction precedes the preparation timer, and the existing game-owned routing creates the real 2H6B session. Do not substitute a positional Unreal startup URL.

```powershell
# PC-A, after its successful preflight. Use a NEW Run value/directory.
$Run = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
& $Tool -Role host -HostAddress $HostIP -Port 7780 `
  -PackageRoot $Package -ProvenancePath $Provenance -MachineLabel PC-A `
  -OutputDirectory "C:\WC-LAN\evidence\$Run-host-match" `
  -InputMode scripted -SimulationSpeed 1 -Seconds 3600 -Launch -Visible
```

```powershell
# PC-B, after PC-A reports the matching UDP listener. NEW output directory.
$Run = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
& $Tool -Role client -HostAddress $HostIP -Port 7780 `
  -PackageRoot $Package -ProvenancePath $Provenance -MachineLabel PC-B `
  -OutputDirectory "D:\WC-LAN\evidence\$Run-client-match" `
  -InputMode scripted -SimulationSpeed 1 -Seconds 3660 -Launch -Visible
```

The host command uses `-WCHost -Port=7780`; the client uses `-WCJoin=<actual host>:7780`. Both capture at 1920×1080/DX11 with frame instrumentation and automatic screenshots. Their game-controlled exit timers bound the process lifetime. One capped tournament can take roughly 46 minutes from the configured timers before startup and stalls; a 40-minute anecdotal duration is not a safe capture limit. Review completed match records before calling a timer exit successful. If the timer expires before results, the attempt is incomplete and must be retained. A launcher timeout records the PID and does not forcibly kill it.

For manual play, use new directories and `-InputMode manual -SimulationSpeed 1 -Launch -Visible` on both PCs. Operate lobby start, entry Ready controls, shop, board, scouting and spectating yourselves. Manual mode omits scripted inputs/authority probes; privacy snapshots and frame capture remain enabled. Log who controlled each seat and the observed interaction defects. Authority-probe checks absent in manual mode remain NOT_RUN, so retain the earlier scripted run as a separate complementary artifact.

If the client cannot join, record its observed error, exact IP/port, host listener record and both package hashes. Do not dismiss security prompts, enable broad permissions or alter the firewall automatically. This launcher intentionally has no networking repair mechanism. Access or Windows policy failures remain a precise blocker for the physical gate.

## Evidence to retain and review

Keep both directories intact, including `physical-launch.json`, `session.json`, namespace-specific `*-session.json`, `*-snapshots.jsonl`, `*-commands.jsonl`, `*-frames.csv`, transition/skill capture metadata and actual PNGs. Record clock/timezone offsets if the PCs' clocks differ. The launch record's local role, PID and hardware must bind to the exported session process. Retained per-match results take precedence over a later process snapshot showing host disconnection after the planned host exit.

Review the following together before assigning any physical LAN result:

1. Two actual physical devices were observed by the operator during the same session. Keep a short device/role note and actual photographs or video showing both displays running that session where available. OS identities corroborate this; process count or different names alone does not prove it.
2. Identical immutable provenance hashes, canonical digest, selected protocol, schema 3.1.0 and every payload-relative byte/hash entry; post-run package checks remain valid on both machines. Retain launcher and helper hashes. No failure may be silently relabeled or dropped.
3. Host is authority/network mode 2, client is network mode 3, seats are 0 and 1, namespace is shared and nonzero, and the roster has two human seats plus six bots. Attribute identities using `(machine identity, process_id)`, not PID alone.
4. Both observed the full tournament through results: rounds 1/2/3 and each positive multiple of 5 were actual neutral fights; other combat rounds were PvP. Pairings, common combat states, once-only settlements and final standings agree. Record missing snapshot overlap as incomplete evidence, never an assumed match.
5. Public snapshots contain no foreign shops, gold, XP, benches or RNG state. Owner-private snapshots name only that controller's seat. Actual replies match the deliberately rejected stale/replayed/foreign-owner/combat commands, while accepted buys/placements/upgrades/leveling follow normal authority. Record all probe statuses and actual reply counts.
6. Observe elimination and continued spectating where they occur, session errors and process exits, visual/audio problems, and frame timings on the named hardware. Screenshot sampling and two concurrent PCs do not provide a normal-speed continuous clip review or a frame-time target pass by themselves.

The Shipping auditor now has a physical-record branch. After an authorized operator makes the intact evidence directories available locally for review, put the host directory at `<review>/host` and the client directory at `<review>/client`; keep the unchanged provenance JSON separately. Do not invent an aggregate loopback `trial.json`. Run:

```powershell
python tests/runtime/audit_shipping_network.py '<new local review directory>' `
  --physical --provenance '<unchanged copied provenance JSON>'
```

This reads both actual `physical-launch.json` records and first-match exports and creates a new `physical-audit/physical-network-analysis.json`, refusing to overwrite an existing physical audit. It checks unique nonempty recorded hostnames, machine-plus-PID identity, actual session PID bindings, private nonloopback target and route arguments, local host/client address distinction, listener PID/port, successful exits, matching provenance/catalog hashes, and complete recorded preflight/post-run relative payload hashes. It then evaluates the existing received-state/RPC/privacy checks and schema/protocol/catalog checks. A matching numeric PID on two distinct bound machines is valid. The raw lower-level same-host reader result is retained alongside the new composite identity evaluation; no session PID, original artifact or old audit is rewritten. The original loopback branch still requires different PIDs.

A functional `PASS` here is explicitly scoped to recorded identity, received state and RPC evidence. `physical_device_observation` remains `NOT_RUN_BY_ANALYZER`; the release decision still needs the paired operator observation of two physical devices and the other review criteria above. Current copied machine paths may be unavailable on the review PC, so the physical branch validates the launcher's pre/post-run hash records against the immutable provenance rather than pretending to rehash an inaccessible drive. Every analyzed input is fingerprinted. Missing physical launch records, postflight, wrong routes/hashes, incomplete matches or privacy failures prevent the functional pass.

Client disconnect/takeover, rejected rejoin, and host-loss abort are separate fresh runs after the complete-match baseline. Do not disconnect during the only full-match evidence run. A future operator should explicitly record the disconnect action/time and actual resulting state; this launcher does not simulate those events.

## Preparation verification

`reports/WC-U460/20260906T153033Z/physical-launcher-fixtures/fixture-results.json` records 25 passed synthetic input/payload fixtures: valid relative relocation, unchanged original manifest, IPv4 normalization/rejections, local role checks, local path restrictions, duplicate/escaped/unstable/altered/missing/extra payload rejection and the runtime Saved exclusion. The fixture files are labeled synthetic and are not game executables. The adjacent `parameter-results.json` records eight additional passed parameter-binding checks, including invalid role, port, speed, duration, input mode and machine label. The adjacent `physical-auditor-fixtures.json` records 12 passed synthetic physical-identity cases, including same numeric PID on distinct bound hosts and rejection of identical hosts, loopback, wrong route/process/manifest/payload and missing postflight. Both existing paired-reader unit tests also passed. No game was launched and no connection was attempted for these checks.

Protocol note: the next candidate uses protocol 6, retaining protocol 5 request-correlated replies and adding the per-unit presentation-only basic-attack ordinal. The physical branch consumes current shared `catalog_checks`; it must not accept a retained older package. Earlier protocol 4 and 5 fixtures and launches keep their original identities. The 12 protocol 5 analyzer fixtures at `reports/WC-U460/20260906T154451Z/physical-protocol5-fixtures/physical-auditor-fixtures.json` remain synthetic analyzer evidence. The protocol 5 packaged loopback tournament at `reports/WC-U450/20260906T164139Z/r2-loopback-2h6b` completed round 33 with 56 audit checks passed; it is not a physical LAN result or a protocol 6 launch. Use fresh actual protocol 6 exports from both physical machines for acceptance.

The prepared launcher and its actual future launch path must still execute on both selected machines. PowerShell parsing and synthetic fixture success do not count as real 2H6B, Windows compatibility on PC-B, finished networking or release acceptance.
