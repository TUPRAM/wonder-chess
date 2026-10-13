"""Build the four summoned units in Blender from code, with the monster kit.

Run:  blender -b -P tools/blender/build_summons.py -- <output root> [summon ...]
Each summon is written to <output root>/wc_vn_s_<summon>/blender_k001/. Candidates for owner review, not approved art.

The four are what heroes call into a fight: Wolf Caller's wolf, Treant Caller's treant, Necromancer's skeleton and
Stone Shaper's rock wall. They are smaller and plainer than a hero so that a board stays readable.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as kit  # noqa: E402
from monster_kit import arc, block, fall, hold, jolt, keys, leaf, lump, slab, spike, strike, tube, wave  # noqa: E402
from build_monsters import biped, biped_walk, quad, quad_fold, quad_walk  # noqa: E402

PI = math.pi
FANG = (0.86, 0.82, 0.68)


def r(a, b):
    return random.uniform(a, b)


# =====================================================================================================================
def wolf():
    """A grey spirit wolf: long muzzle, upright ears, a dark ruff down the back and a brush of a tail."""
    fur, dark, pale, eye = (0.15, 0.16, 0.20), (0.06, 0.065, 0.09), (0.36, 0.38, 0.41), (0.45, 0.90, 1.0)
    lump((0, -20, 69), (15, 27, 18), "Chest", fur, detail=2, rough=1.0, smooth=False)
    lump((0, 22, 65), (12, 25, 14), "Body", fur, detail=2, rough=1.0, smooth=False)
    lump((0, -18, 60), (10, 22, 9), "Chest", pale, detail=2, smooth=False, name="belly")
    for n in range(8):                       # the ruff: tufts from the neck to the hips
        y = -44 + n * 11
        spike((r(-2, 2), y, 84 - n * 1.6), (r(-3, 3), y + 9, 96 - n * 2.2 + r(-2, 2)), 4.2, "Chest" if n < 4 else "Body", dark, name="ruff")
    tube([(0, -38, 72), (0, -50, 80), (0, -58, 86)], [10, 9, 8], "Neck", fur, sides=7, smooth=False, rough=0.5)
    for side in (-1, 1):                     # cheek fur
        spike((side * 7, -56, 82), (side * 13, -50, 76), 3.4, "Neck", pale, name="cheek")
    slab((0, -68, 88), (17, 16, 15), "Head", fur, turn=(8, 0, 0), sides=6, rough=0.6, bevel=0.8, name="skull")
    slab((0, -82, 85), (9.5, 16, 8.5), "Head", fur, turn=(6, 0, 0), sides=6, taper=0.7, rough=0.3, bevel=0.5, name="muzzle")
    lump((0, -90.5, 86.5), (2.6, 2.2, 2.2), "Head", dark, name="nose")
    slab((0, -78, 79.5), (8, 16, 3.6), "Jaw", pale, turn=(6, 0, 0), sides=5, taper=0.6, rough=0.2, bevel=0.4, name="jaw")
    for side in (-1, 1):
        lump((side * 6.4, -74.5, 91), (2.0, 1.6, 2.0), "Head", eye, name="eye")
        spike((side * 6.5, -62, 94), (side * 9.5, -60, 109), 3.6, "Head", fur, name="ear")
        spike((side * 6.5, -63, 95), (side * 9, -62, 105), 2.0, "Head", dark, name="ear_inner")
        for n in range(3):
            y = -80 - n * 3.6
            spike((side * (3.6 - n * 0.6), y, 82), (side * (3.6 - n * 0.6), y - 0.6, 77.6), 0.9, "Head", FANG, sides=4, name="fang")
    tail = arc((0, 44, 66), (0, 86, 58), (0, 0, 12), 6)
    tube(tail, [5, 6.5, 7.5, 7.5, 6.5, 4.5, 1.5], "Tail", fur, sides=7, smooth=False, rough=0.5)
    lump((0, 84, 59), (4.5, 6, 4.5), "Tail", pale, detail=1, smooth=False, name="tail_tip")
    bones = {"Hips": ((0, 0, 66), (0, 0, 78), None), "Body": ((0, 8, 66), (0, 42, 62), "Hips"), "Chest": ((0, -4, 68), (0, -40, 72), "Body"),
             "Neck": ((0, -40, 72), (0, -60, 84), "Chest"), "Head": ((0, -60, 84), (0, -88, 86), "Neck"), "Jaw": ((0, -66, 80), (0, -86, 79), "Head"),
             "Tail": ((0, 42, 64), (0, 86, 58), "Body"), **quad(fy=-30, ry=32, fx=11, rx=10, top=58, knee=32, ankle=10)}
    for side in (-1, 1):
        for label, y, x in (("Front", -30, 11), ("Rear", 32, 10)):
            p = label + ("Left" if side > 0 else "Right")
            back = 7 if label == "Rear" else 0
            tube([(side * x, y, 62), (side * (x + 1), y + back, 46), (side * x, y, 32)], [7, 5.6, 4.2], p + "UpLeg", fur, sides=6, smooth=False)
            tube([(side * x, y, 32), (side * x, y + 3 + back, 20), (side * x, y, 10)], [4.2, 3.4, 3.0], p + "Leg", dark, sides=6, smooth=False)
            lump((side * x, y - 4, 5), (5, 8, 5), p + "Foot", pale, detail=1, smooth=False, name="paw")
    clips = {
        "Idle": [wave("Chest", (2, 0, 0), (0, 0, 1.4), cycles=2), wave("Neck", (4, 0, 5), phase=1), wave("Head", (3, 0, 7), phase=2), wave("Tail", (6, 0, 18), cycles=2),
                 wave("Jaw", (4, 0, 0), cycles=2, phase=1)],
        "Move": quad_walk(38, 44) + [wave("Body", (4, 0, 0), (0, 0, 3), cycles=2), wave("Chest", (-5, 0, 0), cycles=2), wave("Tail", (10, 0, 10), cycles=2),
                                     wave("Head", (4, 0, 0), cycles=2)],
        # A lunging bite: jaws open on the way in and snap shut on the strike.
        "Attack": [strike("Body", (-10, 0, 0), (8, 0, 0), (0, 12, -4), (0, -30, 4)), strike("Neck", (-16, 0, 0), (14, 0, 0)), strike("Head", (-18, 0, 0), (10, 0, 0)),
                   keys("Jaw", (0, (0, 0, 0)), (0.32, (36, 0, 0)), (0.5, (2, 0, 0)), (1, (0, 0, 0))), strike("FrontLeftUpLeg", (20, 0, 0), (-40, 0, 0)),
                   strike("FrontRightUpLeg", (20, 0, 0), (-40, 0, 0)), strike("RearLeftUpLeg", (-20, 0, 0), (34, 0, 0)), strike("RearRightUpLeg", (-20, 0, 0), (34, 0, 0))],
        # A howl, head thrown back.
        "Cast": [hold("Neck", (-38, 0, 0)), hold("Head", (-30, 0, 0)), hold("Jaw", (26, 0, 0)), hold("Body", (-8, 0, 0), (0, 4, -4)), wave("Tail", (0, 0, 14), cycles=3)],
        "Hit": [jolt("Body", (-8, 0, 10), (0, 9, 2)), jolt("Head", (-14, 0, 14)), jolt("Jaw", (18, 0, 0))],
        "Defeat": quad_fold() + [keys("Body", (0, (0, 0, 0)), (0.3, (0, 0, 0), (0, 0, -14)), (0.75, (0, 80, 0), (8, 0, -48)), (1, (0, 80, 0), (8, 0, -48))), fall("Neck", (10, 0, 16)),
                                 fall("Jaw", (20, 0, 0)), fall("Tail", (0, 0, 24))],
    }
    return "SpiritWolf", bones, clips, 112, None


# =====================================================================================================================
def treant():
    """A young treant, shoulder-high to a hero: a short trunk under a round crown of leaves, with branch arms."""
    bark = [(0.26, 0.17, 0.09), (0.33, 0.22, 0.12), (0.20, 0.13, 0.07)]
    leaves = [(0.16, 0.42, 0.12), (0.24, 0.52, 0.14), (0.12, 0.33, 0.10)]
    amber = (1.0, 0.72, 0.20)
    lump((0, 2, 112), (30, 24, 34), "Chest", bark[0], detail=2, rough=2.4, smooth=False, name="trunk")
    lump((0, 3, 82), (24, 20, 16), "Hips", bark[2], detail=2, rough=2.0, smooth=False)
    for k in range(5):                       # ridges of bark up the trunk
        a = k / 5 * math.tau + 0.4
        tube([(26 * math.cos(a + t * 0.9), 21 * math.sin(a + t * 0.9) + 2, 78 + t * 64) for t in (0, 0.25, 0.5, 0.75, 1.0)], [5, 4.6, 4.2, 3.8, 3], "Chest",
             random.choice(bark), sides=5, smooth=False, rough=0.4, name="ridge")
    # The face is on the trunk: two amber eyes under a heavy brow, and a knot-hole mouth.
    slab((0, -20, 132), (38, 8, 11), "Chest", bark[2], turn=(74, 0, 0), sides=7, rough=1.4, name="brow")
    for side in (-1, 1):
        lump((side * 9.5, -23.5, 123), (4.4, 2.6, 4.0), "Chest", (0.03, 0.02, 0.02), smooth=False, name="socket")
        lump((side * 9.5, -25, 123), (2.4, 1.8, 2.4), "Chest", amber, name="eye")
    lump((0, -24.5, 108), (6, 2.2, 3.4), "Chest", (0.04, 0.03, 0.02), smooth=False, name="mouth")
    # The crown: a ball of leaf masses that moves with the head.
    for centre, size in (((0, 2, 172), (36, 32, 26)), ((-24, 6, 162), (22, 20, 18)), ((24, 4, 164), (22, 20, 18)), ((2, -18, 160), (20, 16, 15)),
                         ((0, 24, 160), (22, 18, 16)), ((-10, -4, 190), (18, 17, 13)), ((14, 6, 188), (17, 16, 12))):
        lump(centre, size, "Head", random.choice(leaves), detail=2, rough=2.6, smooth=False, name="crown")
    for n in range(14):
        a, lift = r(0, math.tau), r(0.1, 1.0)
        base = (30 * math.cos(a), 26 * math.sin(a) + 3, 162 + 24 * lift)
        leaf(base, (base[0] * 1.42, base[1] * 1.42, base[2] + r(-2, 9)), 9, "Head", random.choice(leaves))
    for side in (-1, 1):
        word = "Left" if side > 0 else "Right"
        lump((side * 31, 2, 136), (13, 12, 11), "Chest", bark[1], detail=2, rough=1.8, smooth=False, name="shoulder")
        tube([(side * 33, 0, 136), (side * 40, 0, 120), (side * 43, 0, 104)], [8.5, 7.6, 6.6], word + "Arm", bark[0], sides=6, smooth=False, rough=0.7)
        tube([(side * 43, 0, 104), (side * 45, -4, 88), (side * 45, -8, 72)], [6.6, 7.0, 7.6], word + "ForeArm", bark[1], sides=6, smooth=False, rough=0.7)
        for n in (-1, 0, 1):                 # three twig fingers
            spike((side * 45 + n * 4, -9, 70), (side * 45 + n * 9, -15 + abs(n) * 3, 54), 3.2, word + "ForeArm", bark[2], name="finger")
        leaf((side * 42, 2, 112), (side * 56, 6, 122), 8, word + "Arm", leaves[1])
        tube([(side * 14, 0, 80), (side * 17, -3, 60), (side * 17, -4, 40)], [11, 10, 8.5], word + "UpLeg", bark[0], sides=7, smooth=False, rough=0.8)
        tube([(side * 17, -4, 40), (side * 18, -2, 20), (side * 18, 0, 6)], [8.5, 8, 10], word + "Leg", bark[1], sides=7, smooth=False, rough=0.8)
        for n in (-1, 0, 1):                 # root toes
            tube([(side * 18 + n * 4, -3, 6), (side * 18 + n * 10, -14 + abs(n) * 4, 3), (side * 18 + n * 15, -22 + abs(n) * 6, 1)], [4.4, 3.2, 1.2], word + "Leg", bark[2],
                 sides=5, smooth=False, name="toe")
    bones = {"Hips": ((0, 0, 78), (0, 0, 90), None), "Chest": ((0, 0, 90), (0, 0, 138), "Hips"), "Head": ((0, 0, 138), (0, 0, 180), "Chest"),
             **biped(hip=78, knee=40, shoulder=138, elbow=104, hand=70, hx=14, sx=32)}
    clips = {
        "Idle": [wave("Chest", (1.5, 0, 1.5), (0, 0, 1.0)), wave("Head", (2, 0, 3), phase=1), wave("LeftArm", (2, 3, 0), phase=0.5), wave("RightArm", (2, -3, 0), phase=0.9)],
        "Move": biped_walk(24, 30, 16) + [wave("Chest", (0, 4, 0)), wave("Chest", (2, 0, 0), (0, 0, 2.2), cycles=2), wave("Head", (0, 0, 4), cycles=2)],
        # One branch swung down overhead.
        "Attack": [strike("RightArm", (-150, 0, 0), (-36, 0, 0)), strike("RightForeArm", (-20, 0, 0), (-28, 0, 0)), strike("Chest", (-12, 0, 0), (22, 0, 0), (0, 4, 0), (0, -10, -5)),
                   strike("Head", (-6, 0, 0), (8, 0, 0)), strike("LeftArm", (20, 0, 0), (-10, 0, 0))],
        "Cast": [hold("LeftArm", (-150, 20, 0)), hold("RightArm", (-150, -20, 0)), hold("Chest", (-10, 0, 0)), wave("Head", (0, 0, 6), cycles=3)],
        "Hit": [jolt("Chest", (-10, 0, 6), (0, 6, 0)), jolt("Head", (-12, 0, 0)), jolt("LeftArm", (-14, 0, 0))],
        "Defeat": [fall("Hips", (0, 0, 0), (0, 0, -54)), fall("LeftUpLeg", (-80, 0, 0)), fall("RightUpLeg", (-70, 0, 0)), fall("LeftLeg", (120, 0, 0)), fall("RightLeg", (115, 0, 0)),
                   keys("Chest", (0, (0, 0, 0)), (0.5, (10, 0, 0)), (1, (58, 0, 8))), fall("Head", (22, 0, 0)), fall("LeftArm", (-20, 20, 0)), fall("RightArm", (-25, -20, 0))],
    }
    return "Treant", bones, clips, 200, None


# =====================================================================================================================
def skeleton():
    """A raised skeleton with a notched short sword: bare bones, a round skull and two cold lights for eyes."""
    bone, shade, rust, light = (0.50, 0.46, 0.35), (0.32, 0.29, 0.21), (0.20, 0.13, 0.08), (0.30, 1.0, 0.80)
    slab((0, 1, 96), (26, 9, 14), "Hips", bone, sides=7, rough=0.5, bevel=1.0, name="pelvis")
    tube([(0, 3, 98), (0, 4, 112), (0, 3, 126), (0, 1, 140), (0, 0, 150)], [3.4, 3.2, 3.2, 3.0, 2.8], "Chest", shade, sides=6, ridge=0.18, smooth=False, name="spine")
    for n in range(4):                       # ribs: four hoops that narrow toward the waist
        z, reach = 142 - n * 7.5, 15 - n * 1.6
        for side in (-1, 1):
            tube([(0, 3, z + 1), (side * reach * 0.8, 4, z), (side * reach, -4, z - 2), (side * reach * 0.6, -11, z - 4), (side * 1.5, -12.5, z - 5)], [1.7, 1.8, 1.8, 1.6, 1.3],
                 "Chest", bone, sides=5, smooth=False, name="rib")
    tube([(0, -12.5, 124), (0, -13, 144)], [1.8, 2.2], "Chest", bone, sides=5, smooth=False, name="breastbone")
    tube([(-22, 0, 149), (22, 0, 149)], [2.2, 2.2], "Chest", bone, sides=5, smooth=False, name="collar")
    lump((0, -2, 167), (13.5, 15, 14.5), "Head", bone, detail=2, smooth=False, name="skull")
    slab((0, -9, 155.5), (11, 7, 5), "Head", shade, sides=6, taper=0.8, rough=0.2, bevel=0.5, name="jaw")
    for side in (-1, 1):
        lump((side * 4.6, -12.2, 167), (3.2, 2.2, 3.4), "Head", (0.02, 0.02, 0.03), smooth=False, name="socket")
        lump((side * 4.6, -13, 167), (1.5, 1.2, 1.5), "Head", light, name="eye")
        for n in range(3):
            block((side * (1.6 + n * 2.4), -13.6, 157.5), (1.8, 1.4, 2.6), "Head", bone, chip=0.2, bevel=0.2, rough=0, name="tooth")
        word = "Left" if side > 0 else "Right"
        lump((side * 24, 0, 148), (4.2, 4.2, 4.2), "Chest", bone, detail=1, smooth=False, name="shoulder")
        tube([(side * 24, 0, 148), (side * 34, 0, 114)], [3.8, 3.1], word + "Arm", bone, sides=6, smooth=False)
        lump((side * 35, 0, 112), (3.2, 3.2, 3.2), word + "Arm", shade, detail=1, smooth=False, name="elbow")
        tube([(side * 36, 0, 112), (side * 39, -9, 84)], [3.1, 2.6], word + "ForeArm", bone, sides=6, smooth=False)
        lump((side * 39, -10, 80), (3.6, 3.6, 4.4), word + "ForeArm", bone, detail=1, smooth=False, name="hand")
        tube([(side * 11, 0, 92), (side * 14, -4, 50)], [4.8, 3.8], word + "UpLeg", bone, sides=6, smooth=False)
        lump((side * 14, -5, 48), (4, 4, 4), word + "UpLeg", shade, detail=1, smooth=False, name="knee")
        tube([(side * 14, -4, 48), (side * 15, 0, 6)], [3.8, 3.0], word + "Leg", bone, sides=6, smooth=False)
        slab((side * 15, -6, 3), (8, 17, 5), word + "Leg", bone, sides=5, taper=0.7, rough=0.2, bevel=0.5, name="foot")
    # The sword, held point-up in the right hand.
    tube([(-39, -10, 76), (-39, -10, 86)], [1.6, 1.6], "RightForeArm", rust, sides=6, smooth=False, name="grip")
    block((-39, -10, 87.5), (15, 3.6, 3.0), "RightForeArm", rust, chip=0.4, bevel=0.4, rough=0, name="guard")
    slab((-39, -10, 116), (10, 2.0, 56), "RightForeArm", (0.26, 0.27, 0.30), sides=4, taper=1.0, chip=0.5, bevel=0.3, rough=0.3, name="blade")
    spike((-39, -10, 142), (-39, -10, 158), 4.4, "RightForeArm", (0.26, 0.27, 0.30), sides=4, name="point")
    bones = {"Hips": ((0, 0, 92), (0, 0, 104), None), "Chest": ((0, 0, 104), (0, 0, 150), "Hips"), "Head": ((0, 0, 150), (0, -2, 178), "Chest"),
             **biped(hip=92, knee=48, shoulder=148, elbow=112, hand=80, hx=11, sx=24)}
    clips = {
        "Idle": [wave("Chest", (1.5, 0, 2), (0, 0, 0.8)), wave("Head", (3, 0, 7), phase=1), wave("LeftArm", (3, 4, 0), phase=0.5), wave("RightArm", (3, -3, 0), phase=0.9)],
        # A loose, rattling walk.
        "Move": biped_walk(30, 36, 20) + [wave("Chest", (0, 6, 0)), wave("Chest", (3, 0, 0), (0, 0, 2.0), cycles=2), wave("Head", (0, 0, 8), cycles=2)],
        # A downward cut with the sword arm.
        "Attack": [strike("RightArm", (-160, 0, 0), (-30, 0, 0)), strike("RightForeArm", (-30, 0, 0), (-20, 0, 0)), strike("Chest", (-12, -14, 0), (20, 12, 0), (0, 3, 0), (0, -8, -3)),
                   strike("Head", (-6, 0, 0), (10, 0, 0)), strike("LeftArm", (24, 0, 0), (-14, 0, 0))],
        "Cast": [hold("RightArm", (-170, 0, 0)), hold("LeftArm", (-60, 30, 0)), hold("Chest", (-10, 0, 0)), wave("Head", (0, 0, 10), cycles=4)],
        "Hit": [jolt("Chest", (-12, 0, 8), (0, 6, 0)), jolt("Head", (-18, 0, 12)), jolt("LeftArm", (-20, 0, 0))],
        # It falls apart downward: hips drop, the chest folds over and the head rolls off to one side.
        "Defeat": [fall("Hips", (0, 0, 0), (0, 0, -80), at=0.55), fall("LeftUpLeg", (-85, 0, 0), at=0.5), fall("RightUpLeg", (-75, 0, 0), at=0.5), fall("LeftLeg", (125, 0, 0), at=0.5),
                   fall("RightLeg", (120, 0, 0), at=0.5), keys("Chest", (0, (0, 0, 0)), (0.45, (14, 0, 0)), (1, (72, 0, 10))),
                   keys("Head", (0, (0, 0, 0)), (0.5, (10, 0, 0)), (1, (40, 0, 60), (16, -10, -8))), fall("LeftArm", (-30, 30, 0)), fall("RightArm", (-40, -30, 0))],
    }
    return "Skeleton", bones, clips, 190, None


# =====================================================================================================================
def rock_wall():
    """A waist-high wall of rough stone blocks raised out of the ground. It never moves or attacks; it only stands and breaks."""
    stone = [(0.15, 0.16, 0.19), (0.20, 0.21, 0.23), (0.11, 0.12, 0.15), (0.24, 0.23, 0.21)]
    moss = (0.10, 0.24, 0.07)
    width, rows = 112, ((0, 30, "Base", 4), (30, 28, "Base", 3), (58, 26, "Top", 4), (84, 22, "Top", 3))
    for bottom, height, bone, count in rows:
        span = width / count
        for k in range(count):
            x = -width / 2 + span * (k + 0.5) + r(-2, 2)
            block((x, r(-2, 2), bottom + height / 2), (span - 3 + r(-2, 2), 30 + r(-4, 3), height - 2), bone, random.choice(stone), turn=(r(-3, 3), r(-3, 3), r(-4, 4)),
                  chip=1.6, bevel=1.8, rough=1.8, name="stone")
    for x, z in ((-40, 108), (-8, 112), (30, 107)):  # broken teeth along the top
        spike((x, r(-3, 3), z - 6), (x + r(-5, 5), r(-3, 3), z + 14), 9, "Top", random.choice(stone), sides=5, name="tooth")
    for centre in ((-30, -15, 60), (22, -16, 32), (40, -14, 88), (-12, 15, 86)):
        lump(centre, (10, 4, 7), "Top" if centre[2] > 58 else "Base", moss, detail=1, chip=0.8, smooth=False, name="moss")
    for x in (-52, -20, 14, 46):             # rubble pushed up where it rose
        lump((x + r(-4, 4), -24 + r(-3, 3), 5), (r(7, 11), r(6, 9), r(4, 6)), "Base", random.choice(stone), detail=1, rough=1.0, smooth=False, name="rubble")
    bones = {"Base": ((0, 0, 0), (0, 0, 58), None), "Top": ((0, 0, 58), (0, 0, 110), "Base")}
    clips = {
        "Idle": [],
        "Move": [],
        "Attack": [],
        "Cast": [],
        "Hit": [jolt("Top", (-5, 0, 3), (0, 3, 0)), jolt("Base", (-1.5, 0, 0))],
        # The top row slides off and the rest sinks back into the ground.
        "Defeat": [keys("Top", (0, (0, 0, 0)), (0.45, (26, 0, 8), (0, -14, -10)), (1, (70, 0, 14), (0, -34, -44))), fall("Base", (0, 0, 0), (0, 0, -66), at=0.9)],
    }
    return "RockWall", bones, clips, 130, None


SUMMONS = {"wolf": wolf, "treant": treant, "skeleton": skeleton, "rock_wall": rock_wall}

if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:]
    root, wanted = Path(arguments[0]), arguments[1:] or list(SUMMONS)
    for key in wanted:
        try:
            kit.reset(917 + list(SUMMONS).index(key))
            name, bones, clips, height, lengths = SUMMONS[key]()
            kit.build(name, root / f"wc_vn_s_{key}" / "blender_k001", bones, clips, height, lengths)
        except Exception:
            import traceback
            print("SUMMON_FAILED", key, flush=True)
            traceback.print_exc()
