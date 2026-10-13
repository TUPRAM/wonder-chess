# Texture development and revisions

## Initial animation-ready delivery

1. Use the accepted Main/front, Left, Back and Right images as both geometry and
   separate texture guidance where supported. Keep original image hashes/slot order.
2. Request base color and PBR normal, roughness and metallic with the optimized
   geometry. Begin at 2K; choose 4K only from observed review needs. Requesting
   maps does not prove they arrived: download, decode and inventory every map.
3. Keep provider originals immutable. Record material slot, UV set, image size,
   channel meanings, alpha use and source hash in `material-map.csv`. Extract
   embedded maps without re-encoding where possible; document any conversion.
4. Import base color as sRGB, data maps as linear, normals with the appropriate
   normal-map compression/convention. Verify the normal Y convention in a lit
   comparison; do not blindly flip every source. Record packed-channel mappings.
5. Use direct source base color, neutral material tint and no blanket emissive.
   Verify actual skeletal material usage in Unreal and PIE. Fur, moss and stone
   should not become metallic through incorrect channel assignments. Document any
   required physically appropriate constants if a map is absent; never call an
   absent map delivered.
6. Review front, sides, back, underside, eye/muzzle, seams and stretched joints in
   base-color-only, neutral lit and soft board lighting. Preserve texture colors
   while adjusting lighting for readability; record exposure and tone mapping.
7. Check UV overlap where unintended, texel density, padding, mip bleeding and
   normal seams. Bake/transfer higher-detail information only with compatible
   source/target UVs, recorded settings and viewed results. Do not hide a missing
   jaw or fused paw with painted detail.

## Cragstoat priorities

- Keep the accepted light cream/taupe coat and face, warm brown eyes, green moss
  and floral accents, and distinct shoulder stones. These describe reference
  intent; approval of the generated colors is still a review decision.
- Inspect narrow gaps between all five toes on each paw, eyelids, belly, tail
  underside, shoulder ridges and fur/stone boundaries. Count geometry separately
  from markings that merely suggest toes or plate edges.
- Check normal detail and roughness at bent elbows and compressed torso poses.
  Avoid very dark baked shadows under ridges and glossy plastic-looking fur.
- Defer fur cards, new palettes, extra ornaments and elaborate shader effects.
  They change construction/rendering scope and are not required to preserve the
  original Meshy appearance.

## Future passes after initial acceptance

| Pass | Trigger and work | Dependencies to recheck |
|---|---|---|
| T1 Material correctness | Missing/wrong channels, seams or baked-light defects; fix import settings first, then scoped provider/local source correction if needed | Color comparison, deforming seams, mip views |
| T2 Close-up detail | A documented visible loss warrants a 4K candidate or high-to-low detail transfer | UV compatibility, memory, board relevance, normal orientation |
| T3 Game optimization | Actual board/LOD/profile results warrant resizing, compression or map packing | Preserve original source; inspect derivative, LOD transitions, packaged rendering and memory |
| T4 Art revision | Owner requests new colors or construction | New explicit art revision; affected approval and downstream evidence |

No automatic recolor variants. Freeze accepted original map hashes. A derivative
must name parent maps, tool/settings, color space and purpose; compare it against
the original. A UV/topology change can invalidate textures and skin. A map-only
revision on unchanged UVs does not justify rerigging, but material/visual evidence
must be refreshed. Do not overwrite a previously accepted bundle.

## Free local tools already selected for this project

- **Krita:** inspect/edit layered 2D sources and precise reference preparation;
  localized map changes only within the current art scope, with original preserved.
- **Unreal UV Editor/modeling/baking:** candidate UV fixes and detail transfer when
  the installed tool path is qualified; verify skin implications before mesh edits.
- **MeshLab:** geometry diagnostics and isolated comparison, preserving UV/skin
  dependencies; not an assumed replacement for a rig editor.
- **Unreal materials/texture editor and Insights:** actual rendering, streaming and
  memory measurements. A documentation entry is not proof a specific bake ran.

See [tool qualification](TOOLCHAIN.md), [visual standard](VISUAL_STANDARD.md) and
[engineering checkpoints](ENGINEERING.md) for exact checks and existing limits.
