import json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
source=root/"art-source/2d-expansion/r001"
inventory=json.loads((source/"source_inventory.json").read_bytes())
rows=[]
for asset in inventory["sources"]:
 kind=asset["kind"];id=asset["id"]
 if kind=="environment":
  target="T_SanctuaryBackground";size=[2048,1280]
 elif kind=="relics":
  target="T_Relic_"+id.removeprefix("wc_vn_r_");size=[512,512]
 else:
  target="T_"+("Portrait" if kind=="portraits" else "Ability")+"_"+id;size=[1024,1024] if kind=="portraits" else [512,512]
 rows.append({**asset,"unreal_asset":"/Game/WonderChess/VNext/ArtExpansionR001/"+target,"requested_cook_size":size})
manifest={
 "schema":"wonder_vnext.storybook_candidate.1","asset_id":"wc_vn_storybook_r001",
 "status":"IMPORTED_PACKAGE_VERIFICATION_PENDING","owner_authorization":"2026-09-13: I approve the slice; expand current hero portraits, abilities, relics, panels, effects and reference-matched player interface.",
 "previous_slice":"Owner-approved integrated r15 study; historical verification preserved.",
 "human_acceptance":"Expanded candidate pending; final3Dforms and release notaccepted",
 "method":"Builtin imagegen paintings plus native C++/Slate panels, clicktargets, dynamictext, geometry and event-driven effects",
 "painted_source_count":23,"reused_sources":["art-source/2d-slice/r001/sources/bellback_portrait.png","art-source/2d-slice/r001/sources/heavy_bloom.png","art-source/2d-slice/r001/sources/quiet_stone.png"],
 "sources":rows,"fonts":inventory["fonts"],"font_source":inventory["font_source"],
 "reference":"art-source/2d-style/r001/ref02_preparation_screen_direction.png",
 "source_limitations":"Opaque flattened RGB painting sources, not PSD/SVG/layered masters. No 3D model promotion. User review remains separate."
}
(source/"asset_manifest_candidate.json").write_text(json.dumps(manifest,indent=2))
(root/"game/Content/WonderChess/UIFonts/README.md").write_text(
 "# Cinzel font attribution\n\nUnmodified static Cinzel Regular and Bold from the designer's official repository: https://github.com/NDISCOVER/Cinzel/tree/master/fonts/ttf\n\nSIL Open Font License 1.1. The full copyright and license are in Cinzel-OFL.txt, staged with these fonts. No system font dependency or font installation is required. SHA256 identities are recorded in art-source/2d-expansion/r001/source_inventory.json.\n")
print(len(rows))
