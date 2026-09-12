# BW4 fixed-hand save/reopen and preservation

**PASS for file preservation and geometry continuity only. ART_REVISE remains unchanged.**

Opened the correction2 source, final work, and frozen ART_REVISE checkpoint in a fresh Blender 5.1.1 background process with automatic script execution disabled. No live Blender session was accessed and no opened source was saved.

The final work and frozen checkpoint match correction2's complete raw and evaluated glove geometry, face/triangle indexing, all vertex-group names and weights, modifier settings including subdivision levels, world transform, and shape-key inventory. All three selected sword components were compared in the same way. The exact successful matches bind the existing correction2 collision report to the delivered files without rerunning the identical collision queries.

Protected-source hashes: 28/28 match the BW4 intake manifest. The three reopened candidate hashes also remain unchanged before/after inspection. Detailed signatures, per-object comparisons, file hashes, and protected paths are in `reopen_and_preservation.json`.

The root's 96-frame local camera turntable is presentation evidence of this fixed geometry. It is not execution of Idle, Move, Attack, Active, Hit, Defeat, Victory, wrist movement, candidate rig integration, or Unreal. Those gates receive no pass from this check.

The inherited BW2 `preservation_before.json` was also checked against current files: 62/62 hashes match. This explicitly covers the inherited reference, licensed glove/boot, MPFB/head/hair and relevant source inputs listed in that manifest; it is not an assertion that every project file was hashed. Combining the 28 BW4 intake paths and these inherited entries gives 77 unique protected file paths. The two lists overlap and must not be added as though all entries were distinct.
