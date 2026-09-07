# Ada source9 gallery polish handoff

Ada is frozen at source9 / geometry8 / animation8 with 9068 / 4534 / 2261 LOD triangles. The existing head shell, braid, coat, armor, shield and sword are preserved; all seven source action curves and animation FBX hashes remain unchanged.

Changes are limited to fitted shallow eye/iris/brow geometry, a tapered nose and restrained lip contour, and existing palms fused into modeled finger/thumb grips. No shared rig, material, canonical data or Unreal binary was edited.

[Saved source](<C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_human_guardian\wc_u_human_guardian.blend>) · [Export manifest](<C:\Users\iputu\Documents\Wonder Chess\exports\heroes\wc_u_human_guardian\export_manifest.json>) · [Before close face](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T153806Z\ada\inspection8\face.png>) · [After close face](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T153806Z\ada\candidate9-v8\face.png>) · [Before grip](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T153806Z\ada\inspection8\sword-grip.png>) · [After grip](<C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T153806Z\ada\candidate9-v8\sword-grip.png>)

Source SHA-256: `54f04b8f28fd819eb22b7a4f6c8051484c6466513e6cd43d419c835b67d950b3`

Manifest SHA-256: `33566d5d63915c6d17023e6e6b713b9570d9d02e49eb121b3e17df5e974b38c4`

Verification passed for 14 file hashes, saved-source skin/root/scale/support checks across seven clips, and three independent mesh-FBX readbacks. Actual Blender frames were encoded at 20 Hz / 1x and all seven final sampled contact sheets were inspected. This does not certify continuous playback, in-engine rendering, animation-FBX import or finished art.

The short lip line and faceted nose remain deliberate stylization. Fingers retain clear grooves at close zoom; actual cuff/guard contacts and combat-camera readability remain integration review concerns. The existing armor/cloth silhouette was retained because this inspection did not justify wholesale replacement.

Retained failed attempts:

- candidate9-v1: Blender UV collection clear() API failure; source8 preserved
- candidate9-v2: UV name mismatch made remeshed hands use incorrect swatch; actual renders retained
- candidate9-v3: close facial view showed eye/head crossing; tessellated surface-fit repaired it
- candidate9-v5: structural preflight failed at 26338 triangles; narrowed hand reduction, not increased budget
- Earlier candidate close views exposed rough finger/palm joins; curl roots extended into fused palm

Required integration checks:

- Current Unreal revision/reimport and texture consistency
- Continuous all-seven playback at gallery and gameplay camera
- Grip/cuff/guard intersections at release and terminal poses
- Face and surface artistic acceptance; candidate is not certified finished art
- Performance comparison on named hardware at game camera
