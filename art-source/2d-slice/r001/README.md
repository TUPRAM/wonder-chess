# First integrated 2D slice — r001

The owner authorized the bounded real-game trial on 13 September 2026. This packet contains three generated raster sources and the native UI/world presentation work that combines them in Unreal. It is a candidate for owner review, not final art or a public release.

| Component | Authored representation | Current-use limits |
|---|---|---|
| Shop-card family | Editable native Slate framing, five canonical cost colors with numerals, normal/hover/pressed/disabled/focus states | One family across five real shop slots; other frontend controls remain the existing prototype |
| Bellback portrait | One square painted portrait study against its aesthetic and r004 construction references | Current board model remains a proxy; final modeled forms and matching final portrait are unaccepted |
| Heavy Bloom | One square painted bronze flower/weighted-seed inventory icon | Opaque dark background; only actual Heavy Bloom inventory/draft entries use the icon; standalone Lab study never equips it |
| Unit HUD | Runtime health/mana tracks and fills, team labels, reach labels and star pips | Zero mana is empty; passive heroes omit mana; no invented stats |
| Placement | Native check/border, X/hatch and neutral inspection mark | Destination validity reads existing commands; preparation only |
| Quiet stone | One base-color texture and owned rough stone material, repeated on geometry-defined cells | No normal/roughness image claimed; roughness is a material constant; exact seamless texture production is not certified |
| Projectile and impact | Native pooled planar kite, tapered trail and six-ray impact geometry | Existing release/arrival/impact events remain authoritative; this is not a spritesheet |
| Stun | Native compact spiral and five-point stars | Active-duration and expiry follow actual combat state; status test uses a synthetic test catalogue, not a newly assigned hero skill |

## Source and import record

All painted sources were made with the built-in image generator; no CLI or paid external service was used. Exact prompts are under [inputs](inputs). The image tool returned 1254-square RGB sources despite requested 1024-square output. They are preserved unchanged. Unreal imports retain the source while requesting cooked sizes of 1024 for Bellback, 512 for Heavy Bloom and 1024 for stone.

The first Heavy Bloom output painted a checkerboard instead of producing transparency. It is retained as [rejected evidence](sources/heavy_bloom_rejected_checkerboard.png) and was never imported. A targeted image-generation revision replaced that background with dark ink. The selected icon is deliberately opaque; a transparent production cutout remains future work.

The portrait's crown is close to the top edge. Its square presentation keeps the full bell visible; future circular crops need a separate framing pass. Do not infer hidden toe counts, exact 3D proportions or accepted model identity from this crop.

Source metadata and current result are in [asset_manifest_candidate.json](asset_manifest_candidate.json) and the [implementation readout](../../../docs/vnext/art/2D_SLICE_READOUT.md). The original style packet r001 remains a historical reference packet; this production trial does not silently approve all its speculative creatures, fake UI numbers or generic relic objects.

## Stage boundary

The user approved executing this study and viewing it in the real game. No formal references/forms/release acceptance is self-issued. This hybrid UI/environment/VFX trial supplies evidence for those reviews. It does not advance Bellback beyond its existing ART_REVISE modeled-forms state.

The larger 363-row specification is a scope inventory, not a generation order. Only this bounded slice was executed. Expansion should follow owner review of the actual package, then the remaining current-hero portraits and ability icons, canonical relics, matching UI families and event-specific effects. Final hero portraits remain dependent on accepted character identity.

