"""Check saved hero reference images, publish web copies to the catalogue site and record their status."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/vnext/catalog.json"
ART = ROOT / "production/hero-art/hero_art.json"
STATUS = ROOT / "production/hero-art/status.json"
SITE_ART = ROOT / "web/catalogue/art"
VIEWS = ("main", "left", "back", "right")
WEB_SIZE = 768


def reference(hero_id):
    return ROOT / "art-source/asset-studio" / hero_id / "inputs/references/four_view_r002"


def inspect(hero_id, accessories):
    """Return (record, problems). Only file facts are checked; visual quality is a human review."""
    folder = reference(hero_id)
    record = {"folder": folder.relative_to(ROOT).as_posix(), "views": {}, "accessories": {}}
    problems, sizes = [], set()
    for view in VIEWS:
        path = folder / f"{view}.png"
        if not path.exists():
            continue
        with Image.open(path) as image:
            if image.format != "PNG":
                problems.append(f"{view}.png is not a PNG")
            if image.width != image.height or image.width < 1024:
                problems.append(f"{view}.png must be square and at least 1024 px; found {image.width}x{image.height}")
            sizes.add(image.size)
            record["views"][view] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                     "pixels": [image.width, image.height]}
    if record["views"] and len(record["views"]) < len(VIEWS):
        problems.append("missing views: " + ", ".join(v for v in VIEWS if v not in record["views"]))
    if len(sizes) > 1:
        problems.append("the four views differ in pixel size")
    for name in accessories:
        path = folder / "accessories" / f"{name}.png"
        if path.exists():
            record["accessories"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return record, problems


def publish(hero_id, record):
    target = SITE_ART / hero_id
    target.mkdir(parents=True, exist_ok=True)
    for view in record["views"]:
        with Image.open(reference(hero_id) / f"{view}.png") as image:
            image.convert("RGB").resize((WEB_SIZE, WEB_SIZE), Image.LANCZOS).save(target / f"{view}.png", optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report only; write nothing")
    args = parser.parse_args()
    heroes = json.loads(CATALOG.read_text(encoding="utf-8"))["heroes"]
    art = json.loads(ART.read_text(encoding="utf-8"))["heroes"]
    previous = json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {"heroes": {}}
    status, failed, complete = {"heroes": {}}, False, 0
    for hero in heroes:
        record, problems = inspect(hero["id"], [name for name, _ in art[hero["id"]]["accessories"]])
        if not record["views"]:
            continue
        if problems:
            failed = True
            print(f"FAIL {hero['id']}: " + "; ".join(problems))
            continue
        complete += 1
        earlier = previous["heroes"].get(hero["id"], {})
        # An owner decision only stands for the exact images it was given for.
        review = earlier.get("owner_review", "open") if earlier.get("views") == record["views"] else "open"
        status["heroes"][hero["id"]] = dict(record, owner_review=review)
        if not args.check:
            publish(hero["id"], record)
    print(f"{complete} of {len(heroes)} heroes have a complete four-view set")
    if failed:
        raise SystemExit("Fix the listed sets; nothing was recorded")
    if args.check:
        return
    STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools/vnext/build_catalogue_site.py")], check=True)


if __name__ == "__main__":
    main()
