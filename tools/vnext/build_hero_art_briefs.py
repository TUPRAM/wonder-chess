"""Generate the hero look book and the per-image prompts from the catalog and production/hero-art/hero_art.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/vnext/catalog.json"
ART = ROOT / "production/hero-art/hero_art.json"
OUTPUT = ROOT / "production/hero-art/BRIEFS.md"
LOOKS = ROOT / "production/hero-art/HERO_LOOKS.md"
VIEWS = (
    ("main", "FRONT VIEW. The subject faces the viewer directly."),
    ("left", "LEFT SIDE VIEW. The camera looks at the subject's own left side; it faces the left edge of the "
             "image, in exact profile."),
    ("back", "BACK VIEW. The camera is directly behind; the subject faces away from the viewer."),
    ("right", "RIGHT SIDE VIEW. The camera looks at the subject's own right side; it faces the right edge of the "
              "image, in exact profile."),
)
SHARED = ("Painterly semi-realistic fantasy game art in the same style as the Shieldbearer reference: believable "
          "worn materials (steel plate with rivets and scratches, chainmail, stitched leather, weathered cloth "
          "with trim, bone, fur, scales), rendered like a clean 3D character turnaround. Strong readable "
          "silhouette, medium-sized detail and a limited dominant palette. Not a cartoon, not chibi, not a toy. "
          "Straight-on orthographic-style camera, even soft studio light, plain light-grey background #E6E6E6, "
          "no ground shadow, no scenery, no effects, no text. The whole subject is inside the frame with margin "
          "on every side.")
POSE = ("Full body, standing straight in a relaxed A-pose with the arms slightly away from the body and the legs "
        "slightly apart, looking straight ahead.")
EXPRESSION = "a calm, serious expression"


def article(word):
    return "an" if word[0] in "aeiou" else "a"


def layout(hero_id, art):
    """Folder and subfolder names of a hero's reference set; one hero predates the standard names."""
    reference = art.get("reference", {})
    items = {name: reference.get("items", {}).get(name, f"items/{name}") for name, *_ in art["accessories"]}
    return {"folder": f"art-source/asset-studio/{hero_id}/inputs/references/{reference.get('set', 'four_view_r001')}",
            "full": reference.get("full", "full"), "body": reference.get("body", "body"), "items": items,
            "exists": "set" in reference}


def design(hero, art, races, with_items):
    colours = ", ".join(f"{name} {code}" for name, code in art["colors"])
    parts = [f"Expression: {art.get('expression', EXPRESSION)}.",
             f"Design: {hero['name']}, {article(hero['race'])} {hero['race']} {hero['unit_class']}. "
             f"{hero['dossier']['form']}",
             f"{hero['race'].title()} look: {races[hero['race']]}.",
             f"About {art['heads']} heads tall; {art['build']}.",
             f"Dominant colours: {colours}; neutral leather, metal and skin tones are allowed beside them.",
             "Features: " + "; ".join(art["features"]) + "."]
    if with_items:
        parts.append(f"Right hand: {art['right_hand']}. Left hand: {art['left_hand']}.")
        if art.get("extra"):
            parts.append("Also: " + art["extra"] + ".")
    else:
        parts.append("Both hands are empty and relaxed. No held, strapped, summoned or floating item appears "
                     "anywhere in the image; everything worn on the body stays exactly the same.")
    parts.append(f"Seen from behind: {art['back']}.")
    return " ".join(parts)


def sets(hero, art, races):
    """(subfolder, title, prompt text, pose) for every four-view set of one hero."""
    place = layout(hero["id"], art)
    pose = art.get("pose", POSE)
    result = [(place["full"], "Complete hero with every held, strapped and floating item",
               design(hero, art, races, True), pose)]
    if art["accessories"]:
        result.append((place["body"], "The same hero without any item, for rigging",
                       design(hero, art, races, False), pose))
    for name, description, *kind in art["accessories"]:
        alone = ("The creature alone, standing still and centred; no other character."
                 if kind else "The item alone, upright and centred; no character, no hand.")
        result.append((place["items"][name], f"{'Summon' if kind else 'Item'} alone: {name}",
                       f"Subject: {description}, belonging to {hero['name']}, in the same colours and materials. "
                       f"{alone}", ""))
    return result


def load():
    heroes = json.loads(CATALOG.read_text(encoding="utf-8"))["heroes"]
    source = json.loads(ART.read_text(encoding="utf-8"))
    art = source["heroes"]
    missing = [hero["id"] for hero in heroes if hero["id"] not in art]
    if missing or len(art) != len(heroes):
        raise SystemExit(f"Art descriptions must match the catalogue exactly; missing {missing}")
    return heroes, art, source["races"]


def heading(order, hero, place):
    return [f"## {order:02d}. {hero['name']} — `{hero['id']}`", "",
            f"{hero['race'].title()} {hero['unit_class'].title()} · cost {hero['cost']} · "
            f"{'in the game' if hero['enabled'] else 'planned'}", "",
            f"**Folder:** `{place['folder']}/`", ""]


def build():
    heroes, art, races = load()
    lines = ["# Hero art briefs", "",
             "Generated by `tools/vnext/build_hero_art_briefs.py` from `data/vnext/catalog.json` and "
             "`production/hero-art/hero_art.json`. Do not edit by hand.", "",
             "Follow [the visual standard](VISUAL_STANDARD.md). Every set has four views: `main.png`, `left.png`, "
             "`back.png`, `right.png`. Save every image exactly at the path shown.", ""]
    for order, hero in enumerate(heroes, 1):
        entry = art[hero["id"]]
        place = layout(hero["id"], entry)
        lines += heading(order, hero, place)
        if place["exists"]:
            lines += ["**This set already exists and is the style anchor for the roster. Do not regenerate it.**",
                      ""]
            continue
        lines += ["| Colour | Hex |", "|---|---|"]
        lines += [f"| {name} | `{code}` |" for name, code in entry["colors"]]
        for folder, title, text, pose in sets(hero, entry, races):
            lines += ["", f"### `{folder}/` — {title}", ""]
            for view, camera in VIEWS:
                prompt = " ".join(part for part in (SHARED, pose, text, camera) if part)
                lines += [f"**`{folder}/{view}.png`**", "", "```text", prompt, "```", ""]
    return "\n".join(lines)


def build_looks():
    """The readable description of every hero's look, without the repeated prompt text."""
    heroes, art, races = load()
    lines = ["# Hero looks", "",
             "Generated by `tools/vnext/build_hero_art_briefs.py` from `data/vnext/catalog.json` and "
             "`production/hero-art/hero_art.json`. Do not edit by hand; edit `hero_art.json`.", "",
             "What every hero looks like, in the style of [the visual standard](VISUAL_STANDARD.md). The ready "
             "prompt for each image is in [BRIEFS.md](BRIEFS.md). Left and right are the hero's own.", "",
             "## Race looks", "", "| Race | Shared look |", "|---|---|"]
    lines += [f"| {race.title()} | {text} |" for race, text in races.items()]
    lines += ["", "## Image count", "", "| Hero | Sets | Images |", "|---|---|---|"]
    total = 0
    for hero in heroes:
        entry = art[hero["id"]]
        if layout(hero["id"], entry)["exists"]:
            lines.append(f"| {hero['name']} | done | 0 |")
            continue
        names = ["full"] + (["body"] if entry["accessories"] else []) + [name for name, *_ in entry["accessories"]]
        total += 4 * len(names)
        lines.append(f"| {hero['name']} | {', '.join(names)} | {4 * len(names)} |")
    lines += [f"| **Total still to make** | | **{total}** |", ""]
    for order, hero in enumerate(heroes, 1):
        entry = art[hero["id"]]
        place = layout(hero["id"], entry)
        lines += heading(order, hero, place)
        lines += [f"{hero['dossier']['form']} About {entry['heads']} heads tall; {entry['build']}.", "",
                  "Colours: " + ", ".join(f"{name} `{code}`" for name, code in entry["colors"]) + ".", ""]
        lines += [f"- {feature[0].upper()}{feature[1:]}." for feature in entry["features"]]
        lines += [f"- **Right hand:** {entry['right_hand']}.", f"- **Left hand:** {entry['left_hand']}."]
        if entry.get("extra"):
            lines.append(f"- **Beside the hero:** {entry['extra']}.")
        lines.append(f"- **From behind:** {entry['back']}.")
        for name, description, *kind in entry["accessories"]:
            lines.append(f"- **Separate {'summon' if kind else 'item'} `{name}`:** {description}.")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = ((OUTPUT, build().encode("utf-8")), (LOOKS, build_looks().encode("utf-8")))
    if args.check:
        if any(not path.exists() or path.read_bytes() != content for path, content in outputs):
            raise SystemExit("Stale hero art briefs")
        print("Hero art briefs match their sources")
        return
    for path, content in outputs:
        path.write_bytes(content)
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
