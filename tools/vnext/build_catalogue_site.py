"""Generate the public hero catalogue data from the canonical successor catalog; never a second balance source."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/vnext/catalog.json"
SITE = ROOT / "web/catalogue"
OUTPUT = SITE / "data/catalogue.json"
VIEWS = ("main", "left", "right", "back")
STAT_KEYS = ("health", "attackDamage", "attackRate", "range", "armor", "resistance", "movementRate")
PASSIVE = {"directional_guard", "momentum_charge", "stationary_grove"}


def display(stats):
    """Catalogue centipoints become the whole numbers a player reads."""
    return {"health": stats["health"] // 100, "attackDamage": stats["attackDamage"] // 100,
            "attacksPerSecond": round(stats["attackRate"] / 1000, 2), "range": stats["range"],
            "armor": stats["armor"], "resistance": stats["resistance"],
            "moveSpeed": round(stats["movementRate"] / 1000, 2)}


def build():
    raw = SOURCE.read_bytes()
    source = json.loads(raw)
    heroes = []
    for hero in source["heroes"]:
        playable = hero["enabled"]
        ability = hero["ability"] if playable else hero["planned_ability"]
        art = {view: f"art/{hero['id']}/{view}.png" for view in VIEWS
               if (SITE / "art" / hero["id"] / f"{view}.png").exists()}
        heroes.append({
            "id": hero["id"], "name": hero["name"], "race": hero["race"], "class": hero["unit_class"],
            "cost": hero["cost"],
            "role": hero["role_tags"][0], "status": "playable" if playable else "planned",
            "description": hero["dossier"],
            "skill": {"name": ability["name"],
                      "text": ability["tooltip_en"] if playable else ability["behavior"],
                      "type": "passive" if playable and ability["mechanic"] in PASSIVE else
                              "mana" if playable else "planned"},
            "stats": display(hero["stats"] if playable else hero["planned_stats"]),
            "art": art,
        })
    traits = [{"id": trait["id"], "kind": trait["kind"], "name": trait["name"], "thresholds": trait["thresholds"],
               "bonus": trait["behavior"], "members": trait["members"],
               "status": "in_engine" if trait["runtime_enabled"] else "planned"} for trait in source["traits"]]
    def compact(value):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    # One record per line keeps the published file small and its diffs readable.
    return ('{"title":"Wonder Chess","source_sha256":"' + hashlib.sha256(raw).hexdigest() + '",\n"views":' +
            compact(list(VIEWS)) + ',\n"heroes":[\n' + ",\n".join(map(compact, heroes)) +
            '\n],\n"traits":[\n' + ",\n".join(map(compact, traits)) + "\n]}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = build().encode("utf-8")
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != content:
            raise SystemExit("Stale catalogue site data")
        print("Catalogue site data matches canonical source")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(content)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
