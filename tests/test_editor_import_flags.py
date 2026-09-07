"""Regression for false environment values silently selecting audio-only import."""
import ast
import os
from pathlib import Path
import unittest
from unittest.mock import patch


class EditorImportFlags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parents[1] / 'tools/unreal/import_alpha_assets.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'env_flag')
        scope = {'os': os}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
        cls.read_flag = staticmethod(scope['env_flag'])

    def test_zero_does_not_skip_requested_hero(self):
        with patch.dict(os.environ, {'WC_IMPORT_HERO': 'wc_u_human_warrior', 'WC_IMPORT_AUDIO_ONLY': '0'}):
            self.assertFalse(self.read_flag('WC_IMPORT_AUDIO_ONLY'))

    def test_supported_false_values(self):
        for value in ('', '0', 'false', ' NO ', 'Off'):
            with self.subTest(value=value), patch.dict(os.environ, {'WC_IMPORT_AUDIO': value}):
                self.assertFalse(self.read_flag('WC_IMPORT_AUDIO'))

    def test_supported_true_values(self):
        for value in ('1', 'true', ' YES ', 'On'):
            with self.subTest(value=value), patch.dict(os.environ, {'WC_IMPORT_AUDIO_ONLY': value}):
                self.assertTrue(self.read_flag('WC_IMPORT_AUDIO_ONLY'))

    def test_unknown_value_fails_instead_of_selecting_audio(self):
        with patch.dict(os.environ, {'WC_IMPORT_AUDIO_ONLY': 'flase'}):
            with self.assertRaisesRegex(ValueError, 'WC_IMPORT_AUDIO_ONLY'):
                self.read_flag('WC_IMPORT_AUDIO_ONLY')

    def test_missing_value_is_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(self.read_flag('WC_IMPORT_AUDIO_ONLY'))


if __name__ == '__main__':
    unittest.main()
