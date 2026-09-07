"""Synthetic frame/marker joins, never actual gameplay or performance evidence."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

RUNTIME = Path(__file__).parent / 'runtime'
sys.path.insert(0, str(RUNTIME))
from summarize_frontend_profile import analyze


class FrontendProfileEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.session = self.root / 'session.json'
        self.profile_path = self.root / 'frontend-profile.json'
        self.csv_path = self.root / 'match-0-seat-0-pid-123-frames.csv'
        self.marker_path = self.root / 'frontend-profile-markers.jsonl'
        self.session.write_text(json.dumps({'match_namespace': 0, 'seat': 0, 'process_id': 123, 'rhi': 'D3D11'}))
        self.profile = {'pid': 123, 'frame_csv': str(self.csv_path), 'markers_jsonl': str(self.marker_path),
                        'status': 'FAIL', 'failure': 'Synthetic partial run', 'completed_stages': 1,
                        'content_digest': 'fixture', 'protocol_version': 6}
        self.rows, self.markers = [], []
        self.add_stage(0, 'fixture-hero', 'Idle', 'first_detail_presentation')

    def add_stage(self, index, hero, clip, visit, page='detail'):
        offset = index * 10
        for number in range(1, 11):
            self.rows.append(dict(frame_counter=offset + number, wall_seconds=offset + number,
                                  phase=-1, visible_alive=0, encounters=0, frontend_page=page,
                                  frame_ms={2: 120, 4: 250}.get(number, 17), game_ms=3, render_ms=2,
                                  gpu_ms=0, gpu_available=0))
        identity = {'stage_index': index, 'stage': 'stage-' + str(index), 'frontend_page': page,
                    'hero_id': hero, 'clip': clip, 'visit': visit, 'requested_dwell_seconds': 3}
        for event, frame in [('action_begin', 1), ('action_return', 1), ('measure_begin', 3), ('measure_end', 7)]:
            self.markers.append(identity | {'event': event, 'frame_counter': offset + frame,
                                           'wall_seconds': offset + frame, 'actual_frontend_page': page})

    def read(self):
        self.profile_path.write_text(json.dumps(self.profile))
        self.marker_path.write_text(''.join(json.dumps(marker) + '\n' for marker in self.markers))
        with self.csv_path.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=self.rows[0].keys())
            writer.writeheader()
            writer.writerows(self.rows)
        return analyze(self.profile_path, self.session)

    def test_keeps_navigation_and_boundary_hitches_without_polluting_steady_dwell(self):
        report = self.read()
        self.assertEqual(report['status'], 'OBSERVED_PARTIAL_ROUTE')
        self.assertEqual(report['all_settled_frames']['frames'], 3)
        self.assertEqual(report['all_settled_frames']['frame_ms']['max_ms'], 17)
        self.assertEqual(report['all_navigation_and_settling']['frame_ms']['max_ms'], 120)
        self.assertEqual(report['all_first_post_marker']['frame_ms']['max_ms'], 250)
        self.assertEqual(report['all_recorded_frames']['frame_ms']['frames_over_100ms'], 2)
        self.assertEqual(report['all_settled_frames']['gpu_ms']['status'], 'NOT_RUN')
        self.assertEqual(report['unassigned_startup_partial_or_tail']['frames'], 4)

    def test_rejects_cross_process_or_cross_csv_binding(self):
        self.profile['pid'] = 999
        with self.assertRaisesRegex(ValueError, 'same namespace-zero process'):
            self.read()
        self.profile['pid'] = 123
        self.profile['frame_csv'] = str(self.root / 'other.csv')
        with self.assertRaisesRegex(ValueError, 'CSV identity'):
            self.read()

    def test_rejects_actual_page_change_in_steady_interval(self):
        self.rows[5]['frontend_page'] = 'lobby'
        with self.assertRaisesRegex(ValueError, 'another page'):
            self.read()

    def test_rejects_duplicate_frames_and_stage_markers(self):
        self.rows[5]['frame_counter'] = self.rows[4]['frame_counter']
        with self.assertRaisesRegex(ValueError, 'Duplicate or backwards'):
            self.read()
        self.rows[5]['frame_counter'] = 6
        self.markers.insert(1, self.markers[0])
        with self.assertRaisesRegex(ValueError, 'Duplicate stage marker'):
            self.read()

    def test_rejects_short_dwell_and_completed_count_mismatch(self):
        for marker in self.markers:
            marker['requested_dwell_seconds'] = 10
        with self.assertRaisesRegex(ValueError, 'shorter'):
            self.read()
        for marker in self.markers:
            marker['requested_dwell_seconds'] = 3
        self.profile['completed_stages'] = 2
        with self.assertRaisesRegex(ValueError, 'Completed profile count'):
            self.read()

    def test_full_route_requires_each_of_24_heroes_both_clips_and_both_visits(self):
        self.rows.clear()
        self.markers.clear()
        index = 0
        for visit in ('first_detail_presentation', 'warm_revisit'):
            for hero in range(24):
                for clip in ('Idle', 'Active'):
                    self.add_stage(index, 'hero-' + str(hero), clip, visit)
                    index += 1
        for page in ('lobby', 'gallery', 'lobby', 'gallery', 'lobby', 'gallery', 'lobby'):
            self.add_stage(index, 'hero-0', 'Idle', 'warm_revisit', page)
            index += 1
        self.profile.update(status='PASS_ROUTE_EXECUTION_ONLY', completed_stages=103, expected_stages=103)
        report = self.read()
        self.assertEqual(report['status'], 'OBSERVED_COMPLETE_ROUTE')
        self.assertTrue(report['complete_24_hero_idle_active_twice'])
        for marker in self.markers:
            if marker['hero_id'] == 'hero-23':
                marker['hero_id'] = 'hero-22'
        report = self.read()
        self.assertEqual(report['status'], 'OBSERVED_PARTIAL_ROUTE')


if __name__ == '__main__':
    unittest.main()
