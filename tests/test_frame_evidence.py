"""Synthetic reader checks; these never count as game or performance evidence."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('frame_reader', Path(__file__).parent / 'runtime/summarize_frame_evidence.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class FrameEvidenceTests(unittest.TestCase):
    def summarize(self, values):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            session = root / 'session.json'
            session.write_text(json.dumps({'match_namespace': 1, 'seat': 0, 'process_id': 123,
                                           'resolution_x': 1920, 'resolution_y': 1080}))
            with (root / 'match-1-seat-0-pid-123-frames.csv').open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=values[0].keys())
                writer.writeheader()
                writer.writerows(values)
            return reader.summarize(session)

    def test_neutral_load_requires_eight_unfinished_encounters_and_visible_count_is_separate(self):
        base = dict(phase=1, round=15, visible_alive=11, encounters=8, frame_ms=17,
                    game_ms=4, render_ms=3, gpu_ms=0, gpu_available=0,
                    neutral_round=1, neutral_live_encounters=8)
        result = self.summarize([base, {**base, 'visible_alive': 12, 'neutral_live_encounters': 7},
                                 {**base, 'phase': 0, 'visible_alive': 12}])
        self.assertEqual(result['subsets']['eight_live_neutral_encounters']['frames'], 1)
        self.assertEqual(result['subsets']['twelve_visible_and_eight_live_neutral_encounters']['frames'], 0)
        self.assertEqual(result['subsets']['eight_live_neutral_encounters']['gpu_ms']['status'], 'NOT_RUN')

    def test_old_frames_do_not_inherit_neutral_coverage_from_calendar_round(self):
        result = self.summarize([dict(phase=1, round=15, visible_alive=12, encounters=8,
                                     frame_ms=17, game_ms=4, render_ms=3, gpu_ms=0, gpu_available=0)])
        self.assertFalse(result['neutral_instrumentation_available'])
        self.assertEqual(result['eight_neutral_encounters_status'], 'NOT_RUN')
