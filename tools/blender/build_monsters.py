"""Build Wonder Chess monsters and bosses in Blender from code.

Run:  blender -b -P tools/blender/build_monsters.py -- <output root> [monster ...]
Each monster is written to <output root>/wc_vn_n_<monster>/blender_k001/. Candidates for owner review, not approved art.
Looks follow production/monsters/MONSTER_ROUNDS_DESIGN.md.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as kit  # noqa: E402
from monster_kit import arc, block, fall, hold, jolt, keys, leaf, leg, lump, pane, slab, spike, spin, strike, tube, wave  # noqa: E402
from mathutils import Vector  # noqa: E402

PI = math.pi
SLATE = [(0.078, 0.088, 0.108), (0.102, 0.114, 0.138), (0.060, 0.068, 0.086), (0.128, 0.138, 0.158)]
LIME = [(0.42, 0.40, 0.34), (0.50, 0.48, 0.41), (0.36, 0.35, 0.30)]
HORN, HOOF, MOSS, FERN = (0.40, 0.35, 0.26), (0.05, 0.05, 0.058), (0.17, 0.38, 0.10), (0.20, 0.50, 0.14)
BLUE_EYE, SOCKET, QUARTZ = (0.25, 0.85, 1.0), (0.02, 0.022, 0.03), (0.78, 0.80, 0.84)
BARK = [(0.16, 0.10, 0.06), (0.21, 0.14, 0.08), (0.12, 0.08, 0.05)]
GREEN_EYE, GOLD_LIGHT, BRONZE, IRON = (0.35, 1.0, 0.30), (1.0, 0.85, 0.30), (0.42, 0.27, 0.10), (0.13, 0.13, 0.15)


def r(a, b):
    return random.uniform(a, b)


def stone(colours=SLATE):
    return random.choice(colours)


def quad(front_parent="Chest", rear_parent="Body", fy=-44, ry=50, fx=25, rx=23, top=68, knee=39, ankle=15, k=1.0):
    bones = {}
    for side, word in ((1, "Left"), (-1, "Right")):
        for label, y, x, parent in (("Front", fy, fx, front_parent), ("Rear", ry, rx, rear_parent)):
            p = label + word
            bones[p + "UpLeg"] = ((side * x * k, y * k, top * k), (side * x * k, y * k, knee * k), parent)
            bones[p + "Leg"] = ((side * x * k, y * k, knee * k), (side * x * k, y * k, ankle * k), p + "UpLeg")
            bones[p + "Foot"] = ((side * x * k, y * k, ankle * k), (side * x * k, (y - 6) * k, 2 * k), p + "Leg")
    return bones


def quad_walk(swing=27, bend=30):
    return [leg("FrontLeftUpLeg", "FrontLeftLeg", "FrontLeftFoot", 0, swing, bend), leg("RearRightUpLeg", "RearRightLeg", "RearRightFoot", 0.5, swing, bend, -0.6),
            leg("FrontRightUpLeg", "FrontRightLeg", "FrontRightFoot", PI, swing, bend), leg("RearLeftUpLeg", "RearLeftLeg", "RearLeftFoot", PI + 0.5, swing, bend, -0.6)]


def quad_fold():
    out = []
    for p in ("FrontLeft", "FrontRight", "RearLeft", "RearRight"):
        front = p.startswith("Front")
        out += [fall(p + "UpLeg", ((-55 if front else 50), 0, 0), at=0.45), fall(p + "Leg", ((100 if front else -95), 0, 0), at=0.45)]
    return out


# =====================================================================================================================
def ram(boss=False):
    """Slate Ram, and Old Tusk the Slate King built on the same body with a king's damage and trophies."""
    profile = [(-66, 74, 76, 86), (-49, 90, 92, 90), (-31, 96, 96, 91), (-12, 88, 86, 87), (8, 80, 76, 83), (28, 78, 72, 82), (48, 76, 72, 81), (66, 66, 62, 79)]
    for index, (y, width, height, z) in enumerate(profile):
        slab((r(-2, 2), y, z + r(-2, 3)), (width, r(19, 24), height), "Chest" if index < 4 else "Body", stone(), turn=(r(-7, 7), r(-6, 6), r(-4, 4)))
    slab((-20, -40, 132), (54, 9, 50), "Chest", stone(), turn=(72, 0, -16), sides=6)
    slab((20, -40, 132), (54, 9, 50), "Chest", stone(), turn=(72, 0, 16), sides=6)
    slab((0, -22, 138), (30, 8, 40), "Chest", stone(), turn=(60, 0, 3), sides=5)
    slab((-15, 46, 113), (38, 5, 36), "Body", stone(), turn=(80, 0, -12), sides=6)
    slab((15, 46, 113), (38, 5, 36), "Body", stone(), turn=(80, 0, 12), sides=6)
    slab((0, 80, 80), (44, 9, 42), "Body", stone(), turn=(-12, 0, 0))
    slab((0, 91, 92), (12, 16, 12), "Tail", stone(), turn=(-35, 0, 0), sides=5, taper=0.5)
    slab((0, -80, 95), (58, 11, 60), "Neck", stone(), turn=(-14, 0, 4))
    slab((0, -92, 101), (50, 11, 52), "Neck", stone(), turn=(-20, 0, -5))
    slab((0, -113, 100), (44, 28, 48), "Head", stone(), turn=(30, 0, 0), taper=0.62)
    slab((0, -134, 86), (25, 15, 25), "Head", SLATE[2], turn=(38, 0, 0), taper=0.8, sides=6)
    slab((0, -117, 121), (46, 7, 22), "Head", SLATE[3], turn=(64, 0, 0), sides=6)
    slab((0, -126, 78), (20, 12, 9), "Head", SLATE[2], turn=(34, 0, 0), sides=6)
    for side in (-1, 1):
        points, radii, turns = [], [], (1.9 if boss else 1.42)
        for step in range(45):
            t = step / 44
            angle = -0.5 + t * turns * math.tau
            curl = (24 if boss else 21) - 9 * t
            points.append((side * (19 + (30 if boss else 20) * t * t + 4 * t), -100 + curl * math.sin(angle), 111 + curl * math.cos(angle)))
            radii.append((15 if boss else 13.5) - 10 * t)
        if boss and side > 0:   # one horn of the old king is snapped off short
            points, radii = points[:30], radii[:29] + [radii[29] * 1.25]
        tube(points, radii, "Head", HORN, sides=8, ridge=0.07, smooth=False, chip=0.4, name="horn")
        lump((side * 17.5, -128, 105), (5.0, 3.4, 6.0), "Head", SOCKET, smooth=False)
        if not (boss and side < 0):
            lump((side * 19.8, -130, 105), (3.0, 2.4, 3.8), "Head", BLUE_EYE)
        for label, y, x, lean in (("Front", -44, 25, -4), ("Rear", 50, 23, 6)):
            p = label + ("Left" if side > 0 else "Right")
            block((side * x, y, 52), (28, 32, 38), p + "UpLeg", stone(), turn=(lean, 0, side * 4))
            slab((side * (x + 13), y - 2, 44), (20, 5, 20), p + "UpLeg", stone(), turn=(0, 0, 90 + side * 8), sides=5)
            block((side * x, y + (2 if label == "Rear" else 0), 27), (20, 22, 26), p + "Leg", stone(), turn=(-lean, 0, 0))
            for toe in (-1, 1):
                slab((side * x + toe * 5.5, y - 4, 8), (11, 26, 15), p + "Foot", HOOF, turn=(0, 0, toe * 5), sides=5, taper=0.7, chip=0.5, bevel=0.8, rough=0.6)
    for centre, size, bone, turn in (((22, -29, 96), (5, 12.5, 40), "Chest", (0, 24, 0)), ((-27, 30, 84), (4, 12.5, 34), "Body", (0, -18, 0)),
                                     ((6, -113, 118), (3, 20, 14), "Head", (30, 30, 0))):
        slab(centre, size, bone, QUARTZ, turn=turn, sides=4, chip=0.3, bevel=0.3, rough=0)
    for y, x, bone in ((-58, 9, "Chest"), (0, 14, "Chest"), (20, -8, "Body"), (40, 10, "Body"), (60, -4, "Body")):
        z = 124 if y < 0 else 117
        lump((x, y, z), (r(9, 14), r(7, 10), r(3.5, 5)), bone, MOSS, detail=1, chip=1.0, smooth=False)
    for x, y, bone in ((-13, 5, "Chest"), (11, 41, "Body"), (-4, 61, "Body"), (15, 21, "Body")):
        leaf((x, y, 119), (x + r(-6, 6), y + r(-6, 6), 142), 6, bone, FERN)
    if boss:
        # A lifetime of failed hunts is stuck in his back: spear shafts, arrows, and a dead tree rooted in one shoulder.
        for x, y, lean in ((-18, 20, -22), (14, 44, 18), (-6, 58, -8), (22, 8, 28), (-24, 40, -30)):
            tip = (x + lean * 0.9, y + r(8, 26), 118 + r(48, 70))
            tube([(x, y, 112), tip], 1.6, "Body", (0.20, 0.13, 0.07), sides=5, smooth=False, name="shaft")
            spike(tip, (tip[0] + lean * 0.12, tip[1] + 2, tip[2] + 9), 3.2, "Body", IRON, sides=4)
        trunk = [(-30, -44, 128), (-36, -46, 158), (-32, -50, 186), (-40, -52, 212)]
        tube(trunk, [7, 5.5, 4, 2.2], "Chest", BARK[2], sides=6, smooth=False, rough=0.5, name="deadtree")
        for base, tip in (((-36, -46, 158), (-60, -40, 182)), ((-32, -50, 186), (-12, -58, 208)), ((-34, -48, 172), (-44, -70, 190))):
            tube([base, tip], [3, 1], "Chest", BARK[2], sides=5, smooth=False)
        for centre, size, turn in (((30, -12, 100), (6, 13, 50), (0, 30, 0)), ((-34, 10, 92), (5, 13, 44), (0, -24, 0)), ((0, 50, 108), (5, 13, 36), (0, 80, 0))):
            slab(centre, size, "Body" if centre[1] > 0 else "Chest", QUARTZ, turn=turn, sides=4, chip=0.3, bevel=0.3, rough=0)
    bones = {"Hips": ((0, 0, 78), (0, 0, 92), None), "Body": ((0, 20, 80), (0, 60, 80), "Hips"), "Chest": ((0, -10, 82), (0, -60, 84), "Body"),
             "Neck": ((0, -68, 92), (0, -96, 102), "Chest"), "Head": ((0, -98, 104), (0, -138, 88), "Neck"), "Tail": ((0, 84, 90), (0, 100, 96), "Body"), **quad()}
    clips = {
        "Idle": [wave("Body", (0.8, 0, 0), (0, 0, 1)), wave("Chest", (1.6, 0, 0)), wave("Neck", (3.5, 0, 3), phase=-0.7), wave("Head", (2.5, 0, 5), phase=-1.3),
                 wave("Tail", (6, 0, 16), cycles=2)],
        "Move": quad_walk() + [wave("Body", (1.5, 0, 0), (0, 0, 1.6), cycles=2), wave("Body", (0, 3, 0)), wave("Neck", (4, 0, 0), cycles=2), wave("Tail", (0, 0, 10))],
        "Attack": [strike("Body", (-5, 0, 0), (7, 0, 0), (0, 9, 2), (0, -24, -5)), strike("Neck", (-14, 0, 0), (20, 0, 0)), strike("Head", (-12, 0, 0), (17, 0, 0)),
                   strike("FrontLeftUpLeg", (-10, 0, 0), (22, 0, 0)), strike("FrontRightUpLeg", (-10, 0, 0), (22, 0, 0)), strike("Tail", (0, 0, 0), (-30, 0, 0))],
        "Cast": [hold("Body", (6, 0, 0), (0, 7, -3)), hold("Neck", (22, 0, 0)), hold("Head", (16, 0, 0)), hold("Tail", (-25, 0, 0)), wave("Head", (3, 0, 0), cycles=6),
                 keys("FrontRightUpLeg", (0, (0, 0, 0)), (0.2, (-38, 0, 0)), (0.34, (16, 0, 0)), (0.5, (-38, 0, 0)), (0.64, (16, 0, 0)), (1, (0, 0, 0))),
                 keys("FrontRightLeg", (0, (0, 0, 0)), (0.2, (48, 0, 0)), (0.34, (6, 0, 0)), (0.5, (48, 0, 0)), (0.64, (6, 0, 0)), (1, (0, 0, 0)))],
        "Hit": [jolt("Body", (-5, 0, 0), (0, 8, 1.5)), jolt("Neck", (-12, 0, 8)), jolt("Head", (-9, 0, 10))],
        "Defeat": quad_fold() + [keys("Body", (0, (0, 0, 0)), (0.3, (0, 0, 0), (0, 0, -18)), (0.75, (0, 68, 0), (14, 0, -44)), (1, (0, 68, 0), (14, 0, -44))),
                                 fall("Neck", (14, 0, 10)), fall("Head", (10, 8, 0))],
    }
    return ("OldTusk" if boss else "SlateRam"), bones, clips, 150, None


# =====================================================================================================================
def seedpod():
    husk, inner = (0.20, 0.11, 0.05), (1.0, 0.62, 0.12)
    for side in (-1, 1):
        lump((side * 9, 0, 32), (11, 21, 20), "Body", husk, detail=2, rough=0.8, smooth=False)
        lump((side * 5, -15, 34), (2.2, 2.2, 2.8), "Body", (1.0, 0.8, 0.3))
    lump((0, 0, 32), (6.5, 17, 16), "Body", inner, detail=2)
    tube([(0, 2, 50), (0, 0, 60), (1, -3, 68)], [2.0, 1.6, 1.1], "Sprout", (0.45, 0.70, 0.25), sides=6)
    leaf((1, -3, 67), (-9, -8, 76), 7, "Sprout", (0.50, 0.78, 0.28))
    leaf((1, -3, 67), (11, -1, 77), 7, "Sprout", (0.50, 0.78, 0.28))
    bones = {"Hips": ((0, 0, 30), (0, 0, 40), None), "Body": ((0, 6, 32), (0, 20, 32), "Hips"), "Sprout": ((0, 2, 50), (0, 0, 66), "Body")}
    walk = []
    for index, (sx, sy) in enumerate(((1, -1), (-1, -1), (1, 1), (-1, 1))):
        name = ("Front" if sy < 0 else "Rear") + ("Left" if sx > 0 else "Right")
        hip, knee, foot = (sx * 9, sy * 9, 24), (sx * 23, sy * 15, 30), (sx * 27, sy * 18, 0)
        tube([hip, knee], [2.4, 1.9], name + "UpLeg", (0.30, 0.19, 0.09), sides=5, smooth=False)
        tube([knee, foot], [1.9, 0.8], name + "Leg", (0.30, 0.19, 0.09), sides=5, smooth=False)
        bones[name + "UpLeg"] = (hip, knee, "Body")
        bones[name + "Leg"] = (knee, foot, name + "UpLeg")
        walk.append(leg(name + "UpLeg", name + "Leg", None, PI * (index in (1, 2)), 24, 26, sy * -1))
    clips = {
        "Idle": [wave("Body", (2, 0, 0), (0, 0, 1.2), cycles=2), wave("Sprout", (6, 8, 0), cycles=2), wave("Body", (0, 0, 4))],
        "Move": walk + [wave("Body", (3, 0, 0), (0, 0, 1.5), cycles=2), wave("Sprout", (12, 0, 0), cycles=2, phase=1)],
        "Attack": [strike("Body", (-18, 0, 0), (26, 0, 0), (0, 5, 6), (0, -14, -3)), strike("Sprout", (20, 0, 0), (-30, 0, 0))],
        "Cast": [hold("Body", (0, 0, 0), (0, 0, 6)), wave("Body", (0, 0, 9), cycles=5), wave("Sprout", (0, 20, 0), cycles=5)],
        "Hit": [jolt("Body", (-16, 0, 0), (0, 6, 3))],
        "Defeat": [fall("Body", (0, 85, 0), (6, 0, -18)), fall("FrontLeftUpLeg", (0, 60, 0)), fall("RearLeftUpLeg", (0, 60, 0)), fall("Sprout", (0, 30, 0))],
    }
    return "Seedpod", bones, clips, 75, None


# =====================================================================================================================
def reed_archer():
    reed, dry, cord, cattail = (0.30, 0.44, 0.16), (0.55, 0.48, 0.26), (0.10, 0.07, 0.04), (0.20, 0.11, 0.05)
    for k in range(9):
        a = k / 9 * math.tau
        tube([(8 * math.cos(a), 6 * math.sin(a), 60), (9.5 * math.cos(a + 0.5), 7 * math.sin(a + 0.5), 84), (8 * math.cos(a + 1.0), 6 * math.sin(a + 1.0), 108)],
             2.8, "Body", reed if k % 3 else dry, sides=5, smooth=False)
    for z in (66, 100):
        tube([(0, 0, z - 2), (0, 0, z + 2)], [11.5, 11.5], "Body", cord, sides=10, flat=0.78, smooth=False)
    tube([(0, 0, 106), (0, -1, 114)], [3, 2.6], "Head", reed, sides=6)
    tube([(0, -1, 113), (0, -2, 124), (0, -2, 138), (0, -2, 142)], [4.5, 6.5, 6, 2.5], "Head", cattail, sides=8, rough=0.4)
    tube([(0, -2, 141), (0, -2, 154)], [1.0, 0.4], "Head", dry, sides=4, smooth=False)
    # The bow arm (left) and the drawing arm (right).
    shoulder_l, elbow_l, hand_l = (12, 0, 101), (22, -12, 92), (20, -32, 98)
    tube([shoulder_l, elbow_l], [3, 2.6], "LeftArm", reed, sides=5, smooth=False)
    tube([elbow_l, hand_l], [2.6, 2.2], "LeftForeArm", dry, sides=5, smooth=False)
    tube(arc((20, -34, 48), (20, -34, 146), (0, -15, 0), 10), [0.9, 1.6, 2.0, 2.3, 2.5, 2.6, 2.5, 2.3, 2.0, 1.6, 0.9], "LeftForeArm", (0.38, 0.30, 0.12), sides=6, name="bow")
    tube([(20, -34, 48), (20, -34, 146)], 0.35, "LeftForeArm", (0.85, 0.85, 0.8), sides=4, smooth=False, name="string")
    shoulder_r, elbow_r, hand_r = (-12, 0, 101), (-21, -4, 84), (-17, -16, 74)
    tube([shoulder_r, elbow_r], [3, 2.6], "RightArm", reed, sides=5, smooth=False)
    tube([elbow_r, hand_r], [2.6, 2.0], "RightForeArm", dry, sides=5, smooth=False)
    for k in (-1, 0, 1):
        tube([hand_r, (hand_r[0] + k * 3, hand_r[1] - 7, hand_r[2] - 6)], [1.0, 0.5], "RightForeArm", reed, sides=4, smooth=False)
    for k in range(5):
        tube([(-6 + k * 3, 9, 84), (-10 + k * 5, 14, 128 + k * 2)], 0.8, "Body", dry, sides=4, smooth=False, name="arrow")
    bones = {"Hips": ((0, 0, 60), (0, 0, 72), None), "Body": ((0, 0, 62), (0, 0, 104), "Hips"), "Head": ((0, 0, 106), (0, -2, 142), "Body"),
             "LeftArm": (shoulder_l, elbow_l, "Body"), "LeftForeArm": (elbow_l, hand_l, "LeftArm"), "RightArm": (shoulder_r, elbow_r, "Body"),
             "RightForeArm": (elbow_r, hand_r, "RightArm")}
    for side, word in ((1, "Left"), (-1, "Right")):
        hip, knee, foot = (side * 6, 0, 60), (side * 7.5, -4, 31), (side * 7, 1, 2)
        tube([hip, knee], [3.4, 2.8], word + "UpLeg", reed, sides=5, smooth=False)
        tube([knee, foot], [2.8, 2.2], word + "Leg", dry, sides=5, smooth=False)
        for k in (-1, 0, 1):
            tube([foot, (foot[0] + k * 5, foot[1] - 9 + abs(k) * 3, 0.8)], [1.6, 0.6], word + "Leg", cord, sides=4, smooth=False)
        bones[word + "UpLeg"] = (hip, knee, "Hips")
        bones[word + "Leg"] = (knee, foot, word + "UpLeg")
    clips = {
        "Idle": [wave("Body", (1.2, 0, 2)), wave("Head", (2, 0, 5), phase=1), wave("LeftArm", (2, 0, 0), phase=0.6), wave("RightArm", (3, 0, 0), phase=2)],
        "Move": [leg("LeftUpLeg", "LeftLeg", None, 0, 30, 34), leg("RightUpLeg", "RightLeg", None, PI, 30, 34), wave("Body", (3, 0, 0), (0, 0, 1.5), cycles=2),
                 wave("RightArm", (18, 0, 0)), wave("Head", (0, 0, 4))],
        # Raise the bow, draw the right hand back to the cheek, loose.
        "Attack": [keys("LeftArm", (0, (0, 0, 0)), (0.3, (-28, 0, 10)), (0.7, (-28, 0, 10)), (1, (0, 0, 0))),
                   keys("RightArm", (0, (0, 0, 0)), (0.3, (-70, 0, 20)), (0.5, (-40, 0, -25)), (0.58, (-75, 0, 10)), (1, (0, 0, 0))),
                   keys("RightForeArm", (0, (0, 0, 0)), (0.3, (-40, 0, 0)), (0.5, (-95, 0, 0)), (0.58, (-20, 0, 0)), (1, (0, 0, 0))),
                   keys("Body", (0, (0, 0, 0)), (0.5, (-4, 0, -8)), (0.58, (3, 0, -4)), (1, (0, 0, 0)))],
        "Cast": [hold("LeftArm", (-60, 0, 10)), hold("RightArm", (-90, 0, 0)), hold("Body", (-8, 0, 0))],
        "Hit": [jolt("Body", (-10, 0, 6), (0, 5, 0)), jolt("Head", (-14, 0, 0))],
        "Defeat": [fall("Body", (-80, 0, 12), (0, 20, -8)), fall("LeftUpLeg", (60, 0, 0)), fall("RightUpLeg", (45, 0, 0)), fall("Head", (-20, 0, 0)),
                   fall("LeftArm", (0, -50, 0)), fall("Hips", (0, 0, 0), (0, 0, -46))],
    }
    return "ReedArcher", bones, clips, 155, None


# =====================================================================================================================
def lantern_bulb():
    skin, vein, stalk, glow = (0.80, 0.42, 0.08), (0.45, 0.20, 0.04), (0.22, 0.42, 0.14), (1.0, 0.88, 0.40)
    lump((0, 0, 40), (31, 31, 36), "Body", skin, detail=3)
    for k in range(10):
        a = k / 10 * math.tau
        points = [(31.5 * math.sin(t) * math.cos(a), 31.5 * math.sin(t) * math.sin(a), 40 - 36.5 * math.cos(t)) for t in (0.25, 0.7, 1.2, 1.8, 2.4, 2.9)]
        tube(points, 1.0, "Body", vein, sides=4, smooth=False, name="vein")
    tube([(0, 0, 70), (0, 0, 80), (0, -1, 90)], [13, 8, 4.5], "Body", (0.60, 0.36, 0.10), sides=10)
    hook = [(0, -1, 88), (0, -3, 104), (0, -12, 116), (0, -24, 116), (0, -31, 106), (0, -31, 98)]
    tube(hook, [4.2, 3.4, 2.8, 2.3, 1.9, 1.5], "Stalk", stalk, sides=7)
    tube([(0, -31, 98), (0, -31, 91)], 0.5, "Seed", vein, sides=4, smooth=False)
    lump((0, -31, 86), (5, 5, 6.5), "Seed", glow, detail=2)
    for k in range(9):
        a = k / 9 * math.tau + 0.2
        tube([(17 * math.cos(a), 17 * math.sin(a), 12), (30 * math.cos(a), 30 * math.sin(a), 3), (38 * math.cos(a), 38 * math.sin(a), 0.8)], [5, 3.4, 1.2],
             "Body", (0.36, 0.24, 0.10), sides=5, smooth=False, name="root")
    for side in (-1, 1):
        lump((side * 11, -27.5, 46), (3.2, 2.0, 4.2), "Body", (0.12, 0.05, 0.01))
    bones = {"Hips": ((0, 0, 30), (0, 0, 42), None), "Body": ((0, 0, 8), (0, 0, 70), "Hips"), "Stalk": ((0, -1, 88), (0, -24, 116), "Body"),
             "Seed": ((0, -31, 100), (0, -31, 84), "Stalk")}
    clips = {
        "Idle": [wave("Body", (0, 0, 0), (0, 0, 1.5)), wave("Body", (2, 2, 0), phase=1), wave("Stalk", (4, 0, 0), phase=0.5), wave("Seed", (10, 8, 0), phase=1.4)],
        "Move": [wave("Body", (0, 9, 0)), wave("Body", (4, 0, 0), (0, 0, 2.5), cycles=2), wave("Stalk", (8, 0, 0), cycles=2, phase=1), wave("Seed", (20, 0, 0), cycles=2, phase=2)],
        "Attack": [strike("Body", (-10, 0, 0), (14, 0, 0), (0, 3, 3), (0, -8, -2)), strike("Stalk", (-28, 0, 0), (42, 0, 0)), strike("Seed", (-30, 0, 0), (50, 0, 0))],
        "Cast": [hold("Stalk", (-40, 0, 0)), hold("Body", (-6, 0, 0), (0, 0, 5)), wave("Seed", (0, 26, 0), cycles=4), wave("Body", (0, 0, 0), (0, 0, 2), cycles=4)],
        "Hit": [jolt("Body", (-12, 0, 0), (0, 6, 0)), jolt("Stalk", (25, 0, 0))],
        "Defeat": [fall("Body", (0, 80, 0), (24, 0, -6)), fall("Stalk", (0, 40, 0)), fall("Seed", (0, 50, 0))],
    }
    return "LanternBulb", bones, clips, 120, None


# =====================================================================================================================
def moth(boss=False):
    fur, lead, dark = (0.86, 0.86, 0.82), (0.015, 0.015, 0.02), (0.05, 0.04, 0.05)
    glass = [(0.05, 0.16, 0.75), (0.95, 0.55, 0.06), (0.75, 0.05, 0.06), (0.10, 0.45, 0.85), (0.98, 0.80, 0.25)]
    z = 150 if boss else 105
    k = 1.7 if boss else 1.0
    lump((0, 0, z), (13 * k, 17 * k, 13 * k), "Body", fur, detail=2, rough=1.2)
    lump((0, 26 * k, z - 5), (9 * k, 24 * k, 9 * k), "Abdomen", (0.70, 0.70, 0.68) if not boss else (0.55, 0.57, 0.62), detail=2, rough=0.6)
    lump((0, -19 * k, z + 2), (8.5 * k, 8.5 * k, 8.5 * k), "Head", fur, detail=2, rough=0.6)
    if boss:
        lump((0, -8 * k, z + 5), (17 * k, 9 * k, 15 * k), "Body", (0.95, 0.95, 0.92), detail=2, rough=2.0, name="collar")
        for a in range(7):
            angle = (a - 3) * 0.32
            spike((math.sin(angle) * 7 * k, -19 * k, z + 8 * k), (math.sin(angle) * 15 * k, -21 * k, z + (20 + 6 * math.cos(angle * 2)) * k), 2.2 * k, "Head", (0.75, 0.90, 0.98))
    for side in (-1, 1):
        lump((side * 5.5 * k, -24.5 * k, z + 3), (3.6 * k, 3.2 * k, 4.2 * k), "Head", (0.85, 0.50, 0.08) if boss else dark)
        feeler = arc((side * 3 * k, -22 * k, z + 8 * k), (side * 20 * k, -48 * k, z + 20 * k), (0, 0, 8 * k), 6)
        tube(feeler, [1.2 * k, 1.1 * k, 1.0 * k, 0.9 * k, 0.8 * k, 0.6 * k, 0.3 * k], "Head", dark, sides=4, smooth=False)
        for step in range(1, 6):
            p = feeler[step]
            for way in (-1, 1):
                pane([p, p + Vector((way * 5 * k, -2 * k, 2 * k)), p + Vector((way * 4 * k, -6 * k, 3 * k))], "Head", (0.25, 0.22, 0.25), 0.5)
        for index in range(3):
            y = (-8 + index * 9) * k
            tube([(side * 8 * k, y, z - 9 * k), (side * 15 * k, y - 4 * k, z - 22 * k), (side * 11 * k, y - 8 * k, z - 30 * k)], [1.1 * k, 0.9 * k, 0.5 * k], "Body", dark,
                 sides=4, smooth=False)
        bone = "WingLeft" if side > 0 else "WingRight"

        def fan(centre, a0, a1, r0, r1, spokes, rings, lift=0.0):
            """A sector of leaded glass: a black backing plate with separate coloured panes set into it."""
            def at(angle, reach):
                a = math.radians(angle)
                return Vector((centre[0] + side * math.cos(a) * reach, centre[1] - math.sin(a) * reach, centre[2] + lift * reach))
            outline = [at(a0 + (a1 - a0) * s / (spokes * 2), r1 + 2.5 * k) for s in range(spokes * 2 + 1)] + \
                      [at(a1 - (a1 - a0) * s / (spokes * 2), max(0.5, r0 - 2.5 * k)) for s in range(spokes * 2 + 1)]
            pane(outline, bone, lead, 1.4 * k, "lead")
            for s in range(spokes):
                for ring in range(rings):
                    lo, hi = a0 + (a1 - a0) * (s + 0.09) / spokes, a0 + (a1 - a0) * (s + 0.91) / spokes
                    near, far = r0 + (r1 - r0) * (ring + 0.08) / rings, r0 + (r1 - r0) * (ring + 0.92) / rings
                    middle = (lo + hi) / 2
                    cell = [at(lo, near), at(middle, near), at(hi, near), at(hi, far), at(middle, far), at(lo, far)]
                    pane(cell, bone, glass[(s * 2 + ring * 3 + (1 if side > 0 else 0)) % len(glass)], 2.6 * k, "glass")   # thicker than the lead, so it shows on both faces

        root = (side * 9 * k, -4 * k, z + 4 * k)
        if boss:
            # Rose windows: a full wheel of panes on each side, with long banner panes trailing behind.
            hub = (side * 100 * k, -22 * k, z + 4 * k + 9 * k)
            fan(hub, 0, 360, 9 * k, 34 * k, 8, 1)
            fan(hub, 0, 360, 36 * k, 60 * k, 12, 1)
            fan(hub, 0, 360, 62 * k, 80 * k, 16, 1)
            lump((hub[0], hub[1], hub[2]), (8 * k, 8 * k, 2.4 * k), bone, (1.0, 0.95, 0.75), detail=2, name="rosecentre")
            tube([root, (side * 30 * k, -10 * k, z + 8 * k), (side * 46 * k, -16 * k, z + 12 * k)], [3.5 * k, 2.6 * k, 2 * k], bone, lead, sides=5, smooth=False)
            fan(root, -78, -18, 14 * k, 122 * k, 3, 4, lift=0.04)
        else:
            fan(root, 8, 78, 12 * k, 86 * k, 5, 3, lift=0.10)
            fan(root, -62, 2, 10 * k, 60 * k, 4, 2, lift=0.05)
    bones = {"Hips": ((0, 0, z), (0, 0, z + 12), None), "Body": ((0, 10 * k, z), (0, -14 * k, z), "Hips"), "Head": ((0, -14 * k, z + 2), (0, -28 * k, z + 2), "Body"),
             "Abdomen": ((0, 12 * k, z - 3), (0, 48 * k, z - 8), "Body"), "WingLeft": ((9 * k, -4 * k, z + 4 * k), (60 * k, -4 * k, z + 8 * k), "Body"),
             "WingRight": ((-9 * k, -4 * k, z + 4 * k), (-60 * k, -4 * k, z + 8 * k), "Body")}
    flap = 3 if boss else 4

    def wings(amount, cycles, phase=0.0):
        return [wave("WingLeft", (0, -amount, 0), cycles=cycles, phase=phase), wave("WingRight", (0, amount, 0), cycles=cycles, phase=phase)]
    clips = {
        "Idle": wings(16, flap) + [wave("Body", (2, 0, 0), (0, 0, 5), cycles=1), wave("Abdomen", (6, 0, 0), phase=1), wave("Head", (0, 0, 6), phase=2)],
        "Move": wings(24, 2) + [wave("Body", (3, 0, 0), (0, 0, 4), cycles=2), hold("Body", (10, 0, 0)), wave("Abdomen", (8, 0, 0), cycles=2)],
        # Wings sweep back, then snap flat and forward as the light is thrown.
        "Attack": [strike("WingLeft", (0, -34, 12), (0, 22, -14)), strike("WingRight", (0, 34, -12), (0, -22, 14)), strike("Body", (-12, 0, 0), (14, 0, 0), (0, 6, 6), (0, -10, -4)),
                   strike("Head", (-10, 0, 0), (12, 0, 0)), strike("Abdomen", (14, 0, 0), (-18, 0, 0))],
        "Cast": [hold("WingLeft", (0, -40, 0)), hold("WingRight", (0, 40, 0)), hold("Body", (-22, 0, 0), (0, 0, 18)), hold("Abdomen", (30, 0, 0)),
                 wave("WingLeft", (0, -5, 0), cycles=8), wave("WingRight", (0, 5, 0), cycles=8)],
        "Hit": wings(10, 1) + [jolt("Body", (-16, 0, 8), (0, 10, -6))],
        "Defeat": [fall("Hips", (0, 0, 0), (0, 0, -(z - 12 * k)), at=0.7), fall("Body", (20, 0, 60), at=0.7), fall("WingLeft", (0, 20, 0)), fall("WingRight", (0, 30, 0)),
                   fall("Abdomen", (20, 0, 0))],
    }
    return ("GlassQueen" if boss else "GlassMoth"), bones, clips, (z + 60 * k), None


# =====================================================================================================================
def biped(hip=105, knee=55, shoulder=185, elbow=140, hand=95, hx=18, sx=42, parent="Chest"):
    bones = {}
    for side, word in ((1, "Left"), (-1, "Right")):
        bones[word + "UpLeg"] = ((side * hx, 0, hip), (side * (hx + 3), -4, knee), "Hips")
        bones[word + "Leg"] = ((side * (hx + 3), -4, knee), (side * (hx + 4), 0, 4), word + "UpLeg")
        bones[word + "Arm"] = ((side * sx, 0, shoulder), (side * (sx + 12), 0, elbow), parent)
        bones[word + "ForeArm"] = ((side * (sx + 12), 0, elbow), (side * (sx + 15), -10, hand), word + "Arm")
    return bones


def biped_walk(swing=26, bend=32, arms=16):
    return [leg("LeftUpLeg", "LeftLeg", None, 0, swing, bend), leg("RightUpLeg", "RightLeg", None, PI, swing, bend), wave("LeftArm", (arms, 0, 0), phase=PI),
            wave("RightArm", (arms, 0, 0))]


def root_sentinel():
    bark, stone_grey = BARK, [(0.30, 0.31, 0.33), (0.38, 0.39, 0.40), (0.24, 0.25, 0.27)]
    lump((0, 2, 150), (40, 30, 48), "Chest", bark[0], detail=2, rough=3.0, smooth=False)
    lump((0, 4, 108), (30, 25, 22), "Hips", bark[2], detail=2, rough=2.5, smooth=False)
    for k in range(7):                       # roots wind up round the trunk
        a = k / 7 * math.tau
        tube([((30 + 6 * math.sin(t * 3)) * math.cos(a + t * 1.6), (24 + 4 * math.sin(t * 3)) * math.sin(a + t * 1.6) + 3, 96 + t * 100) for t in (0, 0.2, 0.4, 0.6, 0.8, 1.0)],
             [7, 6.5, 6, 5.5, 5, 4], "Chest", random.choice(bark), sides=6, smooth=False, rough=0.6, name="wound")
    for centre, size in (((-26, -20, 168), (15, 11, 13)), ((24, -22, 140), (13, 10, 15)), ((2, -27, 126), (12, 9, 10)), ((-30, 18, 146), (13, 11, 14)), ((30, 16, 172), (12, 10, 12))):
        lump(centre, size, "Chest", random.choice(stone_grey), detail=1, rough=1.2, smooth=False, name="riverstone")
    # The face: a hollow knot with one steady green light.
    tube([(0, -22, 181), (0, -31, 183)], [15, 13], "Head", bark[1], sides=9, smooth=False, rough=0.8, name="knot")
    lump((0, -31.5, 183), (10.5, 3, 10.5), "Head", SOCKET, smooth=False)
    lump((0, -33, 183), (4.2, 2.6, 4.2), "Head", GREEN_EYE)
    slab((0, -18, 203), (54, 12, 18), "Head", bark[2], turn=(70, 0, 0), sides=7, rough=2.2, name="brow")
    for side in (-1, 1):
        lump((side * 44, 2, 188), (20, 19, 17), "Chest", bark[1], detail=2, rough=2.6, smooth=False, name="shoulder")
        for n in range(3):
            leaf((side * (40 + n * 6), 4 - n * 5, 200), (side * (50 + n * 9), 10 - n * 8, 222 - n * 4), 9, "Chest", (0.42, 0.30, 0.08) if n % 2 else (0.30, 0.40, 0.10))
        word = "Left" if side > 0 else "Right"
        tube([(side * 46, 0, 184), (side * 54, 0, 162), (side * 57, 0, 140)], [12, 11, 9.5], word + "Arm", bark[0], sides=7, smooth=False, rough=1.0)
        tube([(side * 57, 0, 140), (side * 59, -5, 118), (side * 59, -10, 100)], [9.5, 10.5, 12], word + "ForeArm", bark[1], sides=7, smooth=False, rough=1.0)
        lump((side * 59, -12, 88), (18, 18, 19), word + "ForeArm", bark[2], detail=2, rough=3.0, smooth=False, name="club")
        slab((side * 59, -24, 122), (17, 4, 30), word + "ForeArm", bark[2], turn=(8, 0, 0), sides=6, rough=1.2, name="armplate")
        tube([(side * 18, 0, 108), (side * 21, -3, 82), (side * 21, -4, 56)], [14, 13, 11], word + "UpLeg", bark[0], sides=7, smooth=False, rough=1.0)
        tube([(side * 21, -4, 56), (side * 22, -2, 28), (side * 22, 0, 8)], [11, 10, 12], word + "Leg", bark[1], sides=7, smooth=False, rough=1.0)
        slab((side * 21, -15, 38), (19, 4, 34), word + "Leg", bark[2], turn=(-4, 0, 0), sides=6, rough=1.2, name="shinplate")
        for n in (-1, 0, 1):
            tube([(side * 22 + n * 5, -4, 8), (side * 22 + n * 13, -18 + abs(n) * 5, 4), (side * 22 + n * 19, -28 + abs(n) * 8, 1)], [5.5, 4, 1.5], word + "Leg", bark[2], sides=5,
                 smooth=False, name="toe")
    slab((0, -27, 152), (40, 6, 44), "Chest", bark[2], turn=(-4, 0, 0), sides=7, rough=1.8, name="chestplate")
    for centre in ((-12, 0, 198), (16, 6, 196), (0, 18, 192)):
        lump(centre, (9, 8, 4), "Chest", MOSS, detail=1, chip=0.8, smooth=False)
    bones = {"Hips": ((0, 0, 105), (0, 0, 120), None), "Chest": ((0, 0, 120), (0, 0, 180), "Hips"), "Head": ((0, -10, 180), (0, -30, 186), "Chest"), **biped()}
    clips = {
        "Idle": [wave("Chest", (1.5, 0, 1.5), (0, 0, 1.2)), wave("Head", (2, 0, 4), phase=1), wave("LeftArm", (2, 3, 0), phase=0.5), wave("RightArm", (2, -3, 0), phase=0.9)],
        "Move": biped_walk(22, 28, 14) + [wave("Chest", (0, 4, 0)), wave("Chest", (2, 0, 0), (0, 0, 2.5), cycles=2), wave("Hips", (0, 0, 0), (0, 0, 2), cycles=2)],
        # Both clubs go up and back, then come down together.
        "Attack": [strike("RightArm", (-150, 0, 0), (-38, 0, 0)), strike("RightForeArm", (-20, 0, 0), (-30, 0, 0)), strike("LeftArm", (-120, 0, 0), (-30, 0, 0)),
                   strike("Chest", (-14, 0, 0), (24, 0, 0), (0, 4, 0), (0, -12, -6)), strike("Head", (-8, 0, 0), (10, 0, 0))],
        # Ground slam for the stun: arms wide, then both fists driven into the floor.
        "Cast": [keys("RightArm", (0, (0, 0, 0)), (0.35, (-160, -30, 0)), (0.55, (-25, 0, 0)), (0.8, (-25, 0, 0)), (1, (0, 0, 0))),
                 keys("LeftArm", (0, (0, 0, 0)), (0.35, (-160, 30, 0)), (0.55, (-25, 0, 0)), (0.8, (-25, 0, 0)), (1, (0, 0, 0))),
                 keys("Chest", (0, (0, 0, 0)), (0.35, (-18, 0, 0)), (0.55, (40, 0, 0), (0, -10, -14)), (0.8, (40, 0, 0), (0, -10, -14)), (1, (0, 0, 0))),
                 keys("LeftUpLeg", (0, (0, 0, 0)), (0.55, (-30, 0, 0)), (0.8, (-30, 0, 0)), (1, (0, 0, 0))), keys("LeftLeg", (0, (0, 0, 0)), (0.55, (50, 0, 0)), (0.8, (50, 0, 0)), (1, (0, 0, 0))),
                 keys("RightUpLeg", (0, (0, 0, 0)), (0.55, (-30, 0, 0)), (0.8, (-30, 0, 0)), (1, (0, 0, 0))), keys("RightLeg", (0, (0, 0, 0)), (0.55, (50, 0, 0)), (0.8, (50, 0, 0)), (1, (0, 0, 0))),
                 keys("Hips", (0, (0, 0, 0)), (0.55, (0, 0, 0), (0, 0, -14)), (0.8, (0, 0, 0), (0, 0, -14)), (1, (0, 0, 0)))],
        "Hit": [jolt("Chest", (-10, 0, 6), (0, 6, 0)), jolt("Head", (-10, 0, 0)), jolt("LeftArm", (-14, 0, 0))],
        "Defeat": [fall("Hips", (0, 0, 0), (0, 0, -72)), fall("LeftUpLeg", (-80, 0, 0)), fall("RightUpLeg", (-70, 0, 0)), fall("LeftLeg", (120, 0, 0)), fall("RightLeg", (115, 0, 0)),
                   keys("Chest", (0, (0, 0, 0)), (0.5, (10, 0, 0)), (1, (62, 0, 8))), fall("Head", (25, 0, 0)), fall("LeftArm", (-20, 20, 0)), fall("RightArm", (-25, -20, 0))],
    }
    return "RootSentinel", bones, clips, 240, None


# =====================================================================================================================
def bramble_hound():
    vine, dark, thorn, berry = (0.10, 0.22, 0.07), (0.07, 0.14, 0.05), (0.42, 0.14, 0.06), (0.95, 0.10, 0.08)
    for k in range(8):                       # the body is a rope of vines wound along the spine
        a = k / 8 * math.tau
        tube([(13 * math.cos(a + t * 2.4) * (1.15 - 0.45 * abs(t - 0.35)), -42 + t * 84, 66 + 14 * math.sin(a + t * 2.4) * (1.1 - 0.4 * abs(t - 0.35)) - 6 * t)
              for t in (0, 0.14, 0.28, 0.42, 0.57, 0.71, 0.85, 1.0)], [5.5, 6.2, 6.5, 6.2, 5.6, 5, 4.6, 4], "Chest" if k % 2 else "Body",
             vine if k % 3 else dark, sides=6, smooth=False, name="vine")
    lump((0, -20, 68), (15, 26, 17), "Chest", dark, detail=2, rough=1.4, smooth=False)
    lump((0, 22, 62), (12, 24, 13), "Body", dark, detail=2, rough=1.4, smooth=False)
    for n in range(9):                       # hackles
        y = -44 + n * 10
        spike((r(-2, 2), y, 82 - n * 1.2), (r(-4, 4), y + 7, 97 - n * 1.6 + r(-2, 3)), 2.6, "Chest" if n < 5 else "Body", thorn)
    tube([(0, -40, 72), (0, -52, 80), (0, -60, 84)], [9, 8, 7.5], "Neck", vine, sides=7, smooth=False, rough=0.6)
    slab((0, -72, 85), (17, 22, 15), "Head", vine, turn=(12, 0, 0), sides=6, taper=0.5, rough=0.8, bevel=0.8, name="skull")
    slab((0, -73, 77), (12, 20, 5), "Jaw", dark, turn=(10, 0, 0), sides=5, taper=0.5, rough=0.4, bevel=0.5, name="jaw")
    for side in (-1, 1):
        lump((side * 6.2, -70, 89), (2.3, 2.3, 2.3), "Head", berry)
        spike((side * 6, -62, 92), (side * 10, -56, 104), 2.6, "Head", vine, name="ear")
        for n in range(4):
            y = -66 - n * 5
            spike((side * (5.5 - n), y, 81), (side * (5.5 - n), y - 1, 75.5), 1.1, "Head", (0.85, 0.80, 0.65), sides=4, name="fang")
            spike((side * (4.5 - n * 0.8), y, 79), (side * (4.5 - n * 0.8), y - 1, 83.5), 1.0, "Jaw", (0.85, 0.80, 0.65), sides=4, name="fang")
    tail = arc((0, 42, 64), (0, 88, 82), (0, 0, -10), 7)
    tube(tail, [4, 3.4, 2.9, 2.4, 2, 1.6, 1.3, 1.1], "Tail", vine, sides=5, smooth=False)
    lump((0, 90, 83), (5, 5, 5), "Tail", thorn, detail=1, smooth=False)
    for n in range(10):
        a, b = r(0, math.tau), r(-1, 1)
        spike((0, 90, 83), (8.5 * math.cos(a) * math.cos(b), 90 + 8.5 * math.sin(b), 83 + 8.5 * math.sin(a) * math.cos(b)), 1.2, "Tail", thorn, sides=4)
    bones = {"Hips": ((0, 0, 66), (0, 0, 78), None), "Body": ((0, 8, 66), (0, 42, 62), "Hips"), "Chest": ((0, -4, 68), (0, -40, 72), "Body"),
             "Neck": ((0, -40, 72), (0, -60, 84), "Chest"), "Head": ((0, -60, 84), (0, -84, 84), "Neck"), "Jaw": ((0, -62, 79), (0, -84, 76), "Head"),
             "Tail": ((0, 42, 64), (0, 88, 82), "Body"), **quad(fy=-30, ry=32, fx=11, rx=10, top=58, knee=32, ankle=10)}
    for side in (-1, 1):
        for label, y, x in (("Front", -30, 11), ("Rear", 32, 10)):
            p = label + ("Left" if side > 0 else "Right")
            back = 6 if label == "Rear" else 0
            tube([(side * x, y, 60), (side * (x + 1), y + back, 46), (side * x, y, 32)], [6, 5, 4], p + "UpLeg", vine, sides=6, smooth=False)
            tube([(side * x, y, 32), (side * x, y + 3 + back, 20), (side * x, y, 10)], [4, 3.2, 2.6], p + "Leg", dark, sides=6, smooth=False)
            lump((side * x, y - 4, 5), (5, 8, 5), p + "Foot", dark, detail=1, smooth=False)
            for n in (-1, 0, 1):
                spike((side * x + n * 3, y - 9, 4), (side * x + n * 4, y - 15, 1), 1.2, p + "Foot", (0.85, 0.80, 0.65), sides=4, name="claw")
            spike((side * (x + 3), y + 2, 44), (side * (x + 9), y + 6, 50), 1.8, p + "UpLeg", thorn)
    clips = {
        "Idle": [wave("Chest", (2, 0, 0), (0, 0, 1.5), cycles=2), wave("Neck", (5, 0, 6), phase=1), wave("Head", (3, 0, 8), phase=2), wave("Tail", (8, 0, 22), cycles=3),
                 wave("Jaw", (6, 0, 0), cycles=2, phase=1)],
        "Move": quad_walk(36, 42) + [wave("Body", (4, 0, 0), (0, 0, 3), cycles=2), wave("Chest", (-5, 0, 0), cycles=2), wave("Tail", (10, 0, 14), cycles=2), wave("Head", (4, 0, 0), cycles=2)],
        # A lunge with the jaws opening wide and snapping shut on the strike.
        "Attack": [strike("Body", (-10, 0, 0), (8, 0, 0), (0, 12, -4), (0, -30, 4)), strike("Neck", (-16, 0, 0), (14, 0, 0)), strike("Head", (-18, 0, 0), (10, 0, 0)),
                   keys("Jaw", (0, (0, 0, 0)), (0.32, (38, 0, 0)), (0.5, (2, 0, 0)), (1, (0, 0, 0))), strike("FrontLeftUpLeg", (20, 0, 0), (-40, 0, 0)),
                   strike("FrontRightUpLeg", (20, 0, 0), (-40, 0, 0)), strike("RearLeftUpLeg", (-20, 0, 0), (34, 0, 0)), strike("RearRightUpLeg", (-20, 0, 0), (34, 0, 0))],
        "Cast": [hold("Neck", (-34, 0, 0)), hold("Head", (-24, 0, 0)), hold("Jaw", (34, 0, 0)), hold("Body", (-8, 0, 0), (0, 4, -4)), wave("Tail", (0, 0, 20), cycles=4)],
        "Hit": [jolt("Body", (-8, 0, 10), (0, 9, 2)), jolt("Head", (-14, 0, 14)), jolt("Jaw", (20, 0, 0))],
        "Defeat": quad_fold() + [keys("Body", (0, (0, 0, 0)), (0.3, (0, 0, 0), (0, 0, -14)), (0.75, (0, 80, 0), (8, 0, -48)), (1, (0, 80, 0), (8, 0, -48))), fall("Neck", (10, 0, 16)),
                                 fall("Jaw", (24, 0, 0)), fall("Tail", (0, 0, 30))],
    }
    return "BrambleHound", bones, clips, 110, None


# =====================================================================================================================
def spore_cap():
    cap, spot, stalk, gill = (0.30, 0.13, 0.36), (0.86, 0.80, 0.72), (0.82, 0.76, 0.62), (0.62, 0.52, 0.44)
    tube([(0, 0, 4), (0, 0, 14), (0, 0, 32), (0, 0, 50), (0, 0, 58)], [17, 15, 13, 12, 14], "Body", stalk, sides=12, rough=0.5)
    lump((0, 0, 60), (41, 41, 26), "Cap", cap, detail=3, squash=0.12)
    tube([(0, 0, 55), (0, 0, 59)], [20, 39], "Cap", gill, sides=20, smooth=False, name="gills")
    for a, reach, size in ((0.3, 22, 6), (1.4, 28, 5), (2.3, 16, 7), (3.4, 26, 5.5), (4.4, 20, 6.5), (5.4, 30, 4.5), (0.9, 8, 5), (3.9, 6, 4)):
        height = 60 + 26 * math.sqrt(max(0.0, 1 - (reach / 41) ** 2))
        lump((reach * math.cos(a), reach * math.sin(a), height - 0.5), (size, size, 1.6), "Cap", spot, detail=1)
    for side in (-1, 1):
        lump((side * 6, -12.6, 46), (2.1, 1.4, 2.8), "Body", (0.03, 0.02, 0.03))
        word = "Left" if side > 0 else "Right"
        tube([(side * 12, -2, 38), (side * 19, -5, 34), (side * 22, -8, 28)], [4, 3.6, 2.6], word + "Arm", stalk, sides=7)
    for k in range(14):
        a = k / 14 * math.tau
        tube([(14 * math.cos(a), 14 * math.sin(a), 8), (22 * math.cos(a), 22 * math.sin(a), 2), (27 * math.cos(a + 0.2), 27 * math.sin(a + 0.2), 0.6)], [2.2, 1.5, 0.5], "Body",
             (0.92, 0.90, 0.84), sides=4, smooth=False, name="thread")
    bones = {"Hips": ((0, 0, 30), (0, 0, 40), None), "Body": ((0, 0, 4), (0, 0, 54), "Hips"), "Cap": ((0, 0, 54), (0, 0, 86), "Body"),
             "LeftArm": ((12, -2, 38), (22, -8, 28), "Body"), "RightArm": ((-12, -2, 38), (-22, -8, 28), "Body")}
    clips = {
        "Idle": [wave("Body", (1.5, 1.5, 0), (0, 0, 1)), wave("Cap", (3, 3, 0), phase=1.2), wave("LeftArm", (0, 8, 0), phase=0.5), wave("RightArm", (0, -8, 0), phase=1.1)],
        "Move": [wave("Body", (0, 10, 0)), wave("Body", (3, 0, 0), (0, 0, 2.5), cycles=2), wave("Cap", (0, -6, 0), phase=0.6), wave("Cap", (5, 0, 0), cycles=2, phase=1),
                 wave("LeftArm", (20, 0, 0)), wave("RightArm", (-20, 0, 0))],
        "Attack": [strike("Body", (-14, 0, 0), (20, 0, 0), (0, 3, 2), (0, -8, -2)), strike("Cap", (-16, 0, 0), (26, 0, 0)), strike("LeftArm", (0, 30, 0), (-40, 0, 0)),
                   strike("RightArm", (0, -30, 0), (-40, 0, 0))],
        # Arms up and the cap pumps as the spores are thrown out.
        "Cast": [hold("LeftArm", (-20, -70, 0)), hold("RightArm", (-20, 70, 0)), hold("Body", (-6, 0, 0)), wave("Cap", (0, 0, 0), (0, 0, 5), cycles=5), wave("Cap", (6, 0, 0), cycles=5, phase=1)],
        "Hit": [jolt("Body", (-12, 0, 0), (0, 5, 0)), jolt("Cap", (-16, 0, 8))],
        "Defeat": [fall("Body", (0, 84, 0), (14, 0, -4)), fall("Cap", (0, 16, 0)), fall("LeftArm", (0, 30, 0))],
    }
    return "SporeCap", bones, clips, 105, None


# =====================================================================================================================
def gargoyle():
    algae = (0.18, 0.30, 0.12)
    block((0, 4, 96), (56, 40, 40), "Hips", stone(LIME))
    block((0, -4, 136), (72, 46, 46), "Chest", stone(LIME), turn=(22, 0, 0))
    slab((0, -24, 138), (46, 8, 36), "Chest", LIME[1], turn=(20, 0, 0), sides=6, name="breast")
    block((0, -30, 164), (30, 30, 26), "Neck", stone(LIME), turn=(38, 0, 0))
    block((0, -50, 178), (34, 38, 30), "Head", LIME[1], turn=(20, 0, 0))
    slab((0, -72, 181), (24, 22, 14), "Head", LIME[0], turn=(8, 0, 0), sides=6, taper=0.75, name="snout")
    slab((0, -70, 166), (22, 24, 9), "Jaw", LIME[2], turn=(-14, 0, 0), sides=6, taper=0.75, name="jaw")
    lump((0, -62, 173), (8, 14, 4), "Head", SOCKET, smooth=False, name="spout")
    slab((0, -48, 197), (38, 6, 12), "Head", LIME[2], turn=(70, 0, 0), sides=6, name="brow")
    for side in (-1, 1):
        lump((side * 12, -68, 186), (4, 3, 3.2), "Head", SOCKET, smooth=False)
        lump((side * 12.5, -69.5, 186), (1.8, 1.4, 1.6), "Head", (0.55, 0.85, 1.0))
        tube([(side * 12, -40, 196), (side * 22, -30, 212), (side * 24, -22, 216)], [6, 4.5, 2.2], "Head", LIME[2], sides=6, smooth=False, rough=0.4, name="horn")
        slab((side * 17, -54, 184), (5, 12, 16), "Head", LIME[0], turn=(0, 0, side * 28), sides=5, name="ear")
        word = "Left" if side > 0 else "Right"
        # Wings folded round the back like a cloak: three overlapping stone panels on each side.
        for n in range(3):
            slab((side * (24 + n * 13), 30 - n * 5, 150 - n * 14), (40, 6, 92 - n * 10), word + "Wing", stone(LIME), turn=(-10, 0, side * (26 + n * 22)), sides=5, taper=0.8,
                 rough=1.2, name="wing")
        tube([(side * 20, 24, 196), (side * 34, 34, 210), (side * 30, 40, 226)], [6, 5, 2], word + "Wing", LIME[2], sides=5, smooth=False, name="wingclaw")
        block((side * 46, -4, 138), (20, 22, 40), word + "Arm", stone(LIME), turn=(0, 0, 0))
        block((side * 50, -16, 104), (17, 19, 38), word + "ForeArm", stone(LIME), turn=(-22, 0, 0))
        for n in (-1, 0, 1):
            spike((side * 50 + n * 5, -26, 86), (side * 50 + n * 7, -34, 72), 3, word + "ForeArm", LIME[2], sides=4, name="claw")
        block((side * 20, -8, 66), (24, 34, 36), word + "UpLeg", stone(LIME), turn=(-28, 0, 0))
        block((side * 21, -8, 30), (19, 22, 40), word + "Leg", stone(LIME), turn=(12, 0, 0))
        slab((side * 21, -18, 7), (22, 30, 13), word + "Leg", LIME[2], sides=5, taper=0.8, name="foot")
    for centre, size in (((-14, -26, 150), (12, 3, 26)), ((20, 22, 120), (10, 4, 30)), ((0, -34, 190), (8, 6, 3)), ((30, -6, 160), (5, 9, 14))):
        lump(centre, size, "Chest" if centre[2] < 180 else "Head", algae, detail=1, chip=0.5, smooth=False, name="algae")
    for n in range(7):                       # a broken chunk of wall ledge still clings to its feet
        a = n / 7 * math.tau
        block((34 * math.cos(a), 6 + 28 * math.sin(a), r(4, 9)), (r(14, 24), r(12, 20), r(8, 16)), "Hips" if n > 20 else "Rubble", stone(LIME), turn=(r(-20, 20), r(-20, 20), r(0, 90)))
    bones = {"Hips": ((0, 0, 92), (0, 0, 108), None), "Rubble": ((0, 20, 2), (0, 40, 2), "Hips"), "Chest": ((0, 2, 112), (0, -14, 156), "Hips"),
             "Neck": ((0, -22, 156), (0, -40, 172), "Chest"), "Head": ((0, -40, 172), (0, -76, 180), "Neck"), "Jaw": ((0, -52, 168), (0, -80, 162), "Head"),
             "LeftWing": ((16, 22, 176), (40, 34, 120), "Chest"), "RightWing": ((-16, 22, 176), (-40, 34, 120), "Chest"),
             **biped(hip=84, knee=48, shoulder=158, elbow=120, hand=88, hx=20, sx=40)}
    clips = {
        "Idle": [wave("Chest", (1.5, 0, 1), (0, 0, 0.8)), wave("Neck", (3, 0, 5), phase=1), wave("Jaw", (3, 0, 0), cycles=2), wave("LeftWing", (0, 3, 2), phase=0.4),
                 wave("RightWing", (0, -3, -2), phase=0.4)],
        "Move": biped_walk(20, 24, 12) + [wave("Chest", (0, 5, 0)), wave("Chest", (2, 0, 0), (0, 0, 2), cycles=2), wave("Rubble", (0, 0, 6), (0, 3, 0)), wave("LeftWing", (0, 0, 5)),
                                         wave("RightWing", (0, 0, 5))],
        # Rear back, jaw dropping, then thrust the head forward and spit.
        "Attack": [strike("Chest", (-16, 0, 0), (16, 0, 0), (0, 5, 0), (0, -8, -3)), strike("Neck", (-20, 0, 0), (22, 0, 0)), strike("Head", (-12, 0, 0), (8, 0, 0)),
                   keys("Jaw", (0, (0, 0, 0)), (0.32, (8, 0, 0)), (0.5, (38, 0, 0)), (0.7, (30, 0, 0)), (1, (0, 0, 0))), strike("LeftWing", (0, 0, 0), (0, -14, 12)),
                   strike("RightWing", (0, 0, 0), (0, 14, -12))],
        # The guard: wings swing open into a wall, arms braced.
        "Cast": [hold("LeftWing", (0, -8, 64)), hold("RightWing", (0, 8, -64)), hold("LeftArm", (-30, -40, 0)), hold("RightArm", (-30, 40, 0)), hold("Chest", (8, 0, 0), (0, 0, -6)),
                 hold("Head", (10, 0, 0))],
        "Hit": [jolt("Chest", (-10, 0, 5), (0, 5, 0)), jolt("Neck", (-12, 0, 0)), jolt("Jaw", (16, 0, 0))],
        "Defeat": [fall("Hips", (0, 0, 0), (0, 0, -52)), fall("LeftUpLeg", (-60, 0, 0)), fall("RightUpLeg", (-60, 0, 0)), fall("LeftLeg", (95, 0, 0)), fall("RightLeg", (95, 0, 0)),
                   fall("Chest", (48, 0, 6)), fall("Neck", (20, 0, 0)), fall("Jaw", (26, 0, 0)), fall("LeftWing", (0, 0, 40)), fall("RightWing", (0, 0, -40)), fall("LeftArm", (-30, 0, 0)),
                   fall("RightArm", (-30, 0, 0))],
    }
    return "GutterGargoyle", bones, clips, 220, None


# =====================================================================================================================
def toad(boss=False):
    skin, dark, belly, sac = ((0.07, 0.11, 0.06), (0.04, 0.07, 0.04), (0.55, 0.55, 0.42), (0.35, 0.60, 0.25)) if boss else \
                             ((0.20, 0.26, 0.08), (0.13, 0.18, 0.06), (0.70, 0.60, 0.16), (0.78, 0.68, 0.20))
    lump((0, 8, 40), (58, 58, 34), "Body", skin, detail=3, rough=1.6)
    lump((0, 4, 27), (52, 52, 24), "Body", belly, detail=3)
    lump((0, -38, 46), (40, 28, 24), "Head", skin, detail=3, rough=1.0)
    lump((0, -46, 32), (36, 22, 12), "Jaw", belly, detail=2)
    lump((0, -50, 25), (26, 18, 17), "Throat", sac, detail=3)
    tube([(-30, -58, 40), (0, -66, 38), (30, -58, 40)], [1.4, 1.6, 1.4], "Head", dark, sides=4, smooth=False, name="mouthline")
    for side in (-1, 1):
        lump((side * 20, -40, 68), (11, 11, 11), "Head", skin, detail=2, rough=0.5)
        lump((side * 22, -46, 70), (8, 6.5, 8), "Head", (0.85, 0.83, 0.62), detail=2)
        slab((side * 23.5, -51.5, 70), (9, 1.2, 2.2), "Head", SOCKET, sides=6, chip=0, bevel=0, rough=0, name="pupil")
        lump((side * 9, -62, 50), (1.8, 1.4, 1.4), "Head", SOCKET)
        word = "Left" if side > 0 else "Right"
        tube([(side * 40, -24, 34), (side * 54, -34, 22), (side * 52, -40, 8)], [12, 10, 8], "Front" + word + "UpLeg", skin, sides=8, rough=0.6)
        lump((side * 54, -48, 4), (13, 15, 4.5), "Front" + word + "Leg", dark, detail=2, name="hand")
        for n in (-1, 0, 1):
            tube([(side * 54 + n * 6, -54, 3), (side * 54 + n * 12, -68, 2)], [3, 2], "Front" + word + "Leg", dark, sides=5, name="finger")
            lump((side * 54 + n * 12.5, -69, 2.4), (3.2, 3.2, 2.2), "Front" + word + "Leg", belly, detail=1)
        tube([(side * 44, 30, 32), (side * 64, 12, 30), (side * 66, -6, 16)], [15, 13, 10], "Rear" + word + "UpLeg", skin, sides=8, rough=0.8)
        tube([(side * 66, -6, 16), (side * 62, 22, 8), (side * 60, 38, 5)], [9, 7.5, 6], "Rear" + word + "Leg", skin, sides=7, rough=0.5)
        lump((side * 62, 48, 3), (15, 18, 3.5), "Rear" + word + "Leg", dark, detail=2, name="foot")
    for n in range(26 if boss else 16):       # warts
        a, t = r(0, math.tau), r(0.25, 1.1)
        lump((54 * math.sin(t) * math.cos(a), 8 + 54 * math.sin(t) * math.sin(a), 40 + 32 * math.cos(t)), (r(3, 6), r(3, 6), r(2, 3.5)), "Body", dark, detail=1)
    pad = [(22 + 13 * math.cos(a), 26 + 13 * math.sin(a), 73.5 - 0.25 * (13 * math.cos(a))) for a in [k / 10 * math.tau for k in range(1, 10)]] + [(22, 26, 73.5)]
    pane(pad, "Body", (0.20, 0.48, 0.16), 1.0, "lilypad")
    for x, y, lean in ((-22, 24, -6), (-28, 16, 4), (-16, 32, 10)):
        tube([(x, y, 68), (x + lean * 0.5, y, 92), (x + lean, y + 2, 112)], [1.4, 1.2, 0.6], "Body", (0.34, 0.46, 0.16), sides=4, smooth=False, name="reed")
        tube([(x + lean * 0.8, y + 1, 100), (x + lean * 0.95, y + 2, 110)], 2.6, "Body", (0.22, 0.12, 0.05), sides=6, name="cattail")
    for centre in ((-6, 30, 74), (14, 0, 73), (-30, -4, 68)):
        lump(centre, (12, 10, 2.5), "Body", (0.16, 0.11, 0.06), detail=1, chip=0.8, smooth=False, name="mud")
    if boss:
        # A whole patch of bog rides on her back: a rotten jetty post, more reeds and pads, a drowned helmet. Many small eyes.
        tube([(10, 34, 66), (12, 36, 104), (11, 37, 128)], [6.5, 6, 5.5], "Body", (0.13, 0.09, 0.05), sides=7, smooth=False, rough=0.7, name="post")
        tube([(11, 37, 112), (30, 40, 116)], 2.2, "Body", (0.13, 0.09, 0.05), sides=5, smooth=False)
        lump((-34, 30, 66), (11, 12, 9), "Body", (0.30, 0.16, 0.08), detail=2, squash=0.2, name="helmet")
        tube([(-34, 19, 66), (-34, 14, 60)], [2, 1], "Body", (0.30, 0.16, 0.08), sides=4, smooth=False)
        for x, y in ((34, 4), (-4, 44), (30, 40), (-40, 8), (0, 16)):
            tube([(x, y, 66), (x + r(-5, 5), y, 96 + r(0, 18))], [1.3, 0.5], "Body", (0.34, 0.46, 0.16), sides=4, smooth=False)
        for n in range(16):
            a = -PI / 2 + (n - 7.5) * 0.17
            reach = 34 + (n % 3) * 3
            lump((reach * math.cos(a), -38 + 26 * math.sin(a) + 2, 56 + (n % 4) * 3.2), (2.6, 2.2, 2.6), "Head", (0.85, 0.90, 0.60), detail=1)
        for side in (-1, 1):
            tube([(side * 30, -60, 40), (side * 32, -62, 22), (side * 31, -60, 4)], [2.2, 2.6, 3.4], "Head", (0.45, 0.60, 0.62), sides=6, name="drool")
    bones = {"Hips": ((0, 0, 36), (0, 0, 50), None), "Body": ((0, 30, 38), (0, -10, 40), "Hips"), "Head": ((0, -14, 46), (0, -62, 46), "Body"),
             "Jaw": ((0, -26, 34), (0, -64, 30), "Head"), "Throat": ((0, -40, 26), (0, -64, 20), "Jaw")}
    for side, word in ((1, "Left"), (-1, "Right")):
        bones["Front" + word + "UpLeg"] = ((side * 40, -24, 34), (side * 52, -40, 8), "Body")
        bones["Front" + word + "Leg"] = ((side * 52, -40, 8), (side * 54, -62, 2), "Front" + word + "UpLeg")
        bones["Rear" + word + "UpLeg"] = ((side * 44, 30, 32), (side * 66, -6, 16), "Body")
        bones["Rear" + word + "Leg"] = ((side * 66, -6, 16), (side * 60, 44, 4), "Rear" + word + "UpLeg")
    clips = {
        "Idle": [wave("Body", (1.5, 0, 0), (0, 0, 1.5)), wave("Throat", (0, 0, 0), (0, -5, -3), cycles=3), wave("Head", (2, 0, 3), phase=1), wave("Jaw", (2, 0, 0), cycles=3)],
        # A hop: crouch, spring up and forward, land.
        "Move": [keys("Body", (0, (0, 0, 0)), (0.2, (6, 0, 0), (0, 0, -6)), (0.5, (-14, 0, 0), (0, 0, 22)), (0.8, (8, 0, 0), (0, 0, -3)), (1, (0, 0, 0))),
                 keys("RearLeftUpLeg", (0, (0, 0, 0)), (0.2, (-10, 0, 0)), (0.5, (50, 0, 0)), (0.8, (-6, 0, 0)), (1, (0, 0, 0))),
                 keys("RearRightUpLeg", (0, (0, 0, 0)), (0.2, (-10, 0, 0)), (0.5, (50, 0, 0)), (0.8, (-6, 0, 0)), (1, (0, 0, 0))),
                 keys("RearLeftLeg", (0, (0, 0, 0)), (0.5, (-60, 0, 0)), (0.8, (0, 0, 0)), (1, (0, 0, 0))), keys("RearRightLeg", (0, (0, 0, 0)), (0.5, (-60, 0, 0)), (0.8, (0, 0, 0)), (1, (0, 0, 0))),
                 keys("FrontLeftUpLeg", (0, (0, 0, 0)), (0.5, (-34, 0, 0)), (0.8, (10, 0, 0)), (1, (0, 0, 0))), keys("FrontRightUpLeg", (0, (0, 0, 0)), (0.5, (-34, 0, 0)), (0.8, (10, 0, 0)), (1, (0, 0, 0)))],
        # The throat swells, the head rears, and the mouth snaps open to spit.
        "Attack": [keys("Throat", (0, (0, 0, 0)), (0.36, (0, 0, 0), (0, -12, -9)), (0.5, (0, 0, 0), (0, 4, 3)), (1, (0, 0, 0))), strike("Head", (-20, 0, 0), (10, 0, 0)),
                   keys("Jaw", (0, (0, 0, 0)), (0.4, (0, 0, 0)), (0.5, (30, 0, 0)), (0.7, (24, 0, 0)), (1, (0, 0, 0))), strike("Body", (-8, 0, 0), (6, 0, 0), (0, 5, 3), (0, -9, -2))],
        "Cast": [keys("Throat", (0, (0, 0, 0)), (0.5, (0, 0, 0), (0, -18, -14)), (0.62, (0, 0, 0), (0, 5, 4)), (1, (0, 0, 0))),
                 keys("Body", (0, (0, 0, 0)), (0.5, (-16, 0, 0), (0, 6, 8)), (0.62, (10, 0, 0), (0, -12, -3)), (1, (0, 0, 0))),
                 keys("Jaw", (0, (0, 0, 0)), (0.5, (4, 0, 0)), (0.62, (42, 0, 0)), (0.85, (36, 0, 0)), (1, (0, 0, 0))), keys("Head", (0, (0, 0, 0)), (0.5, (-22, 0, 0)), (0.62, (6, 0, 0)), (1, (0, 0, 0)))],
        "Hit": [jolt("Body", (-8, 0, 6), (0, 8, 2)), jolt("Head", (-10, 0, 0)), jolt("Jaw", (14, 0, 0))],
        "Defeat": [keys("Body", (0, (0, 0, 0)), (0.3, (0, 0, 0), (0, 0, 10)), (0.75, (0, 150, 0), (0, 0, 16)), (1, (0, 172, 0), (0, 0, 8))), fall("Jaw", (26, 0, 0)),
                   fall("FrontLeftUpLeg", (-30, 0, 0)), fall("FrontRightUpLeg", (-30, 0, 0)), fall("RearLeftUpLeg", (30, 0, 0)), fall("RearRightUpLeg", (30, 0, 0))],
    }
    return ("MireMother" if boss else "BogToad"), bones, clips, 120, {"Move": 24}


# =====================================================================================================================
def bellkeeper():
    robe, robe_dark, bronze, green, wood = (0.22, 0.22, 0.24), (0.13, 0.13, 0.15), BRONZE, (0.18, 0.38, 0.28), (0.10, 0.07, 0.04)
    hem = []
    for k in range(18):                       # a ragged hem: strips of different lengths
        a = k / 18 * math.tau
        drop = r(2, 30)
        hem.append(drop)
        pane([(54 * math.cos(a - 0.2), 54 * math.sin(a - 0.2), 34), (56 * math.cos(a + 0.2), 56 * math.sin(a + 0.2), 34), (58 * math.cos(a + 0.12), 58 * math.sin(a + 0.12), drop),
              (57 * math.cos(a - 0.1), 57 * math.sin(a - 0.1), drop + r(0, 8))], "Robe", robe_dark if k % 2 else robe, 1.2, "tatter")
    tube([(0, 0, 30), (0, 0, 80), (0, 0, 130), (0, 0, 170)], [56, 46, 37, 31], "Robe", robe, sides=18, rough=1.2, name="skirt")
    tube([(0, 0, 168), (0, -2, 200), (0, -4, 232), (0, -4, 246)], [31, 33, 38, 26], "Chest", robe, sides=16, rough=1.0, name="torso")
    # The chest opens on darkness, and the bell hangs inside it.
    slab((0, -30, 196), (40, 6, 60), "Chest", SOCKET, turn=(-4, 0, 0), sides=10, chip=0, rough=0, bevel=0.5, name="opening")
    for side in (-1, 1):
        tube([(side * 22, -32, 226), (side * 25, -34, 196), (side * 21, -33, 166)], [3.5, 3, 3.5], "Chest", robe_dark, sides=5, smooth=False, name="openingedge")
    tube([(0, -32, 228), (0, -34, 216)], 2.0, "Bell", (0.20, 0.14, 0.07), sides=5, smooth=False, name="rope")
    tube([(0, -34, 217), (0, -34, 212), (0, -34, 200), (0, -34, 186), (0, -34, 176), (0, -34, 171)], [3, 9, 14, 16, 20, 23], "Bell", bronze, sides=14, name="bell")
    tube([(0, -34, 173), (0, -34, 171)], [23, 21], "Bell", green, sides=14, smooth=False, name="bellrim")
    lump((0, -34, 172), (4.5, 4.5, 4.5), "Clapper", (0.25, 0.17, 0.08), detail=1)
    slab((9, -52, 188), (1.6, 1.0, 26), "Bell", SOCKET, turn=(0, 14, 0), sides=4, chip=0, bevel=0, rough=0, name="crack")
    # The hood: empty and black.
    lump((0, -4, 268), (27, 30, 31), "Head", robe, detail=3, rough=0.8)
    tube([(0, -22, 266), (0, -31, 264)], [21, 24], "Head", robe_dark, sides=14, smooth=False, name="hoodrim")
    lump((0, -27, 265), (19, 8, 21), "Head", SOCKET, detail=2, smooth=False, name="void")
    tube([(0, 16, 262), (0, 30, 236), (0, 30, 210)], [16, 10, 3], "Head", robe, sides=9, name="hoodtail")
    lump((0, 0, 242), (40, 26, 12), "Chest", robe_dark, detail=2, rough=0.8, name="mantle")
    for side in (-1, 1):
        word = "Left" if side > 0 else "Right"
        tube([(side * 34, -2, 238), (side * 44, -4, 214), (side * 50, -8, 190)], [12, 13, 15], word + "Arm", robe, sides=10, rough=0.7, name="sleeve")
        tube([(side * 50, -8, 190), (side * 52, -22, 170), (side * 50, -34, 156)], [15, 17, 20], word + "ForeArm", robe, sides=10, rough=0.7, name="cuff")
        lump((side * 50, -35, 157), (16, 5, 16), word + "ForeArm", SOCKET, detail=1, smooth=False, name="sleevevoid")
        for n in range(4):                    # pale root hands
            a = (n - 1.5) * 0.3
            tube([(side * 50, -36, 158), (side * 50 + math.sin(a) * 9, -46, 154 - abs(a) * 4), (side * 50 + math.sin(a) * 12, -54, 147 - abs(a) * 6)], [2.6, 2.0, 0.8],
                 word + "ForeArm", (0.72, 0.68, 0.58), sides=5, smooth=False, name="rootfinger")
    # The striker staff in the right hand.
    tube([(-50, -48, 6), (-50, -48, 150), (-50, -48, 292)], [3.0, 2.8, 2.6], "Staff", wood, sides=7, smooth=False, rough=0.3, name="staff")
    tube([(-50, -48, 292), (-50, -48, 298), (-50, -48, 322), (-50, -48, 328)], [3.2, 11, 12, 6], "Staff", bronze, sides=10, name="striker")
    tube([(-50, -48, 300), (-50, -48, 304)], [12.5, 12.5], "Staff", green, sides=10, smooth=False)
    for k in range(7):                        # small bells and dry pods on the hem
        a = k / 7 * math.tau + 0.4
        x, y = 55 * math.cos(a), 55 * math.sin(a)
        tube([(x, y, 30), (x, y, 22)], 0.5, "Robe", SOCKET, sides=4, smooth=False)
        lump((x, y, 18), (4, 4, 5), "Robe", bronze if k % 2 else (0.30, 0.20, 0.10), detail=1, squash=0.5)
    for n in range(12):                       # dead leaves always drift round his feet
        a = r(0, math.tau)
        leaf((r(40, 70) * math.cos(a), r(40, 70) * math.sin(a), 1), (r(46, 80) * math.cos(a + 0.2), r(46, 80) * math.sin(a + 0.2), r(1, 6)), 7, "Leaves",
             random.choice([(0.40, 0.22, 0.06), (0.50, 0.33, 0.08), (0.28, 0.15, 0.05)]))
    bones = {"Hips": ((0, 0, 150), (0, 0, 166), None), "Robe": ((0, 0, 166), (0, 0, 40), "Hips"), "Leaves": ((0, 0, 2), (0, 20, 2), "Hips"),
             "Chest": ((0, 0, 168), (0, -4, 244), "Hips"), "Head": ((0, -4, 246), (0, -8, 296), "Chest"), "Bell": ((0, -32, 228), (0, -34, 172), "Chest"),
             "Clapper": ((0, -34, 214), (0, -34, 170), "Bell"),
             "LeftArm": ((34, -2, 238), (50, -8, 190), "Chest"), "LeftForeArm": ((50, -8, 190), (50, -36, 156), "LeftArm"),
             "RightArm": ((-34, -2, 238), (-50, -8, 190), "Chest"), "RightForeArm": ((-50, -8, 190), (-50, -36, 156), "RightArm"),
             "Staff": ((-50, -48, 158), (-50, -48, 300), "RightForeArm")}
    clips = {
        "Always": [spin("Leaves", 1)],
        "Idle": [wave("Chest", (1.5, 0, 1), (0, 0, 2)), wave("Robe", (0, 0, 2), phase=1), wave("Head", (3, 0, 4), phase=2), wave("Bell", (5, 3, 0), phase=0.6),
                 wave("Clapper", (9, 6, 0), phase=1.5), wave("LeftArm", (2, 3, 0), phase=1)],
        "Move": [wave("Hips", (0, 0, 0), (0, 0, 4), cycles=2), wave("Chest", (4, 0, 0), cycles=2), wave("Chest", (0, 3, 0)), wave("Robe", (5, 0, 0), cycles=2, phase=1.2),
                 wave("Bell", (12, 0, 0), cycles=2, phase=2), wave("Clapper", (20, 0, 0), cycles=2, phase=3), wave("RightArm", (8, 0, 0), cycles=2), wave("LeftArm", (10, 0, 0), phase=1)],
        # He points the striker: a short, flat thrust of the staff.
        "Attack": [strike("RightArm", (-20, 0, 0), (-70, 0, 0)), strike("RightForeArm", (-30, 0, 0), (-40, 0, 0)), strike("Staff", (20, 0, 0), (60, 0, 0)),
                   strike("Chest", (-6, 0, -8), (10, 0, 10)), strike("Bell", (0, 0, 0), (-14, 0, 0))],
        # The toll: the staff swings across his chest and strikes the bell, which swings and rings on.
        "Cast": [keys("RightArm", (0, (0, 0, 0)), (0.3, (-40, -50, 0)), (0.48, (-50, 30, 0)), (0.7, (-40, 20, 0)), (1, (0, 0, 0))),
                 keys("RightForeArm", (0, (0, 0, 0)), (0.3, (-50, 0, 0)), (0.48, (-70, 0, -40)), (0.7, (-50, 0, -20)), (1, (0, 0, 0))),
                 keys("Staff", (0, (0, 0, 0)), (0.3, (0, 40, 0)), (0.48, (0, -70, 0)), (0.7, (0, -40, 0)), (1, (0, 0, 0))),
                 keys("Bell", (0, (0, 0, 0)), (0.48, (0, 0, 0)), (0.58, (-30, 16, 0)), (0.7, (22, -10, 0)), (0.82, (-12, 6, 0)), (0.92, (6, -3, 0)), (1, (0, 0, 0))),
                 keys("Clapper", (0, (0, 0, 0)), (0.48, (0, 0, 0)), (0.6, (40, 0, 0)), (0.72, (-34, 0, 0)), (0.86, (18, 0, 0)), (1, (0, 0, 0))),
                 keys("Chest", (0, (0, 0, 0)), (0.3, (-8, 0, -14)), (0.48, (6, 0, 12)), (1, (0, 0, 0))), keys("LeftArm", (0, (0, 0, 0)), (0.3, (-30, -50, 0)), (0.7, (-30, -50, 0)), (1, (0, 0, 0))),
                 keys("Head", (0, (0, 0, 0)), (0.48, (-14, 0, 0)), (0.7, (8, 0, 0)), (1, (0, 0, 0)))],
        "Hit": [jolt("Chest", (-9, 0, 6), (0, 6, 0)), jolt("Head", (-12, 0, 0)), jolt("Bell", (18, 0, 0))],
        # The robe empties and drops; the bell falls through it.
        "Defeat": [fall("Hips", (0, 0, 0), (0, 0, -118), at=0.7), fall("Chest", (38, 0, 10), (0, 0, -30), at=0.7), fall("Head", (40, 0, 0), at=0.7),
                   fall("Bell", (60, 0, 0), at=0.7), fall("LeftArm", (20, 40, 0)), fall("RightArm", (10, -30, 0)), fall("Staff", (0, -80, 0), at=0.8)],
    }
    return "HollowBellkeeper", bones, clips, 330, {"Cast": 48}


# =====================================================================================================================
def grandmother_root():
    bark, moss_c, gold = BARK, MOSS, [(0.85, 0.52, 0.06), (0.70, 0.25, 0.05), (0.92, 0.70, 0.12), (0.55, 0.16, 0.05)]
    for k in range(14):                       # the skirt of roots she drags herself along on
        a = k / 14 * math.tau
        reach = r(95, 135)
        tube([(34 * math.cos(a), 10 + 30 * math.sin(a), 70), (62 * math.cos(a + 0.15), 10 + 58 * math.sin(a + 0.15), 34), (reach * 0.8 * math.cos(a + 0.3), 10 + reach * 0.8 * math.sin(a + 0.3), 10),
              (reach * math.cos(a + 0.4), 10 + reach * math.sin(a + 0.4), 1.5)], [17, 13, 8, 2.5], "Skirt", random.choice(bark), sides=6, smooth=False, rough=0.9, name="root")
    trunk = [(0, 12, 52), (0, 8, 100), (0, -2, 150), (0, -16, 196), (0, -30, 232), (0, -40, 256)]
    tube(trunk[:3], [62, 54, 50], "Skirt", bark[0], sides=14, smooth=False, rough=3.2, name="trunklow")
    tube(trunk[2:], [50, 48, 44, 30], "Chest", bark[0], sides=14, smooth=False, rough=3.2, name="trunkhigh")
    for k in range(9):                        # deep wrinkles: ridges of bark running up the trunk
        a = k / 9 * math.tau
        tube([((56 - t * 12) * math.cos(a + t * 0.5), 10 - t * 30 + (50 - t * 10) * math.sin(a + t * 0.5), 60 + t * 170) for t in (0, 0.25, 0.5, 0.75, 1.0)],
             [7, 6.5, 6, 5, 3.5], "Chest" if k % 2 else "Skirt", random.choice(bark[1:]), sides=5, smooth=False, rough=0.5, name="ridge")
    # The face, carved by age into the trunk: closed lids, a long knotted nose, a calm mouth.
    for side in (-1, 1):
        tube(arc((side * 9, -66, 226), (side * 33, -56, 224), (0, -4, 8), 5), [3.5, 5, 5.5, 5.5, 5, 3.5], "Head", bark[1], sides=6, smooth=False, name="brow")
        lump((side * 20, -62, 214), (10, 5, 6), "Head", bark[2], detail=2, squash=0.25, smooth=False, name="lid")
        tube(arc((side * 11, -65, 211), (side * 30, -57, 211), (0, -3, -2), 4), 1.0, "Head", SOCKET, sides=4, smooth=False, name="lash")
        tube(arc((side * 26, -56, 204), (side * 34, -48, 180), (side * 5, 0, 0), 4), [3, 3.6, 3.2, 2.4, 1.6], "Head", bark[2], sides=5, smooth=False, name="cheekline")
    tube([(0, -66, 222), (0, -73, 208), (0, -80, 194), (0, -76, 186)], [5.5, 7, 8.5, 6], "Head", bark[1], sides=7, smooth=False, rough=0.6, name="nose")
    lump((0, -81, 192), (6, 5, 5), "Head", bark[2], detail=1, smooth=False, name="noseknot")
    tube(arc((-15, -64, 174), (15, -64, 174), (0, -4, -3), 5), 1.6, "Head", SOCKET, sides=4, smooth=False, name="mouth")
    lump((0, -62, 162), (15, 8, 9), "Head", bark[1], detail=2, rough=1.2, smooth=False, name="chin")
    # A crown of autumn leaves with nests and small glowing mushrooms in it.
    for n in range(70):
        a, t = r(0, math.tau), r(0.1, 1.0)
        base = (40 * t * math.cos(a), -36 + 36 * t * math.sin(a), 252 + 26 * (1 - t))
        tip = (base[0] + r(12, 26) * math.cos(a) * (0.4 + t), base[1] + r(12, 26) * math.sin(a) * (0.4 + t), base[2] + r(8, 26) * (1.2 - t))
        leaf(base, tip, r(9, 14), "Crown", random.choice(gold))
    for k in range(9):
        a = k / 9 * math.tau
        tube([(20 * math.cos(a), -36 + 20 * math.sin(a), 250), (38 * math.cos(a + 0.3), -36 + 36 * math.sin(a + 0.3), 268), (52 * math.cos(a + 0.5), -36 + 50 * math.sin(a + 0.5), 286)],
             [5, 3.2, 1.2], "Crown", bark[2], sides=5, smooth=False, name="bough")
    for centre in ((22, -24, 270), (-26, -44, 272)):
        tube([(centre[0], centre[1], centre[2] - 3), (centre[0], centre[1], centre[2] + 2)], [5, 9], "Crown", (0.34, 0.25, 0.12), sides=9, smooth=False, name="nest")
        for n in range(3):
            lump((centre[0] + (n - 1) * 3, centre[1] + (n % 2) * 2, centre[2] + 3), (1.8, 1.8, 2.3), "Crown", (0.80, 0.90, 0.92), detail=1)
    for centre in ((40, -52, 244), (-36, -60, 240), (-44, -30, 250), (30, -8, 256), (6, -70, 238)):
        tube([centre, (centre[0], centre[1], centre[2] + 6)], [1.2, 1.0], "Crown", (0.9, 0.9, 0.8), sides=5)
        lump((centre[0], centre[1], centre[2] + 7), (4, 4, 3), "Crown", (0.45, 1.0, 0.85), detail=1, squash=0.2)
    for side in (-1, 1):
        lump((side * 50, -14, 224), (28, 30, 14), "Chest", moss_c, detail=2, rough=2.2, smooth=False, name="shawl")
        lump((side * 30, 14, 232), (24, 22, 10), "Chest", (0.13, 0.30, 0.09), detail=2, rough=2.0, smooth=False, name="shawl")
        word = "Left" if side > 0 else "Right"
        shoulder, elbow, wrist = (side * 54, -18, 214), (side * 96, -34, 150), (side * 108, -70, 66)
        tube([shoulder, ((shoulder[0] + elbow[0]) / 2, -24, 186), elbow], [15, 13, 11], word + "Arm", bark[0], sides=7, smooth=False, rough=1.2)
        tube([elbow, ((elbow[0] + wrist[0]) / 2 + side * 5, -54, 106), wrist], [11, 9, 7.5], word + "ForeArm", bark[1], sides=7, smooth=False, rough=1.0)
        for n in range(4):
            a = (n - 1.5) * 0.36
            tube([wrist, (wrist[0] + math.sin(a) * 22, wrist[1] - 26, 34 - abs(a) * 10), (wrist[0] + math.sin(a) * 34, wrist[1] - 46, 4)], [5, 3.4, 1.0], word + "ForeArm", bark[2],
                 sides=5, smooth=False, name="twigfinger")
        for n in range(3):
            leaf((elbow[0], elbow[1], elbow[2] + 8), (elbow[0] + side * r(8, 22), elbow[1] + r(-14, 14), elbow[2] + r(18, 34)), 10, word + "Arm", random.choice(gold))
    for n in range(26):                       # small white flowers that open when she heals
        a, z = r(0, math.tau), r(80, 220)
        reach = 58 - (z - 60) * 0.06
        lump((reach * math.cos(a), 6 - (z - 60) * 0.16 + reach * 0.92 * math.sin(a), z), (2.6, 2.6, 2.6), "Chest" if z > 150 else "Skirt", (0.95, 0.95, 0.88), detail=1)
    bones = {"Hips": ((0, 10, 60), (0, 10, 80), None), "Skirt": ((0, 10, 80), (0, 10, 20), "Hips"), "Chest": ((0, 0, 150), (0, -30, 232), "Hips"),
             "Head": ((0, -40, 170), (0, -70, 200), "Chest"), "Crown": ((0, -36, 250), (0, -36, 290), "Chest"),
             "LeftArm": ((54, -18, 214), (96, -34, 150), "Chest"), "LeftForeArm": ((96, -34, 150), (108, -70, 66), "LeftArm"),
             "RightArm": ((-54, -18, 214), (-96, -34, 150), "Chest"), "RightForeArm": ((-96, -34, 150), (-108, -70, 66), "RightArm")}
    clips = {
        "Idle": [wave("Chest", (1.5, 0, 1), (0, 0, 2)), wave("Crown", (2, 3, 0), phase=1), wave("LeftArm", (2, 2, 0), phase=0.5), wave("RightArm", (2, -2, 0), phase=1.2),
                 wave("Skirt", (0, 0, 1.5), phase=2)],
        # She hauls herself forward on her arms, one after the other, the skirt of roots dragging behind.
        "Move": [wave("LeftArm", (22, 0, 0)), wave("LeftForeArm", (-14, 0, 0), phase=1), wave("RightArm", (22, 0, 0), phase=PI), wave("RightForeArm", (-14, 0, 0), phase=PI + 1),
                 wave("Chest", (4, 0, 7)), wave("Chest", (3, 0, 0), (0, 0, 3), cycles=2), wave("Skirt", (0, 0, -5), phase=0.8), wave("Crown", (5, 0, 0), cycles=2, phase=1)],
        # One long arm lifts high and comes down like a falling bough.
        "Attack": [strike("RightArm", (-120, 0, 30), (10, 0, -10)), strike("RightForeArm", (-40, 0, 0), (-10, 0, 0)), strike("Chest", (-10, 0, -10), (18, 0, 10), (0, 4, 0), (0, -10, -6)),
                   strike("Crown", (-8, 0, 0), (14, 0, 0)), strike("LeftArm", (10, 0, 0), (-10, 0, 0))],
        # Deep Grove: both arms spread wide and low, palms to the ground, and she bows as the grass rises.
        "Cast": [hold("LeftArm", (-30, 50, 0)), hold("RightArm", (-30, -50, 0)), hold("LeftForeArm", (-20, 0, 0)), hold("RightForeArm", (-20, 0, 0)), hold("Chest", (18, 0, 0), (0, 0, -8)),
                 hold("Crown", (14, 0, 0)), wave("Crown", (0, 5, 0), cycles=4), wave("Skirt", (0, 0, 3), cycles=4)],
        "Hit": [jolt("Chest", (-8, 0, 5), (0, 5, 0)), jolt("Crown", (-14, 0, 0))],
        "Defeat": [fall("Chest", (34, 0, 8), (0, 0, -22), at=0.75), fall("Crown", (30, 0, 0), at=0.75), fall("LeftArm", (20, -30, 0)), fall("RightArm", (20, 30, 0)),
                   fall("LeftForeArm", (30, 0, 0)), fall("RightForeArm", (30, 0, 0)), fall("Hips", (0, 0, 0), (0, 0, -16))],
    }
    return "GrandmotherRoot", bones, clips, 300, {"Move": 44, "Cast": 48}


# =====================================================================================================================
def wonder_heart():
    wood, wood_light, light, root = (0.07, 0.04, 0.025), (0.14, 0.08, 0.04), (0.95, 1.0, 0.35), BARK
    for side in (-1, 1):                      # the seed, split open down the front
        lump((side * 24, 8, 190), (36, 44, 80), "Seed", wood, detail=3, rough=1.0)
        tube(arc((side * 10, -36, 124), (side * 10, -36, 256), (side * 6, -8, 0), 8), 2.4, "Seed", wood_light, sides=5, smooth=False, name="lip")
        for n in range(5):
            tube(arc((side * (22 + n * 5), -28 + n * 9, 120), (side * (22 + n * 5), -28 + n * 9, 262), (side * 22, -6, 0), 8), 1.6, "Seed", wood_light, sides=4, smooth=False, name="grain")
    lump((0, -4, 190), (25, 38, 72), "Seed", light, detail=3, name="light")
    lump((0, -36, 190), (11, 10, 56), "Seed", (1.0, 1.0, 0.75), detail=2, name="slit")
    for k in range(5):                        # roots wrap the seed and hold it upright, leaving the split front clear
        a = 0.9 + k / 5 * (math.tau - 1.8) + math.pi / 2 - 0.9
        tube([((56 - t * 16) * math.cos(a + t * 0.9), 6 + (56 - t * 16) * math.sin(a + t * 0.9), 112 + t * 150) for t in (0, 0.2, 0.4, 0.6, 0.8, 1.0)], [9, 8, 7, 5.5, 4, 2],
             "Body", random.choice(root), sides=6, smooth=False, rough=0.7, name="cage")
    lump((0, 6, 108), (50, 50, 26), "Body", root[0], detail=2, rough=3.0, smooth=False, name="cradle")
    bones = {"Hips": ((0, 0, 110), (0, 0, 130), None), "Body": ((0, 6, 110), (0, 6, 150), "Hips"), "Seed": ((0, 6, 120), (0, 6, 262), "Body"),
             "Halo": ((0, 6, 232), (0, 30, 232), "Body")}
    walk = []
    for index, (sx, sy) in enumerate(((1, -1), (-1, -1), (1, 1), (-1, 1))):   # four great root legs
        name = ("Front" if sy < 0 else "Rear") + ("Left" if sx > 0 else "Right")
        hip, knee, foot = (sx * 34, 6 + sy * 34, 108), (sx * 84, 6 + sy * 84, 124), (sx * 112, 6 + sy * 112, 0)
        tube([hip, ((hip[0] + knee[0]) / 2, (hip[1] + knee[1]) / 2, 128), knee], [19, 17, 15], name + "UpLeg", root[1], sides=7, smooth=False, rough=1.4)
        tube([knee, ((knee[0] + foot[0]) / 2 + sx * 6, (knee[1] + foot[1]) / 2 + sy * 6, 62), foot], [15, 12, 9], name + "Leg", root[0], sides=7, smooth=False, rough=1.2)
        for n in (-1, 0, 1):
            a = math.atan2(sy, sx) + n * 0.6
            tube([foot, (foot[0] + 20 * math.cos(a), foot[1] + 20 * math.sin(a), 5), (foot[0] + 38 * math.cos(a), foot[1] + 38 * math.sin(a), 1)], [9, 5, 1.5], name + "Leg", root[2],
                 sides=5, smooth=False, name="rootlet")
        lump(knee, (17, 17, 15), name + "UpLeg", root[2], detail=1, rough=1.4, smooth=False, name="knee")
        bones[name + "UpLeg"] = (hip, knee, "Body")
        bones[name + "Leg"] = (knee, foot, name + "UpLeg")
        walk.append((name, PI * (index in (1, 2)), sx, sy))
    for k in range(16):                       # a slowly turning halo of bark shards and leaves
        a = k / 16 * math.tau
        centre = Vector((104 * math.cos(a), 6 + 104 * math.sin(a), 232 + 10 * math.sin(k * 2.1)))
        out = Vector((math.cos(a), math.sin(a), 0))
        along = Vector((-math.sin(a), math.cos(a), 0))
        if k % 2:
            leaf(centre - along * 9, centre + along * 12 + Vector((0, 0, 6)), 10, "Halo", random.choice([(0.85, 0.60, 0.10), (0.35, 0.60, 0.15), (0.75, 0.30, 0.06)]))
        else:
            pane([centre - along * 10, centre + out * 3 + Vector((0, 0, 14)), centre + along * 11, centre - out * 2 - Vector((0, 0, 12))], "Halo", random.choice(root), 2.6, "shard")
    # Pieces of the earlier bosses are caught in the roots.
    tube(arc((44, -30, 150), (60, -44, 178), (8, -6, 0), 6), [8, 7.5, 6.5, 5.5, 4.5, 3.5, 2.5], "Body", HORN, sides=7, ridge=0.07, smooth=False, name="trophyhorn")
    pane([(-40, -34, 138), (-58, -30, 150), (-56, -32, 176), (-38, -38, 168)], "Body", (0.05, 0.16, 0.75), 1.6, "trophyglass")
    pane([(-41, -35.5, 142), (-54, -32.5, 151), (-53, -33.5, 170), (-40, -38.5, 164)], "Body", (0.95, 0.55, 0.06), 2.2, "trophyglass")
    tube([(-10, 54, 150), (-10, 56, 146), (-10, 58, 136), (-10, 60, 130)], [2, 6, 9, 11], "Body", BRONZE, sides=10, name="trophybell")

    def gait(amount):
        out = []
        for name, phase, sx, sy in walk:
            out += [wave(name + "UpLeg", (-sy * amount * 0.6, sx * amount * 0.5, 0), phase=phase), keys(name + "Leg", (0, (0, 0, 0))),
                    wave(name + "Leg", (sy * amount * 0.5, -sx * amount * 0.4, 0), phase=phase + 1.2)]
        return [entry for entry in out if entry[0] != "keys"]
    clips = {
        "Always": [spin("Halo", 1)],
        "Idle": [wave("Body", (0, 0, 0), (0, 0, 3)), wave("Seed", (1.5, 1.5, 0), phase=1), wave("Body", (1, 0, 1.5), phase=2)],
        "Move": gait(18) + [wave("Body", (2.5, 2.5, 0), (0, 0, 4), cycles=2), wave("Seed", (0, 3, 0), phase=1)],
        # The seed tips back, then pitches forward and the light lashes out.
        "Attack": [strike("Seed", (-16, 0, 0), (22, 0, 0)), strike("Body", (-6, 0, 0), (9, 0, 0), (0, 6, 6), (0, -14, -6)), strike("FrontLeftUpLeg", (10, 0, 0), (-14, 0, 0)),
                   strike("FrontRightUpLeg", (10, 0, 0), (-14, 0, 0))],
        # It rises on its legs and the whole seed shudders as the light gathers.
        "Cast": [hold("Body", (0, 0, 0), (0, 0, 26)), hold("Seed", (-10, 0, 0)), wave("Seed", (0, 0, 5), cycles=9), wave("Body", (1.5, 1.5, 0), cycles=6)] +
                [hold(name + "UpLeg", (-sy * -10, sx * -9, 0)) for name, _, sx, sy in walk],
        "Hit": [jolt("Body", (-6, 0, 4), (0, 8, -3)), jolt("Seed", (-9, 0, 0))],
        "Defeat": [fall("Body", (0, 0, 0), (0, 0, -70), at=0.7), fall("Seed", (62, 0, 14), at=0.85), fall("Halo", (0, 0, 0), (0, 0, -150), at=0.6)] +
                  [fall(name + "UpLeg", (-sy * -26, sx * -24, 0), at=0.7) for name, _, sx, sy in walk],
    }
    return "WonderHeart", bones, clips, 300, {"Idle": 90}


MONSTERS = {"slate_ram": lambda: ram(False), "old_tusk": lambda: ram(True), "seedpod": seedpod, "reed_archer": reed_archer, "lantern_bulb": lantern_bulb,
            "glass_moth": lambda: moth(False), "glass_queen": lambda: moth(True), "root_sentinel": root_sentinel, "bramble_hound": bramble_hound, "spore_cap": spore_cap,
            "gutter_gargoyle": gargoyle, "bog_toad": lambda: toad(False), "mire_mother": lambda: toad(True), "hollow_bellkeeper": bellkeeper,
            "grandmother_root": grandmother_root, "wonder_heart": wonder_heart}

if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:]
    root, wanted = Path(arguments[0]), arguments[1:] or list(MONSTERS)
    for index, key in enumerate(wanted):
        try:
            kit.reset(417 + list(MONSTERS).index(key))
            name, bones, clips, height, lengths = MONSTERS[key]()
            kit.build(name, root / f"wc_vn_n_{key}" / "blender_k001", bones, clips, height, lengths)
        except Exception:
            import traceback
            print("MONSTER_FAILED", key, flush=True)
            traceback.print_exc()
