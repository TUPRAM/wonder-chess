"""Validate and encode actual Unreal 20 Hz PNG captures, without claiming review."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


CAPTURED = "CAPTURED_REVIEW_PENDING"
FPS = 20


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value, label):
    value = float(value)
    require(math.isfinite(value), f"Non-finite {label}")
    return value


def validate_capture(path):
    """Inspect immutable capture bytes; permit a real loop, reject a paused clock."""
    from PIL import Image

    path = Path(path).resolve(strict=True)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    require(data.get("status") == CAPTURED, "Capture has not completed successfully")
    require(data.get("playback_fps") == FPS, "Only recorded 20 Hz capture is supported")
    clips = data.get("clips", [])
    require(clips and data.get("requested_clips") == len(clips), "Incomplete clip inventory")
    result, seen = [], set()
    for clip in clips:
        hero, name = clip.get("hero", ""), clip.get("clip", "")
        require(re.fullmatch(r"wc_u_[a-z0-9_]+", hero), "Invalid hero identity")
        require(name in {"Idle", "Move", "Attack", "Active", "Hit", "Defeat", "Victory"}, "Invalid clip")
        require((hero, name) not in seen, "Duplicate clip identity")
        seen.add((hero, name))
        require(clip.get("status") == CAPTURED, f"Incomplete capture {hero}/{name}")
        seconds = finite(clip["clip_seconds"], "clip duration")
        require(seconds >= 1 / FPS, "Clip shorter than one capture interval cannot prove advance")
        count = clip["required_frames"]
        # Unreal's FMath float conversion can round e.g. 8.000000119 frames to 8.
        # This only tolerates representation noise; the CSV must independently
        # demonstrate the complete duration below.
        require(type(count) is int and count == math.ceil(seconds * FPS - 0.00001) + 1,
                "Required frame count does not cover the authored clip")
        require(clip.get("captured_frames") == count, "Captured frame count differs")
        directory = Path(clip["frames_directory"]).resolve(strict=True)
        require(directory.is_relative_to(path.parent), "Frame directory escapes capture root")
        csv_path = directory / "frames.csv"
        with csv_path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            require(reader.fieldnames == ["frame", "animation_seconds", "wall_seconds", "bytes", "file"],
                    "Unexpected frame CSV columns")
            rows = list(reader)
        require(len(rows) == count, "Missing or extra CSV frame")
        expected_names = {f"frame-{index:05d}.png" for index in range(count)}
        require({p.name for p in directory.glob("*.png")} == expected_names,
                "Missing or extra PNG frame")
        frames, dimensions, previous, previous_wall = [], None, None, None
        advance, wraps, end_clamps = 0.0, 0, 0
        epsilon = 0.0001
        for index, row in enumerate(rows):
            require(row["frame"] == str(index) and row["file"] == f"frame-{index:05d}.png",
                    "Frame numbering or filename is discontinuous")
            image_path = (directory / row["file"]).resolve(strict=True)
            require(image_path.parent == directory, "Image resolves outside frame directory")
            size = image_path.stat().st_size
            require(size > 0 and int(row["bytes"]) == size, "PNG byte count differs from capture")
            with Image.open(image_path) as image:
                require(image.format == "PNG", "Frame is not PNG")
                current_dimensions = list(image.size)
                image.verify()
            with Image.open(image_path) as image:
                image.load()  # Decode pixels too; IHDR alone is not image integrity.
            if dimensions is None:
                dimensions = current_dimensions
                require(all(n > 0 and n % 2 == 0 for n in dimensions), "H.264 needs positive even dimensions")
            require(dimensions == current_dimensions, "Frame dimensions change within a clip")
            time = finite(row["animation_seconds"], "animation time")
            wall = finite(row["wall_seconds"], "wall time")
            require(-epsilon <= time <= seconds + epsilon, "Animation time is out of clip bounds")
            if previous is None:
                require(time <= 1 / FPS + epsilon, "Capture misses the beginning of the clip")
            else:
                require(wall > previous_wall, "Wall timestamps do not advance")
                delta = time - previous
                if delta < -epsilon:
                    wraps += 1
                    delta += seconds
                if abs(delta) <= epsilon:
                    require(time >= seconds - epsilon and advance >= seconds - 1 / FPS - epsilon,
                            "Animation timeline is paused")
                    end_clamps += 1
                    require(end_clamps <= 1, "Animation remains clamped for multiple frames")
                else:
                    require(0 < delta <= 1 / FPS + epsilon, "Animation jumps beyond a 20 Hz step")
                    # A clamped last sample may be shorter; looping samples retain the full step.
                    require(abs(delta - 1 / FPS) <= epsilon or time >= seconds - epsilon,
                            "Animation advances at an unexpected rate")
                advance += max(0, delta)
            frames.append({"frame": index, "path": str(image_path), "bytes": size,
                           "sha256": sha256(image_path), "animation_seconds": time,
                           "wall_seconds": wall})
            previous, previous_wall = time, wall
        require(wraps <= 1, "More than one animation cycle was captured")
        require(advance >= seconds - epsilon, "Recorded animation does not advance through a full clip")
        result.append({"hero": hero, "clip": name, "clip_seconds": seconds,
                       "frames_directory": str(directory), "csv_sha256": sha256(csv_path),
                       "frame_count": count, "dimensions": dimensions, "fps": FPS,
                       "animation_advance_seconds": advance, "animation_wraps": wraps,
                       "encoded_duration_expected_seconds": count / FPS,
                       "endpoint_frame_included": True, "frames": frames})
    return {"capture_path": str(path), "capture_sha256": sha256(path),
            "capture_method": data.get("method"), "source_label": data.get("source_label", "Not supplied"),
            "content_digest": data.get("content_digest"), "clips": result}


def encode_worker(job_path):
    import bpy

    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    output = Path(job["output"])
    reports = []
    for clip in job["capture"]["clips"]:
        scene = bpy.data.scenes.new(f"{clip['hero']}-{clip['clip']}")
        bpy.context.window.scene = scene
        editor = scene.sequence_editor_create()
        first = Path(clip["frames"][0]["path"])
        strip = editor.strips.new_image("ActualUnrealFrames", str(first), channel=1, frame_start=1)
        for frame in clip["frames"][1:]:
            strip.elements.append(Path(frame["path"]).name)
        strip.frame_final_duration = clip["frame_count"]
        scene.render.resolution_x, scene.render.resolution_y = clip["dimensions"]
        scene.render.resolution_percentage = 100
        scene.render.fps = FPS
        scene.render.fps_base = 1.0
        scene.frame_start, scene.frame_end = 1, clip["frame_count"]
        scene.render.use_sequencer = True
        scene.sequencer_colorspace_settings.name = "sRGB"
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0
        scene.view_settings.gamma = 1
        scene.render.image_settings.media_type = "VIDEO"
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.image_settings.color_mode = "RGB"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.constant_rate_factor = "HIGH"
        movie_path = output / f"{clip['hero']}-{clip['clip']}.mp4"
        require(not movie_path.exists(), "Refusing to overwrite movie")
        scene.render.filepath = str(movie_path)
        bpy.ops.render.render(animation=True, scene=scene.name)
        require(movie_path.is_file() and movie_path.stat().st_size > 0, "Encoder produced no movie")
        movie = bpy.data.movieclips.load(str(movie_path), check_existing=False)
        actual = {"hero": clip["hero"], "clip": clip["clip"], "file": str(movie_path),
                  "bytes": movie_path.stat().st_size, "sha256": sha256(movie_path),
                  "frame_count": movie.frame_duration, "fps": movie.fps,
                  "dimensions": list(movie.size), "duration_seconds": movie.frame_duration / movie.fps}
        require(actual["frame_count"] == clip["frame_count"], "Encoded movie frame count differs")
        require(abs(actual["fps"] - FPS) < 0.0001, "Encoded movie fps differs")
        require(actual["dimensions"] == clip["dimensions"], "Encoded movie dimensions differ")
        require(abs(actual["duration_seconds"] - clip["frame_count"] / FPS) < 0.0001,
                "Encoded duration differs")
        bpy.data.movieclips.remove(movie)
        reports.append(actual)
    (output / "encoder-readback.json").write_text(json.dumps({"blender_version": bpy.app.version_string,
        "method": "Blender VSE actual PNG sequence and movieclip metadata readback", "clips": reports}, indent=2), encoding="utf-8")


def run(capture_path, output, blender):
    output = Path(output).resolve()
    require(not output.exists(), "Refusing to reuse an existing output path")
    output.mkdir(parents=True)
    report = {"status": "STARTED", "started_utc": datetime.now(timezone.utc).isoformat(),
              "visual_continuous_review": "NOT_RUN", "audio_review": "NOT_RUN",
              "performance_acceptance": "NOT_RUN", "encoding_only": True,
              "script_sha256": sha256(__file__)}
    try:
        capture = validate_capture(capture_path)
        blender = Path(blender).resolve(strict=True)
        report.update({"capture": capture, "blender": str(blender), "blender_sha256": sha256(blender)})
        job = output / "encoding-job.json"
        job.write_text(json.dumps({"capture": capture, "output": str(output)}, indent=2), encoding="utf-8")
        command = [str(blender), "--background", "--factory-startup", "--python-exit-code", "2",
                   "--python", str(Path(__file__).resolve()), "--", "--worker", str(job)]
        report["command"] = command
        with (output / "blender-encode.log").open("w", encoding="utf-8") as log:
            process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        report["encoder_exit_code"] = process.returncode
        require(process.returncode == 0, "Blender encoder failed; inspect retained blender-encode.log")
        readback = json.loads((output / "encoder-readback.json").read_text(encoding="utf-8"))
        require(len(readback["clips"]) == len(capture["clips"]), "Incomplete movie readback")
        # Re-read the source after encoding to detect any capture mutation.
        require(validate_capture(capture_path) == capture, "Capture bytes changed during encoding")
        report["encoded"] = readback
        report["source_bytes_unchanged"] = True
        report["status"] = "ENCODING_PASS_REVIEW_PENDING"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = f"{type(error).__name__}: {error}"
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (output / "encoding-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if arguments and arguments[0] == "--worker":
        encode_worker(arguments[1])
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="Completed engine-motion.json")
    parser.add_argument("--output", type=Path, required=True, help="Fresh output directory; never reused")
    parser.add_argument("--blender", type=Path, required=True, help="Actual installed Blender executable")
    args = parser.parse_args(arguments)
    try:
        result = run(args.capture, args.output, args.blender)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps({key: result[key] for key in ("status", "encoding_only", "visual_continuous_review")}))
    return 0 if result["status"] == "ENCODING_PASS_REVIEW_PENDING" else 1


if __name__ == "__main__":
    raise SystemExit(main())
