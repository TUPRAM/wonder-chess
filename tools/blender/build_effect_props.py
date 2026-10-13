"""Build the handmade effect pieces (projectiles, debris, blast and smoke shapes) as small static meshes.

Run:  blender -b -P tools/blender/build_effect_props.py -- <output folder> [prop ...]
Each prop is written to <output folder>/<Name>/<Name>.fbx with its baked colour. Projectiles are modelled about one and
a half times real size so they read from the board camera, with their long axis along Y (the direction of flight).
Candidates for owner review, not approved art.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as kit  # noqa: E402
from monster_kit import lump, pane, slab, spike, tube  # noqa: E402

BONE = "Prop"
RED, RED_DARK, IRON, CORD, PAPER = (0.62, 0.04, 0.03), (0.36, 0.02, 0.02), (0.10, 0.10, 0.12), (0.45, 0.36, 0.22), (0.80, 0.72, 0.52)


def pipe_bomb():
    """A red pipe bomb: capped iron ends, a paper band, and a short fuse with a bright tip."""
    tube([(0, -15, 0), (0, 15, 0)], 5.2, BONE, RED, sides=12)
    for y in (-15.5, 15.5):
        tube([(0, y - 2.2, 0), (0, y + 2.2, 0)], 6.3, BONE, IRON, sides=12, smooth=False)
    for y in (-13.2, 13.2):
        tube([(0, y - 0.5, 0), (0, y + 0.5, 0)], 5.6, BONE, RED_DARK, sides=12, smooth=False)
    tube([(0, -3.2, 0), (0, 3.2, 0)], 5.5, BONE, PAPER, sides=12, smooth=False)
    fuse = [(0, 17, 0), (0, 21, 1.5), (1.5, 24, 4.5), (1, 26, 8)]
    tube(fuse, [1.1, 1.0, 0.9, 0.8], BONE, CORD, sides=5, smooth=False)
    lump(fuse[-1], (2.2, 2.2, 2.2), BONE, (1.0, 0.85, 0.3), detail=1)
    return "PipeBomb", 40


def shard(colour, name):
    def make():
        """A torn, curved scrap of casing."""
        points = [(-5, -3, 0), (-1, -5, 1.2), (4, -3.5, 0.6), (6, 1, 0), (2, 4.5, 1.4), (-3, 3.5, 0.5)]
        pane([(x + random.uniform(-1, 1), y + random.uniform(-1, 1), z) for x, y, z in points], BONE, colour, 1.6, "shard")
        return name, 14
    return make


def smoke_ball():
    """A lumpy puff: a few overlapping rounded masses, to be scaled up and let go."""
    lump((0, 0, 0), (20, 20, 18), BONE, (0.30, 0.29, 0.28), detail=2, rough=1.5)
    for k in range(6):
        a = k / 6 * math.tau
        lump((13 * math.cos(a), 13 * math.sin(a), random.uniform(-6, 9)), (11, 11, 10), BONE, random.choice([(0.24, 0.23, 0.23), (0.36, 0.35, 0.34), (0.19, 0.18, 0.18)]),
             detail=2, rough=1.0)
    lump((2, -2, 13), (12, 12, 10), BONE, (0.40, 0.39, 0.37), detail=2, rough=1.0)
    return "SmokeBall", 50


def blast_star():
    """The flash of an explosion as a solid shape: a hot core with long and short spikes in every direction."""
    lump((0, 0, 0), (15, 15, 15), BONE, (1.0, 0.92, 0.55), detail=2)
    for k in range(22):
        a, b = random.uniform(0, math.tau), random.uniform(-1.2, 1.2)
        out = (math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b))
        reach = random.choice([30, 38, 46, 58])
        spike(tuple(v * 9 for v in out), tuple(v * reach for v in out), 7.5 if reach < 45 else 5.5, BONE, (1.0, 0.55, 0.08) if k % 3 else (1.0, 0.25, 0.04), sides=4)
    return "BlastStar", 120


def scorch():
    """A burnt mark for the ground: a ragged black disc with a few rays."""
    outline = [((38 + random.uniform(-9, 9)) * math.cos(k / 18 * math.tau), (38 + random.uniform(-9, 9)) * math.sin(k / 18 * math.tau), 0) for k in range(18)]
    pane(outline, BONE, (0.012, 0.011, 0.010), 0.6, "scorch")
    for k in range(7):
        a = k / 7 * math.tau + random.uniform(-0.2, 0.2)
        reach = random.uniform(48, 66)
        pane([(26 * math.cos(a - 0.16), 26 * math.sin(a - 0.16), 0.2), (reach * math.cos(a), reach * math.sin(a), 0.2), (26 * math.cos(a + 0.16), 26 * math.sin(a + 0.16), 0.2)],
             BONE, (0.02, 0.018, 0.016), 0.5, "ray")
    return "Scorch", 30


# ---- Ranged basic attacks (2026-10-06). The nose of a projectile points along -Y, which becomes the flight direction. --
WOOD, LEAF, BONE_WHITE, WATER, FLAME = (0.30, 0.19, 0.09), (0.25, 0.60, 0.16), (0.82, 0.78, 0.66), (0.12, 0.42, 0.90), (1.0, 0.55, 0.08)


def simple(name, size, make):
    def build():
        make()
        return name, size
    return build


def leaf_seed():
    lump((0, 0, 0), (4.5, 7, 4.5), BONE, (0.36, 0.22, 0.08), detail=2)
    for side in (-1, 1):
        kit.leaf((side * 1.5, 3, 0), (side * 16, 16, 4), 9, BONE, LEAF)
    spike((0, -6, 0), (0, -13, 0), 2.2, BONE, (0.55, 0.40, 0.14))


def leaf_scrap():
    kit.leaf((0, 6, 0), (0, -7, 1.5), 7, BONE, random.choice([LEAF, (0.36, 0.66, 0.18), (0.55, 0.50, 0.12)]))


def hook():
    tube([(0, 12, 0), (0, 0, 0), (0, -10, 0), (4, -17, 0), (11, -17, 0), (14, -10, 0), (12, -4, 0)], [1.8, 2.0, 2.3, 2.5, 2.4, 2.0, 0.5], BONE, IRON, sides=6, smooth=False)
    spike((12.5, -9, 0), (7.5, -5, 0), 1.6, BONE, IRON, sides=4)
    ring = [(3.2 * math.cos(k / 8 * math.tau), 14.5 + 3.2 * math.sin(k / 8 * math.tau), 0) for k in range(9)]
    tube(ring, 1.1, BONE, IRON, sides=5, smooth=False)


def chain_link():
    ring = [(3.4 * math.cos(k / 10 * math.tau), 7.5 * math.sin(k / 10 * math.tau), 0) for k in range(11)]
    tube(ring, 1.35, BONE, IRON, sides=5, smooth=False)


def crystal(length, width):
    def make():
        tube([(0, -length * 0.62, 0), (0, -length * 0.1, 0), (0, length * 0.38, 0)], [0.25, width, 0.25], BONE, (0.55, 0.90, 1.0), sides=5, smooth=False)
    return make


def water_orb():
    lump((0, 0, 0), (9, 11, 9), BONE, WATER, detail=3)
    lump((2, 9, 3), (4.5, 6, 4.5), BONE, (0.25, 0.58, 0.96), detail=2)
    lump((-2, 15, -1), (2.6, 4, 2.6), BONE, (0.40, 0.70, 1.0), detail=2)
    lump((-2.5, -4, 4), (2.6, 2.6, 2.2), BONE, (0.80, 0.92, 1.0), detail=1)


def droplet():
    tube([(0, 0, -3.5), (0, 0, 0), (0, 0, 5)], [2.6, 3.2, 0.3], BONE, (0.30, 0.62, 0.98), sides=7)


def soul_wisp():
    lump((0, 0, 0), (8, 9, 8), BONE, (0.40, 1.0, 0.50), detail=3)
    tube([(0, 5, 0), (2.5, 18, 3), (-2.5, 30, 0), (0, 40, 2)], [6.5, 4.4, 2.4, 0.4], BONE, (0.25, 0.85, 0.40), sides=7)
    for side in (-1, 1):
        lump((side * 3.2, -7.2, 1.5), (2.0, 1.6, 2.6), BONE, (0.02, 0.10, 0.04))
    lump((0, -7.6, -3.4), (2.2, 1.4, 1.6), BONE, (0.02, 0.10, 0.04))


def flame_drop():
    tube([(0, -7, 0), (0, -4, 0), (0, 2, 0), (0, 10, 0), (0, 17, 0)], [1.5, 6, 5, 2.4, 0.3], BONE, FLAME, sides=8)
    tube([(0, -5.5, 0), (0, -3, 0), (0, 3, 0), (0, 8, 0)], [1.2, 4.6, 3.2, 0.3], BONE, (1.0, 0.92, 0.50), sides=7)


def fireball():
    lump((0, 0, 0), (10, 10, 10), BONE, (1.0, 0.40, 0.04), detail=2, rough=1.4)
    lump((0, -3, 0), (6.5, 6.5, 6.5), BONE, (1.0, 0.90, 0.45), detail=2)
    for k in range(9):
        a = k / 9 * math.tau
        spike((6 * math.cos(a), 3, 6 * math.sin(a)), (9 * math.cos(a) + random.uniform(-2, 2), random.uniform(16, 27), 9 * math.sin(a) + random.uniform(-2, 2)), 4.2, BONE,
              FLAME if k % 2 else (1.0, 0.22, 0.03))


def ember():
    lump((0, 0, 0), (2.2, 2.2, 2.2), BONE, (1.0, 0.65, 0.12), detail=1)


def sound_ring():
    for reach, thick, colour in ((17, 2.3, (0.95, 0.10, 0.08)), (10.5, 1.3, (1.0, 0.45, 0.30))):
        ring = [(reach * math.cos(k / 20 * math.tau), 0, reach * math.sin(k / 20 * math.tau)) for k in range(21)]
        tube(ring, thick, BONE, colour, sides=6)


def cannonball():
    lump((0, 0, 0), (11, 11, 11), BONE, (0.07, 0.07, 0.08), detail=3)
    ring = [(11.2 * math.cos(k / 16 * math.tau), 11.2 * math.sin(k / 16 * math.tau), 0) for k in range(17)]
    tube(ring, 0.9, BONE, (0.16, 0.16, 0.18), sides=4, smooth=False)


def rock_chunk():
    kit.block((0, 0, 0), (10, 8, 7), BONE, random.choice([(0.30, 0.29, 0.27), (0.22, 0.21, 0.20)]), turn=(20, 30, 10), chip=1.8, bevel=1.4, rough=1.2)


def arrow():
    tube([(0, 22, 0), (0, -20, 0)], 0.9, BONE, WOOD, sides=5, smooth=False)
    tube([(0, -19, 0), (0, -22, 0), (0, -31, 0)], [1.2, 3.0, 0.15], BONE, IRON, sides=4, smooth=False)
    for k in range(3):
        a = k / 3 * math.tau
        out = (math.cos(a), math.sin(a))
        pane([(0, 12, 0), (out[0] * 4.2, 15, out[1] * 4.2), (out[0] * 4.2, 22, out[1] * 4.2), (0, 23, 0)], BONE, (0.80, 0.78, 0.70), 0.5)


def splinter():
    pane([(-1, 6, 0), (1.2, 5, 0.4), (0.6, -7, 0), (-0.8, -5, 0.3)], BONE, random.choice([WOOD, (0.42, 0.29, 0.14)]), 0.9)


def acorn():
    lump((0, 0, 0), (5, 7.5, 5), BONE, (0.90, 0.62, 0.12), detail=2)
    lump((0, 4.5, 0), (5.6, 3.6, 5.6), BONE, (0.34, 0.20, 0.07), detail=2, rough=0.4)
    spike((0, -6.5, 0), (0, -11, 0), 1.6, BONE, (0.90, 0.62, 0.12))
    tube([(0, 7, 0), (0.6, 10.5, 0.8)], [1.0, 0.7], BONE, (0.30, 0.19, 0.09), sides=5)


def bullet():
    tube([(0, -6, 0), (0, -3, 0), (0, 4, 0), (0, 5, 0)], [0.6, 3.0, 3.0, 2.2], BONE, (0.32, 0.32, 0.34), sides=8)


def rocket():
    tube([(0, 14, 0), (0, -12, 0)], 4.5, BONE, (0.11, 0.11, 0.13), sides=10)
    tube([(0, -12, 0), (0, -18, 0), (0, -25, 0)], [4.7, 3.4, 0.3], BONE, (0.75, 0.08, 0.05), sides=10)
    for y in (-10, 6):
        tube([(0, y - 1, 0), (0, y + 1, 0)], 4.9, BONE, (0.60, 0.42, 0.12), sides=10, smooth=False)
    for k in range(4):
        a = k / 4 * math.tau + 0.785
        out = (math.cos(a), math.sin(a))
        pane([(out[0] * 4, 6, out[1] * 4), (out[0] * 10, 13, out[1] * 10), (out[0] * 10, 17, out[1] * 10), (out[0] * 4, 14, out[1] * 4)], BONE, (0.60, 0.42, 0.12), 0.9)
    tube([(0, 14, 0), (0, 17, 0)], [3.4, 2.6], BONE, (0.05, 0.05, 0.05), sides=8, smooth=False)


def bone_charm():
    tube([(0, -8, 0), (0, 8, 0)], [1.5, 1.5], BONE, BONE_WHITE, sides=6)
    for y in (-9, 9):
        for side in (-1, 1):
            lump((side * 1.5, y, 0), (2.0, 2.0, 2.0), BONE, BONE_WHITE, detail=1)
    tube([(0, 0, 0), (0, 2, -6)], 0.4, BONE, (0.10, 0.07, 0.04), sides=4, smooth=False)
    kit.leaf((0, 2, -6), (1, 6, -19), 6, BONE, (0.42, 0.20, 0.62))
    kit.leaf((0, 2, -6), (-3, -1, -17), 5, BONE, (0.55, 0.30, 0.75))


def bone_chip():
    pane([(-3, 2.5, 0), (2, 3.5, 0.5), (3.5, -2, 0), (-1.5, -3.5, 0.4)], BONE, BONE_WHITE, 1.2)


def dart():
    tube([(0, 10, 0), (0, -8, 0)], 0.8, BONE, (0.40, 0.33, 0.14), sides=5, smooth=False)
    tube([(0, -8, 0), (0, -17, 0)], [0.9, 0.1], BONE, (0.20, 0.55, 0.20), sides=4, smooth=False)
    for k in range(3):
        a = k / 3 * math.tau
        out = (math.cos(a), math.sin(a))
        pane([(0, 5, 0), (out[0] * 4.5, 9, out[1] * 4.5), (out[0] * 3.5, 15, out[1] * 3.5), (0, 12, 0)], BONE, (0.80, 0.14, 0.10), 0.5)


def skull():
    lump((0, 0, 1), (8, 9.5, 8.5), BONE, BONE_WHITE, detail=3)
    kit.block((0, -4.5, -6.5), (8.5, 7, 5), BONE, (0.72, 0.68, 0.56), chip=0.3, bevel=0.8, rough=0)
    for side in (-1, 1):
        lump((side * 3.3, -8.2, 1.2), (2.4, 1.8, 2.8), BONE, (0.02, 0.03, 0.02))
        lump((side * 3.3, -8.8, 1.2), (1.0, 0.8, 1.0), BONE, (0.40, 1.0, 0.45))
    lump((0, -9.2, -2.2), (1.2, 1.0, 1.6), BONE, (0.02, 0.03, 0.02))
    for k in range(5):
        kit.block(((k - 2) * 1.6, -8.3, -8.6), (1.2, 1.0, 1.8), BONE, BONE_WHITE, chip=0, bevel=0.2, rough=0)


MORE = {"leaf_seed": ("LeafSeed", 24, leaf_seed), "leaf_scrap": ("LeafScrap", 14, leaf_scrap), "hook": ("Hook", 30, hook), "chain_link": ("ChainLink", 14, chain_link),
        "crystal_shard": ("CrystalShard", 24, crystal(22, 5)), "crystal_splinter": ("CrystalSplinter", 12, crystal(9, 2.2)), "water_orb": ("WaterOrb", 26, water_orb),
        "droplet": ("Droplet", 10, droplet), "soul_wisp": ("SoulWisp", 40, soul_wisp), "flame_drop": ("FlameDrop", 24, flame_drop), "fireball": ("Fireball", 30, fireball),
        "ember": ("Ember", 6, ember), "sound_ring": ("SoundRing", 34, sound_ring), "cannonball": ("Cannonball", 22, cannonball), "rock_chunk": ("RockChunk", 14, rock_chunk),
        "arrow": ("Arrow", 50, arrow), "splinter": ("Splinter", 12, splinter), "acorn": ("Acorn", 20, acorn), "bullet": ("Bullet", 12, bullet), "rocket": ("Rocket", 44, rocket),
        "bone_charm": ("BoneCharm", 26, bone_charm), "bone_chip": ("BoneChip", 8, bone_chip), "dart": ("Dart", 30, dart), "skull": ("Skull", 22, skull)}


PROPS = {"pipe_bomb": pipe_bomb, "shard_red": shard(RED, "ShardRed"), "shard_iron": shard(IRON, "ShardIron"), "smoke_ball": smoke_ball, "blast_star": blast_star,
         "scorch": scorch}
PROPS.update({key: simple(name, size, make) for key, (name, size, make) in MORE.items()})

# ---- Melee impacts (2026-10-06). ------------------------------------------------------------------------------------
def shock_ring():
    """A flat ring of pale light thrown out by a heavy blow; scaled up as it fades."""
    for reach, thick, colour in ((20, 2.6, (0.95, 0.93, 0.85)), (14, 1.2, (1.0, 0.85, 0.55))):
        ring = [(reach * math.cos(k / 24 * math.tau), reach * math.sin(k / 24 * math.tau), 0) for k in range(25)]
        tube(ring, thick, BONE, colour, sides=6, flat=0.35)


def crack_mark():
    """Cracks left in the stone: dark ragged lines running out from the point of impact."""
    for k in range(8):
        a = k / 8 * math.tau + random.uniform(-0.2, 0.2)
        reach = random.uniform(28, 52)
        points = [(0, 0, 0)]
        for step in range(1, 5):
            t = step / 4
            bend = random.uniform(-0.25, 0.25) * t
            points.append((reach * t * math.cos(a + bend), reach * t * math.sin(a + bend), 0.2))
        tube(points, [2.6, 2.2, 1.7, 1.1, 0.3], BONE, (0.05, 0.045, 0.04), sides=4, smooth=False, flat=0.3)
    lump((0, 0, 0), (9, 9, 1.2), BONE, (0.08, 0.075, 0.07), detail=1)


PROPS.update({"shock_ring": simple("ShockRing", 44, shock_ring), "crack_mark": simple("CrackMark", 50, crack_mark)})


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:]
    root, wanted = Path(arguments[0]), arguments[1:] or list(PROPS)
    for key in wanted:
        try:
            kit.reset(900 + list(PROPS).index(key))
            name, size = PROPS[key]()
            kit.build(name, root / name, None, {}, size, texture=512)
        except Exception:
            import traceback
            print("PROP_FAILED", key, flush=True)
            traceback.print_exc()
