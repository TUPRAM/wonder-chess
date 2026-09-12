# Local correction preservation and source-scope review

Completed: 2026-09-08T14:49:46.951547+00:00

**Protected files: PASS — 10/10 hashes match.** This includes the previous nine MR1/r003/reference/FH1 protected files and the frozen HP1 r014 checkpoint. The r014 SHA-256 remains `95f8c084c97914a9a6ab198764a3ba80f478dac6fbd8e5b3cc8132d37599d851`. All reads had stable size and modification time. The intentionally mutable HP1 work file is excluded from this immutable comparison.

**Source scope: pass with an explicit shared-midline exception and runtime limits.** All six current local Python files were manually reviewed and parse successfully: both attempt scripts, both render helpers, the audit, and cage-and-freeze.

Attempt 1 targets only explicit anatomical-right orbital, nasal sidewall, columella-flank and upper-lip-support cage controls. Its 138 declared target IDs all lie inside the stated local coordinate bounds in the supplied baseline snapshot. These are static source targets, not a claim about effective live changes.

Attempt 2 targets selected right lid/philtral controls **plus five shared midline profile controls: 767, 248, 1098, 1064 and 1030**. Those control columella/philtrum/upper-lip support. Its 44 direct target IDs remain within the local bounds, with no negative-X targets. The two scripts together declare 143 distinct target IDs. Negative-X cage coordinates are asserted fixed, but adjacent subdivided faces on both sides can respond to the shared midline. Therefore this must not be reported as strictly right-only or zero opposite-side surface propagation. Parent acknowledged the exception; this review does not independently certify user authorization.

No reviewed local source contains broad smoothing, a geometry mirror operation, Mirror modifier, or propagation of the correction across the face. The scripts recalculate normals on candidate copies. They do not modify original hair, braid, eyebrows, eyelashes, torso, armor, original material contents, infrastructure or gameplay. Diagnostic light mirroring and eye visibility changes are restored with try/finally.

The cage script works on separate mesh/camera/light copies, reuses the diagnostic ink material without editing it, and freezes a new r016 checkpoint. It does not write the r014 checkpoint.

**Limits:** This review uses filesystem hashes, source text and the supplied baseline JSON. It neither accesses Blender nor evaluates meshes, executes scripts, inspects final pixels or issues artistic/human approval. Root retains responsibility for actual Blender scope and visual evidence.

[Machine-readable hashes and source targets](preservation.json)
