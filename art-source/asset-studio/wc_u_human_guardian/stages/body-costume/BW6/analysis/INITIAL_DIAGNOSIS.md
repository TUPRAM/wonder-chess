# BW6 initial rest-surface diagnosis

Read-only source: `../armor/ada_bw6_torso_initial.blend`, exact hash recorded in `initial_decomposition.json`. Inspected actual `initial_front.png` and `initial_profile.png`. No source mesh was edited or saved by this analysis lane.

The vertical waist spikes belong to `BW6_PaddedCoat_Tailored`. They already exist in its rest cage. Disabling its Armature modifier leaves the sampled rays and bounds effectively unchanged (floating point differences around 1e-7 m). This does not diagnose bad skinning at frame 1; it diagnoses the authored rest surface.

Face 262 has vertices 373,367,359,365 at world coordinates (metres):

| Vertex | X | Y | Z |
|---|---:|---:|---:|
| 373 | .136960 | -.065093 | 1.221140 |
| 367 | .147403 | .111364 | 1.229417 |
| 359 | .150018 | .114897 | 1.247699 |
| 365 | .142639 | -.060516 | 1.241533 |

The adjacent surface travels about 180 mm in depth across a narrow lateral strip. Mirror face 800 shows the same defect. A subsequent check of the actual edit record rules out an initially suspected wrong back-surface hit: none of the fitted points moved to negative Y. The negative-Y vertices above are retained rear/lateral geometry. Exact nearby body rays miss, leaving outer-front vertices at the old Y around .11 m while inner neighbors were moved to .04–.08 m. For example, source vertex 398 moved from Y=.106181 to .040610 at X=.128724,Z=1.189422; the nearby retained front-side point is still Y=.103416 at X=.141263,Z=1.188238. This non-monotone section creates the ridge. The demonstrated defect is missing continuous lateral fitting across the ray-miss boundary. Reconstruct continuous front/lateral sections rather than increasing smoothing or normalizing existing weights.

The upper plate is also physically behind the padded coat. At X=.130, Z=1.450 m, evaluated anterior intersections are body Y=.022856, coat Y=.041873 and plate outer Y=.028069: the coat lies 13.80 mm in front of the plate. At X=.130,Z=1.400, the outer plate is only .23 mm beyond the coat before accounting for the 3.5 mm inward wall. The uniform lateral depth drop used for every plate row is too strong for the upper clavicle rows. Correct those section-specific sidewall routes and inner-wall clearance; do not enlarge the entire plate.

At X=.130,Z=1.120, coat Y=.081136 but navy Y=.056808. The coat protrudes about 24.33 mm through the waist envelope. At X=.150 on the same section the difference is about 57.44 mm. This is another envelope mismatch, not an invitation to enlarge the belt or hide the coat.

Priority: repair continuous rest garment sections, fit the upper plate's inner surface against the resulting padded clavicle, then recheck the connected collar/base and waist. Keep source body proportions unless an actual remaining conflict demonstrates why a local candidate body change is useful.
