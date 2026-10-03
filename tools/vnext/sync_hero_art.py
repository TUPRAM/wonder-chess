"""Check saved hero reference images, publish web copies to the catalogue site and record their status."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/vnext/catalog.json"
ART = ROOT / "production/hero-art/hero_art.json"
STATUS = ROOT / "production/hero-art/status.json"
SITE_ART = ROOT / "web/catalogue/art"
VIEWS = ("main", "left", "back", "right")
WEB_SIZE = 768
THUMB_SIZE = 384

_spec = importlib.util.spec_from_file_location("hero_art_briefs", ROOT / "tools/vnext/build_hero_art_briefs.py")
BRIEFS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BRIEFS)


def inspect_set(folder, label):
    """Return ({view: facts}, problems) for one four-view set. Only file facts; quality is a human review."""
    views, problems, sizes = {}, [], set()
    for view in VIEWS:
        path = folder / f"{view}.png"
        if not path.exists():
            continue
        with Image.open(path) as image:
            if image.format != "PNG":
                problems.append(f"{label}/{view}.png is not a PNG")
            if image.width != image.height or image.width < 1024:
                problems.append(f"{label}/{view}.png must be square and at least 1024 px; "
                                f"found {image.width}x{image.height}")
            sizes.add(image.size)
            views[view] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                           "pixels": [image.width, image.height]}
    if views and len(views) < len(VIEWS):
        problems.append(f"{label} is missing views: " + ", ".join(v for v in VIEWS if v not in views))
    if len(sizes) > 1:
        problems.append(f"{label} views differ in pixel size")
    return views, problems


def inspect(hero_id, art):
    """Return (record, problems, pending). A missing body or item set is pending work, not a fault."""
    place = BRIEFS.layout(hero_id, art)
    folder = ROOT / place["folder"]
    record = {"folder": place["folder"], "full": place["full"], "views": {}, "body": {}, "items": {}}
    record["views"], problems = inspect_set(folder / place["full"], place["full"])
    pending = []
    if not record["views"]:
        return record, [], pending
    if art["accessories"]:
        record["body"], more = inspect_set(folder / place["body"], place["body"])
        problems += more
        pending += [] if record["body"] else [place["body"]]
        for name, subfolder in place["items"].items():
            record["items"][name], more = inspect_set(folder / subfolder, subfolder)
            problems += more
            pending += [] if record["items"][name] else [subfolder]
    return record, problems, pending


def white(band, test):
    return band.point(lambda value: 255 if test(value) else 0)


def cutout(image):
    """Make the flat studio backdrop transparent. Presentation only: the reference PNGs are never changed.

    The backdrop is a smooth, bright, colourless area that touches the frame, or an enclosed pocket of the same
    colour (between an arm and the body). Painted outlines stop the fill, so pale clothing stays.
    """
    rgb = image.convert("RGB")
    width, height = rgb.size
    _, saturation, value = rgb.convert("HSV").split()
    edges = rgb.convert("L").filter(ImageFilter.GaussianBlur(1)).filter(ImageFilter.FIND_EDGES)
    flat = white(edges, lambda v: v < 10)
    pale = ImageChops.multiply(white(saturation, lambda v: v < 18), white(value, lambda v: v > 190))
    # Shrinking first closes hairline gaps in an outline so the fill cannot leak into the figure.
    core = ImageChops.multiply(flat, pale).filter(ImageFilter.MinFilter(7))
    work = Image.new("L", (width + 2, height + 2), 255)
    work.paste(core.crop((8, 8, width - 8, height - 8)), (9, 9))
    ImageDraw.floodfill(work, (0, 0), 128)
    backdrop = white(work.crop((1, 1, width + 1, height + 1)), lambda v: v == 128)
    near = flat
    for band, mean in zip(rgb.split(), ImageStat.Stat(rgb, backdrop).mean):
        near = ImageChops.multiply(near, white(band, lambda v, m=mean: abs(v - m) <= 7))
    pockets = near.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9))
    backdrop = ImageChops.lighter(backdrop, pockets)
    for _ in range(6):
        # Grow back out to the figure's outline, through pale pixels only.
        backdrop = ImageChops.multiply(backdrop.filter(ImageFilter.MaxFilter(5)), pale)
    backdrop = backdrop.filter(ImageFilter.MaxFilter(5))
    result = rgb.convert("RGBA")
    result.putalpha(ImageChops.invert(backdrop).filter(ImageFilter.GaussianBlur(0.8)))
    return result


def publish(hero_id, record):
    """Write each view as a transparent WebP for the hero page and a small one for the grid."""
    target = SITE_ART / hero_id
    target.mkdir(parents=True, exist_ok=True)
    for view in record["views"]:
        with Image.open(ROOT / record["folder"] / record["full"] / f"{view}.png") as image:
            cut = cutout(image)
        cut.resize((WEB_SIZE, WEB_SIZE), Image.LANCZOS).save(target / f"{view}.webp", quality=86, method=6)
        cut.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS).save(target / f"{view}-thumb.webp", quality=82, method=6)
        # Earlier versions published opaque PNG copies; they are replaced by the WebP pair.
        (target / f"{view}.png").unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report only; write nothing")
    args = parser.parse_args()
    heroes = json.loads(CATALOG.read_text(encoding="utf-8"))["heroes"]
    art = json.loads(ART.read_text(encoding="utf-8"))["heroes"]
    previous = json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {"heroes": {}}
    status, failed, shown, complete = {"heroes": {}}, False, 0, 0
    for hero in heroes:
        record, problems, pending = inspect(hero["id"], art[hero["id"]])
        if not record["views"]:
            continue
        if problems:
            failed = True
            print(f"FAIL {hero['id']}: " + "; ".join(problems))
            continue
        shown += 1
        complete += not pending
        if pending:
            print(f"PENDING {hero['id']}: " + ", ".join(pending))
        earlier = previous["heroes"].get(hero["id"], {})
        # An owner decision only stands for the exact images it was given for.
        same = all(earlier.get(key) == record[key] for key in ("views", "body", "items"))
        status["heroes"][hero["id"]] = dict(record, pending=pending,
                                            owner_review=earlier.get("owner_review", "open") if same else "open")
        if not args.check:
            publish(hero["id"], record)
    print(f"{shown} of {len(heroes)} heroes have their four full views; {complete} have every set")
    if not args.check:
        STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "tools/vnext/build_catalogue_site.py")], check=True)
    if failed:
        raise SystemExit("Fix the listed sets; they were not recorded or published")


if __name__ == "__main__":
    main()
