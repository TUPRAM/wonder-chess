"""Draw the Wonder Chess HUD kit: frames, buttons, a banner plaque and the icon set, as PNG files.

Everything is drawn here from shapes and noise, so the kit carries no third-party art. Frames are nine-slice images:
the corners keep their size and the edges stretch. Icons are white-on-clear symbols on a medallion, so the game can
tint them (gold when a synergy is active, dim when not).

    build_hud_kit.py        writes art-source/ui/hud_kit_r001/*.png and a preview sheet

Candidate art for the owner to review; not approved.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parents[2] / "art-source/ui/hud_kit_r001"
S = 4  # supersampling
BRASS, BRASS_LIGHT, BRASS_DARK = (176, 132, 54), (246, 214, 132), (84, 58, 20)
SLATE, SLATE_DARK = (30, 34, 46), (15, 17, 25)
PARCH, PARCH_DARK = (218, 200, 162), (150, 122, 80)


def noise(size, strength, seed, blur=1.2):
    rng = random.Random(seed)
    img = Image.new("L", size)
    img.putdata([rng.randrange(256) for _ in range(size[0] * size[1])])
    img = img.filter(ImageFilter.GaussianBlur(blur))
    return img.point(lambda v: int(128 + (v - 128) * strength))


def shade(base, texture):
    """Multiply-like shading of an RGB image by a grey texture centred on 128."""
    tex = Image.merge("RGB", (texture,) * 3)
    return ImageChops.overlay(base, tex)


def chamfer(w, h, cut, inset=0.0):
    c, i = cut, inset
    return [(i + c, i), (w - i - c, i), (w - i, i + c), (w - i, h - i - c), (w - i - c, h - i), (i + c, h - i), (i, h - i - c), (i, i + c)]


def frame(name, w, h, fill, fill_dark, cut=14, rim=7, seed=1, studs=True, alpha=242, glow=None, pressed=False, grey=False):
    W, H = w * S, h * S
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(x * S, y * S) for x, y in chamfer(w, h, cut)], fill=255)
    # Body: a vertical gradient with grain and a soft inner shadow.
    body = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(body)
    for y in range(H):
        k = y / H
        k = 1 - k if pressed else k
        draw.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(fill, fill_dark)))
    body = shade(body, noise((W, H), 0.55, seed, 1.6 * S / 2))
    body = shade(body, noise((W // 6, H // 6), 0.5, seed + 9, 2).resize((W, H), Image.BICUBIC))
    inner = Image.new("L", (W, H), 0)
    ImageDraw.Draw(inner).polygon([(x * S, y * S) for x, y in chamfer(w, h, cut, rim + 5)], fill=255)
    vignette = inner.filter(ImageFilter.GaussianBlur(5 * S))
    body = Image.composite(body, Image.eval(body, lambda v: int(v * 0.55)), vignette)
    # Rim: brass with a bevel lit from the top left.
    rim_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(rim_mask)
    d.polygon([(x * S, y * S) for x, y in chamfer(w, h, cut)], fill=255)
    d.polygon([(x * S, y * S) for x, y in chamfer(w, h, cut - rim * 0.42, rim)], fill=0)
    metal = Image.new("RGB", (W, H))
    md = ImageDraw.Draw(metal)
    tones = ((150, 150, 150), (215, 215, 215), (70, 70, 70)) if grey else (BRASS, BRASS_LIGHT, BRASS_DARK)
    for y in range(H):
        for x0 in range(0, W, S * 2):
            k = (x0 / W + y / H) / 2
            k = 1 - k if pressed else k
            tone = tuple(int(a + (b - a) * min(1, k * 1.25)) for a, b in zip(tones[1], tones[2])) if k > 0.18 else tones[1]
            mid = tuple(int((t + m) / 2) for t, m in zip(tone, tones[0]))
            md.line([(x0, y), (x0 + S * 2, y)], fill=mid)
    metal = shade(metal, noise((W, H), 0.45, seed + 3, 0.8 * S))
    out = Image.composite(metal, body, rim_mask)
    od = ImageDraw.Draw(out)
    # Engraved inner line and a thin dark outline give the rim weight.
    od.line([(x * S, y * S) for x, y in chamfer(w, h, cut - rim * 0.42, rim)] + [((rim + cut - rim * 0.42) * S, rim * S)], fill=(10, 9, 8), width=S)
    od.line([(x * S, y * S) for x, y in chamfer(w, h, cut - rim * 0.6, rim + 3.2)] + [((rim + 3.2 + cut - rim * 0.6) * S, (rim + 3.2) * S)],
            fill=tuple(int(c * 0.75) for c in tones[0]), width=max(1, S // 2))
    od.line([(x * S, y * S) for x, y in chamfer(w, h, cut, 0.6)] + [((cut + 0.6) * S, 0.6 * S)], fill=(8, 7, 6), width=S)
    if studs:
        for sx, sy in ((cut * 0.72, cut * 0.72), (w - cut * 0.72, cut * 0.72), (cut * 0.72, h - cut * 0.72), (w - cut * 0.72, h - cut * 0.72)):
            r = 3.0
            od.ellipse([(sx - r) * S, (sy - r) * S, (sx + r) * S, (sy + r) * S], fill=tones[2])
            od.ellipse([(sx - r + .8) * S, (sy - r + .6) * S, (sx + r - 1.2) * S, (sy + r - 1.4) * S], fill=tones[0])
            od.ellipse([(sx - 1.6) * S, (sy - 1.8) * S, (sx - .2) * S, (sy - .5) * S], fill=tones[1])
    if glow:
        halo = Image.new("RGB", (W, H), glow)
        ring = rim_mask.filter(ImageFilter.GaussianBlur(3 * S))
        out = Image.composite(ImageChops.screen(out, halo), out, ring.point(lambda v: int(v * 0.55)))
    out.putalpha(mask.point(lambda v: int(v * alpha / 255)))
    out = out.resize((w, h), Image.LANCZOS)
    out.save(OUT / f"{name}.png")
    return out


def plaque(name, w, h):
    """A hanging banner plate: a wide tablet with pointed ends."""
    W, H = w * S, h * S
    point = 26
    shape = [(point, 0), (w - point, 0), (w, h / 2), (w - point, h), (point, h), (0, h / 2)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(x * S, y * S) for x, y in shape], fill=255)
    body = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(body)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip((44, 50, 70), (16, 18, 28))))
    body = shade(body, noise((W, H), 0.5, 77, 1.4 * S / 2))
    d = ImageDraw.Draw(body)

    def inset(points, by):
        cx, cy = w / 2, h / 2
        return [((x + (cx - x) * by / (w / 2)) * S, (y + (cy - y) * by / (h / 2)) * S) for x, y in points]

    d.line(inset(shape, 0.8) + inset(shape, 0.8)[:1], fill=(8, 7, 6), width=S)
    for by, tone, width in ((3.2, BRASS, 5), (2.0, BRASS_LIGHT, 2), (5.6, BRASS_DARK, 2), (8.5, (120, 92, 40), 1)):
        d.line(inset(shape, by) + inset(shape, by)[:1], fill=tone, width=width * S // 2)
    for sx in (point * 0.95, w - point * 0.95):
        r = 3.4
        d.ellipse([(sx - r) * S, (h / 2 - r) * S, (sx + r) * S, (h / 2 + r) * S], fill=BRASS_DARK)
        d.ellipse([(sx - r + 1) * S, (h / 2 - r + .8) * S, (sx + r - 1.2) * S, (h / 2 + r - 1.4) * S], fill=BRASS)
    body.putalpha(mask.point(lambda v: int(v * 0.96)))
    body.resize((w, h), Image.LANCZOS).save(OUT / f"{name}.png")


# ---------------------------------------------------------------------------------------------------------------- icons
def canvas():
    img = Image.new("L", (96 * S, 96 * S), 0)
    return img, ImageDraw.Draw(img)


def P(points):
    return [(x * S, y * S) for x, y in points]


def line(d, points, width=5.0, closed=False):
    pts = P(points) + (P(points[:1]) if closed else [])
    d.line(pts, fill=255, width=int(width * S), joint="curve")
    for x, y in pts:
        r = width * S / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)


def circle(d, x, y, r, width=None):
    box = [(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S]
    if width is None:
        d.ellipse(box, fill=255)
    else:
        d.ellipse(box, outline=255, width=int(width * S))


def cut(d, x, y, r):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=0)


def star(cx, cy, outer, inner, points=5, turn=-90):
    out = []
    for i in range(points * 2):
        a = math.radians(turn + i * 180 / points)
        r = outer if i % 2 == 0 else inner
        out.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return out


def sym_human(d):      # crown
    d.polygon(P([(24, 66), (22, 34), (36, 50), (48, 28), (60, 50), (74, 34), (72, 66)]), fill=255)
    d.rectangle(P([(24, 70), (72, 76)]), fill=255)
    for x in (22, 48, 74):
        circle(d, x, 30 if x != 48 else 24, 4.5)


def sym_elf(d):        # leaf
    d.polygon(P([(48, 16), (70, 40), (68, 62), (48, 80), (28, 62), (26, 40)]), fill=255)
    d.line(P([(48, 26), (48, 84)]), fill=0, width=3 * S)
    for y in (42, 54, 66):
        d.line(P([(48, y), (36, y - 9)]), fill=0, width=2 * S)
        d.line(P([(48, y), (60, y - 9)]), fill=0, width=2 * S)


def sym_dwarf(d):      # anvil
    d.polygon(P([(18, 30), (70, 30), (80, 38), (64, 44), (60, 56), (66, 66), (72, 74), (26, 74), (32, 66), (38, 56), (34, 44), (18, 38)]), fill=255)


def sym_goblin(d):     # wide-eared head
    d.polygon(P([(48, 26), (62, 34), (86, 26), (68, 50), (62, 68), (48, 76), (34, 68), (28, 50), (10, 26), (34, 34)]), fill=255)
    d.polygon(P([(36, 46), (46, 50), (38, 54)]), fill=0)
    d.polygon(P([(60, 46), (50, 50), (58, 54)]), fill=0)
    d.line(P([(40, 64), (44, 67), (48, 64), (52, 67), (56, 64)]), fill=0, width=2 * S)


def sym_orc(d):        # tusked jaw
    d.polygon(P([(22, 34), (74, 34), (78, 56), (64, 72), (32, 72), (18, 56)]), fill=255)
    d.polygon(P([(30, 58), (36, 26), (42, 58)]), fill=255)
    d.polygon(P([(54, 58), (60, 26), (66, 58)]), fill=255)
    d.line(P([(28, 60), (68, 60)]), fill=0, width=3 * S)
    d.polygon(P([(32, 42), (42, 46), (33, 50)]), fill=0)
    d.polygon(P([(64, 42), (54, 46), (63, 50)]), fill=0)


def sym_beastkin(d):   # paw
    d.ellipse(P([(30, 48), (66, 80)]), fill=255)
    for x, y in ((24, 40), (39, 28), (57, 28), (72, 40)):
        d.ellipse(P([(x - 8, y - 10), (x + 8, y + 10)]), fill=255)


def sym_demon(d):      # horns
    d.polygon(P([(30, 46), (48, 40), (66, 46), (62, 68), (48, 80), (34, 68)]), fill=255)
    d.polygon(P([(30, 46), (14, 30), (20, 12), (26, 30), (40, 40)]), fill=255)
    d.polygon(P([(66, 46), (82, 30), (76, 12), (70, 30), (56, 40)]), fill=255)
    d.polygon(P([(36, 54), (45, 58), (37, 61)]), fill=0)
    d.polygon(P([(60, 54), (51, 58), (59, 61)]), fill=0)


def sym_undead(d):     # skull
    d.ellipse(P([(22, 16), (74, 64)]), fill=255)
    d.rectangle(P([(34, 56), (62, 78)]), fill=255)
    cut(d, 37, 42, 8); cut(d, 59, 42, 8)
    d.polygon(P([(48, 50), (44, 60), (52, 60)]), fill=0)
    for x in (41, 48, 55):
        d.line(P([(x, 66), (x, 78)]), fill=0, width=2 * S)


def sym_elemental(d):  # flame
    d.polygon(P([(48, 12), (62, 34), (70, 52), (64, 70), (48, 82), (32, 70), (26, 52), (36, 38), (40, 46), (44, 30)]), fill=255)
    d.polygon(P([(48, 50), (56, 62), (52, 74), (44, 74), (40, 64)]), fill=0)


def sym_dragonkin(d):  # wing
    d.polygon(P([(18, 70), (30, 22), (44, 40), (58, 18), (64, 42), (80, 26), (74, 60), (56, 56), (48, 72), (38, 58)]), fill=255)
    for a, b in (((30, 22), (38, 58)), ((58, 18), (48, 72)), ((80, 26), (56, 56))):
        d.line(P([a, b]), fill=0, width=2 * S)


def sym_tank(d):       # shield
    d.polygon(P([(22, 20), (74, 20), (74, 50), (48, 82), (22, 50)]), fill=255)
    d.polygon(P([(30, 28), (66, 28), (66, 47), (48, 70), (30, 47)]), fill=0)
    d.rectangle(P([(45, 28), (51, 66)]), fill=255)
    d.rectangle(P([(30, 40), (66, 46)]), fill=255)


def sym_fighter(d):    # crossed swords
    for flip in (1, -1):
        cx = 48
        pts = [(cx - 26 * flip, 76), (cx + 20 * flip, 26), (cx + 30 * flip, 16), (cx + 26 * flip, 32), (cx - 18 * flip, 80)]
        d.polygon(P(pts), fill=255)
        line(d, [(cx - 30 * flip, 58), (cx - 12 * flip, 78)], 5)


def sym_assassin(d):   # dagger
    d.polygon(P([(48, 10), (58, 46), (48, 56), (38, 46)]), fill=255)
    d.rectangle(P([(30, 54), (66, 61)]), fill=255)
    d.rectangle(P([(44, 60), (52, 80)]), fill=255)
    circle(d, 48, 84, 6)


def sym_mage(d):       # star
    d.polygon(P(star(48, 48, 36, 14, 4, -90)), fill=255)
    d.polygon(P(star(48, 48, 18, 7, 4, -45)), fill=255)
    cut(d, 48, 48, 5)


def sym_priest(d):     # sun
    circle(d, 48, 48, 15)
    for i in range(8):
        a = math.radians(i * 45)
        d.polygon(P([(48 + math.cos(a) * 36, 48 + math.sin(a) * 36), (48 + math.cos(a + .28) * 20, 48 + math.sin(a + .28) * 20),
                     (48 + math.cos(a - .28) * 20, 48 + math.sin(a - .28) * 20)]), fill=255)


def sym_warlock(d):    # eye in a crescent
    circle(d, 48, 48, 32)
    cut(d, 60, 42, 28)
    d.polygon(P([(40, 54), (58, 44), (76, 54), (58, 64)]), fill=255)
    cut(d, 58, 54, 5)


def sym_sniper(d):     # crosshair
    circle(d, 48, 48, 26, 6)
    for a, b in (((48, 10), (48, 34)), ((48, 62), (48, 86)), ((10, 48), (34, 48)), ((62, 48), (86, 48))):
        line(d, [a, b], 6)
    circle(d, 48, 48, 5)


def sym_engineer(d):   # gear
    for i in range(8):
        a = math.radians(i * 45)
        d.polygon(P([(48 + math.cos(a - .2) * 22, 48 + math.sin(a - .2) * 22), (48 + math.cos(a - .14) * 36, 48 + math.sin(a - .14) * 36),
                     (48 + math.cos(a + .14) * 36, 48 + math.sin(a + .14) * 36), (48 + math.cos(a + .2) * 22, 48 + math.sin(a + .2) * 22)]), fill=255)
    circle(d, 48, 48, 26)
    cut(d, 48, 48, 11)


def sym_shaman(d):     # lightning
    d.polygon(P([(56, 10), (26, 52), (44, 52), (36, 86), (70, 40), (52, 40)]), fill=255)


def sym_summoner(d):   # ring of orbs
    circle(d, 48, 48, 22, 6)
    for i in range(3):
        a = math.radians(-90 + i * 120)
        circle(d, 48 + math.cos(a) * 30, 48 + math.sin(a) * 30, 9)
    circle(d, 48, 48, 7)


def sym_attack(d):
    d.polygon(P([(20, 76), (66, 22), (80, 16), (74, 30), (28, 84)]), fill=255)
    line(d, [(20, 56), (40, 78)], 6)


def sym_speed(d):
    for x in (18, 40, 62):
        d.polygon(P([(x, 24), (x + 14, 24), (x + 28, 48), (x + 14, 72), (x, 72), (x + 14, 48)]), fill=255)


def sym_range(d):
    d.arc(P([(4, 12), (72, 84)]), -60, 60, fill=255, width=6 * S)
    d.line(P([(56, 17), (56, 79)]), fill=255, width=2 * S)
    line(d, [(18, 48), (80, 48)], 5)
    d.polygon(P([(90, 48), (74, 39), (74, 57)]), fill=255)


def sym_armor(d):
    d.polygon(P([(22, 18), (74, 18), (74, 50), (48, 84), (22, 50)]), fill=255)
    d.polygon(P([(32, 28), (64, 28), (64, 47), (48, 68), (32, 47)]), fill=0)


def sym_resist(d):
    d.polygon(P([(22, 18), (74, 18), (74, 50), (48, 84), (22, 50)]), fill=255)
    d.polygon(P(star(48, 44, 17, 7, 4, -90)), fill=0)


def sym_health(d):
    d.polygon(P([(48, 84), (14, 46), (14, 30), (26, 18), (38, 18), (48, 30), (58, 18), (70, 18), (82, 30), (82, 46)]), fill=255)


def sym_mana(d):
    d.polygon(P([(48, 10), (72, 52), (48, 60), (24, 52)]), fill=255)
    circle(d, 48, 58, 25)
    cut(d, 40, 62, 7)


def sym_gold(d):
    circle(d, 48, 48, 36)
    cut(d, 48, 48, 27)
    circle(d, 48, 48, 22)
    d.polygon(P(star(48, 48, 14, 6, 5)), fill=0)


def sym_xp(d):
    d.polygon(P([(48, 12), (80, 48), (60, 48), (60, 84), (36, 84), (36, 48), (16, 48)]), fill=255)


def sym_streak(d):
    sym_elemental(d)


def sym_star(d):
    d.polygon(P(star(48, 50, 38, 16, 5)), fill=255)


def sym_interest(d):
    for y in (66, 50, 34):
        d.ellipse(P([(18, y - 10), (78, y + 10)]), fill=255)
        d.ellipse(P([(18, y - 14), (78, y + 6)]), outline=0, width=2 * S)
        d.ellipse(P([(20, y - 13), (76, y + 5)]), fill=255)


RACES = ["human", "elf", "dwarf", "goblin", "orc", "beastkin", "demon", "undead", "elemental", "dragonkin"]
CLASSES = ["tank", "fighter", "assassin", "mage", "priest", "warlock", "sniper", "engineer", "shaman", "summoner"]
STATS = ["attack", "speed", "range", "armor", "resist", "health", "mana", "gold", "xp", "streak", "star", "interest"]


def icon(name, kind):
    img, d = canvas()
    globals()["sym_" + name](d)
    symbol = img.resize((96, 96), Image.LANCZOS)
    if kind == "stat":
        out = Image.new("RGBA", (96, 96), (255, 255, 255, 0))
        out.putalpha(symbol)
        out.save(OUT / f"icon_{name}.png")
        return out
    # Race: a round medallion. Class: a shield plate. The symbol sits white on top so the game can tint the whole icon.
    W = 96 * S
    plate = Image.new("L", (W, W), 0)
    ring = Image.new("L", (W, W), 0)
    pd, rd = ImageDraw.Draw(plate), ImageDraw.Draw(ring)
    if kind == "race":
        pd.ellipse([3 * S, 3 * S, 93 * S, 93 * S], fill=255)
        rd.ellipse([3 * S, 3 * S, 93 * S, 93 * S], outline=255, width=6 * S)
    else:
        shape = [(8, 4), (88, 4), (92, 8), (92, 56), (48, 93), (4, 56), (4, 8)]
        pd.polygon(P(shape), fill=255)
        rd.line(P(shape) + P(shape[:1]), fill=255, width=6 * S, joint="curve")
    plate = plate.resize((96, 96), Image.LANCZOS)
    ring = ring.resize((96, 96), Image.LANCZOS)
    small = symbol.resize((62, 62), Image.LANCZOS)
    centred = Image.new("L", (96, 96), 0)
    centred.paste(small, (17, 15 if kind == "class" else 17))
    # White ring and symbol at full strength, plate at a third: one tint colours the lot.
    value = ImageChops.lighter(ImageChops.lighter(ring, centred), plate.point(lambda v: int(v * 0.30)))
    out = Image.new("RGBA", (96, 96), (255, 255, 255, 0))
    out.putalpha(ImageChops.lighter(plate.point(lambda v: int(v * 0.86)), ImageChops.lighter(ring, centred)))
    rgb = Image.merge("RGB", (value,) * 3)
    out = Image.merge("RGBA", (*rgb.split(), out.getchannel("A")))
    out.save(OUT / f"icon_{name}.png")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = {}
    made["panel"] = frame("panel", 128, 128, (42, 47, 64), SLATE_DARK, cut=14, rim=7, seed=11)
    made["panel_parchment"] = frame("panel_parchment", 128, 128, PARCH, PARCH_DARK, cut=14, rim=7, seed=23, alpha=250)
    made["button"] = frame("button", 96, 48, (58, 64, 86), (26, 29, 42), cut=8, rim=4, seed=31, studs=False, alpha=252)
    made["button_hover"] = frame("button_hover", 96, 48, (84, 92, 122), (36, 40, 58), cut=8, rim=4, seed=31, studs=False, alpha=255, glow=(110, 84, 30))
    made["button_pressed"] = frame("button_pressed", 96, 48, (40, 44, 62), (20, 22, 32), cut=8, rim=4, seed=31, studs=False, alpha=255, pressed=True)
    made["button_disabled"] = frame("button_disabled", 96, 48, (44, 46, 52), (26, 27, 31), cut=8, rim=4, seed=31, studs=False, alpha=215, grey=True)
    made["button_gold"] = frame("button_gold", 96, 48, (150, 104, 30), (74, 46, 10), cut=8, rim=4, seed=37, studs=False, alpha=255)
    made["button_blue"] = frame("button_blue", 96, 48, (44, 78, 170), (16, 30, 84), cut=8, rim=4, seed=41, studs=False, alpha=255)
    made["row_own"] = frame("row_own", 96, 48, (36, 66, 150), (14, 26, 76), cut=6, rim=3, seed=43, studs=False, alpha=235)
    made["card"] = frame("card", 128, 128, (50, 56, 76), (18, 20, 30), cut=10, rim=5, seed=51, alpha=250)
    plaque("plaque", 256, 96)
    made["plaque"] = Image.open(OUT / "plaque.png")
    icons = [icon(n, "race") for n in RACES] + [icon(n, "class") for n in CLASSES] + [icon(n, "stat") for n in STATS]
    # Preview: frames stretched as they would be in the game, and every icon in gold on slate.
    sheet = Image.new("RGB", (1500, 760), (58, 52, 44))

    def stretch(img, w, h, m):
        out = Image.new("RGBA", (w, h))
        sw, sh = img.size
        xs, ys = [0, m, sw - m, sw], [0, m, sh - m, sh]
        xd, yd = [0, m, w - m, w], [0, m, h - m, h]
        for i in range(3):
            for j in range(3):
                piece = img.crop((xs[i], ys[j], xs[i + 1], ys[j + 1])).resize((xd[i + 1] - xd[i], yd[j + 1] - yd[j]))
                out.paste(piece, (xd[i], yd[j]))
        return out

    for index, (key, w, h, m) in enumerate((("panel", 300, 360, 40), ("panel_parchment", 300, 240, 40), ("card", 190, 260, 36))):
        img = stretch(made[key], w, h, m)
        sheet.paste(img, (20 + index * 330, 20), img)
    x = 20
    for key in ("button", "button_hover", "button_pressed", "button_disabled", "button_gold", "button_blue", "row_own"):
        img = stretch(made[key], 170, 44, 16)
        sheet.paste(img, (x, 400), img)
        x += 185
    img = made["plaque"].resize((460, 96))
    sheet.paste(img, (1010, 20), img)
    for index, ic in enumerate(icons):
        tint = Image.new("RGBA", (96, 96), (236, 196, 96, 255))
        coloured = ImageChops.multiply(ic, tint)
        sheet.paste(coloured.resize((80, 80), Image.LANCZOS), (20 + (index % 16) * 92, 470 + (index // 16) * 96), coloured.resize((80, 80), Image.LANCZOS))
    sheet.save(OUT / "preview.png")
    print("wrote", len(list(OUT.glob("*.png"))), "files to", OUT)


if __name__ == "__main__":
    main()
