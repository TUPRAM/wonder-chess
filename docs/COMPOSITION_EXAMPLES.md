# Four test formations — not proven best teams

These six-unit formations are hypotheses for playtesting. Coordinates are captain-local: row 0 is the rear and row 3 the front. All entries are one star. Neither equal unit count nor a large trait count establishes equal purchase cost or strength.

## Hearthline

Protect two Rangers with two Guardians and two Priests. This activates many bonuses but lacks broad area damage.

| Hero | Cell (column,row) |
|---|---|
| Ada Brightshield | (2, 3) |
| Mira Dawnwell | (2, 1) |
| Liora Leafstep | (1, 0) |
| Elin Moonsong | (4, 1) |
| Borin Stonebell | (5, 3) |
| Tessa Brassbolt | (6, 0) |

Active two-unit bonuses: dwarf, elf, guardian, human, priest, ranger.

Against a grouped army, replacing a Priest with Rowan gains area damage but removes Priest 2. Test rather than assume the extra traits are superior.

## Stormwall

A durable melee line gives two Mages time to damage clustered formations. There is no healer.

| Hero | Cell (column,row) |
|---|---|
| Ada Brightshield | (1, 3) |
| Rowan Emberwick | (2, 0) |
| Borin Stonebell | (6, 3) |
| Dagna Anvilheart | (3, 3) |
| Rok Sunward | (4, 3) |
| Zura Stormcall | (5, 0) |

Active two-unit bonuses: dwarf, guardian, human, mage, orc, warrior.

Retreating Rangers and separated units reduce area value; swapping one melee unit for mobility sacrifices a completed class or race bonus.

## Twilight Raid

Two Rogues pressure vulnerable units while a Ranger and Mage attack from range. The first contact is fragile.

| Hero | Cell (column,row) |
|---|---|
| Liora Leafstep | (1, 0) |
| Elin Moonsong | (2, 1) |
| Sylas Duskrun | (0, 2) |
| Rok Sunward | (4, 3) |
| Zura Stormcall | (6, 0) |
| Kesh Quickwind | (7, 2) |

Active two-unit bonuses: elf, orc, rogue.

Guardians stationed near the rear can absorb arrival pressure. Consider a Guardian swap even when it costs Elf/Orc overlap; trait quantity alone is not team quality.

## Backline Watch

One Guardian, two Priests, two Rogues and an area Mage trade frontline durability for sustain and disruption.

| Hero | Cell (column,row) |
|---|---|
| Ada Brightshield | (3, 3) |
| Mira Dawnwell | (3, 1) |
| Elin Moonsong | (4, 1) |
| Sylas Duskrun | (1, 2) |
| Zura Stormcall | (6, 0) |
| Kesh Quickwind | (6, 2) |

Active two-unit bonuses: elf, human, orc, priest, rogue.

There is only one dedicated Defender. Replacing a Rogue with Borin improves the line and activates Guardian 2, but loses Rogue 2 and one race pairing.

The machine-readable formation fixtures are in `tests/fixtures/example_formations.json`. Compare equal gold/copy investment, mirror starting sides and inspect actual combat traces. No tournament simulation or human playtest was executed to establish these examples as balanced.
