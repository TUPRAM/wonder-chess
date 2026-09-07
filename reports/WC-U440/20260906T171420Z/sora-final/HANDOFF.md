# Sora7 costume reimport handoff

Source7 is frozen. Geometry revision5 contains the fitted guards; animation revision3 is unchanged. Original imported Sora3 rest skeleton, all seven action curves, seven animation FBX bytes and three texture PNG bytes remain unchanged.

Source SHA256: `7f0f95f04c60543c2b0b98f6ee0cc9d38d76c245b2cea7c5b57516d3b7132b8f`. Export-manifest SHA256: `e5a067f05da3247524c5259a1a08546bb20b57488f82aa5d655a83a8ce20da41`.

Source: `art-source/heroes/wc_u_dragonkin_guardian/wc_u_dragonkin_guardian.blend`. Exports: `exports/heroes/wc_u_dragonkin_guardian`. Actual independent verification: `source7-readback/fbx-video-validation.json`, exit0 with `--python-exit-code 2`. All three mesh FBXs, seven animation FBXs and seven MP4 readbacks pass. Actual shield outward-normal Z at release remains +0.406737. LOD triangles: 8474/4235/2095.

The exposed spherical blue elbows were reshaped into shallow pearl guards fitted against the actual posed forearm, over a continuous undersleeve. Source4 appeared edge-on and was rejected visually. Source5 corrected the orientation, but loading retained geometry exposed incorrect relative texture paths. Source6 rebound the three hash-verified existing textures, re-exported meshes and rerendered six views,21 sparse poses and seven full movies. Source7 restores LOD objects to canonical `LOD_SOURCE`; exact geometry, rig, curves and all14 export bytes remain unchanged from source6.

Actual final views and movies: `reports/WC-U440/20260906T171119Z/sora-links/source6`. Proof connecting unchanged geometry to source7: `source7/repair.json`. Six views were inspected, including actual side and gameplay angles. Sparse poses and full movies are retained. Seven movies contain439frames at60FPS,7.316667 seconds including endpoints. This does not certify continuous visual quality or finished art.

Every failed revision is retained. Source4 has an explicit visual-fix record. Source5 magenta missing-texture frames are not approved. Source6 readback failed because the regenerated LOD objects landed in a suffixed source collection; source7 corrects the source organization and passes a fresh readback. Source5 nominal guard-offset metadata retained the old r4 value; the precise actual r5 offset is0.019*2.08=0.03952m and the correction is recorded in source6/repair.json. No acceptance check uses that metadata field.

The parent already cold-loaded and captured Sora3 in Unreal. Source7 now requires deliberate reimport/reference-preservation and cold-load verification. Continuous art, crowded-board readability, audio/effect alignment and performance remain open. No source7 Unreal or finished-art claim is made here. Varek, then Iri, then Oren are authorized to proceed after this source freeze; Varek production has started.
