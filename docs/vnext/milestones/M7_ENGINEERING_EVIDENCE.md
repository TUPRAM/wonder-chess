# M7 engineering evidence — solo development candidate

Recorded 13 September 2026, Asia/Singapore. This is a technical checkpoint for the authorized B0–M7 implementation run. **M7 release acceptance remains open.** The six-creature successor laboratory is not the completed release scope, and the unpassed art, human, performance, supported-machine and remote gates remain requirements.

The source worktree is `C:\Users\iputu\AppData\Local\CodexWorktrees\wc\m7`, based on successor commit `d80635f615810a93c3161c6bfd6c34c758b08260`. No clean-room rebuild, publication, clean-machine installation, or external-player session is claimed here.

## Continuation evidence

This document retains the r4 checkpoint. The [13 September continuation](CONTINUATION_2026_09_13.md) and [current verification inventory](../../../reports/vnext/milestones/resume-20260913/verification.json) supersede its current-work statements with r5/r6 diagnostics, package identity, scoped input and independent-checkout build evidence. Their passes remain specific to the six-creature Development candidate and do not accept M7 release.

## Frozen content and evidence scope

| Identity | Value |
|---|---|
| Runtime profile | `wonder_vnext` |
| Balance version | `wonder_vnext_solo_0.1.0` |
| Canonical source SHA-256 | `6e80932173071ef05e58d90a44db3490cfcfde86d48edf33f4a940ff1748efa0` |
| Runtime SHA-1 embedded in the native header | `75913c8995d924698780bc1df44ecad294ad86d3` |
| Generated/staged runtime SHA-256 | `6988edee019a8eec6be64e0611dd3b9ec2da2942786374e0a6e3f5efa123e46b` |
| Runtime contents | Six heroes, 12 relics, seven neutral definitions and 12 authored waves; zero active traits |
| Runtime status | `gameplay_laboratory_not_release` |
| Content policy changed in this run | At least one eligible relic offer for the owned team when feasible, with the final source version above |

The native and packaged bot trials use accelerated simulation clocks and no human operators. Their matched seeds represent the same deterministic experiments, not independent balance samples. Seeds 1–1000 are regression inputs. The reserved `900001+` holdout range was not consumed by this work.

## Exact package identity verifier

Implemented [verify_milestone_package.py](../../../tools/vnext/verify_milestone_package.py) with two operations:

```powershell
python tools/vnext/verify_milestone_package.py capture `
  --source-root <frozen-worktree> `
  --package-root <archived-Windows-directory> `
  --manifest <fresh-evidence-directory>/package-manifest.json `
  --unreal-pak 'C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealPak.exe'

python tools/vnext/verify_milestone_package.py verify `
  --manifest <evidence-directory>/package-manifest.json
```

Capture requires a fresh manifest outside the package and outside captured source membership. Verification can override source and package roots when exact copies have moved. It requires the recorded source files as well as the package; it is an operator evidence tool, not a dependency of the running game.

The manifest binds byte lengths and SHA-256 for:

- All files beneath `game/Source` and `game/Config`, canonical root data JSON, successor source/generated/staged data, generated native headers, the `.uproject`, the catalogue generator and packaging wrapper, and staged legacy source data when present.
- The source checkout's compiled game executable, the package bootstrap, exactly one actual game executable, all cooked `.pak`/`.utoc`/`.ucas` containers, dependencies and remaining package files.

Capture verifies exact equality of the generated and staged runtime, both generated native headers, the source digest and runtime digest embedded in those headers, and the corresponding identity markers in the actual executable. The package executable must equal the current compiled executable at the exact bootstrap launch path. When `.pak` files exist, the installed `UnrealPak` extracts the runtime catalogue into a temporary directory, even if a loose copy is present. Conflicting loose/packed copies and multiple packed copies fail. Capture compares the effective runtime bytes with generated/staged content. Later verification checks the same containers' complete SHA-256; it does not require UnrealPak on the verifying computer.

Only `Saved/`, `WonderChess/Saved/`, and `Engine/Saved/` are excluded from package membership, to permit runtime saves and logs. Unexpected files elsewhere, deleted files, modified bootstrap/runtime binaries, changed containers or configuration, stale source/header/runtime identities, path traversal, duplicate paths and broadened exclusions fail verification. Links and reparse points cannot enter capture. All inputs are inventoried twice to reject observed mutation during capture.

This establishes exact identity of the recorded inputs and archive. It does **not** prove a bit-reproducible build, independently establish that every observed source file was compiled into the binary, authenticate an unsigned manifest against a malicious replacement, or provide gameplay/art/remote/release acceptance. Actual compile, package and execution records are separate evidence.

## Verifier failure tests

Command executed:

```powershell
python -m unittest discover -s tests -p test_vnext_milestone_package.py -v
```

**PASS: ten tests.** The fixtures exercise unchanged capture/verification; permitted runtime save/log changes; unrecorded package content; corruption of bootstrap, actual executable, cooked container, dependency, configuration and compiled source; missing containers and newly introduced compiled source; a valid-JSON runtime with the wrong version; stale header/binary identity; binaries lacking the catalogue markers; malformed/traversing/duplicated inventory entries; exclusion tampering; misplaced nested executable paths; conflicting loose/packed catalogues; and actual CLI exit codes plus refusal to overwrite an existing manifest or write it inside its own source inventory.

These are deliberately tiny filesystem fixtures, including fake containers used to test hashing and a mocked extractor used only for the sidecar-conflict regression. They are not fabricated Unreal package evidence. Separately, the actual installed UnrealPak successfully extracted exactly one 41,367-byte runtime catalogue from the archived r3 candidate in a read-only probe and from the final r4 capture, matching the runtime SHA-256 above.

Raw [test log](../../../reports/vnext/milestones/package-manifest-tests-r3/tests.log) and [process record](../../../reports/vnext/milestones/package-manifest-tests-r3/process.json) retain exit code 0, tool/test hashes and observed UTC. The final tool SHA-256 is `bf62fa380a2b382906dc004f829a11c5f2b38d2b5f26e5cad024eff2f3123c0b`. Earlier test passes remain in r1/r2; an independent review found the pak precedence, self-inventory and misplaced-executable cases, and confirmed that all three were fixed before final capture.

The separate [checkout identity test](../../../tests/test_vnext_checkout_identity.py) verifies exact source/generated/staged bytes through real temporary Git checkouts with `core.autocrlf=true`, `false` and `input`. It verifies the line-ending contract only; it does not substitute for a separate clean-checkout Unreal build.

## Executed final archive capture

Final archive: `builds/WonderChess-Milestones-r4/Windows`, a **Development** package. The [BuildCookRun log](../../../reports/vnext/milestones/package-r4/package-Development-20260912T160920Z.log) records success and UAT exit 0 after 395.91 seconds, using installed Unreal 5.7.4, Visual Studio 2022 toolchain 14.44.35226 from the `14.44.35207` tools directory, and Windows SDK `10.0.22621.0`. This package contains the reviewed startup-save, piece-view lifecycle, restored-recap and ambiguous-guard-preview fixes.

After package integration reported the final archive stable and the nine-check solo smoke passed, capture and immediate verification both exited `0`. Capture observed stable inputs at `2026-09-12T16:19:15.898734Z`; verification passed at `16:19:19.455018Z`, covering **81 source files and 49 package files**. See the [manifest](../../../reports/vnext/milestones/package-identity-r4/package-manifest.json), [capture log](../../../reports/vnext/milestones/package-identity-r4/capture.log), [verification log](../../../reports/vnext/milestones/package-identity-r4/verify.log) and [process record](../../../reports/vnext/milestones/package-identity-r4/process.json).

| Exact artifact | SHA-256 |
|---|---|
| Manifest | `50b958699c146928fe7175ab9511e7e22c44ac81b613120828b973b182f256ad` |
| `WonderChess.exe` bootstrap, 164,864 bytes | `e3c22795d6f2265fcbd88b66e1c5b33b7b017aac916be1f3dca4d0232020a93a` |
| `WonderChess/Binaries/Win64/WonderChess.exe`, 293,196,288 bytes | `a17818ab35991d069027a6c8f6a6725fb2ca64095942ce0e5f78331d9cad3139` |
| `WonderChess-Windows.pak` | `8ccc287990f95b63b165703d632c0cd5d860216349b2c1da273159fb8c1a4b50` |
| `WonderChess-Windows.ucas` | `82444d47535c40aafbcfe86dc0d0cec5b9cdb8f7ee2ddda2f698dbc0ee0e567c` |
| `WonderChess-Windows.utoc` | `f61efd85ea3cf08392775fba5fdc4d595481c053134ca7b376c51f471ec17cf2` |

The manifest additionally records global containers, configuration, dependencies and every other included file. Its roots use Python's resolved physical Windows paths; the command above operated on the same registered worktree and archive paths stated in this document.

The [r4 solo smoke](../../../reports/vnext/milestones/solo-smoke-r4/solo-exercise.json) passed all nine booleans, including preserving the existing checkpoint while requiring an explicit save decision, buy/deploy, exact disk restoration, rejection of orders while scouting, a complete 43-round tournament, invariants and a fresh restart. Its own boundary is accelerated execution through the same handlers, not actual input or human evidence.

## Scoped actual input and cold-launch checks

The integrating task recorded [real Windows pointer/keyboard observations](../../../reports/vnext/milestones/actual-input-review.json) against the exact r4 executable. These are agent-operated checks on the development computer, with zero external participants. Screenshot paths/hashes, observed states and remaining omissions are preserved in that record.

| Surface | Executed scoped result |
|---|---|
| Solo 1280×720 | PASS: cold startup with existing checkpoint, Load, Bellback at D2 with gold 9 and 50.5 seconds, scout privacy and return, keyboard cursor to E2, labels and Exit |
| Solo 1600×1000 | PASS: three Bellback purchases merged to two stars; deploy C3 and keyboard-move D3; buy XP to level 4; insufficient-gold request preserves state; save and exit |
| Solo 1920×1080 | PASS: a new process restores the two-star Bellback at D3, level 4, gold 3, 28.9 paused seconds and purchased-shop state |
| Laboratory 1280×720 | PASS: select next scenario, A/B comparison, physical scenario save, mirror and restore the original formation from the 639-byte save |
| Scripted laboratory at 1280, 1600 and 1920 widths | PASS: 39 boolean checks at each resolution; same-handler exercise, separately identified from the pointer/keyboard checks |

The earlier Windows security dialog was associated with an older r2 process. That process was closed; the final r4 window was exposed normally. No security UI or firewall settings were changed. The local launch disables optional UDP message discovery, as recorded in the actual arguments.

Complete normal-speed tournaments through actual controls at every resolution, actual relic draft/equip and full-bench merge journeys, external novice comprehension, continuous motion/audio review and final-content performance remain untested. Existing usability issues include terse rejection text and scroll navigation. These scoped passes do not close the full human or supported-machine gate.

## Packaged-engine tournament execution

The actual r4 executable ran the existing `-WCRegression=100 -WCProfileName=wonder_vnext` path with `-nullrhi -nosound -unattended -UDPMESSAGING_TRANSPORT_ENABLE=0`. This path is explicitly handled before the successor frontend guard and supplies a complete offline regression report; it does not enable successor multiplayer. The [process record](../../../reports/vnext/milestones/solo-engine-100-r4/process.json) retains the exact executable path/hash, full arguments, start `2026-09-12T16:17:10.4130952Z`, end `16:21:28.1069726Z`, and exit code `0`.

The [full regression report](../../../reports/vnext/milestones/solo-engine-100-r4/regression.json) records **100 of 100 trials passing**, consecutive seeds 1–100, `complete=true`, `failed=0`, `evidence_write_failed=false`, the exact frozen source digest, **4,288 rounds and 18,685 encounters**. Its executed-binary SHA-256 matches the final manifest's actual executable. The report includes each round's logical hashes and settlement state and every encounter's kind, winner, completion, ticks, timeout and survivors. This is actual packaged-engine simulation evidence; it contains no rendering, audio listening, human play, network transport or frame-time acceptance.

## Native 1,000 and exact engine reconciliation

Executed once against the final frozen content, preserving the complete batch:

```powershell
& .\tests\runtime\run_vnext_tournament.ps1 -Tournaments 1000 -FirstSeed 1 `
  -OutputDirectory '.\reports\vnext\milestones\solo-native-1000'
```

**PASS: 1,000 complete native tournaments, seeds 1–1000.** Compilation and process exit codes are `0`, and all seven recorded source/header/harness hashes remained unchanged during execution. The [process record](../../../reports/vnext/milestones/solo-native-1000/process.json) records start `2026-09-12T15:49:39.1653320Z`, end `16:32:56.6445085Z`, and native executable SHA-256 `cb68840deee67cf011095f427e43ad8c7be9073ffdc5994244a256a4b107853b`.

The [stdout log](../../../reports/vnext/milestones/solo-native-1000/tests.log) reports **37,673,775 passing checks**, including per-tick checks rather than that many independent scenarios. The [summary](../../../reports/vnext/milestones/solo-native-1000/summary.json) records 37,673,774: it is serialized immediately before the final assertion that bots actually drafted and equipped relics. The process subsequently passed that assertion and exited `0`; no record was rewritten to conceal this one-check bookkeeping difference.

Raw tournament, round and encounter CSVs retain all seeds, **186,984 encounters**, 23,719 relic choices, 25,176 equips and zero rejected bot commands. No seed or encounter was excluded. The native runner records its actual compile command and x64 Visual Studio environment setup. The shared simulation sources and generated header were separately matched by SHA-256 against the final package manifest.

Executed reconciliation:

```powershell
python tools/vnext/analyze_runs.py `
  --native reports/vnext/milestones/solo-native-1000 `
  --engine reports/vnext/milestones/solo-engine-100-r4/regression.json `
  --output reports/vnext/milestones/solo-engine-100-r4/reconciliation.json
```

**PASS, zero verification errors.** Every paired tournament clock, all **4,288 round pre/post logical hashes**, and all **18,685 encounter** identities, kinds, winners, ticks, timeouts and survivor counts agree. Native coverage, encounter totals, phase durations, relic counters, source stability and contiguous seed/round/index coverage also reconcile. See the [analysis](../../../reports/vnext/milestones/solo-engine-100-r4/reconciliation.json) and [log](../../../reports/vnext/milestones/solo-engine-100-r4/reconciliation.log).

The [final source/executable binding and strata record](../../../reports/vnext/milestones/solo-engine-100-r4/final-binding-and-strata.json) checks the five shared compiled simulation/header files against the package manifest, identifies the two native-only harness files separately, checks the engine process's executable hash against the actual packaged binary, and records SHA-256 for every input report. This completes the **1,000 native + 100 packaged-engine technical regression count for this exact six-creature candidate**. It does not close the other M7 requirements.

## Final-content pacing findings

Strata below count every row of the same frozen native encounter CSV. A timeout rate is the count of `timeout=1` divided by the encounter denominator; neutral encounters are disclosed separately.

| Encounter stratum | Encounters | Timeouts | Timeout rate | Below-2% screen |
|---|---:|---:|---:|---|
| Overall | 186,984 | 26,219 | 14.0221% | FAIL |
| PvP | 101,862 | 23,377 | 22.9497% | FAIL |
| Ghost | 7,219 | 2,842 | 39.3683% | FAIL |
| Neutral | 77,903 | 0 | 0% | Disclosed separately |

**187 of 1,000 tournaments reached the round cap (18.7%).** Round caps are distinct from combat timeouts; no new numeric cap target is invented here. Median accelerated simulated tournament duration was **31.3608 minutes**, so the existing automated 35–45-minute sample target is also false. Median preparation/combat/settlement durations were 2.90375/24.93167/3.5 minutes, respectively; phase totals reconcile per tournament, and their separate medians need not add to the overall median.

The final solo catalogue is distinct from both arms of the Root75 experiment. Its owned-team relic policy and catalogue identity require this fresh evidence; older control or failed Root75 results are not substituted. The tuning screen remains failed. These accelerated all-bot durations do not establish normal-speed human pacing, enjoyment, retention, or superiority over Auto Chess, and the technical reconciliation pass does not approve the observed timeout or cap behavior.

## Acceptance boundaries that remain open

| M7 requirement | Status of this work |
|---|---|
| Exact final package/source identity | PASS for the recorded r4 Development archive, 81 source files and 49 package files; not release acceptance |
| 1,000 native and 100 packaged-engine tournaments on frozen content | PASS: exact source/binary binding, all requested seeds, 4,288 paired rounds and 18,685 paired encounters reconcile with zero errors |
| Accepted pacing and timeout behavior | FAIL for the automated below-2% timeout and 35–45-minute median sample screens; normal-speed human pacing remains untested |
| Reproducible clean-checkout build | Not run. Checkout byte stability and exact package identity are narrower evidence |
| Complete supported-machine installation and cold launch | PASS for scoped r4 cold launches/restoration on the development computer; independent clean-machine installation remains untested |
| Human full tournament, results, save/resume, restart and settings journey | Scoped real input and separate scripted completion passed; full normal-speed control journeys and external human usability/comprehension remain untested |
| Twenty-unit final-content 1080p performance and minimum specifications | No minimum hardware promise follows from headless/accelerated bot tests; required final-content and additional-hardware measurements remain open |
| Approved three-pilot art slice and expanded release ecosystem | Six proxy heroes, no active runtime traits and the existing art-stage boundaries remain explicit |
| Required successor remote release journey | See [M6 engineering evidence](M6_ENGINEERING_EVIDENCE.md); real authenticated 2/4/8-human sessions and independent remote devices are not accepted |
| Owner release and comparative claims | No asset/release signoff or external comparative study is inferred from passing automated checks |

The stop criteria in [the milestone plan](DEVELOPMENT_MILESTONES.md#11-m7--freeze-and-verify-the-release-candidate) remain in force. Preserved failed candidates are evidence, not replaceable noise. An offline-only release would require an explicit scope revision; this engineering checkpoint does not silently remove M6 or mark M7 complete.
