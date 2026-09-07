"""Synthetic malformed-capture fixtures, not Unreal animation acceptance."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "tools/unreal/encode_engine_motion.py"
SPEC = importlib.util.spec_from_file_location("engine_encoder", SCRIPT)
encoder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(encoder)


def make_capture(root):
    directory = root / "wc_u_human_guardian" / "Move"
    directory.mkdir(parents=True)
    rows = []
    for index in range(21):
        name = f"frame-{index:05d}.png"
        Image.new("RGB", (64, 64), (index * 10, 50, 90)).save(directory / name)
        rows.append({"frame": index, "animation_seconds": (index * 0.05) % 1,
                     "wall_seconds": 100 + index * .07, "bytes": (directory / name).stat().st_size,
                     "file": name})
    write_rows(directory, rows)
    manifest = root / "engine-motion.json"
    manifest.write_text(json.dumps({"status": encoder.CAPTURED, "playback_fps": 20,
        "requested_clips": 1, "source_label": "SYNTHETIC_ENCODER_FIXTURE_NOT_UNREAL_EVIDENCE",
        "clips": [{"hero": "wc_u_human_guardian", "clip": "Move", "clip_seconds": 1,
                   "required_frames": 21, "captured_frames": 21, "frames_directory": str(directory),
                   "status": encoder.CAPTURED}]}), encoding="utf-8")
    return manifest, directory, rows


def write_rows(directory, rows):
    with (directory / "frames.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["frame", "animation_seconds", "wall_seconds", "bytes", "file"])
        writer.writeheader()
        writer.writerows(rows)


class MotionValidation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.manifest, self.directory, self.rows = make_capture(self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def reject_rows(self, text):
        write_rows(self.directory, self.rows)
        with self.assertRaisesRegex(ValueError, text):
            encoder.validate_capture(self.manifest)

    def test_complete_loop_covers_full_authored_timeline(self):
        clip = encoder.validate_capture(self.manifest)["clips"][0]
        self.assertEqual(clip["frame_count"], 21)
        self.assertEqual(clip["animation_wraps"], 1)
        self.assertAlmostEqual(clip["animation_advance_seconds"], 1)
        self.assertEqual(clip["encoded_duration_expected_seconds"], 1.05)

    def test_capture_one_step_after_reset_can_cover_full_loop(self):
        for index, row in enumerate(self.rows):
            row["animation_seconds"] = ((index + 1) * .05) % 1
        write_rows(self.directory, self.rows)
        self.assertAlmostEqual(encoder.validate_capture(self.manifest)["clips"][0]["animation_advance_seconds"], 1)

    def test_missing_png_rejected(self):
        (self.directory / "frame-00007.png").unlink()
        with self.assertRaisesRegex(ValueError, "Missing or extra PNG"):
            encoder.validate_capture(self.manifest)

    def test_actual_unreal_float_duration_count_and_timeline(self):
        # Exact duration/timestamps from retained Pippa Unreal Hit pilot 20260906T161205Z.
        duration = 0.40000000596046448
        times = [.050000001, .100000001, .150000006, .200000003, .250000000,
                 .300000012, .350000024, .000000030, .050000031]
        for row in self.rows[9:]:
            (self.directory / row["file"]).unlink()
        self.rows = self.rows[:9]
        for row, time in zip(self.rows, times):
            row["animation_seconds"] = time
        write_rows(self.directory, self.rows)
        data = json.loads(self.manifest.read_text())
        data["clips"][0].update(clip_seconds=duration, required_frames=9, captured_frames=9)
        self.manifest.write_text(json.dumps(data))
        actual = encoder.validate_capture(self.manifest)["clips"][0]
        self.assertEqual(actual["frame_count"], 9)
        self.assertGreaterEqual(actual["animation_advance_seconds"], duration)
        self.rows[-1]["animation_seconds"] = self.rows[-2]["animation_seconds"]
        self.reject_rows("paused")

    def test_missing_csv_frame_rejected(self):
        self.rows.pop(7)
        self.reject_rows("Missing or extra CSV")

    def test_numbering_rejected(self):
        self.rows[7]["frame"] = 8
        self.reject_rows("numbering")

    def test_paused_animation_rejected(self):
        for row in self.rows:
            row["animation_seconds"] = 0
        self.reject_rows("paused")

    def test_halfspeed_rejected(self):
        for index, row in enumerate(self.rows):
            row["animation_seconds"] = index * .025
        self.reject_rows("unexpected rate")

    def test_time_jump_rejected(self):
        self.rows[7]["animation_seconds"] = .45
        self.reject_rows("jumps")

    def test_repeated_wall_timestamp_rejected(self):
        self.rows[7]["wall_seconds"] = self.rows[6]["wall_seconds"]
        self.reject_rows("Wall timestamps")

    def test_png_byte_mismatch_rejected(self):
        self.rows[7]["bytes"] = 1
        self.reject_rows("byte count")

    def test_changed_dimensions_rejected(self):
        png = self.directory / "frame-00007.png"
        Image.new("RGB", (66, 64), (90, 0, 0)).save(png)
        self.rows[7]["bytes"] = png.stat().st_size
        self.reject_rows("dimensions change")

    def test_partial_capture_rejected(self):
        data = json.loads(self.manifest.read_text())
        data["status"] = "RECORDING"
        self.manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "not completed"):
            encoder.validate_capture(self.manifest)

    def test_existing_output_rejected_without_mutation(self):
        output = self.root / "old-output"
        output.mkdir()
        retained = output / "retained.txt"
        retained.write_text("retained failed evidence")
        with self.assertRaisesRegex(ValueError, "reuse"):
            encoder.run(self.manifest, output, self.root / "no-blender.exe")
        self.assertEqual(retained.read_text(), "retained failed evidence")
        self.assertEqual(list(output.iterdir()), [retained])


if __name__ == "__main__":
    unittest.main()
