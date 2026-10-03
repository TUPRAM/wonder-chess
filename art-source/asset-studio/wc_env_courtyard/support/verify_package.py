"""Read-only checks on the generated courtyard package."""
from pathlib import Path
import hashlib, json
from PIL import Image
root = Path(__file__).resolve().parents[1]
summary = json.loads((root / "generation_summary.json").read_text())
total = 0
for piece, info in summary["pieces"].items():
    provenance = json.loads(Path(info["provenance"]).read_text())
    assert provenance["approval_status"] == "not_approved"
    assert provenance["status"] != "working"
    for record in provenance["files"]:
        total += 1
        file = Path(record["saved_file"])
        assert file.is_file()
        assert hashlib.sha256(file.read_bytes()).hexdigest() == record["saved_image"]["sha256"]
        assert all(Path(ref).is_file() for ref in record["reference_files"])
        assert record["prompt"] and record["attempt"] >= 1
    for review in provenance["review_derivatives"]:
        path = Path(review["path"])
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == review["sha256"]
    if piece != "textures":
        assert len(provenance["review_derivatives"]) == 1
        assert all(v <= 3 for v in provenance["attempts_per_file"].values())
assert total == summary["total_generation_attempts"] == 38
textures = root / "inputs/textures_r001"
for name, expected in {"flagstone_tile.png": (2048,2048), "board_tile_light.png": (1024,1024),
                       "board_tile_dark.png": (1024,1024), "sky_backdrop.png": (2048,1024)}.items():
    with Image.open(textures / name) as image:
        assert image.size == expected and image.format == "PNG"
with Image.open(textures / "review/flagstone_tiling_check.png") as sheet:
    with Image.open(textures / "flagstone_tile.png") as tile:
        assert sheet.size == (4096,4096)
        for x in [0,2048]:
            for y in [0,2048]:
                assert sheet.crop((x,y,x+2048,y+2048)).tobytes() == tile.convert("RGB").tobytes()
print("Verified: 38 attempt records; image/reference paths; hashes; six piece reviews; exact flat dimensions; exact unblended final 2x2; all not approved.")
print("Board grayscale means:", summary["board_grayscale_mean_0_255"])

