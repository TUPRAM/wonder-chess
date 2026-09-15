# First integrated 2D slice — r15

**Owner approved this scoped slice on 13 September 2026: "I approve the slice".** Its implementation and verification below remain historical r15 evidence. The authorized larger collection and reference-inspired interface are now in [Storybook r20](STORYBOOK_READOUT.md). Explicit 2D Art Slice launchers preserve r15; the main Project Support launchers select r20. The full B0–M7 programme remains unfinished.

## What changed

The owner authorized one integrated sample. It now contains:

- One native Slate shop-card family across five real Solo offers, with live names, costs, abilities, owned-copy/merge feedback and normal/hover/pressed/disabled/focus states. The Lab uses the family for its Bellback palette entry.
- Bellback's painted portrait study, with warm face, bark/moss, anatomical-right branch and dorsal bronze bell. The current 3D board creature remains a proxy; final modeled forms and portrait agreement are not accepted.
- Heavy Bloom's bronze flower/weighted-seed icon in actual inventory/draft entries, plus a separately labeled study. It is never falsely equipped on incompatible Bellback.
- Backed health/mana bars and star pips. Zero mana is empty; passive controls have no mana track.
- Green check/border, red X/hatch and neutral inspection marks tied to the real destination rules. Placement prompts hide during combat.
- Quiet limestone on all 64 existing tiles.
- Native pooled kite projectile, tapered ribbon, six-ray impact and compact spiral/five-point stun stars. Existing events and status duration remain authoritative. Deeper semantic colors and a minimum visible line width improve contrast on stone.

The cards and effects have editable native code sources. They are not claimed as SVG exports or raster animation sheets. Live text/stats are separate from the three illustrations. No gameplay code or canonical data changed.

## How to try it

Open `C:\Users\iputu\Documents\Project Support\Wonder Chess`:

| Launcher | Opens |
|---|---|
| Play Combat Clarity - Lab.cmd | Current Storybook r20 formation laboratory; see the new readout |
| Play Combat Clarity - Solo.cmd | Current Storybook r20 solo interface; see the new readout |
| Play 2D Art Slice - Lab.cmd / Solo.cmd | Explicit aliases for the same r15 modes |
| Play Combat Clarity r13 - Lab.cmd / Solo.cmd | Preserved comparison build |

In Lab, inspect the portrait, Heavy Bloom and selected Bellback card in the rail. Choose creatures and hover formation destinations. Start combat for projectile/impact review. **Status effect test** demonstrates actual healing/shield/stun duration through synthetic test abilities; it does not give new skills to Bellback or Cragstoat. **Reset to formation** restores the normal formation.

In Solo, use the real shop. Matching copies merge automatically. **Pause / Resume clock** holds preparation while inspecting the interface. The launcher selects the same 20-mana combat-clarity experiment as r13. Prices, damage, targeting and mana rules remain unchanged.

The friendly launchers use the real Windows package-cache path, avoiding the inaccessible short MSIX-redirected worktree path.

## Verification

| Check | Actual result |
|---|---|
| Unreal 5.7.4 Development build/cook/package | PASS, r15 |
| Python suite | 230 tests PASS |
| Data/specification validation | 400 checks PASS |
| Required document/catalogue generation checks | PASS |
| Lab at 1280×720 and 1920×1080 | 49 Boolean checks each PASS; captured screens inspected |
| Status test at 1920×1080 | 15 checks PASS; active/expired captures inspected |
| Solo at both resolutions | 24 checks each PASS, including completion/restart, relics, save/resume and phase restrictions |
| Original presentation mode in new binary | 41 Lab checks PASS |
| Packaged engine contracts | 2,929 combat-clarity assertions and 581 mana assertions PASS |
| Exact package identity | 93 source files / 49 package files PASS |
| Cooked texture sizes | Runtime logs verify portrait 1024², Heavy Bloom 512² and stone 1024² |
| Physical r14 input | Pause, three real Bellback purchases, gold 10→7, merge feedback and two-star bench merge observed |
| Final r15 physical focus/purchase recheck | **NOT RUN — owner stopped Computer Use with physical Escape. No further Computer Use calls were made.** |
| Human art approval / external study / public release | OPEN |

Inner executable SHA-256: `3c20c2b70cdc9eb6e0edb9d6614663ff69e624b0486d97387dd7374244fb9b7f`.

[Verification](../../../reports/vnext/milestones/2d-slice-20260913/verification.json), [package manifest](../../../reports/vnext/milestones/2d-slice-20260913/package-r15-manifest.json), [source packet](../../../art-source/2d-slice/r001/README.md).

## Findings and corrections

The first Heavy Bloom output painted a checkerboard instead of producing transparency. It was rejected and never imported. A targeted built-in image-generation edit replaced it with an intentional dark background. All chosen sources are opaque RGB at 1254²; Unreal resizes them during cooking. The immediate import report's `built_size` was an editor source-size observation; the later packaged runtime logs establish the actual cooked sizes. Transparent cutouts and layered art remain future work.

Initial compile name-shadowing and narrowing errors were fixed. An initial Python child command selected Unreal Python without Pillow; rerunning with the exact existing authoring interpreter passed all 230 tests.

The r14 Lab HUD assertion ran before the first presentation update, when no piece views existed. The identical substantive check now runs after a settled preparation capture and passes at both resolutions.

The real pointer test exposed a white rectangle covering focused shop cards after purchase. The custom focus overlay had used the drawing API's default white fill. Explicit transparent fill preserves the outline and avoids covering the content. This fix is compiled into r15, but its physical visual recheck was interrupted by the user's Escape action.

The first light-stone capture made placement, stun and healing cues too pale. Deeper colors and visible line widths resolved that issue in r15 screenshots. A separate reviewer found no further new screenshot defect requiring another revision before owner review. Thin speckling along some combat grid lines predates this slice and remains an existing presentation limitation.

The authoritative simulation/data control inputs match r13. These results do not establish enjoyment, accepted pacing, final character models, final-content performance or a public-qualified demo.

## Next development order

1. Review this integrated slice and complete the interrupted physical focus/purchase check. Decide whether the palette, portrait framing and effect contrast should guide the larger batch.
2. Produce the remaining five current-hero portrait studies and six ability icons, using each identity dossier. Final portraits still depend on accepted modeled identity.
3. Complete the twelve canonical relic icons with distinct silhouettes; do not add an unrelated crafting tree.
4. Extend the selected UI family to bench, inventory, resources, scouting and results; then finish each hero's attack/cast/impact cues and upgrade/death presentation.
5. Continue the separate accepted-model route and Wondergrove surroundings, then perform complete-game visual, performance and human playtesting. Bellback's forms remain ART_REVISE, and pacing/release gates remain open.

Work remains local, uncommitted and unpublished on `codex/milestones-b0-m7-20260912`. Prior candidates, user work, approved reference records and r13 are preserved.

Technical sizing reference: [Epic's texture resize modes](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/ETexturePowerOfTwoSetting__Type?lang=en-US). Installed APIs and actual runtime logs verified the implementation.
