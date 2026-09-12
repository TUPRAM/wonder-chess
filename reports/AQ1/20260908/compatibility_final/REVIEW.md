# Ada AQ1 final candidate compatibility reconciliation

Status: **compatibility records reconciled; AQ1 candidate is not packaged and is not approved by Pram**. This is a read-only audit of existing execution records and fresh local file hashes. This lane did not launch Blender or Unreal, change geometry, alter gameplay, or remeasure the imported asset.

The current source is `art-source/heroes/wc_u_human_guardian/candidates/AQ1/ada_baked_r07.blend`, with editable forms in `ada_forms_r08.blend`, exports under `exports/r07`, and imported candidate assets under `game/Content/WonderChess/Candidates/AQ1/Ada_r01`. Git HEAD remains `9623fd82f98ff80a90985b9f552d8851ccece30f`. Hashes, input record identities, individual checks and resolved paths are in `review.json` beside this review.

## Fresh file verification

| Boundary | Result |
|---|---|
| Baseline canonical Ada source, before-copy, supplied illustration, units, rules, traits and asset manifest | 7/7 hashes match the retained baseline |
| Latest r07 FBX/texture exports | 11/11 hashes match r07 export manifest |
| Latest imported Ada candidate binaries | 14/14 hashes match both reimport-r03 and cold-r03 |
| Baked source, form source, export manifest, cold-to-reimport report link | 4/4 hashes match |
| Normal-probe sources/captures | 10/10 recorded hash comparisons match, covering seven unique files |
| r04 actual Unreal animation PNG frames | 150/150 hashes match the encoder's retained source index |
| r04 encoded MP4 clips | 7/7 hashes match |
| Resolved current evidence/content paths | 844 exist; zero missing |

The 604 protected content paths in the import records exist. The import and cold-load records both report empty protected differences. This lane did not freshly hash all 604 protected content files; that broader before/after protection claim remains tied to the actual importer records.

## Geometry, rig and material reconciliation

The executed Blender load record identifies `SK_AQ1_wc_u_human_guardian` as **12,899 mesh vertices and 24,280 triangles**, with one atlas material. The executed Unreal cold-load record reports **22,803 LOD0 render vertices, 27 bones and one LOD**. The higher Unreal vertex count is a different measurement boundary; do not substitute it for Blender's mesh vertex count. The geometry counts agree with the prior r06 candidate. These counts are read from executed records whose artifact hashes were freshly checked, not inferred from filenames or independently remeasured in this audit.

The imported mesh now retains **two material-slot names**, `HeroAtlas` and `M_AQ1_Ada_Baked`. Both refer to the same candidate material instance. Its actual LOD0 has **one section**, which uses slot index 1. The older compatibility review's statement of one imported material slot is stale after reimport. The valid final claims are one source atlas material, two retained imported slots, and one actual render section. Slot count alone is not a draw-call measurement.

The before and latest Blender load records and the r07 export manifest have identical rest-skeleton and action invariant hashes. All seven imported timings match their expected durations within a one-microsecond tolerance:

| Clip | Expected seconds | Imported seconds |
|---|---:|---:|
| Idle | 2.00 | 2.00 |
| Move | 1.00 | 1.00 |
| Attack | 0.65 | 0.649999976 |
| Active | 0.60 | 0.600000024 |
| Hit | 0.40 | 0.400000006 |
| Defeat | 1.00 | 1.00 |
| Victory | 1.50 | 1.50 |

Each importer clip record contains five compressed-pose samples. Those samples are structural checks, not continuous animation approval. The 24,280-triangle candidate exceeds the 15,000 target and stays within the 25,000 comparison experiment ceiling; acceptance of this exception remains pending. LOD1 and LOD2 are not produced.

## Reimport, texture encoding and normal orientation

`reimport-r03.json` records a deliberate import of `ada_baked_r07.blend`, with `reimport=true`, the same mesh identity and the same skeleton identity. `cold-r03.json` was produced by a separate process and records `PASS_SEPARATE_PROCESS_MATCH`. The candidate hash maps and measurement records are equal across these two processes. The baked source hash is `cd6bb6ddb3a54aaa15be3112a804caf0820f9ad1162b7cb8ee345f646bef8a67`; the export manifest hash is `4aa7e2dbc0d779587d6702b31ad83ec0ce2f9b78abcd59929cb50ced10a32ab7`.

Actual PNG headers confirm all three maps are 1024 square: BaseColor is RGB8, Normal and ORM are RGB16. Unreal's recorded BaseColor sRGB flag is enabled; Normal and ORM use linear sampling. The normal uses the normal-map compression setting and one green-channel flip. Normals are imported from FBX and tangents computed with MikkTSpace.

The importer records retain an earlier pending normal-orientation field. The later `normal_probe_unreal_r06/orientation-review.json` supplies the actual asymmetric raised-control comparison and selects **flip**. That later narrow test resolves the orientation comparison for this Blender +Y bake/imported-normal/Mikk configuration; it is not blanket approval of all Ada shading. The earlier failed/incomplete probe attempts remain retained.

The r07 export manifest retains its export-time author-script hashes. Fifteen match the current scripts. `aq1_bake.py` differs: export-time `77da13b18529d007c536cadb681848baf9e342c40f44914da9def446c04c1c68`, current `b7b4c325f264f25cb181a027e12ccaff9251de69438ffa118131e757e1a091e4`. This known later helper revision is recorded as provenance drift; the frozen export metadata was not rewritten to imply that the later helper produced the earlier artifact. All delivered source/export/import artifact hash links still match.

## Latest motion-readiness evidence

The r04 Unreal capture record reports all used textures fully streamed before capture for each of the seven clips. The initial Idle readiness wait is approximately 0.13646 seconds; later clips record waits of approximately 0.00633–0.00777 seconds. This is explicit execution telemetry, not an inferred wait based on file timestamps. The recorded required/captured counts, actual CSV rows and PNG counts all match: Idle 41, Move 21, Attack 14, Active 13, Hit 9, Defeat 21, Victory 31, totalling 150.

The r04 encoder reports `ENCODING_PASS_REVIEW_PENDING`, seven 1920-by-1080 MP4s at 20 fps, and unchanged source frame bytes. The endpoint frame adds 0.05 seconds to each movie's duration; it does not change the animation's authored timing. Fixed 20-Hz game steps and movie encoding are not wall-clock performance measurements, audio listening, human continuous playback, or art acceptance. Consult the separate visual-review records for what was actually viewed. The first-frame facial-noise interpretation in the earlier r03 assessment was already corrected using later frames; no AO source change was made to achieve that clearing.

## Remaining acceptance boundaries

- Pram's approval of Ada against the selected reference remains pending; bulk rollout is not approved by this audit.
- The candidate has no new packaged executable or packaged-match proof. Existing game packages must not be described as an AQ1 package.
- LOD1/LOD2, the triangle-budget exception, final closeup/reference refinements, and any unresolved animation/contact issues remain subject to their specific art reviews.
- This reconciliation does not establish audio acceptance, full human matches, physical LAN verification, or performance approval. Use the dedicated execution reports for those gates; this read-only audit cannot promote them.

