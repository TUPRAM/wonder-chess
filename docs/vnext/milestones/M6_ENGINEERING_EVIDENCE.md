# M6 engineering checkpoint — 2026-09-12

M6 remains **incomplete**. This checkpoint executes additional native authority and privacy checks and fixes three bounded transport prerequisites. It does not enable successor online play, create a dedicated server, authenticate a reconnect, register EOS, or establish independent-device evidence. The accepted solo and human-study prerequisites remain separate.

## Candidate and ownership

The native final checks use `wonder_vnext_solo_0.1.0` with canonical source SHA-256 `6e80932173071ef05e58d90a44db3490cfcfde86d48edf33f4a940ff1748efa0` and generated runtime SHA-1 `75913c8995d924698780bc1df44ecad294ad86d3`. They were compiled against the frozen shared C++ core after the owned-team relic-offer policy was generated. No balance values were altered by this work package.

Files delivered in this work package:

- `tests/runtime/vnext_online_contract_tests.cpp`
- `tests/runtime/run_vnext_online_contract.ps1`
- Bounded changes to `game/Source/WonderChessRuntime/Public/WCMatchRuntime.h` and `Private/WCMatchRuntime.cpp`
- This evidence document

The existing `AWCMatchMode::BeginPlay` successor guard, two-controller legacy lobby limit, and existing solo/frontend ownership remain intact. A future successor network frontend must use authenticated server state; removing the guard alone would not complete that work.

## Executed native evidence

Run from the successor worktree:

```powershell
& .\tests\runtime\run_vnext_online_contract.ps1 -OutputDirectory 'C:\Users\iputu\Documents\Project Support\Wonder Chess\validation\2026-09-12-b0-m7\online-contract-02'
```

Result: **PASS, 248 assertions**, MSVC compilation exit `0`, test process exit `0`, source hashes unchanged during execution. Start `2026-09-12T15:43:57Z`; end `2026-09-12T15:44:17Z`. The per-tick comparison remains active throughout two complete tournaments; the assertion total does not count every equal tick as a separate scenario.

Evidence root: `C:\Users\iputu\Documents\Project Support\Wonder Chess\validation\2026-09-12-b0-m7\online-contract-02`. `process.json` records all input hashes, and `compile.log`/`tests.log` retain actual output. Native executable SHA-256: `d61ecbf887bcc7dc14eafa425d1ac38d5269239ed1cf87d91879318a3bf478cc`.

| Experiment | What executed and passed | Limit |
|---|---|---|
| Native 2H6B, 4H4B, 8H0B configuration | Canonical core initialization with the requested human flags; normal affordable recruitment, deployment, and round-4 relic acquisition | These are native seat configurations, not connected clients or human participants |
| Public scouting disclosure | Deployed IDs/facing/readiness are visible; benched IDs and bench purchases are absent; an unequipped draft result does not change the public projection; compile-time checks prevent private economy/shop/roster/draft/RNG fields from entering `PublicSeat` | Tests the native value projection, not serialized network traffic |
| Cross-seat attacks | A forged seat cannot consume another captain's draft. Publicly known victim unit IDs cannot be sold, moved, rotated, equipped, or unequipped by another owner. A known foreign relic ID cannot be equipped by the attacker | `Match::Submit` expects its caller to supply the already authenticated seat |
| Request tampering | Unauthenticated/out-of-range seats, future sequences, forged revisions, unknown command enums, and invalid draft indexes reject without changing owner resources, identity, inventories, readiness, or RNG | Not a remote authentication or malformed-packet audit |
| Draft retransmission | A repeated accepted draft returns its original acceptance without adding another relic; changing the choice under that request ID rejects | Does not implement reconnect or reconnect UI |
| Delayed messages | Earlier-round revision rejects; after actual takeover bot commands advance sequence, a pre-disconnect command rejects; a prior-match revision rejects after restart even with a current sequence | No claim that a revoked connection can authenticate again |
| Phase locks | New reroll and orientation requests reject during real combat | Does not measure network latency at the cutoff |
| Deterministic attack isolation | Clean and attacked matches follow identical phases, finish real battles, and retain every settlement hash, final health/placement, and shop/bot/relic RNG state | Two local native authorities, not network replicas |
| Takeover and interruption | Repeated takeover notifications preserve state; online origin remains ineligible for offline save after all humans become bots; explicit abort remains aborted with zero fabricated placements | Server process termination and client response still need live transport tests |

The earlier `online-contract-01` remains preserved. It used the source hashes recorded in its own manifest and reported per-tick checks separately. Use `online-contract-02` for this frozen candidate.

The final durable save rerun also passed against this same content: `save-files-04` contains 51 file-suite, 4 cold-writer, and 6 separate-process cold-reader checks, all exit `0`, with `source_stable=true`. Its executable SHA-256 is `811ed5c4db58ca875f8fd5a0438d379232eb31b98b00050e7b10f3d686ad27d7`. This includes rejection of online-origin save/load after takeover and does not authorize offline conversion of online matches.

## Transport prerequisites changed

The transport previously advertised `wc::NetworkProtocolVersion` (currently 6), while its server compatibility check and outgoing client handshake used literal 5. Both now use the same published constant. Existing schema and content-digest comparisons remain required before accepting gameplay commands.

Facing now survives the native intent queue, the reliable `ServerIntent` RPC argument, and construction of the authoritative `wc::Command`. The RPC validates its range against `Facing::Forward` through `Facing::Left`. Existing C++ callers that omit the new argument retain forward facing through the default argument.

The RPC command-range check now admits every currently defined command through `CommandType::SetFacing`, including relic draft/equip/unequip, and still rejects values outside the enum. The core continues to validate the actual command, phase, ownership, sequence, revision, eligibility, and resource effects. The transport still derives the seat from its controller binding and rejects a controller whose seat is no longer human.

Source contract inspection passed six checks covering shared protocol use, complete command range, all facing forwarding steps and bounds, server-derived active-human identity, and preserved successor/legacy gates. Evidence: `C:\Users\iputu\Documents\Project Support\Wonder Chess\validation\2026-09-12-b0-m7\transport-contract-02\audit.json`. These are **static checks**, not RPC execution. The previous audit incorrectly searched `RefreshView` for the outgoing handshake, which is in `Tick`; that audit error was corrected without another runtime-source change.

Transport source SHA-256 at that inspection:

- `Private/WCMatchRuntime.cpp`: `0002e14452d7aabeba93cd8f72af43b642139f54a827ef936f67d938d1b00b9e`
- `Public/WCMatchRuntime.h`: `3017520acd7ee9bab3c71f8a5a525a6e481e89a2b4cf0b892eb1db2c3d6f7a9c`

The integrating run's final [r4 BuildCookRun log](../../../reports/vnext/milestones/package-r4/package-Development-20260912T160920Z.log) records a successful Development package, and its [exact identity manifest](../../../reports/vnext/milestones/package-identity-r4/package-manifest.json) captures these transport sources and the matching compiled/package executable. See [M7 engineering evidence](M7_ENGINEERING_EVIDENCE.md) for exact hashes and verification. Build/package success does not establish execution of the new RPC fields through real client/server endpoints; that gate remains open.

## Existing evidence reused with its original boundary

`tests/runtime/runtime_tests.cpp` already exercises ownership, idempotent purchase replay, changed request payloads, preparation destinations, editing after ready, takeover, and restart. `vnext_tournament_tests.cpp` already exercises facing authority and replay, private independent shops, relic acquisition/conservation, semantic snapshot validation, online-origin restrictions, and deterministic full-match restoration. The new suite adds cross-seat relic/known-unit attacks, concrete private projection checks across larger human configurations, and attacked-versus-clean tournament comparisons.

The existing analyzer regressions were rerun:

```powershell
python -m unittest discover -s tests/runtime -p test_network_audit.py -v
python -m unittest discover -s tests/runtime -p test_session_transition_audit.py -v
```

Both passed: 2 network-evidence reader tests and 4 session-transition reader tests. They deliberately use synthetic exports and establish **analyzer behavior only**.

The preserved [2026-09-06 routed Shipping loopback report](../../../reports/WC-360/shipping-network-routed/audit/analysis.md) records a prior actual two-process legacy run, 35 paired checks, seven real RPC probe types, and matching received state through round 23. It was re-read, not re-executed, and certifies only its recorded legacy executable hashes. Its original limitations include scripted inputs, one physical computer, no packet capture, and unavailable Shipping engine-log error counts.

The preserved [candidate-5 failure report](../../../reports/WC-360/candidate5-network/audit/analysis.md) is also relevant: matching final results did not compensate for client combat rounds missing after oversized replication bunches. Successor payload and continuous received-state evidence must be measured again when twenty deployed units, new ability events, relics, and eventual summons enter the wire representation.

## Remaining M6 engineering and external prerequisites

| Remaining gate | Verified current state | Next concrete engineering or acceptance work |
|---|---|---|
| Successor network frontend | Legacy game mode explicitly refuses `wonder_vnext`; new solo frontend is local | Connect a successor interface to authenticated owner/public replication; include private relic offers/inventory and correct command feedback; keep local solo authority distinct |
| Four/eight human sessions | Native core supports them; legacy `PostLogin` admits at most two controllers and `StartTournament` accepts at most two humans | Extend session/controller ownership, entry synchronization, spectator rules, and disconnect handling together, then execute real 2/4/8-client matches |
| Authenticated reclaim | Existing `PostLogin` rejects joining an active match; no reclaim API exists | Bind an authenticated identity to a persistent seat, define takeover timeout and reconnect entitlement, rotate/revoke controller authority, enforce exactly one live controller, and reject messages from earlier bindings |
| Takeover epoch | Native `TakeOver` changes human/takeover/ready state; it does not itself rotate a controller epoch | Treat revoked-connection rejection as a transport responsibility; establish an explicit new binding/epoch before adding reclaim, rather than setting `human=true` directly |
| Dedicated-server build | Configured engine is installed UE 5.7.4, changelist 51494982, with `Engine/Build/InstalledBuild.txt`; project contains Game and Editor targets, no Server target | Verify a suitable source-engine build, add/build/cook the project server target, and retain server/client executable and content identities |
| EOS/session operations | No EOS plugin, session registration, or artifact configuration was established by this work | Obtain/verify the intended product configuration and authentication/session policy before implementing service-backed rooms and unranked discovery; keep secrets outside Git |
| Actual privacy and packet behavior | Native projection passed; current successor wire path is not enabled | Inspect each client's received public/owner state, reject cross-seat access, record payload bounds and continuous round coverage, and test malformed/reordered/duplicate inputs through the actual endpoint |
| Latency, jitter, loss, crash | No new live network trial was run | Execute scoped local network emulation and process-failure trials on exact server/client builds, with explicit abort reporting and no fabricated winner |
| Independent remote 2H6B → 4H4B → 8H0B | Not run in this work package | People operate independent devices through join, scout, draft, disconnect/reclaim, lose/spectate, finish, and rematch; record build/network/hardware identities and every failure |

Epic's installed-version documentation specifies a source-engine build and C++ multiplayer project for the dedicated-server tutorial and describes the separate Server target/build/cook path. [Unreal Engine 5.7 dedicated-server documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-dedicated-servers-in-unreal-engine?application_version=5.7).

OSS EOS requires product registration/configuration and enabled/configured project plugins. No registration, credentials, hosting, or public deployment was performed here. [Unreal Engine 5.7 OSS EOS documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/online-subsystem-eos-plugin-in-unreal-engine?application_version=5.7).

The existing multiprocess shipping launcher was assessed but not run: it targets legacy package provenance and omits the successor profile, while the current successor game-mode guard prevents the needed journey. Re-running that legacy package could not close successor M6. The next live transport trial requires the successor frontend/server integration above; this limitation does not block independent solo or native verification work.

M6 advancement requires the actual remote and authenticated lifecycle evidence in the milestone contract. No entry, remote, dedicated-server, or human gate is marked complete by this checkpoint.
