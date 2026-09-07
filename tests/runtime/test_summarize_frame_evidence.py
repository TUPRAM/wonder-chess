"""Focused CSV/JSON fixtures; these tests never launch or certify a game."""
import csv
import json
from pathlib import Path
import tempfile
import unittest

from summarize_frame_evidence import metrics, summarize


class FrameEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='wc-frame-fixture-')
        self.directory = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)

    def write(self, rows, namespace=1, legacy=False, rhi='D3D11', arguments=None):
        session = {'match_namespace': namespace, 'seat': 0, 'process_id': 123,
                   'cpu': 'Fixture CPU', 'active_rhi_adapter': 'Fixture GPU', 'rhi': rhi,
                   'resolution_x': 1920, 'resolution_y': 1080, 'simulation_speed_multiplier': 1}
        path = self.directory / 'session.json'
        path.write_text(json.dumps(session))
        (self.directory / 'launch.json').write_text(json.dumps({'arguments': arguments if arguments is not None else ['-WCProfile'],
                                                               'boundary': 'Synthetic file fixture only'}))
        columns = ['wall_seconds', 'phase', 'round', 'visible_alive', 'logical_alive', 'encounters',
                   'frame_ms', 'game_ms', 'render_ms', 'gpu_ms', 'gpu_available', 'public_chars', 'public_utf8_bytes']
        if not legacy:
            columns += ['neutral_round', 'neutral_live_encounters', 'frontend_page']
        base = {'wall_seconds': 1, 'phase': 1, 'round': 1, 'visible_alive': 12, 'logical_alive': 24, 'encounters': 4,
                'frame_ms': 16, 'game_ms': 3, 'render_ms': 2, 'gpu_ms': 5, 'gpu_available': 1,
                'public_chars': 10, 'public_utf8_bytes': 10, 'neutral_round': 0,
                'neutral_live_encounters': 0, 'frontend_page': 'closed'}
        with (self.directory / f'match-{namespace}-seat-0-pid-123-frames.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            writer.writerows({**base, **row} for row in rows)
        return path

    def test_percentiles_hitches_and_empty_metrics(self):
        value = metrics(list(range(100, 0, -1)))
        self.assertEqual((value['p50_ms'], value['p95_ms'], value['p99_ms']), (50, 95, 99))
        self.assertEqual(value['frames_over_33_33ms'], 67)
        self.assertEqual(value['frames_over_100ms'], 0)
        self.assertEqual(metrics([100, 101])['frames_over_100ms'], 1)
        self.assertIsNone(metrics([])['p95_ms'])

    def test_windows_command_line_string_preserves_paths_and_detects_instrumentation(self):
        import subprocess
        arguments = [r'C:\Project With Spaces\WonderChess.uproject', '-game', '-WCProfile',
                     '-WCFrontEndAudit', '-WCFrontEndAllHeroes', r'-WCEvidenceDir=C:\Reports With Spaces\trial',
                     r'-Label=escaped"quote', '-NullRHI']
        result = summarize(self.write([{}], arguments=subprocess.list2cmdline(arguments)))
        self.assertEqual(result['instrumentation']['launch_arguments'], arguments)
        self.assertTrue(result['instrumentation']['profile_flag_recorded'])
        self.assertTrue(result['instrumentation']['null_rhi'])
        self.assertEqual(result['instrumentation']['capture_flags'], ['-WCFrontEndAudit', '-WCFrontEndAllHeroes'])
        self.assertEqual(result['subsets']['all_profiled_frames']['gpu_ms']['status'], 'NOT_RUN')

    def test_exact_unfinished_neutral_counter_and_no_round_inference(self):
        path = self.write([{}, {'round': 4, 'neutral_round': 1, 'neutral_live_encounters': 8, 'encounters': 8},
                           {'round': 5, 'neutral_round': 1, 'neutral_live_encounters': 7, 'encounters': 8},
                           {'phase': 0, 'neutral_round': 1, 'neutral_live_encounters': 8, 'encounters': 8},
                           {'round': 10, 'neutral_round': 1, 'neutral_live_encounters': 9, 'encounters': 9},
                           {'round': 10, 'neutral_round': 1, 'neutral_live_encounters': 8, 'encounters': 9}])
        result = summarize(path)
        self.assertEqual(result['subsets']['eight_live_neutral_encounters']['frames'], 1)
        self.assertEqual(result['subsets']['neutral_combat_frames']['frames'], 4)
        self.assertEqual(result['subsets']['pvp_combat_frames']['frames'], 1)

    def test_legacy_columns_do_not_infer_neutral_or_page(self):
        result = summarize(self.write([{}], legacy=True))
        self.assertFalse(result['neutral_instrumentation_available'])
        self.assertEqual(result['combat_kind_unclassified_frames'], 1)
        self.assertEqual(result['eight_neutral_encounters_status'], 'NOT_RUN')
        self.assertEqual(result['subsets']['pvp_combat_frames']['frames'], 0)

    def test_actual_frontend_pages_and_namespace_boundary(self):
        rows = [{'phase': -1, 'frontend_page': page} for page in ('lobby', 'gallery', 'detail', 'settings', 'mode', 'closed', 'unknown')]
        result = summarize(self.write(rows, namespace=0))
        self.assertEqual(result['subsets']['frontend_namespace0_frames']['frames'], 7)
        self.assertEqual(result['subsets']['lobby_frames']['frames'], 1)
        self.assertEqual(result['subsets']['gallery_and_detail_frames']['frames'], 2)
        self.assertEqual(result['subsets']['hero_detail_frames']['frames'], 1)
        self.assertEqual(result['frontend_page_coverage']['unclassified_frames'], 1)
        self.assertEqual(summarize(self.write(rows, namespace=1))['subsets']['lobby_frames']['frames'], 0)

    def test_gpu_unavailable_zero_null_and_invalid_are_excluded(self):
        result = summarize(self.write([{'gpu_ms': 0}, {'gpu_ms': 99, 'gpu_available': 0},
                                       {'gpu_ms': 'null'}, {'gpu_ms': 'nan'}, {'gpu_ms': -2}, {'gpu_ms': 7}]))
        gpu = result['subsets']['all_profiled_frames']['gpu_ms']
        self.assertEqual(gpu['samples'], 1)
        self.assertEqual(gpu['p95_ms'], 7)
        self.assertEqual(gpu['unavailable_or_invalid_samples'], 5)

    def test_nullrhi_suppresses_gpu_and_rendered_viewport_claim(self):
        result = summarize(self.write([{}], rhi='Null', arguments=['-nullrhi', '-WCProfile']))
        self.assertEqual(result['subsets']['all_profiled_frames']['gpu_ms']['status'], 'NOT_RUN')
        self.assertFalse(result['viewport_1080p_observed'])
        self.assertEqual(result['subsets']['all_profiled_frames']['frame_ms']['samples'], 1)

    def test_header_only_and_missing_file_are_not_run(self):
        path = self.write([], namespace=0, arguments=['-WCFrontEndAudit'])
        result = summarize(path)
        self.assertEqual(result['status'], 'NOT_RUN')
        self.assertIn('do not enable -WCProfile', result['not_run_reason'])
        self.assertFalse(result['viewport_1080p_observed'])
        self.assertIsNone(result['subsets']['all_profiled_frames']['frame_ms']['p50_ms'])
        session = json.loads(path.read_text())
        session['process_id'] = 124
        path.write_text(json.dumps(session))
        self.assertTrue(summarize(path)['source']['csv_missing'])

    def test_capture_context_is_bound_without_acceptance_promotion(self):
        path = self.write([{}], arguments=['-WCProfile', '-WCShots', '-WCFrontEndAudit'])
        context = self.directory / 'concurrency.json'
        context.write_text(json.dumps({'boundary': 'Fixture overlapping Blender and regression', 'process_id': 999}))
        result = summarize(path, [context])
        self.assertEqual(result['status'], 'OBSERVED_PRELIMINARY')
        self.assertEqual(len(result['instrumentation']['capture_flags']), 2)
        self.assertIn('NOT_ASSESSED', result['instrumentation']['performance_acceptance'])
        self.assertTrue(any(item['path'] == str(context) for item in result['inputs']))

    def test_truncated_csv_row_is_rejected(self):
        path = self.write([{}])
        csv_path = self.directory / 'match-1-seat-0-pid-123-frames.csv'
        with csv_path.open('a') as stream:
            stream.write('1,2\n')
        with self.assertRaisesRegex(ValueError, 'truncated CSV row'):
            summarize(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
