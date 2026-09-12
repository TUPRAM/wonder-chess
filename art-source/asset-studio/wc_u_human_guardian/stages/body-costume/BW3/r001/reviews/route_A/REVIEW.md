# Route A initial thumb trajectory — REVISE

The external route delays the previously observed collisions but still drives the thumb through the fixed handle, followed by palm/thumb folding. The failure occurs with digits 2–5 actually open, so closing those digits is not its cause. The current endpoint must not be extended into an integrated grip.

Source: `thumb_route_A_initial.blend`, SHA-256 `f7d42c9f6c04948d54745439de5a288979c2cbb922e11d0b64386d80c0aa1a3a`. The source hash is unchanged after the read-only background Blender evaluation.

Executed every integer frame **1–25**, onset half-frame samples, and endpoint **145** on the actual evaluated derived glove and underlying body. Digits 2–5 were asserted open at every sample; their maximum basis-matrix error was **0.0**. No actions were detached, poses overridden, parameters optimized, modifiers changed, or `.blend` saved.

| Event | Glove first detected / preceding clear sample | Body first detected / preceding clear sample |
| --- | --- | --- |
| Triangle enters handle | 16 / 15.5 | 16.5 / 16 |
| Triangle penetrates deeper than 0.5 mm | 16 / 15.5 | 17 / 16.5 |
| Palm/thumb transverse crossing | 20 / 19.5 | 17.5 / 17 |
| Thumb crossing another digit | None detected | None detected |

These are sampled onset intervals, not continuously solved contact times. The exact reused triangle/slab query confirms handle entry; the quoted penetration extrema below are vertex measurements rather than maximum triangle-interior depth.

At both frames **25 and 145**:

- Glove: **51** confirmed nonadjacent transverse crossing pairs — **45 palm/thumb**, **6 thumb/thumb**. Worst evaluated hand vertex **3154** is **13.311875 mm** inside the handle.
- Body: **49** pairs — **43 palm/thumb**, **6 thumb/thumb**. Worst evaluated hand vertex **1467** is **13.496122 mm** inside the handle.
- The nine stored distal-thumb pad samples have gaps **0.288776–5.121794 mm**, median **2.419617 mm**, p95 **4.809618 mm**. Only **3/9** samples lie in the −0.5/+1.0 mm band, although all nine lie inside the usable axial span.

Distal-pad proximity therefore does not establish a coherent contact pose: other thumb/web surfaces tunnel deeply while the endpoint pad is still mostly separated. The body begins self-crossing before the glove, which also makes glove-only visual judgment insufficient.

**Recommended focus for the one bounded correction:** preserve the fixed fixture and verify clearance of the entire thumb, including proximal/web surfaces, through the turn into the grip. Establish that before minimizing distal-pad gaps. If a further trajectory correction cannot maintain that clearance without collapsing the web, retain the best study and move to the planned local thumb/web surface or deformation reconstruction rather than another unconstrained angle search. This recommendation is an inference from the observed order and location of failures; no alternative correction was tested here.

The queries reuse the checked BW2/BW3-onset code. Region names use dominant deform-group weights as approximate anatomical labels. Shared-vertex triangle pairs are excluded; coplanar overlap and tangential contact are not classified. The hand-region bounds exclude unrelated torso/left-hand geometry. No artistic approval, runtime claim, or integrated-grip pass is issued.

`route_A_summary.json` provides the concise results. `route_A_results.json` retains every integer/half-frame observation, representative crossing triangles, pad distances, and source hash. `route_A_audit.log` records execution progress.
