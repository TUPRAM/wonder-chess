# BW3 frozen BW2 onset diagnosis — read only

**Finding:** the source thumb route enters the fixed handle well before the first detected hand self-crossing. The thumb alone then folds into the palm even when index through little are held fully OPEN. Neighboring-finger closure is not required to produce the thumb failure. The first useful correction is therefore an external thumb-base/opposition route and its surface response, before renewed pad-contact fitting. This does not yet prove that weights, rest shape, or pivot placement can remain unchanged through a corrected route.

Source: `BW2/r001/ada_bw2_grip_checkpoint_r001_ART_REVISE.blend`, SHA256 `d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf`, unchanged after all diagnostics. Action: `BW2_RIGHT_GRIP_CARRY_DIAGNOSTIC`. Blender 5.1.1 background only. No live MCP, source save, optimization, weight edit, rest-geometry edit, or new grip was performed.

## First source-motion onsets

Each interval below is **last preceding sampled non-crossing frame → first sampled crossing frame**, refined to quarterframes. It bounds the sampled onset; it is not a certified continuous-time collision time.

| Source surface | Thumb / palm | Thumb / index-middle region | Middle / ring |
|---|---|---|---|
| Glove, evaluated level 1 | 14.75 → **15.00** | 17.00 → **17.25** | 16.00 → **16.25** |
| Glove, posed raw cage | 14.00 → **14.25** | 16.25 → **16.50** | 14.50 → **14.75** |
| Body, evaluated level 1 | 15.00 → **15.25** | 18.00 → **18.25** | 18.75 → **19.00** |
| Body, posed raw skin cage | 11.00 → **11.25** | 17.75 → **18.00** | 17.50 → **17.75** |

No confirmed transverse self-crossing was found at frame 1 in these four surfaces. The earlier raw-cage failures establish that the deformation problem begins before the smoothed surface visibly cuts through; they do not, by themselves, prove that the rest topology is unusable.

| Glove / ideal fixed cylinder | Raw posed cage | Evaluated level 1 |
|---|---|---|
| First positive triangle penetration | 3.00 → **3.25** | 3.25 → **3.50** |
| First triangle penetration greater than 0.5 mm | 3.25 → **3.50** | 3.50 → **3.75** |

The fixture retains the original radius 14 mm, span 109 mm, usable span 105 mm, and wrist-relative frame. No body-versus-handle query was performed by this onset script; the body columns concern self-crossings only.

## Frame 14 vertex 6670 is the distal thumb

Actual evaluated weights are `finger1-3.R = 0.9854528904` and `finger1-2.R = 0.0145471003`. It is not an assumed label from the contact JSON.

Its frame 14 hand-space position is `(0.027941342, 0.103029874, 0.039690054)` metres, close to the fixed cylinder's centerline. The evaluated glove minimum signed-cylinder vertex distance is about **−13.9069 mm**, reproducing the supplied approximately −13.9067 mm result within evaluation/transform precision. Incident evaluated triangles are 11241, 11246, 11247, 13617, 13622, 13623.

The first evaluated thumb/palm crossing at frame 15 is between triangles **15859 and 17352**, with vertices `[6802, 5569, 8840]` and `[1956, 5105, 9027]`; the confirmed intersection is near hand coordinates `(0.034500, 0.077165, 0.018256)` m. The first middle/ring example at frame 16.25 is triangles **9288 and 9917**, near `(-0.021692, 0.129361, 0.062426)` m. Exact examples are in `onset_results.json`.

## Verified thumb-only isolation

For each sample, the source action was evaluated, all pose-basis matrices captured, and the action detached **only in memory**. The sampled source thumb/arm matrices were assigned explicitly; fingers 2–5 were fixed to their recorded frame 1 OPEN matrices. Evaluated non-thumb basis matrices were asserted OPEN before testing. This prevents the action from silently reapplying curls during evaluation or render.

The isolated thumb reproduces the same glove thumb/palm onset, the same handle-entry onset, and the same frame 14 deep distal-thumb penetration. It also reproduces the body's thumb/palm onsets, including raw-cage frame 11.25. Middle/ring crossings disappear at every tested isolated sample. Thumb crossings with index/middle-weighted base surfaces remain; those region labels are approximate deform ownership and should not be interpreted as proof that an extended distal index finger is being hit.

The thumb's frozen-pad center moves from hand-space Z **+61.116 mm** at OPEN to **+25.699 mm** at frame 25; the cylinder center is at Z **+39.601 mm**. Its path crosses the handle and ends on the palm-side/negative-Z side of that cylinder. The individual worst thumb vertex reaches Z **+39.690 mm** at frame 14 and **+15.022 mm** at frame 25. This is direct surface evidence supporting a different external route. It does not establish a unique alternative set of angles.

Six actual `isolated_verified_*` images were rendered and inspected: glove at frames 1, 14, 15, 25 and body at 15, 25. The frame 25 body and glove show the same long thumb fold while all four other fingers remain visibly open. Use those images for isolation evidence.

An earlier render attempt allowed the original action to reapply other-finger curls during render. Its six images are retained with the explicit prefix **`REJECTED_NOT_ISOLATED_`**. They are not valid isolation evidence. `thumb_isolation_trajectory_verified.json` and the final `onset_results.json` supersede the unverified intermediate records.

## Decision supported by the evidence

Start with a deliberate external thumb route on the independent BW3 derivative: clear the palm and the fixed fixture before the sweep toward opposition, then add flexion. Test the actual posed web/body/glove response before deciding on local skinning or rest-surface reconstruction. The baseline shows that changing only the neighboring fingers' closure order cannot solve the thumb failure.

Middle/ring clearance is a second independent relationship: it appears later and vanishes when those digits are OPEN. A staged closure or proximal spread adjustment is a reasonable hypothesis for that relationship, but no alternative sequence was tested by this read-only diagnosis. Do not rank improved pad distances above these collisions.

The retained source remains ART_REVISE. No new candidate or correction was approved by this audit.

## Coverage and numerical limits

The final record contains **263 surface-state evaluations**: all 25 integer frames for two trajectories × two objects × two surface levels (200), plus 63 adaptive quarterframe evaluations around first onset intervals. The existing BW2 triangle routines were reused; no new general collision framework was introduced.

The posed raw body test disables helper/display/subdivision modifiers in memory and explicitly restricts triangles to the body's skin group. The evaluated test uses the normal active level-1 surface. Topological neighbors sharing a vertex are excluded from self-crossing classification. Nonadjacent transverse edge/triangle intersections are confirmed, while coplanar contact, tangency and fully contained regions without transverse intersections are not certified. Dominant deform-group ownership is an approximate anatomical classifier.

Cylinder tests include triangle interiors against the ideal capped cylinder, not just the frozen pad samples. The display fixture's 96-sided surface differs radially by up to approximately 0.0075 mm. Quarterframe sampling improves onset localization but is not continuous collision certification. This task does not cover frames 26–145, new routes, glove/body inter-surface fit, sword integration, or runtime acceptance.

Files: `onset_results.json`, `thumb_isolation_trajectory_verified.json`, `audit_onset.py`, `audit_onset_verified_isolation.log`, `render_thumb_isolation.py`, `render_thumb_isolation_verified.log`, and the six `isolated_verified_*` renders.
