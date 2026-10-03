"""Package existing GPT Image outputs; resize only to owner-specified export dimensions."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / "support/generation_record.json").read_text(encoding="utf-8"))
REPO = ROOT.parents[2]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def image_info(path):
    with Image.open(path) as im:
        return {"dimensions": list(im.size), "format": im.format, "sha256": sha(path)}

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

summaries = {}
for piece, result in PLAN["results"].items():
    folder = ROOT / "inputs" / ("textures_r001" if piece == "textures" else "references/" + piece + "_r001")
    records = [dict(rec) for rec in PLAN["records"] if rec["piece"] == piece]
    targets = list(PLAN["texture_export_sizes"]) if piece == "textures" else ["main.png", "left.png", "back.png", "right.png"]
    counts = {name: sum(rec["file"] == name for rec in records) for name in targets}
    selected = {}
    for rec in records:
        source = Path(rec["source_file"])
        saved = Path(rec["saved_file"])
        assert source.is_file() and saved.is_file(), (piece, rec["file"])
        rec["source_image"] = image_info(source)
        rec["tool"] = "image_gen.imagegen"
        rec["transparent_background"] = False
        rec["prompt_note"] = "Exact submitted prompt; tool-internal rewritten prompt, if any, was not exposed."
        rec["hash_note"] = "File hashes computed during packaging on the recorded date."
        rec["reference_hashes"] = {ref: sha(ref) for ref in rec["reference_files"]}
        if piece == "textures" and rec["disposition"] == "candidate":
            native = folder / "native_sources" / (Path(rec["file"]).stem + "_attempt" + str(rec["attempt"]).zfill(2) + ".png")
            native.parent.mkdir(exist_ok=True)
            if not native.exists():
                shutil.copy2(source, native)
            size = tuple(PLAN["texture_export_sizes"][rec["file"]])
            with Image.open(source) as im:
                assert im.width * size[1] == im.height * size[0], "No aspect-ratio distortion permitted"
                if im.size != size:
                    im.resize(size, Image.Resampling.LANCZOS).save(saved, format="PNG")
                else:
                    shutil.copy2(source, saved)
            rec["export"] = {
                "operation": "Uniform LANCZOS resize to explicitly requested delivery dimensions; no crop, repaint, mirror, content or color edit",
                "native_source_preserved": str(native),
                "native_dimensions": rec["source_image"]["dimensions"],
                "delivered_dimensions": list(size),
                "native_generation_at_delivered_resolution": rec["source_image"]["dimensions"] == list(size),
            }
        rec["saved_image"] = image_info(saved)
        if rec["disposition"] == "candidate":
            selected[rec["file"]] = {"path": str(saved), "selected_attempt": rec["attempt"], **rec["saved_image"]}
    for entry in selected.values():
        assert entry["format"] == "PNG"
    if piece != "textures" and len(selected) == 4:
        dims = {tuple(entry["dimensions"]) for entry in selected.values()}
        assert len(dims) == 1
        width, height = dims.pop()
        assert width == height and width >= 1024
    provenance = {
        "schema": "wonder-chess.courtyard-reference-provenance.v1",
        "date": PLAN["date"], "timezone": PLAN["timezone"],
        "image_model": "GPT Image via built-in image_gen",
        "exact_model_version": None,
        "model_version_note": "The tool did not expose a precise model version, seed or API settings. None invented.",
        "approval_status": "not_approved",
        "status": result["status"],
        "brief": {"path": "production/environment/courtyard/BRIEFS.md", "sha256": sha(REPO / "production/environment/courtyard/BRIEFS.md")},
        "attempts_per_file": counts,
        "selected_files": selected,
        "not_generated": [name for name, count in counts.items() if count == 0],
        "best_rejected": result.get("best_rejected", {}),
        "remaining_visible_defects": result["remaining_visible_defects"],
        "files": records,
        "review_derivatives": [],
    }
    reviews = sorted((folder / "review").glob("*.png"))
    for review in reviews:
        references = ([str(folder / "flagstone_tile.png")] * 4 if review.name == "flagstone_tiling_check.png"
                      else [str(folder / name) for name in targets if (folder / name).exists()])
        if piece != "textures":
            references += [str(folder / name) for name in result.get("best_rejected", {}).values()]
        provenance["review_derivatives"].append({
            "path": str(review),
            "prompt": None,
            "method": "Deterministic assembly of source images without blending or source alteration; labels outside images for four-view sheets",
            "script": str(ROOT / "support/build_reviews.py"),
            "source_files": references,
            **image_info(review),
        })
    write_json(folder / "provenance.json", provenance)
    summaries[piece] = {"status": result["status"], "attempts": counts, "saved": selected,
                        "best_rejected": result.get("best_rejected", {}),
                        "remaining_visible_defects": result["remaining_visible_defects"],
                        "provenance": str(folder / "provenance.json")}

textures = ROOT / "inputs/textures_r001"
lumas = {}
for name in ["board_tile_light.png", "board_tile_dark.png"]:
    with Image.open(textures / name) as im:
        lumas[name] = round(ImageStat.Stat(im.convert("L")).mean[0], 2)
assert lumas["board_tile_light.png"] > lumas["board_tile_dark.png"] + 40
summary = {"date": PLAN["date"], "approval_status": "not_approved",
           "total_generation_attempts": len(PLAN["records"]),
           "pieces": summaries, "board_grayscale_mean_0_255": lumas,
           "scope": "2D reference and flat images only. No 3D generation, upload or engine integration."}
write_json(ROOT / "generation_summary.json", summary)
asset = json.loads((ROOT / "asset.json").read_text())
asset.update(status="generation_finished_with_two_stopped_pieces", approval_status="not_approved",
             result_summary="Four complete four-view candidates; wall section and yard props stopped at failed-view limits; four flat images exported.")
write_json(ROOT / "asset.json", asset)
print(json.dumps({"total_attempts": len(PLAN["records"]), "pieces": {p: {"status": s["status"], "attempts": s["attempts"], "files": list(s["saved"])} for p, s in summaries.items()}}, indent=2))
