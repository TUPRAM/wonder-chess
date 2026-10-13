# Interface and teaching design (Phase 5)

Status: design accepted by the owner on 2026-10-10 (decisions in `README.md` section 5). No code written.

References: **Solo** = `game/Source/WonderChessRuntime/Private/WCVNextSolo.cpp`,
**Lab** = `.../Private/WCVNextLab.cpp`. The solo screen is Slate built in C++; there is no UMG.
Line numbers are from the survey of 2026-10-09.

## 1. What already exists

| Feature | State | Where |
|---|---|---|
| Damage chart | Live, per hero, dealt / taken / healed, top eight rows, replaces the synergy list during a fight | Solo:891-916, 2031-2051 |
| Shop odds | "Level N odds" row of five chips, with next-round income, inside the shop | Solo:1176-1193 |
| Synergy list | Count, "of 2 / 4", detail card with members | Solo:810-890 |
| Trait badges | On board name plates, in the inspector, on shop cards | Lab:1468-1480 |
| Pause | In solo | Solo:1252 |
| How to play | Static five-page guide, opened by F1 or Help; bilingual | Solo:188-246 |
| Verification | Scripted input by widget tag, staged captures, autoplay with screenshots | Solo:39-50, 1921-2029; Lab:2235-2320 |

The damage chart and odds row are uncommitted work in the tree. They are treated here as
the starting point, not as something to rebuild.

## 2. Part A: gaps in what exists

| # | Gap | Design |
|---|---|---|
| A1 | The chart sums only one side by a fixed side number. It is unverified when the viewed seat is the second seat of a pairing | Resolve the viewer's side from the pairing; add a test fight where the viewer is second |
| A2 | Shield absorption is not shown | Add a fourth mode, "Blocked": damage absorbed by shields and prevented by guard. Both are already on each event |
| A3 | Totals vanish when the fight ends | Keep the last fight's totals and show them in the existing Recap modal |
| A4 | No physical / magic / true split | Colour each bar in segments by damage type, which each event carries |
| A5 | Enemy rows | A toggle between "Mine" and "Theirs" |
| A6 | The guide's page 3 says trait bonuses are inactive | Correct the text (also listed in Phase 0) |
| A7 | No speed control | Out of scope. Pause is enough for now |

## 3. Part B: showing the new mechanics

Each engine slice adds things a player must be able to read. The rule is one cue per
mechanic, built from pieces that exist (floating text, name-plate badges, the particle
kinds already in `WCVNextCombatPresentation.cpp`), added in the same slice as the mechanic.

| Slice | Mechanic | Cue |
|---|---|---|
| S2 | Buff or debuff on a stat | Small up or down arrow badge on the name plate, coloured by stat |
| S3 | Fight-start shield, regeneration | Existing shield look; small green tick number once per second |
| S4 | Miss | Floating "Miss" in grey |
| S4 | Crit | Larger floating number with a mark |
| S4 | Lifesteal, reflect, bonus true damage | Floating number in its own colour on the unit that gains or loses health |
| S5 | Damage over time | Badge on the name plate; tick numbers in the damage type's colour |
| S5 | Ground zone | Ring on the affected cells for its duration |
| S6 | Line, cone, chain | Brief highlight of the cells hit; a streak between chained targets |
| S7 | Hex, silence, taunt | One badge each on the name plate; taunt also draws a line to the taunter |
| S8 | Blink, leap | Vanish and appear glow at both cells |
| S9 | Summon | Spawn glow; summons get a thinner name plate with the owner's colour and no star |

Every cue is exercised by the existing visual exercise and frame recorder, so each slice
ends with captures. Whether the result reads well to a person stays a human review.

**Tooltips.** Every new or changed ability and trait gets `tooltip_en` and `tooltip_id` in
the catalogue. The solo screen reads only the English one today; reading the Indonesian
one when the language flag is set is a small change made once, in S1.

## 4. Part C: the guided first match

### What exists and why it is not enough

- The five-page guide is static text. It does not react to what the player does and does
  not open by itself.
- The formation scenario format holds two armies and nothing else: no gold, level, bench,
  shop or steps, and it is refused in solo mode.
- A preparation save holds a full match state, but it is tied to the content digest, so a
  hand-made tutorial save would break at every balance change.

### Design

A **guided match** is a real solo match with three additions: a prepared start, held
timers, and a script of steps. It reuses the real shop, board, fight and screens, so what
the player learns is exactly what they will use.

**1. Prepared start.** A new entry point creates a match from a described state instead of
from a seed alone: the player's gold, level, board, bench and shop offers, and one bot
opponent with a fixed board. The description lives in the catalogue under a new `tutorial`
key, written with hero ids, so it survives balance changes and is checked by the validator.

**2. Held timers.** While a step is waiting for the player, the preparation clock does not
run. Fights run at normal speed.

**3. Step script.** Each step has: a short message in both languages; the widget to
highlight, by the tags the screen already uses for automated input; the condition that
completes it (a command was issued, a unit reached a cell, a level was reached, a fight
ended); and which inputs are allowed meanwhile. Anything not allowed is ignored with a hint.

### The five stages

Each stage is one preparation and one fight against the same bot.

| Stage | Teaches | Prepared state | Steps |
|---|---|---|---|
| 1. Field your team | Deploying; level sets how many | Level 3, three heroes on the bench, no gold | Drag each hero to the board; press Ready; watch the fight |
| 2. Grow | Buying, selling, star-up, buying experience | Gold for two purchases; the shop holds two copies of a hero already owned | Open the shop; buy both copies; see the star-up; buy experience; field the extra hero |
| 3. Synergies | Race and class, the 2 and 4 steps | Shop holds a hero that completes a trait pair | Buy it; open the synergy list; read the bonus; fight and see the difference in the chart |
| 4. Positions | Front and back rows, the guarded side | An enemy board that punishes a bad layout | Move the tank forward and the ranged hero back; face the guard; fight |
| 5. Gold and relics | Interest, streaks, lock, reroll, a relic draft | Nine gold, a monster round next | See interest at ten gold; lock the shop; beat the wave; choose and equip a relic |

After stage 5 the match continues as a normal solo match, or the player leaves.

### Behaviour

- Offered automatically on the first launch of solo mode, and always available from Help.
- "Leave the guide" is always on screen and asks for confirmation.
- Progress by stage is stored in the player profile so a returning player can resume.
- The opponent bot is scripted to field a fixed board per stage, so each lesson's fight has
  a predictable result. It gets no stat changes.

### What must be built

| Piece | Where it belongs |
|---|---|
| Match creation from a described state | Match code, next to the existing constructor |
| `tutorial` key: schema, validator, generator | Catalogue tooling |
| Timer hold | Solo tick, where pause already lives |
| Step runner: message, highlight, completion test, input filter | Solo screen |
| Widget tags for any control that lacks one | Solo screen |
| First-run flag and stage progress | Player profile |
| Text for about 25 steps, English and Indonesian | Catalogue `tutorial` key |

### Dependencies

- Stage 5 teaches streak income and uses auto-deploy wording, so the guided match is
  written after Phase 4's rules are settled.
- Stages 1-4 need nothing from the engine slices. They use heroes that exist today.
- Stage content should be revisited once after S9, when the roster is complete.

### Tests and evidence

- A scripted run completes all five stages through the existing input exerciser, using
  widget tags, and captures each step.
- A validator test fails if a tutorial state names a hero that is disabled or a shop offer
  that the level's odds could never produce.
- Leaving and resuming at each stage is exercised.
- Whether a new player actually understands each stage is a human study and a separate gate.

## 5. Done means

- Part A: each gap closed with a test or capture; A1 with a regression test.
- Part B: one cue per mechanic, delivered and captured in its slice.
- Part C: the scripted five-stage run passes; both languages present; first-run offer works.
