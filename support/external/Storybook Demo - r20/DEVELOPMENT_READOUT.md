# Storybook interface and collection — r20 candidate

The owner approved the integrated r15 slice and authorized this expansion on 13 September 2026. The new local candidate combines the complete current collection with a native preparation interface based on the owner's original REF02 attachment.

## Implemented scope

- Five additional portrait studies: Cragstoat, Grandmother Root, Snapvine, Prism Organ and Reefglass; reuse approved Bellback.
- Six distinct ability illustrations: Sheltering Bell, Stonebound Lunge, Stay and Blossom, Thornline, Crossing Hymn and Leading Tide.
- Eleven additional relic illustrations, completing twelve with Heavy Bloom. The long/close lens, tall/wide hourglass and wick/lantern families use different outer forms.
- A separate painted sanctuary backdrop: framing roots, hanging bronze bells, white flowers, distant ivory ruins and open sky behind the actual 3D board.
- Native bronze/ink/parchment panels with live recruitment, bench, resources, scouting, inspection, relic draft/equipment, save recovery, recap and final results. The ten-slot bench sits above the five-card shop. Trait counts explicitly retain their inactive-bonus status.
- A Collection view showing all current portraits, abilities and relics, with 64/32-unit icon samples and canonical descriptions.
- Original static Cinzel Regular/Bold fonts, bundled with the full SIL Open Font License from the designer's repository. No system-font installation is needed.
- Distinct seed/leaf, barbed thorn, faceted glass and crescent-water ranged projectiles, directional guard/wave effects, actual charge footfalls, thorned resolved lashes, true-death departure and completed-merge presentation.
- A fitted perspective camera with the full 64-cell board kept inside its live input region. The painted sanctuary is upright behind the board; it contains no baked text, click targets, values or creature models.

Painted artwork is separate from live text, values and click targets. Source PNGs are flattened opaque RGB paintings, not layered PSDs or SVGs. Native C++/Slate owns responsive layout and states. Character models remain gameplay proxies; these portrait studies do not accept or replace final modeled forms.

## Verified local candidate

The source import completed with 23 new textures and one new backdrop material in `ArtExpansionR001`. First native compilation passed. The package build caught and corrected a JSON shared-reference error in the new visual-exercise report; its failed log is preserved. Authoring checks passed: 230 Python tests, kit validation, document generation, legacy catalog generation and successor catalog generation.

The earlier r16 source caught a shared-reference report compile error, then packaged successfully. Its graphical and physical input review exposed an inverted backdrop, washed-out disabled cards, stock progress bars and a flat camera. r17 corrected those and passed eight graphical runs, but visual review still found clipped shop labels at 720p and a stretched Lab ability illustration. Source review found a modal keyboard-priority edge case. r18 corrected sizing but introduced a native visibility-binding regression: six modal siblings were visible/enabled. Its exercise records initially passed because they did not consume the new modal diagnostics; screenshots and logs correctly rejected that candidate. r19 binds the attributes on the actual constructed widget and the runner now rejects nonexclusive modal logs and checks real focus ownership. All failed attempts and earlier package evidence are preserved.

The final r20 package passes eight graphical runs: Lab at 720p/1080p, status cues, Solo command/lifecycle exercises at both resolutions, nine-stage Solo visual captures at both resolutions, and the preserved unstyled Lab comparison. All 64 board centers and native click projection roundtrips pass, with board boundaries kept inside the input aperture. Native status appearance/expiry, four ranged cue identities, actual death departure, completed merge presentation, save/resume, draft/equip, scouting privacy and finished-tournament/restart checks pass. The visual journeys accelerate the actual tournament; they are not normal-speed human sessions.

Both packaged combat-clarity and mana contract suites pass. Exact identity verification binds 122 source files to 49 packaged payload files. All 18 frozen gameplay/control source hashes match their pre-expansion values. Source art comprises 23 new paintings, with the approved Bellback portrait, Heavy Bloom icon and quiet stone reused separately.

At 1600×1000, physical input passed purchase and XP updates, disabled-card rejection while keeping art readable, bench inspection, perspective C3 deployment, keyboard movement to D3, public scouting and return, collection navigation/scrolling, and buying again after closing the collection. All six portrait/ability pairs and all twelve relics were viewed in the native collection. Far Hourglass remains thin at 32 Slate units; minor filigree/frays are decorative. The illustrations need owner preference/recognition review. Nine manual captures preserve this scope.

r19 then exposed Unreal's cached enabled state on collapsed widgets: one modal was visible but six retained enabled flags. The stricter runner rejected the candidate. Installed Unreal source confirmed that prepass skips non-visibility attributes for collapsed children. r20 initializes and synchronizes real modal enabled states from an always-ticking host before modal focus/painting; the strict audit remains intact.

Final r20 logs confirm one visible and one enabled modal with native focus for save, draft and results at both resolutions; actual menu/collection input is recorded separately. The branch remains local, uncommitted and unpublished. No clean-machine install, final-content performance gate, final 3D art acceptance or external human study was performed in this expansion.

## How to review the candidate

The delivery folder is `C:\Users\iputu\Documents\Project Support\Wonder Chess`. `Play Wonder Chess.cmd` opens Solo with the reference-inspired player interface. `Play Storybook - Lab.cmd` opens the formation and combat workbench. The familiar `Play Combat Clarity - Solo.cmd` and `Play Combat Clarity - Lab.cmd` aliases also select this Storybook candidate. Explicit r15 art-slice and r13 comparison launchers remain available.

In Solo, use **Pause** to hold preparation. Click a portrait in the shop to recruit, select the bench card, then click a near-half cell to deploy. Three matching copies merge automatically. Click a captain in the right rail to scout, then **You** to return. Side panels scroll. Hover cards for details. Select a creature before equipping a compatible relic from the left inventory. **Ready for battle** advances when all seats are ready.

Open **Menu → Creature & relic collection** for all six portraits, six ability symbols and twelve relics. It shows both 64- and 32-Slate-unit samples with current names and descriptions. The top menu also provides save/load, recap and exit. The new interface continues to use the existing optional 20-mana combat-clarity rules; this art batch changes no activation, damage, cost or target rule.

The reference's tree-and-bell sanctuary, ivory/bronze board, dark side rails, parchment cards, bench-above-shop arrangement and title treatment guide the implementation. The panels remain native controls so purchases, legal placement, scouting, tooltips, accessibility focus and live game state can be maintained independently from the painted imagery. The present 3D figures and basic motion are the largest remaining visual difference from the reference.

## Sources and evidence

- [Expansion brief and authorization](<C:/Users/iputu/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/CodexWorktrees/wc/m7/art-source/2d-expansion/r001/BRIEF.md>)
- [Source/import manifest](<C:/Users/iputu/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/CodexWorktrees/wc/m7/art-source/2d-expansion/r001/asset_manifest_candidate.json>)
- [Exact hero/environment prompts](<C:/Users/iputu/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/CodexWorktrees/wc/m7/art-source/2d-expansion/r001/prompts.json>)
- [Exact ability prompts](<C:/Users/iputu/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/CodexWorktrees/wc/m7/art-source/2d-expansion/r001/abilities/prompts.json>)
- [Relic prompts and revision provenance](<C:/Users/iputu/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/CodexWorktrees/wc/m7/art-source/2d-expansion/r001/relics/manifest.json>)
- [Source inventory](<C:/Users/iputu/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/CodexWorktrees/wc/m7/art-source/2d-expansion/r001/source_inventory.json>)
- [Verification directory](<C:/Users/iputu/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/CodexWorktrees/wc/m7/reports/vnext/milestones/storybook-20260913>)

Owner acceptance of this expanded candidate, normal-speed player experience, final 3D forms and public release quality remain separate from technical verification. This advances M2/B3 presentation; it does not close B0–M7, change the six-creature roster, rebalance abilities or resolve the pacing screen.
