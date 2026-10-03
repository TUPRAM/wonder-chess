"""Make the catalogue site's web-sized brand images from the owner's logo sources."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "art-source/asset-studio/wc_brand_logo/inputs/references/icon_r001"
TARGET = ROOT / "web/catalogue/brand"
# output name: (source file, longest side in pixels)
OUTPUTS = {"icon.png": ("wonder-chess-icon.png", 96), "favicon.png": ("wonder-chess-icon.png", 64),
           "touch-icon.png": ("wonder-chess-icon.png", 180), "logo.png": ("source-logo.png", 720)}

SQUARE = {"favicon.png", "touch-icon.png"}


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    for name, (source, longest) in OUTPUTS.items():
        with Image.open(SOURCE / source) as image:
            # Trim the empty transparent margin so the mark fills its box.
            image = image.convert("RGBA")
            image = image.crop(image.getbbox())
            image.thumbnail((longest, longest), Image.LANCZOS)
            if name in SQUARE:
                # Browsers expect square tab icons; centre the mark on a transparent square.
                square = Image.new("RGBA", (longest, longest), (0, 0, 0, 0))
                square.paste(image, ((longest - image.width) // 2, (longest - image.height) // 2))
                image = square
            image.save(TARGET / name, optimize=True)
            if name == "favicon.png":
                # Served from the site root because browsers request /favicon.ico by default.
                image.save(TARGET.parent / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
            print(f"{name}: {image.width}x{image.height}")


if __name__ == "__main__":
    main()
