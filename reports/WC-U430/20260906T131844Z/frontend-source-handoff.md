# Native front-end integration checkpoint

Owner: `update_frontend`. Scope: `WCMatchHUD.cpp`, the `AWCMatchHUD` declaration, and new `WCFrontEnd*` presentation code. No maps, binary assets, canonical data, balance files, controller/mode implementations or build configuration were edited by this lane.

Implemented source:

- Native Slate lobby, mode setup, settings, searchable/filterable 24-hero grid, optional showcase, and shared hero detail template.
- Actual separate local scene using existing authored courtyard modules and skeletal hero assets. Seven selectable clip names, rotation, turntable, reduced-motion behavior, selected-star display and local showcase persistence. Missing meshes/clips produce an explicit message.
- Three-star stats use `StarValue`, `AttackInterval` and `MovementInterval`; ordered ability effects and lore come from catalog metadata. Race/class tiers use canonical JSON, and gameplay trait bonuses use `TraitValue`.
- Existing authoritative controller actions handle Solo/LAN. Native screens consume `entryState`, participant readiness, and the integration lane's entry RPCs. Introduction blends to the existing arena camera before a match exists.
- Gameplay HUD preserves shop/placement interactions, switches quick interfaces to canonical short names, handles typed neutral inspection/health bars and eight neutral recap entries, and presents current monster-wave names.

Verification actually observed:

- First Unreal Editor target build compiled `WCFrontEndScene.cpp` and `WCMatchHUD.cpp`, then failed on two Slate API mismatches and an incremental-GC warning in `WCFrontEnd.cpp`.
- Installed UE 5.7 headers were read. The fixes use `ScrollBarAlwaysVisible`, the correct shared-reference brush pointer, and `TObjectPtr` references.
- Second Editor target build exited 0: `reports/WC-U410/20260906T131353Z/editor-build-02.log` and its adjacent JSON.
- The optional audit source was added after that successful build and still requires compilation/execution at this checkpoint.

Reproducible native launch options added:

```text
-WCFrontEndPage=Gallery
-WCFrontEndPage=Detail -WCFrontEndHero=wc_u_human_guardian -WCFrontEndStar=2 -WCFrontEndClip=Active
-WCFrontEndAudit -WCEvidenceDir=<fresh absolute evidence directory>
```

`WCFrontEndAudit` uses actual native Slate navigation for selected actions, view-model enumeration for exhaustive filtering, and catalog/asset presence checks. This is not a physical input test, continuous motion review, or two-machine LAN result. Screenshot/navigation ordering was corrected before the first package: each capture occupies a separate stage, without same-frame screen mutation. It samples Ada, Pippa and Sora, checks written capture files, and tests duplicate/cancel entry only against an idle standalone authority. It still requires actual compilation and execution. Root integration was notified and sources were frozen for the early package operation.

Not yet verified by this lane: packaged Slate interaction, 720p/1080p layout, actual graphical composition, all 24 finished assets, continuous clips, audio listening, or human/LAN matches. The integration lane owns editor/package execution and final evidence. This report does not close WC-U430 acceptance.

## First packaged capture checkpoint — 2026-09-06T13:33Z

The integration lane produced an early Shipping package. The frontend audit executed from that package and wrote eight actual viewport PNGs plus `reports/WC-U430/20260906T133231Z/frontend-720/20260906T133235-frontend-audit.json`.

Observed audit result: **319 passed / 108 failed / 427 checks executed**. All 108 failures were missing extension presentation assets: 12 skeletal meshes, 12 portraits, 84 animation clips. The run checked 72 selected-star stat rows and 75 ordered effect/star rows; it found 12 meshes, 12 portraits and 84 clips. The native Slate selected-action tests, filter fixtures, and standalone duplicate/cancel/introduction readiness fixtures passed. This evidence does not establish human input, two-machine LAN, completed art or continuous animation review.

Visual inspection of actual lobby, gallery, Ada detail and introduction PNGs found unacceptable hero framing behind the left panel, distorted portrait aspect ratio, over-detailed default skill text and an almost black introduction background. These are independent visual failures despite passing functional checks. No visual gate is closed.

Source corrections prepared after those observations: nearby courtyard approach within the existing ground plane; camera offset sign correction and iterative projected-bounds fitting within the model pane; smaller distant planters and actual banner poles; square portraits; readable search input; updated clip selection styling; concise skill effects and optional Advanced details. The foundation top is z=0 after its authored geometry and placement transform, matching hero root height. The integration lane will compile and rerender before these corrections can be called verified.

Outstanding focused HUD work at this checkpoint: neutral silhouettes/behavior before lock, selectable trait contributor/recipient inspection, and final composition/trait comparisons. Audio listening, long-text EN/ID, both resolutions, all-clip motion and restart/human/LAN evidence remain open unless separately proven by the integration lane.

## Corrected engine capture and next source checkpoint — 2026-09-06T14:00Z

The corrected Editor target build passed at `reports/WC-U430/20260906T135707Z/editor-build-corrected`. The subsequent real Unreal runtime captures in `reports/WC-U430/20260906T135947Z/frontend-corrected720` were inspected. Ada and her full weapon now occupy the intended model pane, and concise selected-star skill text is readable. This is engine runtime evidence, not a new Shipping package. Foot/shadow separation, flat scenery and the camera path through roofs remained visual defects.

The next source revision, handed to the integration lane for compilation, adds:

- A short fade covering the perspective-to-orthographic camera cut. Cancel, skip/teardown and return-to-preview explicitly clear any frontend fade. The authority still owns the three-second introduction and first preparation deadline.
- An authored paving patch, a more distant roofline and scoped atmosphere/sun components. Model baseline placement derives from transformed floor bounds and imported reference-mesh minimum, rather than a guessed centimetre correction. Actual CPU-skinned LOD0 minimum and foot-bone heights are sampled only by audit; their results must be inspected before calling contact corrected.
- Known neutral-wave cards during preparation with original portraits when imported, real counts, shared-evaluator HP/basic scaling, range and actual declared ability behavior. No loot or equipment inventory is introduced.
- Selectable two-column trait counts. Trait inspection separates distinct deployed hero types from all matching deployed copies. Tier 4 replaces tier 2; recipient highlights use the observed encounter side and require an active tier. Only public deployment is read. `-WCHUDTrait=human` is an opt-in presentation focus fixture, not evidence of physical input.
- Eight standings sorted by actual placement, with final deployed short names/stars and active trait tiers. Ties retain actual shared placements; only captain-duel wins are labeled as such. Empty final deployments remain explicit.
- An Ada Move sample and introduction captures near 0, 0.5, 1.5 and 2.5 seconds after observing the real Introduction state. Actual request UTC/elapsed times are recorded, not assumed exact frame times. Expensive CPU skin probes and screenshot frames are excluded from performance acceptance.

These new HUD/grounding/transition edits had not yet compiled or executed when handed off. The root integration lane may extend `WCFrontEndAudit.cpp` and its audit-only header fields for an opt-in all-24 Idle/Active traversal at each resolution. That traversal must preserve the distinction between direct view-model selection, native Slate clip events, presence/static capture and continuous clip review.

No character source, export or binary was edited by this frontend lane at this checkpoint. Future hero ownership was narrowed to Rok, Zura and Kesh; all Dwarf folders remain read-only here.

2026-09-06 14:20 UTC — Actual native 720p follow-up

Root's latest editor/HUD/scene build passed. Actual captures in reports/WC-U430/20260906T141900Z/frontend-ground720 were viewed: lobby and seat-introduction-1500ms. The former crop and visible floating feet are corrected in these samples. The audit's actual CPU-skinned LOD0 probe measured Ada Active lowest gap approximately -0.000003 cm and Move -0.086653 cm against the transformed tile top. These single-frame probes are not whole-clip contact acceptance or performance evidence. The intro now reaches the board through the covered camera cut without flying through roofs. It still contained six stale showcase heroes; their exact source was identified in WCBoardPresenter.cpp's phase<0 fallback and handed to the root owner, who reports removing that fallback while preserving WCArtReview.

The native audit executed 428 checks with 108 failures, corresponding to the same missing twelve extension model/portrait/clip sets at that binary's capture time (12 meshes, 12 portraits, 84 clips absent). This is not a full roster pass. Recorded 72 star-stat rows and 75 effect-star rows; 12 actual screenshots were written. Introduction sampling requested frames at actual +0.0000215, +0.511764, +1.519066 and +2.531879 seconds after observed entry. Root now owns the all24 gallery-audit extension and audit-only declarations; do not concurrently edit those files.

Remaining observed visual limitations: the lobby's olive plane/backdrop and cropped facade are flat and require art direction/polish; final character art acceptance remains open. The new gameplay HUD synergy contribution panel, neutral cards and eight final compositions still need targeted rendered inspection; a successful compile alone does not prove them.
