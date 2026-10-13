# Color preservation and soft storybook lighting — G1

**Version 1.2 amendment:** [UV/bake engineering](ENGINEERING.md#5-g3c--uv-and-bake-checkpoint)
preserves original color-map bytes and allows separately hashed color-preserving
resampling when UVs change. Compare matched unlit views; resampling does not authorize
recoloring. Material families and neutral/board scenes are specified in that manual.
The diagnostic studio is a calibration candidate, not owner-approved G1 lighting.

## Outcome and fixed boundaries

The owner wants the light, recognizable colors seen in the accepted Meshy result
and a game without harsh, dark creature shadows. Preserve the color source and
calibrate the display environment. This standard applies to new production and
future approved visual revisions; it does not overwrite accepted Bellback files.

**Color source:** the exact accepted Meshy model/material bundle and base-color
images, recorded by SHA-256. If Meshy produced an untextured model, first texture it
in Meshy and review the colored result. A later retexture is a new visual candidate.

Do not multiply base color by a non-white tint, modify hue/saturation, paint highlights,
apply team-color vertex tints, bake extra AO into the pigment map, or use a global
emissive addition to compensate for inadequate lighting. Existing intentional
emissive features from the accepted design and time-limited ability VFX are distinct;
record their masks and purpose rather than making the whole creature glow.

## 1. Establish an honest comparison

1. Preserve the original files and hash maps before importing or remapping anything.
2. Capture the actual Meshy viewer/result that the owner accepted. Record its view,
   available environment/exposure settings, date and source task. If settings are
   unavailable, mark them unknown; do not invent them.
3. Use the same model pose, approximate camera angle and visible material regions
   in Unreal. Include a neutral gray ground and a reference gray/color card.
4. Make a diagnostic Base Color/unlit capture to separate texture-import mistakes
   from lighting. This is an inspection view, not the final game material.
5. Capture the normal lit studio view and the actual board view at fixed exposure.
   Include front, back, each side, underside and the game camera from both teams.
6. Compare eyes, muzzle, pale surfaces, saturated patches, metallic/glass regions
   and the shaded legs. Check both highlights and shadows, not only an average color.

A texture hash proves preserved bytes, not equal rendered appearance. Texture
compression, sampling, lighting and tone mapping can alter displayed pixels. Do not
promise a pixel-identical Meshy render when its environment is unknown. The G1
owner-approved side-by-side appearance is the display reference for subsequent work.

## 2. Import materials without accidental recoloring

Use [the map template](templates/material-map.csv) to record each actual source.

| Input | Import/check | Do not assume |
|---|---|---|
| Base color | Color/sRGB sampling; original accepted map; white color factor unless source factor explicitly differs | A normal or mask map is color data |
| Normal | Normal-map import; verify orientation on a known light/view | Flip green or scale strength solely because an older asset did |
| Roughness | Linear/non-sRGB mask; actual exported channel | Every provider uses the same packed channel convention |
| Metallic | Linear/non-sRGB mask; read source material binding | A colored metallic surface should be white or uniformly metal |
| Occlusion | Read exported binding; compare with/without contribution for double-darkening | Multiply it into the base-color image or blindly add extra baked AO |
| Opacity/transmission | Separate recorded material property; start from accepted appearance | A painted glass texture proves true transmission exists |
| Emission | Only the source/approved design's explicit region or authored ability effect | A dark imported object needs blanket self-illumination |

For GLB/glTF, inspect the actual material JSON and texture bindings. Metallic and
roughness are commonly packed, but provider-exported FBX/texture bundles must be
checked individually. Preserve UV channel, texture orientation, material-slot order,
source factors and normal convention. Fix an incorrect importer setting before
editing the material's artistic response. Any deliberately changed roughness,
normal response or glass treatment is recorded and visually compared even when
the base-color texture remains unchanged.

**Bellback caution:**
[import_production.py](../../support/tools/bellback_production/import_production.py)
contains a muzzle tint and modified roughness/normal response;
[refresh_visual_r2.py](../../support/tools/bellback_production/refresh_visual_r2.py)
adds emissive brightness. These are historical candidate recipes, not this standard.
Read them for transport lessons; create a new controlled material for the comparison.

## 3. Lighting procedure in the current renderer

Current source at adoption uses DX11, manual camera exposure, one directional light
and a movable Sky Light; Lumen and virtual shadow maps are disabled in the project
configuration. Check the actual settings again before editing. Do not switch renderers
or enable expensive features merely because an online tutorial assumes them.

1. Duplicate/isolate the review environment and material references. Preserve the
   old accepted captures/package. Record all starting settings in
   [lighting-profile.json](templates/lighting-profile.json).
2. Supply a known neutral environment for ambient illumination. Verify that the
   Sky Light really captures valid sky/environment data, or use a specified neutral
   cubemap with documented rights. A painted background plane is not proof of useful
   ambient illumination. A near-black captured environment cannot be fixed reliably
   by guessing a larger intensity.
3. Raise useful diffuse fill until shaded faces and legs are readable. Check the
   lower hemisphere and overlapping body parts. Maintain depth through gentle
   directional contrast; avoid washing out the source colors.
4. Adjust the main light to a restrained neutral key. Confirm pale surfaces retain
   detail. Keep light color, exposure and white balance stable across comparisons.
5. Evaluate actual shadow support in this renderer. Use supported soft shadowing
   or a controlled soft contact-shadow representation. If harsh creature cast
   shadows cannot be softened adequately in the current path, compare reduced/
   disabled cast shadows plus restrained contact grounding as a separate candidate.
   Merely increasing directional Source Angle is not a universal dynamic-shadow fix.
6. Reduce excessive ambient occlusion and other darkening only after separating
   their contribution in diagnostics. Retain enough local depth to read overlapping
   parts; avoid a black halo or broad black pools beneath every creature.
7. Check reflections on ceramic, stone, brass and glass. Avoid clipped white patches,
   colored environment contamination and reflections that hide the source palette.
8. Repeat on the real board, both team orientations, single model and twenty models.
   Check the pale board and backdrop as well as the creatures. Measure performance.

Use named revisions such as `look_r001`, not endlessly changing one shared light.
Change one major variable group at a time (ambient, key/shadow, AO, reflection).
Capture matched before/after evidence so the cause of improvement is visible.

## 4. Grounded and hovering variants

Grounded creatures use a soft compact contact shadow and visible foot/root contact.
Do not raise the whole actor to conceal bad deformation: test the actual skinned
soles against the board surface. Rooted gardens and low predators must remain readable
inside their inner-leg shadows.

Prism Organ and Reefglass need an agreed hover height and a soft shadow positioned
to explain that separation. Their hover motion must not drive selection bounds or
authoritative cell position. Keep translucency from erasing their silhouette.

## 5. Freeze the approved collection look

Required evidence: original map hashes; source viewer image; diagnostic color view;
lit studio and board captures; actual material graph/settings; light/AO/exposure/
reflection values; camera/resolution; renderer/engine version; performance result;
owner's exact review decision and intended use.

Save the actual UE material/environment assets and the lighting-profile record.
Hash the profile and dependencies. Later heroes reference this accepted profile
instead of being tinted independently. If a hero looks wrong under the shared look,
first diagnose import/map/normal/geometry differences; do not silently change the
global profile or individual pigment to compensate.

Open decisions at handbook adoption: actual environment cubemap, numerical light
intensities, shadow method, AO amount, reflection treatment and final reference
captures. They will be resolved by G1 measurement and owner review. There is no
approved numeric lighting preset yet.

## Official references — checked 21 September 2026

- [Epic Sky Lights](https://dev.epicgames.com/documentation/en-us/unreal-engine/sky-lights-in-unreal-engine): environment capture/cubemap and grounding options.
- [Epic shadowing](https://dev.epicgames.com/documentation/en-us/unreal-engine/shadowing-in-unreal-engine): choose a method supported by the actual rendering configuration.
- [glTF material specification, Khronos source](https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc): inspect source factors and texture channels when interpreting GLB.

These sources describe capabilities; none is evidence that the new Wonder Chess
lighting profile has been implemented or accepted.
