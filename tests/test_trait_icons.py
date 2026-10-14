"""Race and class badges: one for every catalogue trait, drawn files present, colours apart within each kind."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_trait_icons", ROOT / "tools/production/build_trait_icons.py")
ICONS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ICONS)


class TraitIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((ROOT / "data/vnext/catalog.json").read_text(encoding="utf-8"))
        cls.traits = {trait["id"]: trait["kind"] for trait in catalog["traits"]}

    def test_every_catalogue_trait_has_a_badge_of_its_kind(self):
        self.assertEqual(set(ICONS.TRAITS), set(self.traits))
        for trait, (_, kind, _) in ICONS.TRAITS.items():
            self.assertEqual(kind, self.traits[trait], trait)
            self.assertIn(trait, ICONS.GLYPHS)

    def test_colours_differ_within_races_and_within_classes(self):
        for kind in ("race", "class"):
            colours = [colour for _, k, colour in ICONS.TRAITS.values() if k == kind]
            self.assertEqual(len(colours), len(set(colours)), kind)

    def test_drawn_files_exist_for_game_and_site(self):
        out = ROOT / "art-source/ui/trait_icons_r001"
        for trait in ICONS.TRAITS:
            self.assertTrue((out / f"trait_{trait}.png").is_file(), trait)
            self.assertTrue((out / "svg" / f"trait_{trait}.svg").is_file(), trait)
            self.assertTrue((ROOT / "web/catalogue/art/traits" / f"{trait}.svg").is_file(), trait)
        for kind in ("race", "class"):
            self.assertTrue((out / f"rim_{kind}.png").is_file(), kind)

    def test_site_copies_match_the_drawing(self):
        for trait in ICONS.TRAITS:
            drawn = (ROOT / "art-source/ui/trait_icons_r001/svg" / f"trait_{trait}.svg").read_text(encoding="utf-8")
            self.assertEqual(drawn, (ROOT / "web/catalogue/art/traits" / f"{trait}.svg").read_text(encoding="utf-8"), trait)
            self.assertEqual(drawn.strip(), ICONS.svg(ICONS.badge(trait), label=ICONS.TRAITS[trait][0]), trait)


if __name__ == "__main__":
    unittest.main()
