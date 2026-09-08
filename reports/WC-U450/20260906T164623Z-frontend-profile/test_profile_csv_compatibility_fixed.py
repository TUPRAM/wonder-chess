import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(r'C:\Users\iputu\Documents\Wonder Chess')
spec = importlib.util.spec_from_file_location('frame_reader', ROOT / 'tests/runtime/summarize_frame_evidence.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

class ProfileColumnCompatibility(unittest.TestCase):
    def test_additive_frame_counter_preserves_page_metrics_and_gpu_absence(self):
        with tempfile.TemporaryDirectory(prefix='wc-profile-csv-') as directory:
            root = Path(directory)
            session = root / 'session.json'
            session.write_text(json.dumps({'match_namespace': 0, 'seat': 0, 'process_id': 321,
                'simulation_speed_multiplier': 1, 'resolution_x': 1280, 'resolution_y': 720}))
            (root/'launch.json').write_text(json.dumps({'arguments':['-WCProfile','-WCFrontEndProfile'],
                'boundary':'Synthetic column compatibility fixture; no game was launched'}))
            rows=[]
            for index, page in enumerate(('lobby','gallery','detail')):
                rows.append(dict(wall_seconds=10+index, phase=-1, round=0, visible_alive=0, logical_alive=0,
                    encounters=0, frame_ms=16+index, game_ms=4, render_ms=3, gpu_ms=0, gpu_available=0,
                    public_chars=100, public_utf8_bytes=100, neutral_round=0, neutral_live_encounters=0,
                    frontend_page=page, frame_counter=10000+index))
            with (root/'match-0-seat-0-pid-321-frames.csv').open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=rows[0])
                writer.writeheader(); writer.writerows(rows)
            result=reader.summarize(session)
            self.assertEqual(result['subsets']['all_profiled_frames']['frame_ms']['samples'],3)
            self.assertEqual(result['subsets']['lobby_frames']['frames'],1)
            self.assertEqual(result['subsets']['gallery_list_frames']['frames'],1)
            self.assertEqual(result['subsets']['hero_detail_frames']['frames'],1)
            self.assertEqual(result['subsets']['all_profiled_frames']['gpu_ms']['status'],'NOT_RUN')
            self.assertEqual(result['subsets']['eight_live_neutral_encounters']['frames'],0)
            self.assertEqual(result['instrumentation']['capture_flags'],[])

if __name__ == '__main__': unittest.main(verbosity=2)

