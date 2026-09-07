# Neris, Orla and Tala facial source handoff

The three sources are frozen for Unreal integration. Fresh close front and three-quarter inspection showed separate projecting eye and brow blocks. Each revised asset fits its original eye colors and brow expression to the retained head surface. All other retained vertex coordinates, palette swatches and skin weights match their starting canonical signatures.

| Hero | Source / geometry / animation | LOD triangles | Before face | After face | Source |
| --- | --- | --- | --- | --- | --- |
| Neris | 5 / 5 / 1 | 7570 / 3784 / 1890 | [Before](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T161455Z-face-fit\neris-before-v2\face-three-quarter.png>) | [After](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T161455Z-face-fit\neris-candidate5\face-three-quarter.png>) | [Blend](<C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_elf_mage\wc_u_elf_mage.blend>) |
| Orla | 4 / 4 / 1 | 8606 / 4295 / 2139 | [Before](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T161455Z-face-fit\orla-before\face-three-quarter.png>) | [After](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T161455Z-face-fit\orla-candidate4\face-three-quarter.png>) | [Blend](<C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_dwarf_priest\wc_u_dwarf_priest.blend>) |
| Tala | 4 / 4 / 1 | 7572 / 3786 / 1891 | [Before](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T161455Z-face-fit\tala-before\face-three-quarter.png>) | [After](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T161455Z-face-fit\tala-candidate4\face-three-quarter.png>) | [Blend](<C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_orc_guardian\wc_u_orc_guardian.blend>) |

Verification passed for 42 export hashes, nine independent normalized mesh-FBX readbacks, and 21 saved-source skin/root/scale/action checks. All 21 final source contact sheets were inspected and encoded at 20 Hz / 1x. Their 21 animation FBX hashes remain unchanged. These are sampled source reviews; continuous in-engine playback and finished-art acceptance remain separate.

Neris retains her low hair knot, broken-circle headpiece and palm focus. Orla retains her silver braids, closed hood and carried octagonal lantern. Tala retains her tusks, tight braids, rounded tower shield and mace. No shared rig/material, canonical data or Unreal binary was changed.

One read-only helper failure is retained: neris-before.log records an incorrect assumed component-dimensions key. The repaired run derived dimensions from actual bounds and completed in neris-before-v2. All three geometry candidates passed their first executed structural and motion preflight.

Required remaining integration checks:

- Actual Unreal material, portrait and LOD transition inspection
- Continuous seven-clip playback per hero at gallery/game camera and both orientations
- Existing fitted-cloth, anatomy and hand/prop artistic acceptance
- Frame times on named hardware and crowded compositions

Neris source SHA-256: `87e5c30e9e26bf8bcb3b1d6f8c90a83fdce5322be8372ef3081a6565a9e473bd`

Neris manifest SHA-256: `6923b493d80ba1364da103ee2d6ae2906a9761dd30a2578a1cd182fd98efbe9a`

Orla source SHA-256: `160e979c9e5901640b6f977e57daf849aa3ecc8941cd8aefbc5b7bb54648025a`

Orla manifest SHA-256: `55089692b66df76607f7c02b2216e2610cb4ec5d8103afe7cd231f22c657d36c`

Tala source SHA-256: `69077f38af82b96e306d5419df84df0f10128456ce02791b7416484c304f7eea`

Tala manifest SHA-256: `031e997f902f282d22ce7178a75a2f7465a2fb2690480548db01f6fa46c2bc6e`
