"""Record a stretch of the running game frame by frame, then summarise it.

The game runs on a fixed clock, saves every frame of the chosen window as an image and writes one line of state per
frame (positions, clips, feet, hands, held items, particles, combat events). This tool launches that run, builds
contact sheets and a GIF from the frames, and checks the state lines for likely defects.

  frame_inspect.py clip  <hero> <clip>            one hero holding one clip (Idle, Move, Attack, Cast, Hit, Defeat, ...)
  frame_inspect.py duel  <hero a> <hero b>        a one-against-one fight, camera on hero a
  frame_inspect.py fight                          the preset six-against-six fight, board camera
  frame_inspect.py solo                           a real solo match from the first second, with the interface

Common options: --start --end (seconds of play), --fps, --distance --aim --side (camera on the focus hero),
--gap (rows between duellists), --alt (Earthbreaker and Hammerer in the six-against-six), --tag (output folder name),
--every (contact-sheet step), --ui.

Output: support/runs/frames/<tag>/ with frame-0000.png..., frames.jsonl, sheet-*.png, clip.gif and report.json.
Cosmetic inspection only; it never changes combat. The game must not already be running.
"""
import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
EDITOR = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe")


def running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq UnrealEditor.exe"], capture_output=True, text=True).stdout
    return "UnrealEditor.exe" in out


def launch(args, extra, out):
    if running():
        raise SystemExit("Unreal is already running; close the game first.")
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("frame-*.png")) + list(out.glob("sheet-*.png")):
        old.unlink()
    log = out / "run.log"
    command = [str(EDITOR), str(ROOT / "game/WonderChess.uproject"), "-game", "-WCStorybook", "-WCProfileName=wonder_vnext",
               "-windowed", f"-ResX={args.width}", f"-ResY={args.height}", "-nosplash", "-unattended", "-nosound",
               "-UDPMESSAGING_TRANSPORT_ENABLE=0", "-benchmark", f"-fps={args.fps}", "-WCFrameRec",
               f"-WCRecStart={args.start}", f"-WCRecEnd={args.end}", f"-WCRecUI={int(args.ui)}",
               f"-WCRecDistance={args.distance}", f"-WCRecAim={args.aim}", f"-WCRecSide={args.side}",
               f"-WCEvidenceDir={out}", f"-abslog={log}"] + extra
    hidden = subprocess.STARTUPINFO()
    hidden.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    hidden.wShowWindow = 0
    process = subprocess.Popen(command, startupinfo=hidden)
    deadline = time.time() + args.timeout
    while process.poll() is None and time.time() < deadline:
        time.sleep(2)
    if process.poll() is None:
        process.kill()
        print("The run did not finish in time and was stopped.")
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if "WC_FRAMEREC_COMPLETE" not in text:
        print("Warning: the recorder did not report completion.")
    for line in text.splitlines():
        if "Fatal error" in line or "WC_HERO_MODEL_REJECTED" in line:
            print(line[-200:])


def sheets(out, every, columns=6, width=320):
    frames = sorted(out.glob("frame-*.png"))
    picked = frames[::every]
    made = []
    for page in range(0, len(picked), columns * 4):
        chunk = picked[page:page + columns * 4]
        first = Image.open(chunk[0])
        height = round(first.height * width / first.width)
        rows = math.ceil(len(chunk) / columns)
        sheet = Image.new("RGB", (columns * width, rows * height), "black")
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(chunk):
            tile = Image.open(path).convert("RGB").resize((width, height))
            x, y = (index % columns) * width, (index // columns) * height
            sheet.paste(tile, (x, y))
            draw.rectangle([x, y, x + 46, y + 14], fill="black")
            draw.text((x + 3, y + 1), path.stem[-4:], fill="white")
        name = out / f"sheet-{page // (columns * 4):02d}.png"
        sheet.save(name)
        made.append(name)
    if frames:
        step = max(1, len(frames) // 90)
        images = [Image.open(p).convert("RGB").resize((640, round(640 * Image.open(p).height / Image.open(p).width))) for p in frames[::step]]
        images[0].save(out / "clip.gif", save_all=True, append_images=images[1:], duration=int(1000 * step / 30), loop=0)
    return frames, made


def analyse(out, focus):
    path = out / "frames.jsonl"
    if not path.exists():
        return {"error": "no frame state was written"}
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = {"frames": len(rows), "findings": []}
    if not rows:
        return report
    report["seconds"] = [rows[0]["time"], rows[-1]["time"]]
    report["particles_peak"] = max(r["particles"] for r in rows)
    tracks = {}
    for row in rows:
        for unit in row["units"]:
            tracks.setdefault(unit["id"], []).append((row["frame"], unit))
    for unit_id, track in tracks.items():
        hero = track[0][1]["hero"]
        if focus and hero != focus:
            continue
        note = {"hero": hero, "id": unit_id, "side": track[0][1]["side"]}
        # A piece that jumps: more than 60 cm between consecutive frames.
        jumps = []
        for (f0, a), (f1, b) in zip(track, track[1:]):
            step = math.dist(a["at"], b["at"])
            if step > 60 and f1 == f0 + 1:
                jumps.append({"frame": f1, "cm": round(step)})
        if jumps:
            note["position_jumps"] = jumps[:8]
        # Held items: the grip should stay a fixed distance from the hand bone, and clear of the spine.
        items = {}
        for frame, unit in track:
            for index, item in enumerate(unit.get("items", [])):
                if "gap" in item:
                    items.setdefault(index, []).append((frame, item))
        for index, samples in items.items():
            gaps = [s["gap"] for _, s in samples]
            clear = min(samples, key=lambda s: s[1]["spine_clearance"])
            entry = {"bone": samples[0][1]["bone"], "hand_to_grip_cm": [round(min(gaps), 1), round(max(gaps), 1)],
                     "closest_to_spine_cm": round(clear[1]["spine_clearance"], 1), "closest_frame": clear[0]}
            if max(gaps) - min(gaps) > 1.5:
                entry["problem"] = "the item slides in the hand"
            if clear[1]["spine_clearance"] < 12:
                entry["problem_body"] = "the weapon's line passes within 12 cm of the spine: it is inside the torso"
            note.setdefault("items", []).append(entry)
        # Feet: a foot near the ground that travels sideways is sliding.
        slides = []
        for (f0, a), (f1, b) in zip(track, track[1:]):
            if "lfoot" not in a or f1 != f0 + 1:
                continue
            body = math.dist(a["at"][:2], b["at"][:2])
            for foot in ("lfoot", "rfoot"):
                low = min(a[foot][2], b[foot][2]) - a["at"][2]
                moved = math.dist(a[foot][:2], b[foot][:2])
                if low < 14 and moved > 4 and body < 1 and a.get("clip") in ("Idle", "Attack", "Cast"):
                    slides.append({"frame": f1, "foot": foot, "cm": round(moved, 1), "clip": a.get("clip")})
        if slides:
            note["foot_slides"] = {"count": len(slides), "worst": max(slides, key=lambda s: s["cm"]), "first": slides[0]}
        clips = []
        for frame, unit in track:
            if "clip" in unit and (not clips or clips[-1][1] != unit["clip"]):
                clips.append((frame, unit["clip"]))
        note["clips"] = clips[:20]
        report["findings"].append(note)
    # Two living pieces closer than 90 cm centre to centre are standing inside each other.
    closest, overlaps = None, 0
    lift = {}
    for row in rows:
        alive = [u for u in row["units"] if not u["hidden"] and u["health"] != 0]
        for i, a in enumerate(alive):
            if "hips" in a:
                best = lift.setdefault(a["id"], [a["hero"], a["hips"][2], a["hips"][2]])
                best[1], best[2] = min(best[1], a["hips"][2]), max(best[2], a["hips"][2])
            for b in alive[i + 1:]:
                gap = math.dist(a["at"][:2], b["at"][:2])
                if closest is None or gap < closest["cm"]:
                    closest = {"cm": round(gap), "frame": row["frame"], "pieces": [a["hero"], b["hero"]]}
                overlaps += gap < 90
    report["closest_pair"] = closest
    report["overlapping_pair_frames"] = overlaps
    report["hip_height_cm"] = {str(k): {"hero": v[0], "lowest": round(v[1]), "highest": round(v[2])} for k, v in lift.items()}
    events = [dict(e, frame=r["frame"]) for r in rows for e in r["events"]]
    report["events"] = len(events)
    report["first_events"] = events[:12]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenario", choices=("clip", "duel", "fight", "solo"))
    parser.add_argument("names", nargs="*")
    parser.add_argument("--start", type=float)
    parser.add_argument("--end", type=float)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--distance", type=float, default=640)
    parser.add_argument("--aim", type=float, default=100)
    parser.add_argument("--side", type=float, default=35)
    parser.add_argument("--gap", type=int, default=1)
    parser.add_argument("--alt", action="store_true")
    parser.add_argument("--look", help="clip scenario: full id of the model to show on the focus piece")
    parser.add_argument("--ui", action="store_true")
    parser.add_argument("--every", type=int, default=3)
    parser.add_argument("--tag")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--no-run", action="store_true", help="only rebuild sheets and the report from an earlier run")
    args = parser.parse_args()
    hero = lambda name: name if name.startswith("wc_vn_") else "wc_vn_" + name
    focus = None
    if args.scenario == "clip":
        focus = hero(args.names[0])
        clip = args.names[1] if len(args.names) > 1 else "Attack"
        extra = ["-WCLab", f"-WCHeroReviewId={focus}", f"-WCRecFocus={focus}", f"-WCRecClip={clip}"]
        start, end, tag = 2.0, 4.5, f"clip_{args.names[0]}_{clip}"
        if args.look:
            # Dress the focus piece as a model that is not a playable hero, such as a monster.
            extra.append(f"-WCHeroReviewLook={args.look}")
            tag = f"clip_{args.look}_{clip}"
    elif args.scenario == "duel":
        focus = hero(args.names[0])
        extra = ["-WCLab", "-WCLabAutoStart", f"-WCRecDuel={focus},{hero(args.names[1])},{args.gap}", f"-WCRecFocus={focus}"]
        start, end, tag = 2.0, 8.0, f"duel_{args.names[0]}_{args.names[1]}"
    elif args.scenario == "fight":
        extra = ["-WCLab", "-WCLabAutoStart"] + (["-WCLabAltHeroes"] if args.alt else [])
        start, end, tag = 2.0, 10.0, "fight_alt" if args.alt else "fight"
        args.ui = False
    else:
        extra = ["-WCSolo", "-WCSeed=417031", f"-WCSavePath={ROOT / 'support/runs/frames/solo-save.json'}"]
        start, end, tag = 1.0, 6.0, "solo"
        args.ui = True
    args.start = start if args.start is None else args.start
    args.end = end if args.end is None else args.end
    out = ROOT / "support/runs/frames" / (args.tag or tag)
    if not args.no_run:
        launch(args, extra, out)
    frames, made = sheets(out, args.every)
    report = analyse(out, focus)
    report["images"] = len(frames)
    report["sheets"] = [str(p.relative_to(ROOT)) for p in made]
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=1)[:6000])


if __name__ == "__main__":
    sys.exit(main())
