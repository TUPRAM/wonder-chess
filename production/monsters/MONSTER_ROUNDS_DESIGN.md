# Monster and boss rounds — design proposal (2026-10-04)

Status: **proposal for owner review. Nothing here is in the game yet.** Numbers are starting targets and have not
been simulated. Looks are written for Codex four-view art in the hand-painted fantasy standard.

## 1. Shape of the campaign

| Kind | Rounds | What it is | Reward for winning |
|---|---|---|---|
| Teaching | 1, 2, 3 | One new small monster each round | None |
| Pack | 5, 15, 25, 35, 45, 55 | A group of ordinary monsters that tests one habit | Bonus gold |
| Boss | 10, 20, 30, 40, 50, 60 | One large boss with two or more helpers | Relic choice (pick 1 of 3) |

- Owner decision 2026-10-04: relics come only with bosses, so relic rounds become **10, 20, 30, 40, 50, 60** (today: 3, 15, 25); pack rounds pay gold. Which relics are offered is a later discussion. The validator locks the old list, so this
  is a rules change that needs the validator and tests updated.
- Losing a monster round costs captain health like any lost round, and gives no reward.
- Story frame: the Wondergrove outside the walls is waking up and pushing into the castle courtyard. Small things
  come first; older and stranger things follow. Monsters are plant, stone, insect and bog creatures so that they
  never look like a hero race.

### Scaling
Health and damage multipliers continue the line already in the catalogue (health +0.4 and damage +0.25 every five
rounds). Bosses use their own base stats and the multiplier of their round.

| Round | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Health × | 1.0 | 1.4 | 1.8 | 2.2 | 2.6 | 3.0 | 3.4 | 3.8 | 4.2 | 4.6 | 5.0 | 5.4 |
| Damage × | 1.0 | 1.25 | 1.5 | 1.75 | 2.0 | 2.25 | 2.5 | 2.75 | 3.0 | 3.25 | 3.5 | 3.75 |

Rounds 50–60 are meant as the closing stretch: a team that is still alive there should find these rounds hard.

## 2. Ordinary monsters (11)

Stats are base values before the round multiplier, shown the way the game shows them (health, attack damage,
range in tiles). "Skill" lists the existing engine effect the monster would borrow. **Monsters have no skills in
the game today; giving them skills is new engine work.**

### Existing seven (looks are new, stats are the catalogue's)

**Skittering Seedpod** — 210 health, 21 damage, range 1. No skill.
Knee-high walking seed. A split brown husk the shape of a chestnut, cracked open down the front; two small amber
eyes glow inside the crack. Four thin, jointed root legs like a crab's. One pale green sprout with two leaves on
top that bobs as it runs. No arms. Moves in quick, nervous bursts. Dies by splitting in half.

**Reed Archer** — 180 health, 28 damage, range 4. No skill.
Chest-high figure woven from green and tan river reeds, bound at the joints with darker cord. Head is a single
brown cattail with no face. Left arm ends in a bow grown from one bent reed and a string of spider silk; right
hand has three long reed fingers. A sheaf of reed arrows grows out of its back like quills. Thin legs, bare root
feet. Stands very still, then shoots.

**Lantern Bulb** — 280 health, 18 damage, range 2. Skill: small shield on the weakest ally (shield).
Waist-high onion-shaped plant bulb with papery amber skin, glowing warm yellow from inside so the veins show.
A curled green stalk on top bends over like a lantern hook, with one glowing seed hanging from it. Sits on a ring
of short stubby roots and shuffles rather than walks. No face; the glow pulses when it acts.

**Slate Ram** — 800 health, 55 damage, range 1. Skill: short charge (momentum charge, as Boar Rusher).
A ram built from stacked plates of dark grey slate, shoulder-high to a human, on four short thick legs. Massive
curled horns of paler stone with chipped edges. Green moss and small ferns in the seams of its back. Eyes are two
deep holes with a faint blue light. Lowers its head and paws the ground before it charges.

**Glass Moth** — 450 health, 60 damage, range 4. No skill.
A moth with a human-sized wingspan. Wings are leaded stained glass: black lead lines with panes of deep blue,
amber and a little red, slightly translucent. Round furry white body, six thin black legs tucked up, two feathered
antennae. Large dark eyes. Hovers a hand above the ground; wings beat slowly. Attacks with a thin beam of coloured
light from between the antennae.

**Root Sentinel** — 1,350 health, 80 damage, range 1. Skill: stun every enemy next to it (as Earthbreaker).
Taller than an orc. A broad guardian of twisted grey-brown roots wrapped around river stones. Wide shoulders, no
neck; the face is a hollow knot with one steady green light inside. Forearms end in clubs of knotted root. Bark
plates on chest and shins; a few dry leaves on the shoulders. Slow, heavy steps. (Stonier and squarer than the
Treant Caller's treant, which is leafy and slim, so the two do not get confused.)

**Hollow Bellkeeper** — becomes the round-30 boss; see section 4.

### New four

**Bramble Hound** — 320 health, 45 damage, range 1, moves fast. No skill.
Wolf-sized hound made of tightly wound thorn vines, dark green with red-brown thorns along the spine like raised
hackles. Lean body, long legs, whip tail ending in a seed burr. Head is a wedge of vines with two red berry eyes
and a jaw of long thorns. Runs low. Comes in packs of four or more.

**Spore Cap** — 380 health, 20 damage, range 3. Skill: heals the ally with the lowest health (as Chapel Healer).
Waist-high mushroom creature. Wide dome cap, dusky purple with pale spots, edges frayed. Thick cream stalk body
with two tiny dark eyes just under the cap and two short arm-like nubs. Walks on a skirt of fine white threads.
A slow cloud of pale green spores drifts up from the cap; the cloud thickens when it heals.

**Gutter Gargoyle** — 900 health, 50 damage, range 3. Skill: guards allies behind it (as Shieldbearer).
The one monster that comes from the castle itself: a rain-spout gargoyle woken by the grove. Squat, human-height,
carved from pale weathered limestone streaked green with algae. Bat wings folded like a cloak, hunched shoulders,
long open mouth made to pour water, blunt horns, clawed feet still attached to a broken chunk of wall ledge that
it drags along. Spits a hard jet of water.

**Bog Toad** — 700 health, 40 damage, range 3. Skill: spit that damages a small area (as Bomber).
Cart-wheel-sized toad, low and very wide. Warty olive skin with mustard-yellow belly and throat sac, mud dried on
its back with small reeds and one lily pad stuck to it. Bulging pale eyes with horizontal pupils. Thick front
legs, folded back legs. Throat swells before it spits a glob of dark mud.

## 3. Teaching and pack rounds

Positions are on the monsters' half of the board. "Front" is the row nearest the player.

| Round | Name | Line-up | What it teaches | Reward |
|---|---|---|---|---|
| 1 | Screen the Seedpod | 1 Seedpod, front centre | A fight happens by itself; buy two pieces | — |
| 2 | Spread against Reeds | 1 Seedpod front, 1 Reed Archer back | Ranged enemies exist; put something in front | — |
| 3 | Protect the Lantern | 2 Seedpods front, 1 Reed Archer back, 1 Lantern Bulb middle | Support monsters keep others alive | — |
| 5 | The Quarry Gate | 2 Slate Rams front, 1 Glass Moth back | You need a real front line by now | +2 gold |
| 15 | Thorn Run | 5 Bramble Hounds spread across the front, 1 Spore Cap back | Many small fast enemies: area damage and a healer to kill first | +3 gold |
| 25 | The Wet Wall | 2 Gutter Gargoyles front, 2 Bog Toads back, 1 Spore Cap back centre | A guarded back line: reach it or out-range it | +4 gold |
| 35 | Moth Light | 1 Root Sentinel front centre, 4 Glass Moths in a back arc, 2 Lantern Bulbs middle | Heavy ranged damage behind one tank and shields | +5 gold |
| 45 | The Whole Grove | 2 Root Sentinels, 2 Slate Rams front; 2 Bog Toads, 2 Spore Caps, 2 Reed Archers back | Everything at once; a full ten-unit team is expected | +6 gold |
| 55 | Last Bloom | 3 Root Sentinels, 3 Gutter Gargoyles front; 4 Glass Moths, 2 Spore Caps back | The hardest pack; a check before the final boss | +8 gold |

## 4. Bosses

Each boss is about twice the height of a hero and stands on one tile (two-by-two bodies are not supported today;
the model simply overhangs its tile). Base stats are before the round multiplier.

### Round 10 — Old Tusk, the Slate King
- **Stats:** 2,600 health, 90 damage, range 1. With him: 2 Slate Rams.
- **Skill — Rockslide Charge:** lowers his head, then charges the farthest enemy and hits everything next to
  where he lands (charge + area damage). Every 8 seconds.
- **What it asks of the player:** do not leave fragile pieces alone in a back corner.
- **Look:** a ram the size of a wagon made of huge slabs of dark slate with pale quartz veins. Horns are full
  double spirals as wide as his body, the tips broken and jagged. A crown of old iron arrowheads and broken spear
  shafts is stuck in the moss along his back. A small dead tree grows from one shoulder. One eye glows blue; the
  other is a cracked hole. Stone dust falls from him when he moves.

### Round 20 — The Glass Queen
- **Stats:** 3,000 health, 110 damage, range 4. With her: 3 Glass Moths, 2 Lantern Bulbs.
- **Skill — Rose Window:** her wings open flat and two beams of coloured light cross the board through the
  current target (crossing beams, as Prism Scholar). Every 7 seconds.
- **What it asks:** spread out; kill the Lantern Bulbs that shield her.
- **Look:** a moth with a wingspan three times a hero's height. Each upper wing is a round cathedral rose window:
  black lead tracery, panes of ruby, cobalt and gold, with a pale centre that lights up before she fires. Lower
  wings are long trailing panes like stained-glass banners. Thick white fur collar, slim silver-grey body, a small
  crown of clear crystal shards between long feathered antennae. Eyes are faceted amber.

### Round 30 — The Hollow Bellkeeper
- **Stats:** 4,200 health, 100 damage, range 3. With him: 4 Seedpods, 2 Reed Archers, 1 Spore Cap.
- **Skill — Toll:** strikes the bell in his chest; every enemy within two tiles is stunned for about one second
  (area stun). Every 9 seconds.
- **What it asks:** ranged damage and staying out of the ring; melee teams need to survive the stuns.
- **Look:** a towering thin figure in a tattered ash-grey hooded robe that hangs as if nothing is inside. The hood
  is empty and black. Where the chest should be, the robe opens on a large cracked bronze bell, green with age,
  hanging from a rope of roots. Long sleeves end in pale root hands. Carries a striker staff as tall as himself:
  dark wood with a heavy bronze head. Small bells and dry seed pods hang from the hem. Dead leaves always drift
  around his feet.

### Round 40 — Grandmother Root
- **Stats:** 6,000 health, 120 damage, range 1. With her: 2 Root Sentinels, 3 Spore Caps.
- **Skill — Deep Grove:** grass spreads over the tiles around her and heals her and every monster standing on it
  each second for six seconds (stationary grove, as Grove Druid). Every 12 seconds.
- **What it asks:** burst damage, or kill the Spore Caps and fight her outside the grass.
- **Look:** a vast seated-looking tree-woman: a wide skirt of roots that she drags herself along on, a hunched
  trunk body with bark like deep wrinkles, and long arms of branch that reach the ground. Her face is carved by
  age into the trunk: closed eyelids, a long knotted nose, a calm mouth. A full crown of autumn leaves in gold
  and rust, with birds' nests and small glowing mushrooms in it. Moss shawl on her shoulders. When she heals,
  small white flowers open across her.

### Round 50 — The Mire Mother
- **Stats:** 7,000 health, 130 damage, range 3. With her: 4 Bog Toads, 2 Gutter Gargoyles.
- **Skill — Flood:** a wave rolls down the lane she faces, damaging and pushing every enemy in it back one tile
  (tidal push, as Tide Caller). Every 8 seconds.
- **What it asks:** formations get broken; the player needs a team that still works when shuffled.
- **Look:** a toad as large as a cottage, low and immensely wide. Black-green skin, pale drowned-looking belly,
  throat sac that glows dull green when it swells. A whole patch of bog rides on her back: reeds, a rotten jetty
  post, lily pads, a rusted helmet. Dozens of small pale eyes cluster around two huge ones. Webbed front feet the
  size of shields. Water pours constantly from the corners of her mouth.

### Round 60 — The Wonder Heart (final)
- **Stats:** 9,000 health, 150 damage, range 4. With it: 2 Root Sentinels, 2 Gutter Gargoyles, 2 Glass Moths,
  2 Spore Caps.
- **Skills:** it alternates two of the earlier bosses' attacks: **Toll** (area stun) and **Rose Window**
  (crossing beams), one every 6 seconds.
- **What it asks:** everything learned so far. This is intended as the end of the match.
- **Look:** the grove's heart, torn loose and walking. A huge seed of dark polished wood, split open down the
  front, with a blinding gold-green light inside. It is carried upright in a cage of thick roots that work as
  four legs, and ringed by a slowly turning halo of floating bark shards and leaves. Fragments of the earlier
  bosses are caught in the roots: a piece of slate horn, a pane of stained glass, a small bronze bell. No face;
  the light narrows to a slit before it attacks.

## 5. What this needs before it can be built

1. **Engine:** monsters have no skills today. Every skill above reuses an effect heroes already have, but
   attaching skills to monsters, and letting a boss alternate two skills, is new work with tests.
2. **Rules:** new relic rounds; pack-round gold; waves for rounds 50, 55 and 60; four new monsters and six bosses
   in the catalogue (one already exists as the Bellkeeper).
3. **Art:** 16 models in total (10 ordinary monsters and 6 bosses). Codex draws four views of each first.
   Rough Meshy cost: 30 credits per model plus about 25 for each rigged humanoid (Reed Archer, Root Sentinel,
   Gutter Gargoyle, Bellkeeper, Grandmother Root), so roughly 600 of the 731 credits left. Non-humanoid monsters
   would be moved by code, as Ember Wisp and Forge King are.
4. **Balance:** none of the numbers have been simulated. Bot matches should be run to see how far real matches
   go and whether each boss is beatable at its round.

## 6. What was built on 2026-10-05, and where it differs from the proposal

- All sixteen monsters and bosses are modelled, rigged and animated from `tools/blender/build_monsters.py` and are in the game.
- Waves run to round 60 with a boss every tenth round. **The engine allows at most six monsters in a wave**, so rounds 30, 35, 45, 50,
  55 and 60 are smaller than the tables above.
- Skills are borrowed hero abilities: Lantern Bulb (shield), Slate Ram and Old Tusk (charge), Root Sentinel and the Bellkeeper (area
  stun; the Bellkeeper's reaches two tiles), Spore Cap (heal), Gutter Gargoyle (guard), Bog Toad (area damage), Glass Queen and
  Wonder Heart (crossing beams), Grandmother Root (healing grove), Mire Mother (wave). Seedpod, Reed Archer, Glass Moth and
  Bramble Hound have none.
- The Wonder Heart has one skill, not two alternating ones; the engine gives a unit a single ability.
- Old Tusk charges his current target, not the farthest enemy.
- Relic drafts are on rounds 10 to 60, but the engine holds three relic slots, so bosses 40, 50 and 60 add none yet. Relics are still
  given whether or not the boss was beaten. Pack rounds pay the existing flat 2 gold for a win.
- Boss health was set about 40% under the proposal because each fight must end inside the 45-second combat limit. Nothing is balanced.
