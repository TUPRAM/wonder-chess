"""Write a hero's grip bones and weapon hold into hero_presentation.json from its grip-rig report.

    apply_grip_config.py <hero_id> <grip-rig.json> [wrist_turn_degrees]

The hand is turned about its own axis so the thumb faces forward, the four fingers and the thumb close, and the
weapon's handle lies along the knuckle line in the palm with its working end leaving on the thumb side.
"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
config = root / "game/Content/WonderChess/VNextData/hero_presentation.json"
hero, report = sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
turn = float(sys.argv[3]) if len(sys.argv) > 3 else -80.0
if report.get("status") != "RIGGED":
    raise SystemExit("The grip rig did not succeed")
raw = config.read_bytes()
data = json.loads(raw)
entry = data[hero]
side = report["job"]["hand"].replace("Hand", "")
length, axis, palm = report["hand_length_cm"], report["hand_axis"], report["palm_normal"]
entry["mesh"] = report["job"]["out_mesh"]
entry["curls"] = [{"bone": report["job"]["hand"], "axis": axis, "angle": turn},
                  {"bone": f"{side}Fingers1", "axis": report["finger_curl_axis"], "angle": 65},
                  {"bone": f"{side}Fingers2", "axis": report["finger_curl_axis"], "angle": 75}]
if report["thumb_vertices"]:
    entry["curls"].append({"bone": f"{side}Thumb", "axis": axis, "angle": 40})
grip = entry["items"][0]["grip"]
grip.update(rest_direction=report["inward"], reach=round(0.45 * length, 1),
            palm=[round(component * 0.18 * length, 1) for component in palm])
text = json.dumps(data, indent=2) + "\n"
config.write_bytes((text.replace("\n", "\r\n") if b"\r\n" in raw else text).encode("utf-8"))
print(hero, "grip written")
