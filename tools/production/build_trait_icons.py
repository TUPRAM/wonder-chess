"""Draw the race and class badges: one colour and one bold symbol per trait, a circle for races and a shield for classes.

The owner chose this look on 2026-10-14 (solid colour badge with a light bevel, "A with a bevel") after comparing it with
a dark-badge version and with Auto Chess's icons. Writes:

    art-source/ui/trait_icons_r001/svg/trait_<id>.svg, rim_race.svg, rim_class.svg   the drawings
    art-source/ui/trait_icons_r001/trait_<id>.png, rim_<kind>.png                   256 px, for Unreal
    art-source/ui/trait_icons_r001/preview.png                                       a review sheet
    web/catalogue/art/traits/<id>.svg                                                the catalogue site's copies

The game draws a badge in its own colour (dimmed while the trait is not active) and lays a rim over it, tinted silver at
the first step and gold at the second. PNG files are drawn with the installed Edge or Chrome. Candidate art for the
owner's review in the game; not approved.
"""
import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "art-source/ui/trait_icons_r001"
SITE = ROOT / "web/catalogue/art/traits"
G, H = "{G}", "{H}"   # symbol colour, and the colour of holes cut into the symbol


def rot(px, py, cx, cy, deg):
    a = math.radians(deg)
    x, y = px - cx, py - cy
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)


def poly(points, fill=G):
    return f'<path d="M{" L".join(f"{x:.2f} {y:.2f}" for x, y in points)} Z" fill="{fill}"/>'


def sword(hilt, tip, width=6.5, guard=10, grip=9):
    """A straight sword from the hilt point to the tip, with a cross guard and a round pommel."""
    (hx, hy), (tx, ty) = hilt, tip
    length = math.hypot(tx - hx, ty - hy)
    ux, uy = (tx - hx) / length, (ty - hy) / length          # along the blade
    nx, ny = -uy, ux                                          # across it
    w = width / 2
    blade = [(hx + nx * w, hy + ny * w), (tx - ux * 6 + nx * w, ty - uy * 6 + ny * w), (tx, ty),
             (tx - ux * 6 - nx * w, ty - uy * 6 - ny * w), (hx - nx * w, hy - ny * w)]
    g = 2.2
    guard_poly = [(hx + nx * guard + ux * g, hy + ny * guard + uy * g), (hx - nx * guard + ux * g, hy - ny * guard + uy * g),
                  (hx - nx * guard - ux * g, hy - ny * guard - uy * g), (hx + nx * guard - ux * g, hy + ny * guard - uy * g)]
    e = 2.2
    end = (hx - ux * grip, hy - uy * grip)
    grip_poly = [(hx + nx * e, hy + ny * e), (hx - nx * e, hy - ny * e), (end[0] - nx * e, end[1] - ny * e), (end[0] + nx * e, end[1] + ny * e)]
    return poly(blade) + poly(guard_poly) + poly(grip_poly) + f'<circle cx="{end[0] - ux * 2.5:.2f}" cy="{end[1] - uy * 2.5:.2f}" r="4.2" fill="{G}"/>'


def gear(cx=32, cy=32, outer=26, inner=19.5, teeth=8, hole=7.5):
    points = []
    for i in range(teeth):
        base = 360 / teeth * i
        for deg, r in ((base - 13, inner), (base - 8, outer), (base + 8, outer), (base + 13, inner)):
            a = math.radians(deg - 90)
            points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return poly(points) + f'<circle cx="{cx}" cy="{cy}" r="{inner - 2}" fill="{G}"/><circle cx="{cx}" cy="{cy}" r="{hole}" fill="{H}"/>'


def sparkle(cx, cy, r, fill=G):
    k = r * 0.16
    return (f'<path d="M{cx} {cy - r} C{cx + k} {cy - k} {cx + k} {cy - k} {cx + r} {cy} C{cx + k} {cy + k} {cx + k} {cy + k} {cx} {cy + r} '
            f'C{cx - k} {cy + k} {cx - k} {cy + k} {cx - r} {cy} C{cx - k} {cy - k} {cx - k} {cy - k} {cx} {cy - r} Z" fill="{fill}"/>')


HOLE_STROKE = 'stroke="{H}" stroke-linecap="round" fill="none"'

GLYPHS = {
    # ---- races ----
    "human": f'<path d="M10 45 L8 17 L21 28 L32 9 L43 28 L56 17 L54 45 Z" fill="{G}"/><rect x="9" y="48" width="46" height="7" rx="2" fill="{G}"/>'
             f'<circle cx="32" cy="35" r="4.5" fill="{H}"/>',
    "elf": f'<path d="M9 55 C8 30 25 10 56 8 C57 38 38 56 9 55 Z" fill="{G}"/><path d="M14 50 L45 19" {HOLE_STROKE} stroke-width="4"/>',
    "dwarf": f'<path d="M5 15 H43 L59 11 C57 21 51 26 43 26 H40 C38 29 37 32 37 36 H42 L47 47 H17 L22 36 H27 C27 32 26 29 24 26 H14 C9 26 6 21 5 15 Z" fill="{G}"/>'
             f'<rect x="11" y="49" width="42" height="7" rx="2" fill="{G}"/>',
    "goblin": f'<path d="M32 13 C42 13 47 22 47 32 C47 43 40 52 32 52 C24 52 17 43 17 32 C17 22 22 13 32 13 Z" fill="{G}"/>'
              f'<path d="M19 25 L4 15 L18 40 Z" fill="{G}"/><path d="M45 25 L60 15 L46 40 Z" fill="{G}"/>'
              f'<path d="M22 29 L30 32.5 L29 37 L22 34 Z" fill="{H}"/><path d="M42 29 L34 32.5 L35 37 L42 34 Z" fill="{H}"/>'
              f'<path d="M25 43 Q32 47.5 39 43" {HOLE_STROKE} stroke-width="3.2"/>',
    "orc": f'<path d="M10 22 C10 13 18 9 32 9 C46 9 54 13 54 22 V40 C54 50 45 56 32 56 C19 56 10 50 10 40 Z" fill="{G}"/>'
           f'<path d="M15 23 L32 31 L49 23" {HOLE_STROKE} stroke-width="4.5" stroke-linejoin="round"/>'
           f'<circle cx="23" cy="33" r="3.2" fill="{H}"/><circle cx="41" cy="33" r="3.2" fill="{H}"/>'
           f'<rect x="17" y="41" width="30" height="6" rx="3" fill="{H}"/>'
           f'<path d="M18.5 47 L21 33 L26.5 47 Z" fill="{G}"/><path d="M45.5 47 L43 33 L37.5 47 Z" fill="{G}"/>',
    "beastkin": f'<path d="M32 30 C41 30 49 37 49 45 C49 51 44 54 38.5 53 C35.5 52.4 34 51.2 32 51.2 C30 51.2 28.5 52.4 25.5 53 C20 54 15 51 15 45 C15 37 23 30 32 30 Z" fill="{G}"/>'
                + "".join(f'<ellipse cx="{x}" cy="{y}" rx="6" ry="7.6" transform="rotate({a} {x} {y})" fill="{G}"/>'
                          for x, y, a in ((12.5, 26, -28), (24, 14.5, -9), (40, 14.5, 9), (51.5, 26, 28))),
    "demon": f'<path d="M32 29 C40 29 45 35 45 42 C45 50 39 56 32 56 C25 56 19 50 19 42 C19 35 24 29 32 29 Z" fill="{G}"/>'
             f'<path d="M21 36 C12 31 8 21 12 5 C15 16 21 23 29 29 Z" fill="{G}"/><path d="M43 36 C52 31 56 21 52 5 C49 16 43 23 35 29 Z" fill="{G}"/>'
             f'<path d="M23 40 L30 42.5 L29 46 L23 43.5 Z" fill="{H}"/><path d="M41 40 L34 42.5 L35 46 L41 43.5 Z" fill="{H}"/>',
    "undead": f'<path d="M32 8 C44 8 53 17 53 29 C53 37 49 42 43 44 V53 H21 V44 C15 42 11 37 11 29 C11 17 20 8 32 8 Z" fill="{G}"/>'
              f'<circle cx="23.5" cy="29" r="6.3" fill="{H}"/><circle cx="40.5" cy="29" r="6.3" fill="{H}"/><path d="M32 35 L28.3 41 H35.7 Z" fill="{H}"/>'
              f'<path d="M27 47 V53 M32 47 V53 M37 47 V53" {HOLE_STROKE} stroke-width="2.6"/>',
    "elemental": f'<path d="M32 5 L48 27 L32 59 L16 27 Z" fill="{G}"/><path d="M17 27.5 L32 34 L47 27.5" {HOLE_STROKE} stroke-width="3" stroke-linejoin="round"/>',
    "dragonkin": f'<path d="M7 51 C9 30 24 13 58 6 C53 15 52 21 55 28 C48 28 43 32 44 39.5 C37.5 36.5 31.5 38.5 30.5 46 C23 41.5 14 43.5 7 51 Z" fill="{G}"/>'
                 f'<path d="M11 47 C19 32 33 19 52 11" {HOLE_STROKE} stroke-width="2.8"/>',
    # ---- classes ----
    "tank": f'<path d="M14 55 V30 C14 16 22 8 32 8 C42 8 50 16 50 30 V55 Z" fill="{G}"/>'
            f'<path d="M18 27 H46 V34 H36 V48 H28 V34 H18 Z" fill="{H}"/>',
    "fighter": sword((22, 42), (57, 7)) + sword((42, 42), (7, 7)),
    "assassin": f'<path d="M32 60 L25.5 30 H38.5 Z" fill="{G}"/><rect x="17" y="24" width="30" height="6" rx="2.5" fill="{G}"/>'
                f'<rect x="28.5" y="10" width="7" height="14" fill="{G}"/><circle cx="32" cy="8" r="5" fill="{G}"/>',
    "mage": sparkle(30, 34, 26) + sparkle(51, 12, 8),
    "sniper": f'<circle cx="32" cy="32" r="15.5" stroke="{G}" stroke-width="6" fill="none"/>'
              f'<path d="M32 4 V19 M32 45 V60 M4 32 H19 M45 32 H60" stroke="{G}" stroke-width="6" stroke-linecap="round" fill="none"/>'
              f'<circle cx="32" cy="32" r="4.5" fill="{G}"/>',
    "engineer": gear(),
    "warlock": f'<path d="M41 6 A26 26 0 1 0 58 44 A20 20 0 1 1 41 6 Z" fill="{G}"/>' + sparkle(45, 25, 8),
    "priest": f'<path d="M26.5 6 H37.5 V26.5 H58 V37.5 H37.5 V58 H26.5 V37.5 H6 V26.5 H26.5 Z" fill="{G}"/>',
    "shaman": f'<path d="M38 3 L14 37 H29 L23 61 L50 25 H35 Z" fill="{G}"/>',
    "summoner": f'<circle cx="32" cy="32" r="22" stroke="{G}" stroke-width="6.5" fill="none"/>'
                f'<path d="M32 15 L47 42 H17 Z" fill="{G}"/><circle cx="32" cy="33" r="4.6" fill="{H}"/>',
}

# id: (name, kind, badge colour). Races are circles, classes are shields; a colour is used at most once in each kind.
TRAITS = {
    "human": ("Human", "race", "#2F6CE5"),
    "elf": ("Elf", "race", "#13A58B"),
    "dwarf": ("Dwarf", "race", "#8E5A2C"),
    "goblin": ("Goblin", "race", "#E9B820"),
    "orc": ("Orc", "race", "#4C9D2C"),
    "beastkin": ("Beastkin", "race", "#F07F28"),
    "demon": ("Demon", "race", "#D6332E"),
    "undead": ("Undead", "race", "#DCD3B6"),
    "elemental": ("Elemental", "race", "#C93FC0"),
    "dragonkin": ("Dragonkin", "race", "#7B48D8"),
    "tank": ("Tank", "class", "#3F79C9"),
    "fighter": ("Fighter", "class", "#D6332E"),
    "assassin": ("Assassin", "class", "#6B3FB6"),
    "mage": ("Mage", "class", "#C93FC0"),
    "sniper": ("Sniper", "class", "#4C9D2C"),
    "engineer": ("Engineer", "class", "#F07F28"),
    "warlock": ("Warlock", "class", "#8E1F3A"),
    "priest": ("Priest", "class", "#E9B820"),
    "shaman": ("Shaman", "class", "#13A58B"),
    "summoner": ("Summoner", "class", "#22A9D6"),
}
INK = "#1E1A12"
SILVER, GOLD = "#D9DFE8", "#F5C24C"
VIEW = 'viewBox="-4 -4 72 72"'


def mix(hexcolour, other, amount):
    a = [int(hexcolour[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02X}" for x, y in zip(a, b))


def is_light(hexcolour):
    r, g, b = (int(hexcolour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.6


def frame(kind, paint, grow=1.0):
    if kind == "race":
        return f'<circle cx="32" cy="32" r="{29 * grow:.2f}" {paint}/>'
    return (f'<path d="M8 5 H56 V33 C56 46 46 54.5 32 60.5 C18 54.5 8 46 8 33 Z" {paint} '
            f'transform="translate(32 33) scale({grow:.3f}) translate(-32 -33)"/>')


def badge(trait, uid=None):
    """The inside of one bevelled badge (no <svg> wrapper): a top-lit colour fill, a darker rim, an inner highlight
    along the upper edge, and the symbol with a slight drop below it."""
    _, kind, colour = TRAITS[trait]
    uid = uid or trait
    light = is_light(colour)
    symbol = INK if light else "#FFFFFF"
    drop = mix(colour, "#FFFFFF", 0.55) if light else mix(colour, "#000000", 0.55)
    defs = (f'<defs><linearGradient id="fill-{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{mix(colour, "#FFFFFF", 0.24)}"/><stop offset="0.55" stop-color="{colour}"/>'
            f'<stop offset="1" stop-color="{mix(colour, "#000000", 0.22)}"/></linearGradient>'
            f'<linearGradient id="shine-{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.6"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    body = frame(kind, f'fill="url(#fill-{uid})" stroke="{mix(colour, "#000000", 0.5)}" stroke-width="2.6"')
    shine = frame(kind, f'fill="none" stroke="url(#shine-{uid})" stroke-width="1.8"', 0.89)
    place = "translate(32 32) scale(0.74) translate(-32 -32)" if kind == "race" else "translate(32 30) scale(0.66) translate(-32 -32)"
    glyph = GLYPHS[trait]
    shadow = glyph.replace(G, drop).replace(H, drop)
    top = glyph.replace(G, symbol).replace(H, colour)
    return (f'{defs}{body}{shine}<g transform="translate(0 1.5)"><g transform="{place}">{shadow}</g></g>'
            f'<g transform="{place}">{top}</g>')


def rim(kind, colour="#FFFFFF"):
    """The outline drawn round a badge when its trait is active: the game tints it silver or gold."""
    return frame(kind, f'fill="none" stroke="{colour}" stroke-width="3.6"', 1.075)


def svg(inner, size=None, label=None):
    dims = f' width="{size}" height="{size}"' if size else ""
    aria = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" {VIEW}{dims}{aria}>{inner}</svg>'


def icon(trait, state="active2", size=64, uid=None):
    """A badge as the game shows it: inactive (dimmed), active2 (silver rim) or active4 (gold rim)."""
    kind = TRAITS[trait][1]
    ring = rim(kind, SILVER if state == "active2" else GOLD) if state in ("active2", "active4") else ""
    dim = ' opacity="0.4"' if state == "inactive" else ""
    return svg(f"<g{dim}>{badge(trait, uid)}{ring}</g>", size, TRAITS[trait][0])


# ---------------------------------------------------------------------------------------------------------------------
def edge():
    for path in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                 r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if Path(path).exists():
            return path
    return None


def render(cells, out_dir, size=256):
    """Draw each (name, svg) cell at size x size on a transparent page with a headless browser, then cut them apart."""
    from PIL import Image
    columns = 6
    rows = (len(cells) + columns - 1) // columns
    page = ['<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:transparent}'
            f'div{{position:absolute;width:{size}px;height:{size}px}}svg{{display:block;width:{size}px;height:{size}px}}</style>']
    for index, (_, markup) in enumerate(cells):
        page.append(f'<div style="left:{index % columns * size}px;top:{index // columns * size}px">{markup}</div>')
    browser = edge()
    if not browser:
        raise SystemExit("No Edge or Chrome found to draw the PNG files; run with --no-png to write the SVG files only.")
    with tempfile.TemporaryDirectory() as temp:
        html, shot = Path(temp) / "sheet.html", Path(temp) / "sheet.png"
        html.write_text("".join(page), encoding="utf-8")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--default-background-color=00000000", f"--user-data-dir={Path(temp) / 'profile'}",
                        f"--window-size={columns * size},{rows * size}", f"--screenshot={shot}", html.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        sheet = Image.open(shot).convert("RGBA")
        for index, (name, _) in enumerate(cells):
            x, y = index % columns * size, index // columns * size
            sheet.crop((x, y, x + size, y + size)).save(out_dir / f"{name}.png")


def preview(out_dir):
    """A review sheet: every badge at three sizes and in its three states, on the slate and parchment the HUD uses."""
    races = [t for t, v in TRAITS.items() if v[1] == "race"]
    classes = [t for t, v in TRAITS.items() if v[1] == "class"]
    def row(label, items, background="#1E2230", ink="#C9CDD8"):
        return (f'<div style="display:flex;align-items:center;gap:6px;padding:8px 12px;background:{background}">'
                f'<b style="width:120px;color:{ink};font:600 13px Segoe UI">{label}</b>{"".join(items)}</div>')
    named = [f'<div style="width:70px;text-align:center;color:#E8E9EF;font:12px Segoe UI">{icon(t, "active2", 56, t + "-n")}<br>{TRAITS[t][0]}</div>'
             for t in races + classes]
    blocks = [row("Races and classes", named[:10]), row("", named[10:])]
    for size in (30, 22):
        blocks.append(row(f"{size} px", [icon(t, "active2", size, f"{t}-{size}") for t in races + classes]))
        blocks.append(row(f"{size} px on parchment", [icon(t, "active2", size, f"{t}-p{size}") for t in races + classes], "#DCCAA2", "#2B2216"))
    states = []
    for t in ("orc", "mage", "undead", "priest"):
        states += [icon(t, s, 48, f"{t}-{s}") for s in ("inactive", "active2", "active4")] + ['<span style="width:18px"></span>']
    blocks.append(row("Fewer than 2 / 2 / 4", states))
    html = '<!doctype html><meta charset="utf-8"><body style="margin:0;background:#151925">' + "".join(blocks) + "</body>"
    browser = edge()
    if not browser:
        return
    with tempfile.TemporaryDirectory() as temp:
        page = Path(temp) / "preview.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--user-data-dir={Path(temp) / 'profile'}", "--window-size=1500,560", f"--screenshot={out_dir / 'preview.png'}", page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-png", action="store_true", help="write the SVG files only")
    args = parser.parse_args()
    catalog = json.loads((ROOT / "data/vnext/catalog.json").read_text(encoding="utf-8"))
    missing = sorted({t["id"] for t in catalog["traits"]} ^ set(TRAITS))
    if missing:
        raise SystemExit(f"Icons and catalogue traits differ: {missing}")
    for kind in ("race", "class"):
        colours = [v[2] for v in TRAITS.values() if v[1] == kind]
        if len(set(colours)) != len(colours):
            raise SystemExit(f"Two {kind} icons share a colour")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "svg").mkdir(exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    cells = []
    for trait in TRAITS:
        markup = svg(badge(trait), label=TRAITS[trait][0])
        (OUT / "svg" / f"trait_{trait}.svg").write_text(markup + "\n", encoding="utf-8")
        (SITE / f"{trait}.svg").write_text(markup + "\n", encoding="utf-8")
        cells.append((f"trait_{trait}", markup))
    for kind in ("race", "class"):
        markup = svg(rim(kind))
        (OUT / "svg" / f"rim_{kind}.svg").write_text(markup + "\n", encoding="utf-8")
        cells.append((f"rim_{kind}", markup))
    if not args.no_png:
        render(cells, OUT)
        preview(OUT)
    print(f"{len(TRAITS)} badges and 2 rims written to {OUT.relative_to(ROOT)}" + ("" if args.no_png else " (SVG and 256 px PNG)"))


if __name__ == "__main__":
    main()
