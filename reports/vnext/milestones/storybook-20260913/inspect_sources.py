"""Record raw art and font provenance without modifying any image pixels."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
root = Path(__file__).resolve().parents[4]
source = root / "art-source/2d-expansion/r001"
records = json.loads((source / "generation_records.json").read_bytes())
rows = []
for row in records:
    path = root / row["selected_source"]
    raw = row.get("revision", {}).get("output", row["generator_output"]).split(" as ", 1)[1].split(" by default.", 1)[0]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as im:
        im.load()
        size, mode = list(im.size), im.mode
    assert digest == hashlib.sha256(Path(raw).read_bytes()).hexdigest()
    rows.append(dict(path=row["selected_source"], kind=row["kind"], id=row["id"], size=size, mode=mode,
                     bytes=path.stat().st_size, sha256=digest, raw_generator_output_unchanged=True))
relics = json.loads((source / "relics/manifest.json").read_bytes())
for path in sorted((source / "relics").glob("wc_vn_r_*.png")):
    with Image.open(path) as im:
        im.load()
        size, mode = list(im.size), im.mode
    rows.append(dict(path=path.relative_to(root).as_posix(), kind="relics", id=path.stem,
                     size=size, mode=mode, bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     detailed_provenance="relics/manifest.json"))
assert len(rows) == 23 and all(x["mode"] == "RGB" for x in rows)
fonts=[]
for path in sorted((root / "game/Content/WonderChess/UIFonts").iterdir()):
    fonts.append(dict(path=path.relative_to(root).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size))
report=dict(utc=datetime.now(timezone.utc).isoformat(),source_count=len(rows),sources=rows,fonts=fonts,
            font_source="https://github.com/NDISCOVER/Cinzel",font_license="SIL Open Font License 1.1, full notice staged alongside unmodified static font files",
            generation="Built-in image_gen only; no separately paid service or downloaded third-party paintings.",
            approval="Owner approved prior r15 slice and authorized expansion; this new candidate still awaits owner visual review.",
            boundary="Source decoding, opaque mode, file identity and full-size agent inspection. Native-size rendering and gameplay package checks are separate.")
(source / "source_inventory.json").write_text(json.dumps(report, indent=2))
print(json.dumps({"sources":len(rows),"rgb":all(x["mode"]=="RGB" for x in rows),"font_files":len(fonts),"bytes":sum(x["bytes"] for x in rows)}))
