# Source basis, changes and external references

## Source hierarchy

The user selected Wonder Chess, a fresh codebase, detailed heroes, Blender/Unreal production, and a first playable tournament with bots replacing seven future humans. The supplied high-fantasy prompt establishes six races/classes, 24 detailed units, simple skills, shared data, and original fantasy art. The v2 prompt specifies initial combat/asset contracts. The subsequent Playable-First Decision Brief proposes twelve heroes and an eight-seat bot alpha instead of website-first delivery.

Files consulted: `High_Fantasy_Auto_Battler_Master_Prompt(1).md`; `Wonder_Chess_Master_Implementation_Prompt_v2.md`; `Wonder_Chess_Playable_First_Decision_Brief.md`; earlier visible first-run instruction. They remain unchanged. This package is a new active implementation proposal, not an assertion that the source already contained these named heroes or exact detailed rules.

## Explicit v3 changes

1. First acceptance is a packaged 1H7B Unreal tournament, with 0H8B regression and 2H6B authority checks. Website-first sequencing and six-only public roster are removed.
2. All 24 heroes now have complete authored identities, art, biography, tactics and numerical active abilities. Twelve are alpha; twelve are expansion-only and excluded from the shop/cook gate.
3. Four alpha races each have three heroes; six classes each have two. Only two-unit thresholds activate in alpha. Full-roster four-unit design values remain separate and unadvertised.
4. Priest support potency now scales positive active attack-speed buffs as well as active heals/shields. This makes Elin’s skill compatible with her class benefit. Damage-only Mage buffs still do not invent damage on Neris’s nondamaging future skill.
5. The proposed eight-seat economy is made exact: 60 health, 24-round cap, 10 gold, three costs, specified shop odds/XP/interest and independent draws.
6. Ghost donor/recipient, pending projectiles, same-tick release order, elimination ties, disconnect policy and movement-corner rules are explicit rather than deferred to coding guesses.
7. Blender authoring clips use 60 FPS, aligned to 50 ms tick multiples. Rig families, per-hero output paths, generated dossiers and content adapters are supplied.
8. Source text data is canonical. Generated docs/Unreal-shaped rows have executable drift checks. The reference library tests limited numerical/economy/pairing/settlement contracts, not the full game.
9. The first Codex prompt pursues the complete assignment through internal checkpoints; it does not intentionally stop after bootstrap or bulk biographies.

All character names, world geography, specific palettes, numerical balance and bot coefficients are original proposals created for this kit. No external source validates their artistic quality, balance or market success. No name/trademark clearance is claimed. Core translations are draft.

## Primary technical references checked on September 6, 2026

Reference links are for Codex to re-check against the actual installed version. They support platform capabilities, not the proposed game's outcomes. Some documentation URLs redirect; prefer the official current endpoint. Several Blender manual fetches failed during preparation; the FBX API search result was accessible, but installed-version behavior remains unexecuted.

| ID | Reference | Use and limitation |
|---|---|---|
| T1 | `https://developers.openai.com/codex/guides/agents-md/` | Project instruction discovery; redirected to official ChatGPT Learn documentation. Does not grant local editor access. |
| T2 | `https://developers.openai.com/codex/skills/` | Reusable skill instructions and scripts; not proof a third-party helper is installed. |
| T3 | `https://docs.blender.org/api/main/bpy.ops.export_scene.html` | FBX selection, scale, axes and animation settings. Development/main reference may differ from installed release; inspect operator RNA. |
| T4 | `https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html` | Command-line invocation reference; page fetch unavailable in this session. Verify installed `blender --help` before using flags. |
| T5 | `https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python` | Unreal Python is editor tooling, not the shipped gameplay runtime. |
| T6 | `https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-quick-reference-in-unreal-engine` | GameMode/GameState/PlayerState responsibilities; actual bot/private-state routing still needs implementation. |
| T7 | `https://dev.epicgames.com/documentation/en-us/unreal-engine/data-driven-gameplay-elements-in-unreal-engine` | DataTable rows need matching FTableRowBase structures/field names; generated JSON alone is not an imported table. |
| T8 | `https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine` | Engine FBX mesh/animation pipeline and compatibility considerations; Blender round trip remains to be executed. |
| T9 | `https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine` | Authoritative networking and need for real multi-instance tests. Bots alone do not validate internet play. |
| T10 | `https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project` | Build/cook/stage/package path; only an actual packaged run proves the delivered executable works. |

## Evidence boundaries

This session had ordinary Python and a C++ compiler available. Blender, Unreal Editor and PowerShell were not available on PATH. The package validation report records exactly what was executed. No `.blend` files, original model renders, imported `.uasset` files, compiled Unreal module, network sessions, complete combat simulations or playable `.exe` were created or tested here. The purpose is a detailed, executable handoff to the environment with those applications.
