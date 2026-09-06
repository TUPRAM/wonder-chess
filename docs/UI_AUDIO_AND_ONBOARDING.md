# In-game experience, audio and onboarding

## 1. User journey

Launch → title screen → eight-seat bot lobby → first preparation → battle → recap/standings → next preparation → elimination/spectate or final results → restart. Every transition has actual game state behind it. The menu never launches a website in place of the game. Lobby labels disclose the seven bots, their names and chosen difficulty policy; do not show fake online players or matchmaking activity.

Default PC controls: left click selects, right click/back cancels, drag/drop or click-select/click-place moves, Escape opens options in offline mode. Explicit buttons cover essential actions so keyboard shortcuts are conveniences, not prerequisites. In network mode options do not pause the server. Fullscreen/windowed changes must not strand input focus.

## 2. HUD layout

At 1920×1080, reserve the center for the board, bottom for five shop cards and eight compact bench positions, top for phase/timer/opponent, left for trait summaries and right for eight-seat standings. Scale relative layout; do not hard-code all positions in pixels. Portraits may crop, but text and interactable areas remain live widgets.

Show gold, level, XP progress, current/max deployed count and the cost of each action. A full deployment counter signals a rule, not a prompt to buy. Give lock, reroll and XP buttons distinct shapes/text; do not rely on color. Empty purchased shop slots remain empty. If a purchase would merge despite a full bench, show that possible outcome before confirmation and still validate server-side.

In preparation, scout through the standings. Show only public deployments/traits/level/health and revealed pairing; never expose private shops or benches. A clearly labeled Return to Your Board button always remains available. Scouting cannot lose a pending selection, spend gold or alter the opponent. During combat, select another encounter from standings and reconstruct its current state, not a replay starting at time zero.

## 3. Hero inspection

Show model-derived portrait, name, race, class, cost, star level, current/max health, physical armor, magic resistance, basic damage, damage type, delivery, attacks/sec and skill tooltip. Expand advanced values for active magnitude, duration, range, first delay and cooldown. Distinguish raw star stats from trait/buff-derived values.

Use explicit labels: “Physical,” “Magic,” and “True”; never use only red/blue/white numbers. Shield value is a separate bar/number, not extra health. Stun has a small shared icon and a readable pose. Star pips do not obscure the face or rival team ownership.

Basic-attacks-per-second may be shown nominally with a tooltip for the tick-quantized effective value. Skill cooldown does not secretly change when attack speed increases. Avoid a misleading universal “power” score on the user-facing card; the bot’s heuristic is not a truth about combat outcomes.

## 4. Feedback and mistakes

Every rejected action reports a concise reason: insufficient gold, full bench without merge, invalid cell, wrong ownership, combat lock, stale shop or max level. Keep the attempted item selected when useful, but avoid replaying it automatically against a refreshed shop.

A successful purchase has a small visual transfer to bench and a quiet confirmation. An upgrade shows the consumed copies, resulting star and survivor location. A new trait lights once and presents its actual numerical bonus. A canceled drag produces no purchase/sale sound. All feedback follows authoritative acknowledgment; optimistic previews roll back clearly after a reject.

Provide undo only for a local uncommitted preview; do not advertise an economy undo that rewinds hidden shop RNG or already committed transactions. Formation presets are a later convenience unless implemented through legal ordinary moves.

## 5. First-match tutorial

Use a short optional guided preparation: buy Ada, place her on the front half, inspect her shield, purchase a partner and observe one two-unit trait. Then show a legal three-copy merge in a separate tutorial fixture or when it naturally happens. Do not alter normal tournament RNG secretly to force a tutorial outcome. A separate tutorial fixture must be labeled and keep its own profile.

Instructions are brief, skippable and replayable from menu. The first real tournament returns to normal independent shops and no hidden advantage. Explain that the captain arranges the team and heroes fight automatically. Explain what seven bot opponents are doing while the player watches one fight.

## 6. Recap and results

After each encounter, show winner/draw, player-health loss formula, damage to health, shield absorption, effective healing and survivors. Metrics come from actual events. “Damage absorbed” is not the amount of shielding cast; “healing” excludes overheal. Do not invent explanatory tips unsupported by the state.

Display ghost label where relevant and explain that the donor is unaffected by the copied fight. At timeout show the adjudication label rather than pretending a last strike happened. After elimination, offer spectate or return to menu/new tournament without requiring the eliminated human to ready for later rounds. Continue bots to final standings when spectating.

Shared placements use the documented competition-rank convention. Capped adjudication and host-aborted results are visually distinct from a normal final victory. Restart creates a fresh match and resets tutorial overlays, inspection panels, subscriptions and audio loops.

## 7. Audio and effects

Provide master/music/effects sliders and persistent local settings. Music is optional but must never mask essential cues. An original short fantasy ambience/music treatment may use properly licensed/owned resources or deliberate original synthesis; do not include unlicensed tracks or pass a single repeated beep as a polished soundscape. Placeholder cues are allowed during development but remain labeled before review.

Required families: buy, sell, merge, reroll, ready, phase change, health loss, victory/draw/defeat, movement, melee contact, ranged launch/impact, magic impact, shield, heal, stun and dash. Individual hero dossiers define variants. Limit concurrent voices, group area impacts and attenuate noninspected fights. No sound from invisible encounters should mislead the observed fight.

Keep effects brief and grounded in declared mechanics. Rowan’s cloud does not secretly deal damage over time; Zura’s lightning does not imply stun; Sylas’s dash does not mean invulnerability. No default camera shake for every attack. Reduced-motion mode suppresses camera pulses and decorative particles without removing indicators.

## 8. Language and usability

`data/locales/en.json` and `id.json` seed core labels. Translations are draft, not certified. Keep proper names stable; translate meaningful class/race/skill explanations through keyed data. Perform native-language review before marketing claims or a public release. Do not equate Indonesian with every Southeast Asian language.

Keyboard focus must be visible; controls need readable text, good contrast and non-color identification. Provide drag alternatives, minimum touch-friendly sizing and scalable HUD at 1280×720. This prepares later mobile evaluation but does not establish Android performance or usability. Test on an actual physical device before promising a mobile build.
