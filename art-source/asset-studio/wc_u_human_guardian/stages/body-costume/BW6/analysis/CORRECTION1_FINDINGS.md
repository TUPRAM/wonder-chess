# Correction 1 independent fit localization

Reopened `../armor/ada_bw6_torso_correction1.blend` read-only and reproduced the owner's frame-1 transverse triangle queries. Exact source hash and full crossing points are recorded in `correction1_localized_crossings.json`. Counts below are triangle pairs, not numbers of independent defects. They do not cover coplanar overlap, containment or unsampled motion.

Viewed actual `correction1_front.png` and `correction1_coat_only.png`. The waist spikes and buried upper plate seen in the initial source are visibly improved. The collar-only silhouette is smooth; the jagged interior seen in the assembled view therefore needs separation from inherited body/head neck-cut context. The torso and collar remain unapproved.

| Pair | Confirmed pairs | Located region |
|---|---:|---|
| Coat vs body | 1,833 | All within absolute X<168.45 mm; none in sleeve region absolute X>230 mm |
| Of those: neck/upper shoulder | 1,091 | Z=1.46377–1.52443 m |
| Of those: torso | 530 | Z=1.16040–1.29858 m |
| Of those: waist/hem | 212 | Z=1.08940–1.15941 m |
| Navy vs coat | 130 | Low anterior corners: Z=1.07181–1.09508, absolute X up to .14487, Y=.06077–.08462 m |
| Left side enclosure vs body/coat | 162 / 304 | Underarm/armhole: absolute X=.1725–.2111, Z=1.3231–1.4210 m |
| Right side enclosure vs body/coat | 162 / 331 | Underarm/armhole: absolute X=.1710–.2110, Z=1.3137–1.4209 m |

The coat/body failures cannot be attributed to retained distal sleeves. Region bins above are explicitly defined geometric thresholds, not exact topological ownership labels.

The new collar intersects near raw faces 1209, 1229 and 1242. Face 1209 spans X=-.10808 to -.09419, Y=-.03028 to -.00744, Z=1.47378–1.50177 m. Posterior-side faces 1229/1242 span Z=1.50630–1.54764. Their lower edge lies on the newly designed near-level collar ellipse; the annular bridge descends from the surrounding shoulder into that lower loop. This cuts the neck-base/trapezius volume. The proposed correction is a saddle-shaped lower interface that rises over the side/rear shoulders while retaining a lower front, with actual body/coat clearance throughout the bridge. Merely widening the top opening does not repair the base.

Surrounding faces also fail, so the repair region must extend beyond the new rings. Nearest face 516 is at the anterior neck base, and face 558 at the posterior left shoulder. Nearest-face localization is approximate and is not a claim of exact subdivision lineage; actual cage coordinates are included in the JSON.

Torso-side failures remain in broad front-to-back connecting faces. For example face 426 spans roughly X=.1202–.1502, Y=-.0791–.0959, Z=1.2708–1.2915. A contour can have vertices outside the body but a broad chord through it. Add deliberate outside surface routing around the lateral cross-section, not another independent axial fitting pass. The side armor fails for the same construction class, at higher underarm sections.

The navy failures are concentrated at its low front corners near the old garment hem. A new belt alone cannot be described as repaired underlying contact. Verify a deliberate overlap or reconstruct the corresponding underlayer interface and retain the original master.

No candidate was edited, no candidate seven-clip test was run, and no runtime or human acceptance is established by this analysis.
