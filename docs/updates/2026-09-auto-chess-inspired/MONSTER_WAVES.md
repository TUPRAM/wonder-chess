# Original monster-round design and authoring inputs

Status: **PROPOSED, NOT IMPLEMENTED OR BALANCED.** This document supplies concrete starting inputs for the runtime owner to migrate into canonical neutral schemas/data. It is not a second runtime configuration. Do not read Markdown tables from the game or hand-copy the numbers into multiple widgets.

## Purpose and schedule

Enchanted creatures and ward constructs participate in the Dawn Compact's field trials. Their defeat dissolves non-graphically like hero manifestations. Use original silhouettes and materials related to Brighthaven, its gardens and beacon network. No reference-game wolves, dragons, meshes, names or loot assets are copied.

Neutral rounds are 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40 under the proposed default cap 40; the classification predicate remains valid for any positive round. Each living seat faces an isolated instance of the same wave. These are not PvP pairings, a shared raid or a ninth seat. The shared resolver publishes the correct wave label and preview to players and bots before preparation starts.

Rounds 1–3 are deliberately forgiving: no captain damage on a loss/draw, no forced shop contents, no hidden stat boost, no private tutorial RNG. Preserve the current starting level 3, 10 gold and shop rules as the first tuning baseline. The user requested introductory monster rounds, not a mandatory one-unit level-one economy. Optional tutorial explains buying, placement and inspection while normal preparation remains actionable.

## Seven neutral archetypes

All values are visible design proposals in ordinary displayed units; convert health/damage/shield to integer centipoints in canonical authoring. Attack/movement rates become milli-rates. Every neutral occupies one tile, has no race/class trait, and uses normal target/path/mitigation/defeat semantics. For creatures without an active skill, represent that absence explicitly rather than using a fake no-op.

| ID / display name | HP | Basic damage / type | Attacks/sec | Range tiles | Armor / magic resistance points | Movement cells/sec | Basic windup / travel ms |
|---|---:|---|---:|---:|---|---:|---|
| wc_n_sprout / Sprout | 220 | 18 physical | 0.70 | 1 | 5 / 5 | 1.00 | 250 / 0 |
| wc_n_thorn / Thorn | 260 | 24 physical | 0.75 | 3 | 5 / 5 | 0.90 | 300 / 200 |
| wc_n_wisp / Wisp | 320 | 22 magic | 0.65 | 3 | 0 / 15 | 1.00 | 300 / 200 |
| wc_n_stoneback / Stoneback | 700 | 42 physical | 0.60 | 1 | 25 / 5 | 0.75 | 350 / 0 |
| wc_n_prowler / Prowler | 480 | 34 physical | 1.00 | 1 | 10 / 5 | 1.20 | 250 / 0 |
| wc_n_sentinel / Sentinel | 850 | 46 physical | 0.65 | 1 | 20 / 15 | 0.80 | 350 / 0 |
| wc_n_warden / Warden | 1400 | 60 magic | 0.65 | 3 | 20 / 25 | 0.80 | 350 / 250 |

| Archetype | Optional active, exact proposed behavior | First / cooldown / cast / recovery ms |
|---|---|---|
| Sprout, Thorn | None; ordinary attacks only | Not applicable |
| Wisp | Spark: 65 magic damage at current enemy within 3 tiles, 200 ms projectile travel; no splash/stun | 3000 / 8000 / 350 / 300 |
| Stoneback | Shell: self shield 180 for 2500 ms, instant at release, normal strongest-shield replacement | 2000 / 9000 / 350 / 350 |
| Prowler | Bound: farthest-enemy-adjacent dash, max 4 tiles; reserve valid empty destination at commit; no damage, immunity or forced displacement | 2500 / 10000 / 350 / 350 |
| Sentinel | Bell shock: stun adjacent enemies for 750 ms at release, no damage, self excluded, max 8 targets | 3500 / 10000 / 450 / 350 |
| Warden | Beacon burst: fixed target-cell area, range 4 / radius 1, 250 ms travel, 130 magic damage to living occupants up to 12 targets; no stun or persistent ground damage | 4000 / 9000 / 600 / 400 |

Basic recoveries derive from effective attack interval minus windup under the common evaluator; movement is tick-quantized. Neutral skills use one magnitude at the authored wave scale, not hero star levels. Shield magnitude scales with wave HP factor; basic/active damage with wave damage factor; durations, range, armor and attack/movement speed remain fixed. This keeps increased difficulty explicit rather than secretly accelerating all actions.

## Wave lineup, formation and tuning curve

Formation coordinates below are **neutral-local** (column, row) in an 8×4 deployment area: row 0 at the back, row 3 at the front. Reuse side-B rotation `(7-c,7-r)` when building the encounter; do not interpret these as world/hero-side cells. Each listed slot is unique and every wave has at most six creatures. Factors apply once with half-up integer rounding to canonical base values. All values are unmeasured hypotheses.

| Round | Wave label | Neutral-local lineup | HP factor | Damage factor | Intended preparation question |
|---|---|---|---:|---:|---|
| 1 | Garden stirrings | Sprout(3, 3), Sprout(4, 3) | 1.00 | 1.00 | Can I buy and place a frontline hero? |
| 2 | Thorn watch | Sprout(3, 3), Thorn(4, 1) | 1.00 | 1.00 | Can I distinguish a ranged attacker? |
| 3 | Lantern sparks | Sprout(2, 3), Sprout(5, 3), Wisp(3, 1) | 1.00 | 1.00 | Can I protect a support/caster behind the frontline? |
| 5 | Stone shell | Stoneback(3, 3), Thorn(2, 1), Thorn(5, 1) | 1.00 | 1.00 | Can the team handle a shield and ranged support? |
| 10 | Prowler path | Stoneback(3, 3), Prowler(1, 2), Prowler(6, 2), Wisp(3, 0) | 1.20 | 1.10 | Does my rear line have protection against a public dash threat? |
| 15 | Bell ward | Sentinel(3, 3), Stoneback(4, 3), Thorn(1, 1), Thorn(6, 1) | 1.40 | 1.20 | Can spacing reduce simultaneous adjacent stuns? |
| 20 | Broken beacon | Warden(3, 1), Stoneback(2, 3), Stoneback(5, 3) | 1.50 | 1.30 | Can the team survive a telegraphed burst while breaking the front? |
| 25 | Garden siege | Sentinel(3, 3), Stoneback(4, 3), Prowler(1, 2), Prowler(6, 2), Wisp(2, 0) | 1.70 | 1.40 | Does the formation still protect support amid mixed threats? |
| 30 | Twin ward | Sentinel(2, 3), Sentinel(5, 3), Thorn(1, 1), Thorn(6, 1), Wisp(3, 0) | 1.90 | 1.50 | Can I avoid unnecessary clustering and read control timing? |
| 35 | Beacon breach | Warden(3, 1), Sentinel(2, 3), Stoneback(5, 3), Prowler(1, 2), Prowler(6, 2) | 2.10 | 1.60 | Can a developed composition handle both front and rear pressure? |
| 40 | Final ward | Warden(3, 0), Sentinel(2, 3), Sentinel(5, 3), Prowler(1, 2), Prowler(6, 2), Wisp(4, 1) | 2.30 | 1.70 | A final combined test before cap adjudication if multiple seats survive |

If a later explicit profile extends beyond 40, define additional canonical waves or a documented bounded repeat/scaling rule before starting it. The resolver recognizing 45 is not permission to fabricate a missing wave. Profile validation must require a wave for every reachable neutral round and reject missing/duplicate/illegal cells, absent definitions, excessive counts, nonpositive rates and unsafe numeric products. Regression fixtures can classify 41/45 without launching an incomplete playable profile.

## Art and presentation briefs

- **Sprout:** squat seed body, thick curved leaf shoulders and two rooted feet; clearly deliberate creature anatomy and expressive face, not an untextured sphere. Soft green/ochre, readable walking compression and leaf-swipe contact.
- **Thorn:** low plant creature with a bent reed launcher silhouette; visible aim bend, thorn release and recovery. Keep the projectile separate from unrelated foliage.
- **Wisp:** small lantern-like core with an opaque readable center and restrained orbiting light. A brief gather/release animation announces magic; avoid permanent full-screen bloom or particles hiding its HP marker.
- **Stoneback:** broad turtle-like carved ward construct with interlocking shell panels, low limbs and a clear face. Shield appears as a thin shell accent, not a large opaque sphere. Heavy gait must not imply extra footprint or collision.
- **Prowler:** original feline ward manifestation with a low spring posture, long shoulder/back line and luminous paw marks. Crouch → bounded dash → planted recovery communicates repositioning. No implied stealth or damage in the trail.
- **Sentinel:** compact standing bell construct, broad hanging shoulder frame and articulated legs. Bell lift precedes the short stun shock. Keep the effect within the declared neighboring tiles.
- **Warden:** original multi-panel beacon construct with a high prism crown, broad lower support and an obvious front-facing aperture. Use opaque geometry with restrained emissive seams. Aperture charge, projectile release and fixed-cell impact must show actual timing; no dragon transformation or copied boss model.

Each neutral needs authored source, materials/UVs, proper rig or explicitly validated mechanical rig, portraits for preview, collision/selection proxy and normal-speed Idle/Move/Attack/Hit/Defeat; active users also require Active. Shared motion can be reused only when contact, proportions and timing pass review. Victory is optional for neutrals; required hero clips are unaffected. No new rig/mesh is deemed complete from a still render or primitive graybox. Gameplay grayboxes must be labeled and replaced before visual acceptance.

Use one arena and camera. Preview and recap use original silhouettes/icons; no loot chests or item drops. The displayed +2 gold is pending next-preparation income and never requires a click. The final round pays no next-round income; a local celebration cannot accidentally grant a reward twice.

## Runtime verification requirements

Use the [systems settlement contract](SYSTEMS_MIGRATION.md): separate encounter kind/ownership, all real simultaneous fights, public wave data, once-only settlement, no PvP history advancement, ordinary snapshot traits and no neutral captain. Round 40 neutral outcomes and any simultaneous eliminations precede cap adjudication. Zero survivors is handled by the existing documented tie/adjudication policy, not a fabricated winner.

Test empty deployment, blocked dash landing, canceled reservations, stun interruption, source defeat with released packets, shield replacement/overflow, missed fixed-cell impacts, neutral timeout/draw and last-survivor end. Eight-seat copies must have independent state and IDs but identical authored difficulty. Camera/scouting changes must not change seeds or outcomes. Both human and bots obey the same public preview and command rules.

Run canonical validation, native combat tests, imported asset checks and packaged full matches. Measure neutral success/timeout rates by wave, source/trait/hero coverage, gold curves, actual match duration and worst-case CPU/GPU work. Tune from those results, not from the table looking plausible. No results are supplied or implied by this planning document.
