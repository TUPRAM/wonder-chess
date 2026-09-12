# Interface work: source comparison and exact residual defects

All inspection was read-only. `outside_localized_and_self.json` belongs to the now-superseded `ada_bw6_torso_outside_work.blend`, which the owner identified as having an unsafe last-N-vertices collar edit. `interface_localized_and_self.json` belongs to `ada_bw6_torso_interface_work.blend`. Exact hashes are embedded; neither result is interchangeable with a subsequent candidate.

The same existing nonadjacent transverse-triangle self screen at frame 1 gives:

| Source coat | Raw cage pairs | Evaluated pairs |
|---|---:|---:|
| BW5 r003 retained coat | 14 | 0 |
| BW6 correction 1 | 178 | 1,816 |
| BW6 interface work | 270 | 2,911 |

These are pair counts, not independent defect counts, and do not certify coplanar overlap, tangency, containment or continuous time. The BW5 raw failures lie around the lateral torso/underarm. The major neck failures were introduced in BW6. Raw lower-torso pairs increased from 14 to 52 in correction 1 and remain 52 in interface work.

Exact raw examples:

- BW5: faces 842/862 cross near (-.17447,-.07359,1.35517) m.
- BW6 correction 1 and interface: faces 628/863 cross near (-.17936,-.08500,1.34902) m. Broad underarm faces 863 and 325 are repeatedly involved.
- Interface: retained anterior-neck face 381 crosses new faces 1103–1105 and 1141–1143. Face 381/1141 crosses near (.04147,.03219,1.48474) m.
- New interface rings intersect each other: 1141/1143 crosses near (.04409,.03964,1.47653) m, and 1141/1181 also crosses. Actual polygons, vertex IDs and world positions are retained in `coat_self_provenance.json`.

The ring construction has a concrete angular correspondence failure. Its ordered outer loop winds -360 degrees, but six consecutive angle steps reverse direction: approximately +.255, +.255, +7.432, +2.120, +2.120 and +8.111 degrees. Outer vertices 558→564 and 19→13 are the largest reversals. Reusing each outer vertex's `atan2` for every new ring reproduces these reversals in the collar tube. Sorting vertex IDs would destroy correspondence. The appropriate intervention is a new monotone circumferential loop and a reconstructed bridge against a clean outer boundary; the existing folds cannot be repaired by an outside-body projection.

On interface work, the whole-coat OUTSIDE modifier has no vertex-group restriction. Its influence therefore applies everywhere; earlier hard-coded group diagnostics were corrected to report effective influence 1.0. At frames 1,20,49, the outer coat without final Solidify has zero transverse body crossings. With the 6 mm inward wall restored, frames 20/49 have 60/52 sleeve crossings. Thus this source's remaining body contacts are wall clearance, unlike the older outside_work's unprotected outer sleeve contacts. They are at X=.3154–.3521,Z=1.2588–1.3010 and X=.3614–.3786,Z=1.3814–1.4161 m. This does not resolve the separate coat self-folds.

All other 10 owned parts—plates, turned borders, side enclosures, navy and belt—have zero raw/evaluated transverse self pairs at frame 1. Coat evaluated self counts are 3,081 at frame20 and 2,133 at49. Only these three poses were checked in this lane; no full 97-frame or canonical seven-clip run was made.

Navy defects have two distinct locations:

- Low navy/coat contacts: interface work has 34 pairs at X±.14013,Y=.07420–.08013,Z=1.07431–1.08067 m. Repair the lower corner overlap locally; changing the upper silhouette does not address them.
- Upper navy/front-plate contacts: interface work retains 114 pairs at X±.10062,Y=.09938–.11993,Z=1.18641–1.19818 m. The prior outside_work had 372 and visible humps. This armor/underlayer pair was missing from the earlier body/coat-only matrix. Keep the visible waist below the hem, but fit the upper overlapping rows between the final coat and plate inner wall. The outside_work sample X=.075,Z=1.190 had coat Y=.10320, plate outer Y=.11372 and navy outer Y=.11923 m; the upper navy was 5.51 mm in front of the plate. Source-specific section data is in `outside_navy_sections.json`; do not reuse its exact coordinates after plate edits.

Recommendation: replace the failed local neck/underarm envelope construction rather than add more projection or smoothing. Retain the old master and the failure evidence. A clear body/coat query does not compensate for a self-crossing garment. These sources remain construction studies and do not establish art, runtime or human approval.
