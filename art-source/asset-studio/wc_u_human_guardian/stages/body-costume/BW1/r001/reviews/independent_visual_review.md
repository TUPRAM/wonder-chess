# BW1 independent visual review

Status: **ART_REVISE — full-body construction blockout, not forms approval.**

Reviewer: independent image-review agent. This first review inspected the images directly before reading any implementation scripts. No Blender calls, geometry edits, source reconstruction, or human approval were performed. The intentionally bald, already-revised head is excluded from body judgments.

## Evidence actually inspected

- `stages/references/ada_construction_r002.png`: approved construction reference supplied by the task owner.
- `stages/references/construction_decisions_r002.md`: explicit interpretation of the reference, including the rear split and three shaped shoulder plates.
- `captures/body_costume_r001_clay.png`: full-body three-quarter costume blockout.
- `captures/cloth_blockout_r000.png` and `captures/cloth_blockout_r001.png`: same-view cloth comparison.

## Three largest visible issues

1. **Armor planes and shoulder construction.** The breastplate is presently a broad, softly rounded rectangular panel. Its nearly straight upper and side boundaries and shallow front fail to establish the reference's neckline, sternum break, taper and side planes. The shoulder parts read as cylindrical bands around the upper arm rather than a shaped cap and overlapping smaller plates. This changes the guardian silhouette toward bulky sports padding. Focus the upcoming arm proof on one shoulder: define its crown and lower plate contours, then show the overlap together with the sleeve and raised arm. Keep the breastplate a blockout until that local proof works.
2. **Cloth volume and panel edges.** Cloth r001 is visibly cleaner than r000, but the torso and skirt now read as stiff slab-like forms. The skirt and tabard have broad, inflated edge rounding; the tabard tip is blunt and swollen instead of a clear pointed hanging panel. The sleeves show little distinction between padded fullness, elbow allowance and cuff gathering. Restore garment-specific volume in the proof sleeve, preserve a clear cuff opening, and give the tabard a thinner controlled edge and deliberate point. Do not add quilting to compensate for these forms.
3. **Footwear construction.** The current footwear is not yet a convincing closed boot. The visible toe/instep-side arrangement has gaps or incomplete enclosure, the instep armor forms a raised arc, and the sole appears as a simple flat platform with little heel/toe-box construction. The shin shell also has a broad open upper rim and an abrupt relation to the knee part. In the leg proof, establish an enclosing boot upper and toe box over a deliberate sole/heel, then articulate the greave and knee as separate protective parts. Show foot roll and ankle bend before judging the fit.

## Improvements supported by the cloth comparison

The r001 image removes the jagged shoulder and underarm openings visible in r000. It also reduces the breast-contour imprint and removes the large visible intrusion across the viewer-left front skirt panel. These are visible improvements and should be preserved. A stronger cloth envelope still needs fullness and controlled openings; the change does not yet establish finished tailoring.

The body reads as one coherent anatomical foundation, with continuous arms, hands and legs. There is no visible reason in these views to replace it with unrelated downloaded limbs.

## Evidence limitations

These are three-quarter views, so exact shoulder/waist/hip relationships, limb lengths, rear-panel split, breastplate depth, backplate fit and flat ground contact cannot be approved from this set. The reference is an illustration and is not registered to the Blender camera; no numerical proportion error is claimed. Front, profile and back views including the feet are still needed.

No grip or movement evidence was included in this initial review. An open hand beside the wrist cuff does not prove glove fit, thumb contact or sword/shield contact. Static gaps and intersections must be checked in the actual arm and leg pose evidence. No topology, skin weights, exported skeleton, runtime performance or reusable-recipe success was reviewed.

## Recommended next bounded action

Proceed with the requested single arm assembly and single leg/boot assembly. Prioritize the shoulder/sleeve interaction and closed boot construction over surface detail. Retain the cleaner cloth r001 envelope, and keep all full-character approval pending. Append a separate pose-evidence review after the actual views arrive.

## Addendum: r002 blockout and leg stance

Additional images actually inspected: `captures/blockout_r002_front.png`, `captures/blockout_r002_profile.png`, `captures/blockout_r002_back.png`, `captures/blockout_r002_three_quarter.png`, and `captures/leg_stance_r000.png`. No implementation scripts or live Blender state were consulted.

The expanded views establish a full-body A-pose blockout and show the intended rear tabard split. Preserve that split and the layered separation. The images still support **ART_REVISE**, not a convincing arm or leg proof.

The major remaining defects are:

- **Floating, planar armor construction.** In profile the front and back armor stand away from the underlying torso as thick panels; side closure, straps and attachment remain unresolved. The new breastplate facets are horizontal bands across a rectangular form rather than a sternum break and intentional curved side planes. The backplate remains a soft rectangle. Shoulder bands still lack a convincing cap and articulated plate contour. Faceting alone has not fixed the construction.
- **Stiff cloth and unresolved assembly edges.** The frontal tabard has a clearer point than the earlier rounded version, but the coat and hanging panels still resemble thick, smooth slabs. The collar/neck boundary and shoulder-neckline edges are visibly irregular. The broad torso and skirt remain coherent as placeholders; these views do not establish tailored thickness, armpit movement or independent hanging-cloth behavior.
- **Boot/sole and shin transitions.** The leg close-up shows a large, block-like sole whose outline does not consistently follow the boot upper. Its toe and heel relationships differ between the visible feet, and the upper-to-sole junction has irregular projecting edges. The greave is a thick open trough with a broad top rim, blunt bottom, and a weak transition toward the ankle. The knee plate is a pointed patch rather than a shaped cup with established overlap. Stance alone does not prove flexibility or stable planted contact.

One bounded construction intervention is worth attempting next: **replace one sole/heel with a small, closed footprint-following loft beneath the current boot upper.** Deliberately define toe width, heel outline, a restrained surrounding rim and a shallow sole/heel profile; do not uniformly enlarge the current slab. Preserve the master foot and separate boot, greave and knee parts. Inspect that one construction from front, side and back before spending effort on folds or fasteners. Its relation to the greave lower edge should then be judged in the root agent's ankle/foot-roll pose evidence, without making the whole assembly rigid to hide fit problems.

No numerical dimensional mismatch is asserted from these unregistered illustration/render comparisons. The new camera coverage resolves the prior absence of front/profile/back views, but still does not demonstrate grips, finger/ thumb contact, knee bend, ankle bend, walking range, collision-free motion, topology quality or second-body reuse. These acceptance observations remain not reviewed until actual evidence is supplied.

## Final bounded review: local trials and retained contextual candidate

Final status: **ART_REVISE. Neither the complete arm/grip proof nor the complete leg/boot proof passes this visual review. No recipe promotion, second-body success, completed forms, or human approval is claimed.**

Additional evidence actually inspected in this final review:

- `captures/footprint_sole_stance.png` and `captures/footprint_sole_ankle.png`.
- `captures/arm_pose_elbow_bend.png` and `captures/arm_pose_shoulder_raise.png`.
- `captures/leg_pose_move_range_step.png`.
- `captures/knee_attachment_stance.png`, `captures/knee_attachment_bend.png`, `captures/knee_attachment_kneel.png`, `captures/knee_pivot_kneel.png`, and `captures/knee_surface_stance.png`.
- `captures/candidate_context_front.png`, `captures/candidate_context_profile.png`, `captures/candidate_context_back.png`, `captures/candidate_context_three_quarter.png`, `captures/candidate_context_other_three_quarter.png`, and `captures/candidate_context_reversed_key.png`.
- `hand-pose-study/sword_grip_final.png`, `hand-pose-study/sword_grip_final_dorsal.png`, and `hand-pose-study/shield_grip_final.png`.

The final contextual views visibly contain a smooth knee cup on the anatomical-right leg. The author reports that this is the restored first thigh attachment (`upperleg02.R`), after rejecting and separately freezing later corrections. The visibly displaced/missing cup in `knee_surface_stance.png` and detached cup in `knee_pivot_kneel.png` are **failed experiment evidence, not the retained final candidate**. This reviewer inspected pixels, not the final Blender parenting data.

### What visibly helped and should be retained

**Continuous cloth enclosure:** the earlier r000-to-r001 change removed major static openings and skirt intrusion, producing a usable connected coat blockout. Retain that starting construction. Its static improvement does not establish dynamic clearance.

**Footprint-following sole:** on the anatomical-right boot, the new sole follows the visible toe/upper outline more closely and has less oversized platform thickness than `leg_stance_r000.png`. The ankle sample shows the sole rotating with the foot rather than remaining behind. This is a useful local construction improvement. It does not establish a complete boot: the heel/upper junction still has irregular edges and separation, and only a limited static pose sample was assessed.

**Layer separation and rear split:** separate cloth, armor, boot and knee components remain legible, and the rear split survives in the final back view. These are useful authoring decisions, not proof that the parts fit or move correctly.

### Exact remaining major defects

1. **Grip closure fails.** The isolated hand studies show curled fingers, but the cylinder is not convincingly enclosed between the fingers, palm and opposing thumb. The fingers curl below or away from the handle in the supplied palmar views; the dorsal view does not establish a stable anatomical grip. Full-character sword and shield images retain open contextual hands. Do not present those as successful equipment contact, and do not claim glove deformation from these bare-hand contact views.
2. **Arm assembly is not convincing.** Elbow and shoulder samples reveal large exposed cavities and abrupt sleeve/bracer transitions. The bracer reads as separate floating strips/open shells around the bent forearm, and the raised shoulder exposes the hollow band construction. There is no convincing demonstrated plate overlap and attachment through this range. Additional material detail would not fix it.
3. **Cloth fails leg clearance.** In `leg_pose_move_range_step.png` the lifted thigh visibly passes through the front/side hanging coat. The kneeling view likewise shows the forward thigh emerging through the panel. The blockout is therefore not movement-ready despite its improved neutral enclosure.
4. **Knee protection does not track the intended anatomy.** The first cup/strap construction sits above the exposed knee in bend and leaves a broad uncovered gap above the greave. In the kneeling test, its orientation and coverage do not form a convincing protective assembly. The pivot trial detaches the cup below the knee; the surface trial displaces it beneath the boot in the stance image. These later trials are correctly rejected. Restoring the first attachment avoids those specific regressions but does not pass knee coverage or kneeling behavior.
5. **Boot and greave remain incomplete.** The improved sole is worth keeping, but the boot upper/heel seam has irregular projecting edges, the greave retains a thick trough-like rim and blunt lower end, and there is no established knee/greave/ankle articulation. The other side still retains its larger placeholder sole; this unilateral difference is an honest study boundary.
6. **Major armor and tailoring forms remain blockouts.** The chest and back retain unresolved panel depth and side attachment; the chest facets remain bands rather than deliberate reference planes. The collar and shoulder-neckline show irregular edges. The coat, tabard and belt transitions are too slab-like. Both three-quarter directions and reversed lighting confirm these construction defects; they are not merely artifacts of one favorable camera/light.

### Stop decision and next method recommendation

Stop the current bounded corrections and preserve the best candidate at **ART_REVISE**. The useful retained findings are the connected foundation, cleaner cloth envelope, component separation, rear split and footprint-based sole. The local trials do not justify independent replay or a second-body fit as successful recipes yet.

The next assignment should isolate one complete hand-to-handle contact problem or one knee/greave articulation problem with an explicitly inspected joint/handle coordinate frame and small editable corrective construction. Treat those as new methods with their own evidence. Do not add more global shape tuning, decorative detail, neural training or a large tool interface around the currently failed assemblies.

No continuous video, source topology, weights, save/reopen behavior, third-party license, runtime skeleton, export, Unreal import or reimport was verified by this independent image review. The author and other reviewers may separately supply those results; they must remain distinct from this visual assessment.
