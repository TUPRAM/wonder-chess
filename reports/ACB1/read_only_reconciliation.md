# ACB1 game preparation — read-only reconciliation

Inspected 2026-09-09 local date by the delegated game-reconciliation agent while the root agent performs Ada closure. No game was launched, no build/test was executed, no profile/package/source/state file was changed. This report is preparation for the required actual normal-speed play and one-issue closure, not completion of ACB1-GAME.

## Current candidate identity

- Current repository: `C:/Users/iputu/Documents/Wonder Chess`, branch `main`, HEAD `9623fd82f98ff80a90985b9f552d8851ccece30f`. This matches the public snapshot named by ACB1; the working tree has newer uncommitted art/MCP work.
- Canonical project: `game/WonderChess.uproject`; engine association 5.7. Existing Shipping receipt records **UE 5.7.4**, changelist 51494982 / compatible changelist 47537391.
- Existing intact package: `builds/WonderChess-Update24-Checkpoint-r4/Windows/`.
- Launcher: `WonderChess.exe`, SHA256 `38a46da697e48af83ec0105bd68b44073d95b3b902f710d53ac3f2280d6e8058`.
- Actual payload executable: `WonderChess/Binaries/Win64/WonderChess-Win64-Shipping.exe`, SHA256 `67b00eeca8f60f6f8bc62df95fb833f1174f3a3c086ef9c452b39ea0262af0f0`.
- Immutable original provenance: `reports/WC-U430/20260907T171400Z-protocol-fix/provenance.json`, SHA256 `803716ab43aeb861d5efffd13c348438a651a2d676240a40c49492b47be35d33`.
- **Verified this preparation:** all 31 packaged-payload files, totaling 604,245,301 bytes, still match recorded SHA256. Actual file set has 31 files, no missing or unexpected files after the provenance contract's `Saved` exclusion.
- **Verified this preparation:** all 16 canonical-data entries, 6 generated-data entries, 3 game-config entries and project descriptor match this package's recorded inputs. Profile `alpha_24`, schema `3.1.0`, balance `alpha_24_v0.4.1`, protocol 6; catalog digest `95509d001ca0e6c55fa64a616df6e2e9a01a3809a9b9c82d9bd0a725dad3a1ec`.
- Of 38 recorded game-source entries, only the three already dirty AQ1 presentation files differ: `WCAnimationReview.cpp`, `WCBoardPresenter.cpp`, `WCFrontEndScene.cpp`. Their diff adds bounded opt-in Ada candidate mesh/animation routing and texture-readiness gating. Preserve these changes on any later build. Default presentation paths remain the established roster paths when the opt-in argument is absent.
- Original package source checkpoint was committed as `7f50c6c`; newer repository documentation commits and dirty editor work do not make this old binary a rebuilt candidate. Ada HP1 r016 is not the package's Ada source revision 9.
- Prior package directories, including r3, r4 and historical twelve-hero candidates, remain present. Do not overwrite or select the historical package accidentally.

## Normal-speed launch and profile preservation

The simplest observed source-supported launch is the intact r4 launcher, then **Play > Solo**; **Heroes** opens the 24-hero gallery. No launch was performed here.

`tools/unreal/launch_alpha.ps1` exists and has verified parameters, but its default `Executable` still points to the historical `WonderChess-Alpha-Candidate` directory. Always supply the actual Update24 r4 launcher:

```powershell
& './tools/unreal/launch_alpha.ps1' -Mode Play `
  -Executable './builds/WonderChess-Update24-Checkpoint-r4/Windows/WonderChess.exe' `
  -Speed 1 -EvidenceDirectory './reports/ACB1/<new-run>/normal-speed'
```

The evidence path above is a placeholder to replace with a fresh owned directory. This command is prepared, **not executed**. Do not add `-Exercise` or `-RestartOnce` to the human/interactive-agent run. The wrapper's Play mode uses 1920x1080 windowed dimensions; `-EvidenceDirectory` adds WCProfile/WCShots/WCEvidenceDir and an absolute log. Native control is the required input route. A direct inner Shipping launch must preserve the wrapper's verified `WonderChess` project argument, cwd and quoting. `-WCFast=1` is normal speed, not an acceleration pass; no fast flag defaults to 1. F9 captures a game screenshot, Escape/right mouse cancel or open options, Tab/Enter provide focus/activation, Space readies during eligible preparation. Actual UI discovery still takes precedence over source assumptions.

Preserve this existing profile before testing settings persistence:

- `C:/Users/iputu/AppData/Local/WonderChess/Saved/Config/Windows/GameUserSettings.ini` (1,226 bytes), SHA256 `9223aae0895632fb0a3f081f6697b8f3e59ff56cdcff2fe0f1fa8ae31c07dfd9` at inspection.
- Existing `Engine.ini` beside it, and user Saved/Crash records, must remain intact.
- Current stored game settings: English, master approximately 0.6, music 0.25, effects approximately 0.6, reduced motion false; 1920x1080, windowed-fullscreen value 1. These were read, not changed.
- Repository DefaultEngine specifies D3D11, TAA, 60 FPS cap and 100% screen scale. These are configured defaults, not fresh measured graphics results.

Do not render Blender or build/profile concurrently with the normal-speed game sample. Native input is shared with the user/root; this agent has not taken desktop control.

## Feature-to-evidence boundary

All gameplay outcomes below remain historical until the root performs the current-session run. A package hash match permits identifying the historical candidate; it does not convert historical manual/listening gaps into passes.

| System | Preparation classification | Existing evidence / next observation |
|---|---|---|
| Candidate identity | Verified this preparation, byte/input scope only | Complete 31-file payload and data/config hashes above |
| Launch/menu/settings | Historical report only | r4 launcher exists; current menu interaction, settings persistence and return not run |
| Hero gallery | Historical report only | `reports/WC-U430/20260907T171400Z-protocol-fix/gallery1080/20260907T172238-frontend-audit.json`, 531 historical checks; all 24 manual usability rows remain open |
| Shop/bench/formation/traits | Historical report only | Existing runtime transactions and selection-rejection fixture; exercise native click/drag, rejected moves, full bench merge, scouting and home |
| Combat/tournament | Historical report only | r4 packaged100 and matching native100; interactive whole-match progression not run here |
| Player journey | Historical report only | r4 restart audit used legal scripted commands and acceleration, not manual/interactive-agent play |
| Networking | Historical report only; physical device access blocked | r4 same-machine 2H6B loopback exists; second physical PC not supplied |
| Recovery / remote eight humans | Source-defined limitations | Two-human cap and no current in-match reclaim; detailed below |
| Assets/motion/audio | Historical capture only; approval open | 168 hero and 40 neutral clip records; no listening or continuous approval here |
| Performance | Historical report only | 150-second r4 opening, not whole-match/busy/gallery; no fresh measurements here |

## Recovered timeout and selection investigation inputs

The matching native dataset remains at `reports/WC-U450/20260907T170300Z-closeout/native100/`. `summary.json` binds its digest to the exact r4 catalog. `encounter-outcomes.csv`, `compositions.csv`, `bot-decisions.csv`, `round-economy.csv`, `tournaments.csv`, ability and trait coverage are present. Packaged batch evidence remains at `reports/WC-U450/20260907T172100Z-r4/packaged100/regression.json`; its trials include deployments, command/rejection counts, placements, fight/timeout/ghost counts and hero-use tables.

I recomputed the following from the **historical** encounter CSV. This is a new read-only analysis of old events/outcomes, not fresh tournament execution.

| Mode/wave | Encounters | Timeouts | Seat-A / human-side wins |
|---|---:|---:|---:|
| PvP | 6,288 | 1,656 | 3,090 |
| Ghost | 524 | 155 | 256 |
| PvE waves 1/2/3/5/10 | 800 each | 0 each | 800 each |
| PvE 15 | 781 | 1 | 780 |
| PvE 20 | 547 | 12 | 431 |
| PvE 25 | 309 | 17 | 249 |
| PvE 30 | 132 | 1 | 32 |
| PvE 35 | 14 | 2 | 13 |
| PvE 40 | 2 | 0 | 0 |

Totals reconcile: **1,844 / 12,597**; PvP **26.34%**, ghosts **29.58%**, PvE **33 / 5,785 = 0.57%**. Most timeouts are PvP/ghosts. Round-30 losses are largely not timeout adjudication. Do not fix the global timeout rate by tuning wave 30 or blindly nerfing healing.

The retained CSV does **not** contain tick-by-tick path/target/idle or effective damage/heal/shield trajectories. Native `bot-decisions.csv` records chosen action/utility terms but lacks offered hero identity, rejected/unselected candidate scores and opportunity denominators. `compositions.csv` gives deployed/bench unit identity, cost derivable from the catalog, level/gold/round, but cannot recover every unpurchased offer. Do not infer Neris weakness from the historical 69 unit-rounds versus Dagna 12,366. A fresh bounded replay/instrumentation is required for causal classification.

Useful source locations:

- `Private/Simulation/WonderSimulation.cpp:372` FindPath, `:422` ChooseEnemy, `:790` effective heal, `:794` shield, `:843` timeout assessment, `:969` action/target/movement decisions. Preserve these mechanics unless a fixture proves a bug.
- `Private/Simulation/WonderTournament.cpp:42` SkillBudget, `:83` Evaluate, `:928` FormationScore, `:1015` candidate choice, `:1055` utility deltas, `:1069` weighting, `:1157` chosen-action log. Candidate class weighting gives guardian the frontline factor, priest support, and other classes damage, while role coverage separately counts warrior as frontline: a policy hypothesis to test, not a demonstrated balance defect.
- `Private/WCMatchHUD.cpp:398` CanEdit, `:1760` click, `:1766` drag release, `:1986` purchase/placement action path; `Private/WCMatchRuntime.cpp:1050` acknowledgment completion, `:1057` correlated reply, `:1175` intent queue. These are likely focused locations if native play reproduces selection/rejection frustration.

CSV SHA256: encounter outcomes `17210816837af20bd2a4eecb33da5932423b9f32bbf1b0a6f92730d8b9db425b`; bot decisions `69c7433fb6739f119fafb4c034521792b19a2fe7a863b91438d1277beca49dc8`.

## Physical and remote network path

`docs/current/PHYSICAL_LAN_WC_U460.md` and `tests/runtime/run_physical_lan.ps1` exist. The launcher defaults to preflight; actual launch needs the unchanged provenance, complete local package on each PC, host's real private IPv4/unused UDP port, distinct physical machines and new evidence directories. `-InputMode manual -SimulationSpeed 1 -Launch -Visible` is the source-supported interactive route. Do not substitute loopback for physical evidence. No second PC/address/access has been provided to this agent.

Current code is explicitly limited to two humans:

- `Private/WCMatchRuntime.cpp:124` PostLogin rejects when a Match already exists or Controllers >=2.
- `:137` Logout installs the bot immediately for a departed match seat.
- `:155` RequestEntry rejects humans >2; `:189` StartTournament permits only 0/1/2; `:195` requires exactly two connected humans in LAN mode.
- `Private/WCMatchHUD.cpp:1899` host route uses `listen?WCHumans=2`; start/restart requests two for network mode.
- Only `WonderChess.Target.cs` and `WonderChessEditor.Target.cs` are present under game/Source; no dedicated-server target exists. No implemented authentication-backed seat reclamation was found in these session paths. Existing behavior rejects in-match joins and continues a departed seat under bot control.

Therefore 4H4B, 8H0B, dedicated deployment and authenticated recovery are real future implementation/test gates, not features proven by the LAN menu. Do not just lift the cap or use a display name as reclaim authentication. Choose hosting/build/distribution and seat-identity requirements explicitly before the remote lane; no purchase/cloud/public deployment is authorized by this preparation.

## Prioritized issue/test queue for the root

These are investigation priorities. Only identity and source limitations were verified here; none is mislabeled a freshly reproduced runtime defect.

| Priority | Severity if reproduced / gate | Owner | Reproduction or prerequisite |
|---:|---|---|---|
| 1 | S0 progression blocker | Runtime + interactive reviewer | Full normal-speed solo through elimination/spectating/results/restart; retain first failed baseline if stalled/crashed |
| 2 | S0 economy/ownership corruption | Runtime | Near-deadline/rapid repeated transactions, failed buys, swaps and full-bench merge; compare acknowledged authoritative state |
| 3 | S1 usability | HUD + interactive reviewer | Native select/place/drag/reject/scout/home at actual resolution; screenshot exact input and outcome |
| 4 | S1 timeout mechanic if pathological | Simulation | Replay named PvP/ghost timeout from historical seeds with target/path/idle/effective contribution trace before tuning |
| 5 | S1 beta networking gap | Network | Physical 2H6B requires second actual Windows device/address/operator; current gate blocked by access |
| 6 | S0/S1 beta recovery gap | Network/product | Current source rejects in-match join; define authenticated reclaim/grace/handover and then prove exactly one authority |
| 7 | S1 beta eight-human gap | Network/build | Current hard cap2 + absent Server target; decision and bounded source-backed implementation plan required |
| 8 | S1 misleading strategy/policy if confirmed | Bot/simulation | Add offer/affordability/candidate/deployment opportunity denominators and test Neris/Dagna policy bias separately from stats |
| 9 | S1 severe load if reproduced | Runtime/performance | Uncontended full match, max12 visible PvP, max simultaneous PvE, gallery24, transitions; current150-second sample insufficient |
| 10 | S1 presentation/audio if blocking comprehension | Art/audio/UI reviewer | Actual display-scale effects/contact and audible stacked playback; silence or sampled stills cannot close listening |

The historical-default path in `tools/unreal/launch_alpha.ps1:4` is also a concrete launch-risk candidate: omitting `-Executable` selects the old package. It is easy to correct and verify if no more consequential runtime issue is reproduced, but should not displace the requested native play audit.

Next three executable tasks after Ada closure: (1) preserved-profile r4 native-input normal-speed whole match and highest-impact reproducible issue closure; (2) targeted timeout replay plus offer-normalized policy diagnosis using matching source/data; (3) physical 2H6B when the real second machine is available, alongside explicit current-source-to-remote-eight-human implementation decisions. Art acceptance is not a prerequisite for these tasks.
