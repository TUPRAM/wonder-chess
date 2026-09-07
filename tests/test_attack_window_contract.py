"""Pure authored/import-readback fixtures; no editor or visual acceptance claims."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('attack_windows', Path(__file__).resolve().parents[1] / 'tools/unreal/attack_window_contract.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AttackWindowContractTests(unittest.TestCase):
    def clip(self):
        return {'frames': [1, 79], 'release_frame': 16, 'presentation_windows': [
            {'name': 'R', 'start_frame': 1, 'release_frame': 16, 'end_frame': 40},
            {'name': 'L', 'start_frame': 40, 'release_frame': 55, 'end_frame': 79}]}

    def test_exact_two_full_cycles_and_shared_boundary(self):
        plan = module.attack_window_plan(self.clip(), 60, 250)
        self.assertEqual(plan['duration_seconds'], 1.3)
        self.assertEqual(list(plan['markers'].values()), [0, .25, .65, .65, .9, 1.3])
        self.assertEqual(module.validate_imported_markers(plan, 1.3, list(plan['markers'].items())), plan['markers'])

    def test_ordinary_unmarked_clip_preserves_behavior(self):
        self.assertIsNone(module.attack_window_plan({'frames': [1, 40], 'release_frame': 16}, 60, 250))
        self.assertEqual(module.validate_imported_markers(None, .65, [('Footstep', .2)]), {})
        with self.assertRaises(ValueError): module.validate_imported_markers(None, .65, [('WC_Attack_R_Start', 0)])

    def test_other_hero_uses_own_canonical_windup(self):
        clip = self.clip()
        clip['release_frame'] = 19
        clip['presentation_windows'][0]['release_frame'] = 19
        clip['presentation_windows'][1]['release_frame'] = 58
        self.assertEqual(module.attack_window_plan(clip, 60, 300)['markers']['WC_Attack_L_Release'], .95)
        with self.assertRaises(ValueError): module.attack_window_plan(clip, 60, 250)

    def test_bad_layouts_refused_before_import(self):
        cases = []
        for key, value in [('start_frame', 41), ('release_frame', 56), ('end_frame', 80), ('name', 'R')]:
            clip = self.clip(); clip['presentation_windows'][1][key] = value; cases.append(clip)
        clip = self.clip(); clip['presentation_windows'].pop(); cases.append(clip)
        clip = self.clip(); clip['presentation_windows'][0]['damage'] = 99; cases.append(clip)
        clip = self.clip(); clip['release_frame'] = 17; cases.append(clip)
        clip = self.clip(); clip['presentation_windows'][0]['start_frame'] = True; cases.append(clip)
        for clip in cases:
            with self.subTest(clip=clip), self.assertRaises(ValueError): module.attack_window_plan(clip, 60, 250)

    def test_imported_missing_duplicate_and_wrong_timing_refused(self):
        plan = module.attack_window_plan(self.clip(), 60, 250)
        markers = list(plan['markers'].items())
        for actual in [markers[:-1], markers + [markers[0]], markers + [('WC_Attack_X_Start', 0)],
                       [(name, value + .01) for name, value in markers], [(name, float('nan')) for name, value in markers]]:
            with self.subTest(actual=actual), self.assertRaises(ValueError): module.validate_imported_markers(plan, 1.3, actual)
        with self.assertRaises(ValueError): module.validate_imported_markers(plan, .65, markers)


if __name__ == '__main__': unittest.main()
