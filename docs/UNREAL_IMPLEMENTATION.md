# Unreal implementation contract

## 1. Project and build first

Create a fresh C++ project at `game/WonderChess.uproject`. Discover installed engine version, compatible Visual Studio/build tools, Windows SDK and executable paths. Use a known working configuration in that environment; do not require the newest release or silently upgrade a project. Record versions in `reports/environment.json`.

Package a minimal menu/map early, launch it outside the editor and capture its log. This validates the actual toolchain before costly art work. A project that plays only in-editor has not passed package acceptance. Python and editor modules must not enter the shipping runtime dependency chain. Technical references: Epic’s packaging, Python editor and gameplay framework documentation in the source log.

Suggested modules: `WonderChessRuntime`, `WonderChessEditor`, and optional isolated `WonderChessTests`. Use the runtime module API macro appropriate to its actual name. Provided row headers are compile candidates with declared names; they are not already-built Unreal binaries.

## 2. Ownership

| Component | Authority / purpose |
|---|---|
| `FWCMatchState` | Serializable seats, phase, round, pairing, frozen results and rule version |
| `FWCSeatState` | Persistent economy, roster, private shop/bench, controller binding |
| `FWCBoardState` | Logical cells, occupants, reservations, deterministic paths |
| `FWCCombatState` | Battle copies, timers, event queue, effects, initiative, outcomes |
| `UWCMatchAuthority` | Validated commands, phase locks, pairing and atomic settlement |
| `UWCDefinitionRegistry` | Load/validate immutable definitions and generated data version |
| `UWCCombatRunner` | Fixed-step simulation of every active encounter |
| `UWCBotPolicy` | Permitted observation → scored intent; no direct state mutation |
| `AWCGameMode` | Server-side session/rule orchestration |
| `AWCGameState` | Replicated public phase, standings, opponent and board summaries |
| `AWCPlayerController` | Authenticated human intent and owner-only reply/state channel |
| `AWCPlayerState` | Public competitor identity and permitted summary, including bot seats |
| `AWCUnitView` | Mesh/animation/health-bar representation of an existing logical unit |
| `UWCObservedEncounterPresenter` | Reconstruct/switch visible encounter without advancing gameplay |
| `UWCUIModel` | UI values and localized labels derived from permitted state |

Names are suggested; ownership boundaries are required. Do not put the entire game in one Level Blueprint, one God Actor, or per-unit Event Tick decisions. Bots do not need fake local PlayerControllers that accidentally receive private replication.

## 3. Data integration

Compile `generated/unreal/WCDataRows.h` in the appropriate public module location before importing its matching JSON rows. Keep field/property names exact. `DT_Units_Alpha.json` and `DT_Abilities_Alpha.json` contain twelve records each. The design24 files are reference content and must not automatically expand the alpha shop or asset cook list.

Canonical text data is outside `Content`; imported `.uasset` DataTables and `UPrimaryDataAsset` presentation definitions live under `/Game/WonderChess/Data` and `/Game/WonderChess/Heroes`. A unit row references stable ability ID, not a guessed display name. A presentation asset references mesh, AnimBP, montage/clip set, materials, portrait and effect/audio assets. Keep numeric balance in generated tables, not duplicated in those presentation assets.

At import, compare all integer values and IDs against the source catalog digest. Reject missing abilities, mismatched versions and unknown selectors. Do not suppress extra/missing-field warnings to make an import appear successful. Write an explicit importer matching the installed Python/editor or C++ API. `fill_data_table_from_json_file` or equivalent is a tool option only after verifying availability and row type; the kit does not pretend an arbitrary JSON file automatically becomes a valid DataTable.

Cook only assets referenced through explicit registry/primary asset rules and selected maps. Loose authoring JSON, Blender source, test-only maps and editor scripts are not required by the shipped build. If runtime JSON is deliberately chosen instead, stage and validate it explicitly; do not depend on the developer’s working directory. The preferred alpha path is cooked DataTables plus presentation assets.

## 4. Combat implementation

Port numeric fixtures first. Use integer centipoints, basis points, milli-rates and a 50 ms simulation tick. Validate bounds before intermediate multiplication. Use one shared effect executor for Damage, Heal, Shield, Stun, Dash and StatModifier; selectors handle areas. Never create a separate code path for each hero when data can express the difference.

Use a bounded catch-up accumulator and profile full-speed/simulated-fast-forward separately. Rendering stalls must not discard combat ticks or generate different results. Long frame catch-up may reduce presentation update frequency, not change the authoritative sequence. Log stalls; do not call an infinite catch-up loop a performance solution.

Events include match/encounter/unit/action IDs, scheduled tick, released state, effect type and allowed payload. Source values are captured at release, areas follow the explicit fixed-center contract, and duplicate event IDs are rejected or naturally impossible under the queue model. Animation notifies request only presentation events and must not apply damage a second time.

The entire eight-seat tournament uses the same runner. No-renders all-bot tests must execute combat, not sampled power-based outcomes. Presentation may interpolate cells and animate actions; collision and animation state do not become authority.

Provide overlays for cell/occupant/reservation, current target, state/timers, action queue, trait sources, active effects and numeric derived stats. Debugging a hero must not require reading a screenshot of a hidden Blueprint graph.

## 5. UI and input implementation

UMG is appropriate for the alpha. Build menu, lobby, HUD, shop, bench, unit inspection, trait panel, standings, recap, pause/options and results as separate widgets/view models. Enhanced Input or the installed supported input system may handle clicks/keys; keep UI focus and world selection distinct.

Drag/drop and click-select/click-place submit the same Move/Swap command. Immediate preview is cosmetic; accept/rollback after authoritative reply. A shop button sends the slot index and revision, not a client-supplied price or unit stats. Clear focus on phase change and avoid stale drag operations when combat begins.

Localize using the supplied draft keys and engine string tables/localization process. Proper hero names can remain stable, while classes/races and tooltips are translated. Ability values displayed in UI derive from tables/evaluator. Do not bake text into portraits or switch the whole UI to images.

## 6. Networking and privacy

The listen-server path is enough for the early 2H6B check; it is not hosted production infrastructure. All public seat summaries and visible formations replicate through explicit public state. Owner-private shop, bench, exact gold/XP and command history go only to their owner. Inspect network data access, not only whether the UI hides a field.

Use reliable RPCs for discrete economic/placement commands with authenticated owner, command ID, sequence and phase/revision checks. Avoid one RPC for every visual interpolation step. Replicate combat state snapshots/events at a measured cadence sufficient for twelve visible combatants; reconstruction must handle joining the observation of an already-running encounter. Dropped cosmetic events cannot change outcomes.

The first twelve hero skills need no complex distributed lockstep. Server authoritative outcomes are the chosen model. Cross-platform deterministic replay is not assumed. Fixed integer calculations and seeded ordering help reproduction, but record the tested compiler/platform/build boundary.

For non-host disconnect: server installs a bot command source preserving the seat; rejoin is unsupported in the alpha. Host disconnect: explicit aborted match, no winner or misleading placement. No host migration or account reconnect promises. Test duplicate requests, stale phase, out-of-order sequences, disconnected spectators and invalid seat access.

## 7. Visual presentation

Rebuild only the selected encounter’s full visual actors. Maintain an actor pool or bounded spawn/despawn strategy after profiling. At eight seats there are up to 48 logical combat units, but normally at most twelve hero visuals in the inspected encounter. Scouting preparation may use frozen public formation views; it must not spawn private bench units or alter active combat.

Use one hero master material and constrained instances. Keep Lumen, Nanite, expensive translucency and complex shadows optional rather than required for the art style. Select a scalable baseline first, and measure GPU/CPU costs before enabling enhancements. Small animated heroes do not automatically benefit from every advanced rendering feature.

Use in-place locomotion and explicit action presentation from events. A target switch reorients the actor without changing logical cell distance. Short hit reactions must not visually cancel a committed action whose result already resolved. Blend to a stable defeated pose/dissolve once; release pooled actors cleanly.

Portraits should come from accepted models, with consistent camera/background and no unreviewed concept/model mismatch. Rare/three-star effects remain restrained so the board stays readable.

## 8. Maps, packaging and release evidence

Proposed maps: `L_WC_Menu`, `L_WC_Courtyard`, `L_WC_AssetReview` (development only), and `L_WC_TestHarness` (development only). Set game/default maps explicitly. Avoid launch paths that rely on whichever level happened to be open in the editor.

Cook the menu and courtyard, primary presentation assets, tables, UI, fonts selected under proper license, effects and sound. Reopen the package from a path outside the source tree. Verify no missing content after an empty derived-data cache where practical, settings save/load, resolution changes, input focus, full match, elimination and restart.

Provide Development build first with logs; Shipping is a separate configuration check. The provided PowerShell wrapper is an inspectable scaffold and must be validated with the installed UAT flags. Never remove failed build logs. A successfully spawned process is not proof it reached the menu; inspect its output and capture the actual window.

Record executable path, engine/build versions, commit/content hashes, exact commands, exit codes, cooked map list, run log, screenshots/video and known issues. No engine binary is bundled in this handoff kit.
