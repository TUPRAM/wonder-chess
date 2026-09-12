# Method 14 modifier and fit separation

Read-only source `../armor/ada_bw6_torso_monotone_coat.blend`; its hash is in `monotone_localized_and_self.json`. Inspected actual `monotone_front.png`. This candidate is not viable as a combined assembly: front/back plates and navy intersect the revised coat extensively.

At rest the raw coat has the same 14 underarm/lateral transverse self pairs as the original BW5 cage. The evaluated outer surface with both Shrinkwrap and Solidify disabled has **zero** self pairs and only **12 body pairs**, localized to the right underarm at X=.16572–.16651,Z=1.34818–1.34970 m. This is materially cleaner than the prior reconstructed collar surface.

| Frame-1 coat stack | Body pairs | Self pairs |
|---|---:|---:|
| Evaluated outer surface, no Wrap, no wall | 12 | 0 |
| OUTSIDE 18 mm, no wall | 0 | 224 |
| No Wrap, final 6 mm inward wall | 12 | 231 |
| OUTSIDE 18 mm then inward wall | 0 | 1,187 |

Of the 224 projection-only self pairs, 182 lie above Z=1.49 around the collar and 42 below around the underarm. Of the 231 wall-only pairs, 166 are collar and 65 underarm. These bins are geometric localization, not independent defect counts. Both modifiers independently fold tight local transitions. The clean outer surface is useful; neither broad projection nor the current offset wall establishes a usable final garment. Rebuild the local curvature or controlled inner surface and address actual localized body conflicts before reapplying global constraints.

The full-stack coat/body pairs at frames 20/49 are 36/8, in the moving right sleeve. Those remain when Solidify is disabled: the projected outer faces themselves cross the body between their vertices. This native projection is not continuous surface collision resolution.

At rest, front/coat has 1,614 pairs, back/coat 528, navy/coat 1,700 and navy/front 254. At frame49 front/back counts rise to 1,652/532. Those fit defects are separate from the coat's modifier-induced self folds. The owner's observation that long source faces miss the intended depth warp between control vertices is consistent with these actual surfaces; new semantic section cuts should be reviewed at the evaluated surface before relying on the profile function.

All ten other owned parts pass the same raw/evaluated self screen at rest. Only frames 1,20,49 were probed; no full97, canonical candidate clips or Unreal test was performed. No source file was saved.
