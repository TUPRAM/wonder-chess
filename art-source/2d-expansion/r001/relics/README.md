# Relic expansion r001 source handoff

Eleven new relic icon studies complete the current twelve-relic collection alongside the previously approved Heavy Bloom source. The user authorized this expansion after approving the first integrated slice on 2026-09-13. This authorization is not an approval of these new individual paintings or of the eventual packaged interface.

**Source stage: complete and inspected. Engine and owner review: pending.**

## Selected sources

All selected PNGs are untouched 1254 × 1254 RGB generator output with an opaque dark ink background. Cook to 512 × 512 UI textures with sRGB enabled, UI compression, no mipmaps, and suitable UI filtering. Do not treat the backdrop as alpha or remove it programmatically. Surrounding frames, labels, states and live mechanic descriptions belong to the native interface.

| Source filename | Distinctive silhouette |
|---|---|
| wc_vn_r_quick_wick.png | Two exposed flame-tipped ivory wick branches in a small bronze ferrule. |
| wc_vn_r_long_lens.png | Long diagonal telescope with a distant point. |
| wc_vn_r_broad_canopy.png | Broad three-lobe canopy sheltering three separated drops. |
| wc_vn_r_close_focus.png | Thick circular lens with a short handle and near bright point. |
| wc_vn_r_tight_choir.png | Three close ivory ceramic pipes bound with dark thread. |
| wc_vn_r_silk_trigger.png | Ivory diagonal silk strand across a compact bronze release catch. |
| wc_vn_r_patient_lantern.png | Rounded enclosed lantern with a steady amber core. |
| wc_vn_r_far_hourglass.png | Tall narrow hourglass with pointed vertical sighting fins. |
| wc_vn_r_wide_hourglass.png | Broad hourglass encircled by a horizontal waist ring. |
| wc_vn_r_narrow_metronome.png | Triangular wooden instrument with a pale pendulum and narrow arc. |
| wc_vn_r_urgent_shard.png | Angular diagonal glass shard, leading flash and trailing ember. |

## Provenance and review

- Tool: built-in image_gen__imagegen; thirteen calls, eleven selected outputs and two retained rejected revisions.
- Exact initial and revision prompts: prompts/.
- Input references and hashes, original generator paths, selected raw hashes, canonical descriptions and inspection notes: manifest.json.
- Generated originals copied without altering pixels. Source selected bytes: 18,929,831.
- Rejected Quick Wick r1 used an oversized floral vessel that weakened its difference from the enclosed lantern. Revision2 removed the vessel.
- Rejected Silk Trigger r1 clipped the main strand at both image boundaries. Revision2 brought both ends inside the square.
- Every returned image was visually inspected. Full-size source checks passed for identity motif, single-object composition, absence of text/framing, and backdrop family.
- Source technical verification: eleven canonical identities match; all eleven decode as square RGB PNGs; all eleven hashes match their untouched selected generator originals. See source_verification.json.
- No gameplay source, existing artwork, model, Unreal binary or shared ledger was edited by this subtask.

## Native-size review boundary

size_review.html lays out the complete twelve-icon family at 32, 64 and 128 CSS pixels. Opening its local file URL was rejected by CUA's browser security policy. No alternate-browser or indirect workaround was attempted. The HTML exists for manual review, but no browser rendering or small-size pass is claimed.

The native game integration still needs 32/64-pixel inventory readability, larger offer views, grayscale distinction for the paired concepts, and actual selected/equipped/incompatible/disabled state review. Far Hourglass's thin inner stream and Silk Trigger's fine frays are detail only; their overall silhouettes must carry recognition. Quick Wick intentionally has more negative space after its correction and needs an actual small-size check. The source batch must not self-issue an owner approval or packaged-art acceptance.

## Reproduce the source checks

Run the authoring Python with Pillow:
```powershell
& 'C:/Users/iputu/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' 'art-source/2d-expansion/r001/relics/verify_sources.py'
```

This reads PNGs and computes metadata; it does not edit image pixels. The main integration task owns engine import, package and player-facing visual review.

