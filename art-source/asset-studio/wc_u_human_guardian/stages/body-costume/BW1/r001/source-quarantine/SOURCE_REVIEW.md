# BW1 selected free-source inspection

Acquired and inspected on 2026-09-09. This record concerns source acquisition, static text geometry, and source thumbnails. **No Blender import, fit, pose, visual acceptance or reusable-recipe acceptance was performed by this inspection task.** The main BW1 authoring task owns those later observations.

## Selected candidates

| Candidate | Observed contents | Current decision |
|---|---|---|
| `toigo_gloves_short`, MargaretToigo (OBJ/MHCLO author identifier `MRT`) | A left/right pair, 2,294 vertices, 2,272 quad faces, 2,954 UV coordinates. Two connected components of 1,147 vertices; 40 total boundary edges; no edge incident to more than two faces. One MHCLO correspondence record per vertex. | Eligible for isolated CC0 adaptation and fit testing. It is an adaptation if reused, not original geometry. |
| `toigo_ankle_boots_male`, MargaretToigo (`MRT`) | A left/right pair, 2,084 vertices, 2,060 quad faces, 2,436 UV coordinates. Two components of 1,042 vertices; 44 boundary edges; no edge incident to more than two faces. One MHCLO correspondence record per vertex. | Eligible for isolated CC0 adaptation and fit testing. Source thumbnail shows a practical low block heel and ankle shaft, not a completely flat sole. Ada-specific sole, toe-box, ankle and cuff work remains necessary. |

The glove thumbnail visibly shows separate covered fingers/thumb and a short wrist opening. The boot thumbnail visibly shows open ankle shafts and a low heel. These are creator thumbnails, not newly rendered Blender evidence. They do not prove grip or ankle deformation.

Both candidates have `basemesh hm08` correspondence. The glove references source indices through 14,429; the boot through **18,001**, so fitting requires the full 19,158-vertex indexed MPFB source, including helpers. The extracted editing head cannot support this correspondence.

MHCLO weights are fitting coordinates. There are 264 glove and 398 boot records containing weights outside [0,1]; their sums remain within 0.0000100001 of one. These are extrapolating surface correspondence values, **not skeletal weights**. Do not normalize or clamp them as though they were bone weights.

There are no delivered rigs or skeletal-weight files. Finger/ankle weights must be inherited from the body or authored, then reviewed in actual poses. The raw OBJ has no named groups or material directives; its UVs are present, while the MHCLO/MHMAT documents carry asset and material metadata.

## Rights and acquisition evidence

The original MakeHuman pack pages list both selected assets as CC0:

- [Gloves01 project page](https://static.makehumancommunity.org/assets/assetpacks/gloves01.html)
- [Shoes01 project page](https://static.makehumancommunity.org/assets/assetpacks/shoes01.html)

The raw source pages are preserved as `gloves01_page.html` and `shoes01_page.html`. The original packed registries are preserved as `gloves01.json` and `shoes01.json`; they name MargaretToigo and CC0 for these two candidates. Both selected OBJ and MHCLO headers explicitly state `# author MRT` and `# license CC0`. No separate LICENSE or README file was delivered in either archive. File hashes, exact headers, raw registry entries, material text and full archive inventories are in `source_inspection.json`.

Only one glove and one boot were extracted. The two complete official packs remain quarantined because the publisher distributes the candidates in packs; no other garments are installed or loaded.

| Archive | Official download used | Bytes | SHA256 |
|---|---|---:|---|
| `gloves01_cc0.zip` | `https://files2.makehumancommunity.org/asset_packs/gloves01/gloves01_cc0.zip` | 3,192,691 | `ecdaee1d02749d17352791d415cb622a883350cc8a4b90eda3725aef35d9afb2` |
| `shoes01_cc0.zip` | `https://files.makehumancommunity.org/asset_packs/shoes01/shoes01_cc0.zip` | 82,953,569 | `ded3f70428505eabbf1f6d7b5f61196a7366ef20757103d276ad0ed336c35ada` |

Both ZIP CRC checks passed. The glove pack has 57 entries; the shoe pack has 164. All entries were checked for parent traversal, absolute paths, drive prefixes, symlinks and script/executable/Blender-file extensions. None were found. This is a bounded archive inspection, not a claim of complete security verification.

The initial Python HTTPS requests failed certificate validation. Native Windows HTTPS verification succeeded without disabling validation. The first glove download ended early and is retained as `gloves01_cc0.incomplete`; the complete replacement came from the other documented mirror and passed ZIP integrity. Creator-node URLs refused the connection, so the archived official pack page, packed registry and actual file headers supply the provenance here. No login, purchase, upload or permission change occurred.

### Rejected before extraction

`culturalibre_hero_boots_1` was **not selected or extracted**: the pack registry and MHCLO declare CC0/CC-0, while its delivered OBJ header declares `AGPL3` and author `Unknown`. The exact conflicting source headers and hashes are retained in `source_inspection.json`. This may be a legacy exporter header, but that is an unverified explanation. Do not erase the conflict or treat it as cleared rights.

## Materials and dependencies

The selected folders are self-contained for the declared maps:

- Glove: `gloves_hand.obj`, `toigo_gloves_short.mhclo`, `gloves_hand.mhmat`, `Gloves03UV.png`, creator thumbnail.
- Boot: `boots_ankle_male.obj`, `toigo_ankle_boots_male.mhclo`, `boots_ankle_male.mhmat`, `BootsAnkleM.png`, `BootsAnkle-norm.png`, `BootsAnkle-spec.png`, creator thumbnail.

MHMAT's `data/shaders/glsl/phong` string identifies a MakeHuman shader convention; no shader executable/script is bundled or should be downloaded to honor it. The pilot is untextured: use the mesh/correspondence and replace imported material slots with the study clay. The source maps stay quarantined as original provenance, not new Ada texture work.

## Installed MPFB 2.0.17 native load path

Code inspection found the operator `bpy.ops.mpfb.load_clothes(filepath=...)`. It accepts an absolute MHCLO path and requires no global pack installation. The live scene must select the **full indexed MPFB Basemesh** with its shape keys and the intended local MPFB Skeleton as the related rig. Ensure armature pose is reset for the initial fit. Do not apply masks or subdivision to the indexed source.

The following is an execution specification, not an execution log. Use the live RNA properties verified by the main task before invoking it:

```python
scene.MPFB_LC_object_type = 'Clothes'
scene.MPFB_ASLS_fit_to_body = True
scene.MPFB_ASLS_set_up_rigging = True
scene.MPFB_ASLS_interpolate_weights = True
scene.MPFB_ASLS_import_subrig = False
scene.MPFB_ASLS_import_weights = False
scene.MPFB_ASLS_delete_group = False
scene.MPFB_ASLS_add_subdiv_modifier = True
scene.MPFB_ASLS_subdiv_levels = 1
scene.MPFB_ASLS_makeclothes_metadata = False
bpy.ops.mpfb.load_clothes(filepath=selected_absolute_mhclo_path)
```

Concrete paths:

```text
C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/source-quarantine/selected/clothes/toigo_gloves_short/toigo_gloves_short.mhclo
C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/source-quarantine/selected/clothes/toigo_ankle_boots_male/toigo_ankle_boots_male.mhclo
```

Important installed-code behavior:

1. The operator's fitted branch calls `HumanService.add_mhclo_asset` with `set_up_rigging=(rig is not None)` and `interpolate_weights=True`. It fits to the body's current shape-key mix and can inherit the existing source rig's weights. UI flags are not the entire behavior contract.
2. That service creates `Delete.<asset>` source vertex groups and MASK modifiers unconditionally for these delivered delete-vertex lists, even when `MPFB_ASLS_delete_group=False`. These are nondestructive masks, but **disable only the newly added garment Delete masks in viewport and render** so body intersections are not concealed. Preserve the existing helper mask. Keep source vertex count, shape-key count and coordinate correspondence unchanged.
3. The fitted branch hardcodes `material_type='MAKESKIN'`. Replace imported garment material slots with uniform study clay afterward; setting a UI material flag alone does not guarantee untextured output.
4. Keep `makeclothes_metadata=False`: the operator's trailing optional block refers to locals created only in the non-fit branch. The fitted service already attaches source metadata.
5. A successful load may store a short relative asset identifier. Later refitting through asset-library resolution could fail because these packs are deliberately not globally installed. Preserve the absolute source path in trial provenance; do not treat loading once as replay proof.
6. Import inherited weights are starting data only. Check each thumb/finger and foot/ankle region independently through the required grip and motion evidence.

Inspected installed files (no code modifications):

```text
.../mpfb/ui/apply_assets/loadclothes/operators/loadclothes.py
.../mpfb/ui/apply_assets/loadclothes/loadclothespanel.py
.../mpfb/ui/apply_assets/assetlibrary/assetsettingspanel.py
.../mpfb/services/blenderconfigset.py
.../mpfb/services/humanservice.py
.../mpfb/services/clothesservice.py
```

The prefix in RNA is `MPFB_` plus `ASLS_` or `LC_`, not the short configuration names by themselves. The installed file hashes are recorded in the JSON inspection.

## Construction learning boundary

Observed: two connected hand envelopes with individual fingers; two boot envelopes with open shafts, UVs, fitting correspondence and low-heel silhouette. The raw files expose no creator modifier history, garment patterns, sculpt layers, crease attributes, skeleton or pose results.

Inferred methods to test: preserve the glove's finger topology while fitting palm allowance and wrist cuff; preserve the boot's sole/toe/shaft differentiation while adding Ada-specific shaft and ankle allowance. The source registry's boot description mentions subdivision and sole/heel crease settings, but the flattened OBJ does not encode those settings. Reconstructing a useful crease/volume treatment is a new operation requiring its own image and pose evidence.

Executed here: acquire, quarantine, inventory, inspect license headers, parse geometry/correspondence, extract the two allowed candidates and view their delivered thumbnails. No adaptation, fitting, deformation review, independent replay or second-body fit is claimed. No recipe is promoted.
