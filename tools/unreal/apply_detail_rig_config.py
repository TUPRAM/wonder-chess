"""Write a hero's jointed-finger poses and weapon hold into hero_presentation.json from its detail-rig report.

    apply_detail_rig_config.py <hero_id> <detail-rig.json> [weapon hand: Right|Left|None]

The weapon hand closes around the handle; the other hand hangs relaxed. The handle lies across the palm along the
knuckle line with the working end leaving on the thumb side.
"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
config = root / "game/Content/WonderChess/VNextData/hero_presentation.json"
hero, report = sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
weapon = sys.argv[3] if len(sys.argv) > 3 else "Right"
if report.get("status") != "RIGGED":
    raise SystemExit("The detail rig did not succeed")
GRIP = {"finger": (70, 80, 45), "thumb": (20, 30, 25)}
RELAXED = {"finger": (16, 20, 14), "thumb": (6, 10, 8)}
raw = config.read_bytes()
data = json.loads(raw)
entry = data[hero]
entry["mesh"] = report["job"]["out_mesh"]
entry["curls"] = []
for side, hand in report["hands"].items():
    pose = GRIP if side == weapon else RELAXED
    for label, digit in hand["digits"].items():
        for bone, angle in zip(digit["bones"], pose["thumb" if label == "Thumb" else "finger"]):
            entry["curls"].append({"bone": bone, "axis": digit["flex_axis"], "angle": angle})
if weapon in report["hands"] and entry.get("items"):
    hand = report["hands"][weapon]
    length = hand["hand_length_cm"]
    entry["items"][0]["bone"] = f"{weapon}Hand"
    entry["items"][0]["grip"].update(rest_direction=hand["toward_thumb"], reach=round(0.42 * length, 1),
                                     palm=[round(component * 0.16 * length, 1) for component in hand["palm_normal"]])
text = json.dumps(data, indent=2) + "\n"
config.write_bytes((text.replace("\n", "\r\n") if b"\r\n" in raw else text).encode("utf-8"))
print(hero, "detail rig written:", len(entry["curls"]), "bone poses")
