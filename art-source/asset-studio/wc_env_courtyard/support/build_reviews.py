"""Build honest courtyard review derivatives without editing source images.

Examples:
  build_reviews.py ../inputs/references/wall_section_r001 --rejected-left rejected/left_attempt02.png
  build_reviews.py ../inputs/textures_r001 --tiling
  build_reviews.py ../inputs/textures_r001 --textures

Four-view panels preserve every source pixel at 1:1 scale. Missing views are blank.
Flat-image contact sheets use explicitly labeled, proportional review thumbnails.
These sheets record review status only and never mark an asset approved.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


VIEWS = ("main", "left", "back", "right")
TEXTURES = ("flagstone_tile", "board_tile_light", "board_tile_dark", "sky_backdrop")
LABEL_HEIGHT = 76
GAP = 20
PAPER = (245, 245, 245)
BLANK = (230, 230, 230)


def font(size: int):
    for path in ("C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def open_source(path: Path):
    with Image.open(path) as source:
        source.load()
        return source.convert("RGB")


def resolve(folder: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else folder / path


def build_sheet(folder: Path, names, overrides, output_name: str):
    entries = []
    for name in names:
        override = overrides.get(name)
        path = resolve(folder, override) if override else folder / f"{name}.png"
        if override and not path.is_file():
            raise FileNotFoundError(path)
        entries.append((name, path, bool(override), open_source(path) if path.is_file() else None))
    existing = [entry[3] for entry in entries if entry[3] is not None]
    if not existing:
        raise ValueError(f"No images found in {folder}")
    width = max(im.width for im in existing)
    height = max(im.height for im in existing)
    sheet = Image.new("RGB", (len(names) * width + (len(names) - 1) * GAP, height + LABEL_HEIGHT), PAPER)
    draw = ImageDraw.Draw(sheet)
    label_font, detail_font = font(26), font(20)
    for index, (name, path, rejected, source) in enumerate(entries):
        x = index * (width + GAP)
        status = "REJECTED" if rejected else ("NOT GENERATED" if source is None else "CANDIDATE")
        label = f"{name.upper()} — {status}"
        draw.text((x + 16, 8), label, font=label_font, fill=(145, 25, 25) if rejected else (35, 35, 35))
        if source is None:
            draw.rectangle((x, LABEL_HEIGHT, x + width - 1, LABEL_HEIGHT + height - 1), fill=BLANK)
            draw.text((x + 16, 43), "No source image exists", font=detail_font, fill=(90, 90, 90))
        else:
            draw.text((x + 16, 43), f"{path.name} | {source.width} × {source.height} | 1:1 pixels", font=detail_font, fill=(90, 90, 90))
            # Top-aligned canvases preserve baseline/scale discrepancies rather than hiding them.
            sheet.paste(source, (x, LABEL_HEIGHT))
    output = folder / "review" / output_name
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(output.resolve())


def build_tiling(folder: Path):
    source = open_source(folder / "flagstone_tile.png")
    sheet = Image.new("RGB", (source.width * 2, source.height * 2))
    for x in (0, source.width):
        for y in (0, source.height):
            sheet.paste(source, (x, y))
    output = folder / "review" / "flagstone_tiling_check.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(output.resolve())


def build_textures(folder: Path):
    """Three square thumbnails over one wide sky, without changing source files."""
    sources = {name: open_source(folder / f"{name}.png") for name in TEXTURES}
    thumb_width = 640
    sheet_width = 3 * thumb_width + 2 * GAP
    sky = sources["sky_backdrop"]
    sky_height = round(sheet_width * sky.height / sky.width)
    lower_y = LABEL_HEIGHT + thumb_width + GAP
    sheet = Image.new("RGB", (sheet_width, lower_y + LABEL_HEIGHT + sky_height), PAPER)
    draw = ImageDraw.Draw(sheet)
    label_font, detail_font = font(26), font(20)

    def paste_review(name, x, y, box_width, box_height):
        source = sources[name]
        draw.text((x + 16, y + 8), f"{name.upper()} — CANDIDATE", font=label_font, fill=(35, 35, 35))
        draw.text((x + 16, y + 43), f"{source.width} × {source.height} source | review scaled", font=detail_font, fill=(90, 90, 90))
        thumbnail = source.copy()
        thumbnail.thumbnail((box_width, box_height), Image.Resampling.LANCZOS)
        sheet.paste(thumbnail, (x + (box_width - thumbnail.width) // 2, y + LABEL_HEIGHT + (box_height - thumbnail.height) // 2))

    for index, name in enumerate(TEXTURES[:3]):
        paste_review(name, index * (thumb_width + GAP), 0, thumb_width, thumb_width)
    paste_review("sky_backdrop", 0, lower_y, sheet_width, sky_height)
    output = folder / "review" / "all_textures.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(output.resolve())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Piece reference directory or flat-texture directory")
    for view in VIEWS:
        parser.add_argument(f"--rejected-{view}", help="Rejected candidate path, absolute or relative to folder")
    parser.add_argument("--tiling", action="store_true", help="Build exact unblended 2x2 flagstone check")
    parser.add_argument("--textures", action="store_true", help="Build compact flat-image contact sheet with labeled scaled previews")
    args = parser.parse_args()
    folder = args.folder.resolve()
    if args.tiling:
        build_tiling(folder)
    if args.textures:
        build_textures(folder)
    if not args.tiling and not args.textures:
        build_sheet(folder, VIEWS, {view: getattr(args, f"rejected_{view}") for view in VIEWS}, "all_views.png")


if __name__ == "__main__":
    main()
