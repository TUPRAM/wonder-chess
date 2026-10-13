"""Save screenshots of one game window while the owner plays it, as layout and pacing reference.

Only the window whose title contains --title is captured, and only while it is the window in front; anything else on
screen is never saved. Pictures go to support/runs/reference-play/<start time>/ as JPEG with a small index file.

    record_reference_play.py --title "Auto Chess" --every 2 --minutes 40
    record_reference_play.py --list          show the title of the window in front for ten seconds, saving nothing

Stop early by closing the console window or pressing Ctrl+C. The pictures are private reference only: study layout,
pacing and readability from them; never copy another game's art, names or text into Wonder Chess.
"""
import argparse
import ctypes
import ctypes.wintypes
import json
import time
from datetime import datetime
from pathlib import Path

from PIL import ImageGrab

ROOT = Path(__file__).resolve().parents[2]
user32 = ctypes.windll.user32
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass


def front_window():
    handle = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(handle)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(handle, buffer, length + 1)
    rect = ctypes.wintypes.RECT()
    user32.GetClientRect(handle, ctypes.byref(rect))
    corner = ctypes.wintypes.POINT(0, 0)
    user32.ClientToScreen(handle, ctypes.byref(corner))
    return buffer.value, (corner.x, corner.y, corner.x + rect.right, corner.y + rect.bottom)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--title", default="Auto Chess")
    parser.add_argument("--every", type=float, default=2.0)
    parser.add_argument("--minutes", type=float, default=40.0)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        for _ in range(10):
            print("In front:", front_window()[0])
            time.sleep(1)
        return
    out = ROOT / "support/runs/reference-play" / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    index, saved, skipped = [], 0, 0
    print(f"Recording windows titled '{args.title}' every {args.every:g} s for up to {args.minutes:g} minutes.")
    print("Switch to the game and play. Close this window or press Ctrl+C to stop.")
    start = time.time()
    try:
        while time.time() - start < args.minutes * 60:
            tick = time.time()
            title, box = front_window()
            if args.title.lower() in title.lower() and box[2] - box[0] > 300 and box[3] - box[1] > 200:
                image = ImageGrab.grab(bbox=box, all_screens=True).convert("RGB")
                if image.width > args.width:
                    image = image.resize((args.width, round(image.height * args.width / image.width)))
                name = f"shot-{saved:04d}.jpg"
                image.save(out / name, quality=82)
                index.append({"file": name, "seconds": round(tick - start, 1)})
                saved += 1
                if saved % 15 == 0:
                    print(f"{saved} pictures saved")
            else:
                skipped += 1
            time.sleep(max(0.05, args.every - (time.time() - tick)))
    except KeyboardInterrupt:
        pass
    (out / "index.json").write_text(json.dumps({"title": args.title, "every_seconds": args.every, "saved": saved,
                                                "skipped_other_window": skipped, "shots": index}, indent=1), encoding="utf-8")
    print(f"Done: {saved} pictures in {out}")


if __name__ == "__main__":
    main()
