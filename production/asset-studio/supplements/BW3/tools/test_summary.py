"""Tests for read-only measurement summarization, not Blender or collision tests."""
import copy
import json
from pathlib import Path
import unittest
from summarize_supplied_contact import summarize

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'evidence/BW2_contact_measurements.json').read_text())

class SummaryTests(unittest.TestCase):
    def test_actual_supplied_closure_is_not_waived(self):
        s = summarize(DATA)
        self.assertEqual(s['closure']['frames_over_threshold'], list(range(4, 25)))
        self.assertEqual(s['closure']['maximum_at_frame'], 14)
        self.assertAlmostEqual(s['closure']['maximum_vertex_penetration_mm'], 13.906720174744448)
        self.assertEqual(s['held']['count_over_threshold'], 0)
        self.assertEqual(s['full_timeline']['status'], 'FAIL_SAMPLED_PENETRATION_SCREEN')
    def test_duplicate_frames_rejected(self):
        d=copy.deepcopy(DATA);d['frames'][1]['frame']=1
        with self.assertRaises(ValueError):summarize(d)
    def test_missing_measurement_not_treated_as_zero(self):
        d=copy.deepcopy(DATA);del d['frames'][13]['whole_right_glove_vertex_screen']['maximum_sampled_penetration_mm']
        with self.assertRaises(ValueError):summarize(d)
    def test_nonfinite_rejected(self):
        d=copy.deepcopy(DATA);d['frames'][13]['whole_right_glove_vertex_screen']['maximum_sampled_penetration_mm']=float('nan')
        with self.assertRaises(ValueError):summarize(d)
    def test_declared_contact_status_cannot_hide_collision(self):
        d=copy.deepcopy(DATA)
        for f in d['frames']:f['phase']='PASS_APPROVED'
        self.assertEqual(summarize(d)['closure']['count_over_threshold'],21)
    def test_gap_in_coverage_rejected(self):
        d=copy.deepcopy(DATA);d['frames'].pop(5)
        with self.assertRaises(ValueError):summarize(d)
    def test_held_interval_validated(self):
        d=copy.deepcopy(DATA);d['carry_spec']['held_frames']=[25,150]
        with self.assertRaises(ValueError):summarize(d)
    def test_threshold_is_explicit(self):
        with self.assertRaises(ValueError):summarize(DATA,-1)
        self.assertEqual(summarize(DATA,15)['closure']['count_over_threshold'],0)
        self.assertEqual(summarize(DATA)['threshold_mm'],.5)

if __name__=='__main__':unittest.main()
