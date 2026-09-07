"""Cold-read imported audio, then run the owned glyph reimport in this commandlet."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import wave
import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
records = []
for source in sorted((root / "exports/audio").glob("*.wav")):
    asset_path = "/Game/WonderChess/Audio/" + source.stem
    asset = unreal.load_asset(asset_path)
    if not isinstance(asset, unreal.SoundWave):
        raise RuntimeError("Missing imported SoundWave: " + asset_path)
    with wave.open(str(source), "rb") as stream:
        expected = stream.getnframes() / stream.getframerate()
    duration = float(asset.get_editor_property("duration"))
    channels = int(asset.get_editor_property("num_channels"))
    compression = asset.get_sound_asset_compression_type()
    if abs(duration - expected) > .001 or channels != 1 or compression != unreal.SoundAssetCompressionType.PCM:
        raise RuntimeError("Imported audio does not match source PCM: " + asset_path)
    uasset = root / "game/Content/WonderChess/Audio" / (source.stem + ".uasset")
    records.append({"asset": asset_path, "duration_seconds": duration,
                    "source_duration_seconds": expected, "channels": channels,
                    "compression": str(compression),
                    "uasset_sha256": hashlib.sha256(uasset.read_bytes()).hexdigest()})
if len(records) != 32:
    raise RuntimeError("Expected all 32 current sounds, found " + str(len(records)))
report = {"status": "COLD_ASSET_READ_PASS", "engine": unreal.SystemLibrary.get_engine_version(),
          "count": len(records), "records": records,
          "boundary": "SoundWave cold load, PCM type, channels and duration; playback listening remains separate."}
(root / "reports/WC-350/hero-audio-import-cold.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
unreal.log("WC_AUDIO_COLD_PASS 32 SoundWaves PCM mono exact source durations")
os.environ["WC_EFFECT_REPORT"] = "effect-import-uv2.json"
runpy.run_path(str(root / "tools/unreal/import_effect_assets.py"), run_name="__main__")
