# AS1 Blender helper fixture: actual capture review

Reviewer: Codex tool-verification agent. Review date: 2026-09-08.

This is a tool fixture review, not an Ada reference, modeled-form, motion or asset approval. The fixture was authored in a new factory-startup background process. No existing Ada source or active GUI scene was opened.

The reviewer received and inspected all eight actual PNGs with the local image viewing tool: front and three-quarter material/clay captures from the original runner, then the same four captures from the corrected isolated runner. Paths and source hashes are recorded in the adjacent render metadata and execution results.

| Final capture | Actual observations | Result within this fixture |
| --- | --- | --- |
| `final-renders-material/front.png` | Blue upright box on the left, red sphere on the right, both visible against a dark background. Straight front camera and expected framing. | Expected geometry and materials visible. |
| `final-renders-material/three-quarter.png` | Top and side of the box become visible; sphere slightly overlaps the box in projection as expected from the changed camera. | Camera change produces the expected view. |
| `final-renders-clay/front.png` | Both forms become neutral gray while retaining the front framing and surface shading. | Clay material override visibly works. |
| `final-renders-clay/three-quarter.png` | The same three-quarter geometry remains visible with neutral surfaces. | Clay override and alternate camera work together. |

All final images are 384 by 384 pixels. The source uses a deliberately simple weighted box and an unskinned sphere; the sphere is intentionally elevated. There is no floor, no character, no continuous movement, and no claim of presentation quality. Eight Cycles samples are sufficient for this bounded functional capture test and are not a production review preset.

The hash-checked calibration image is an editor reference empty with rendering disabled. Its absence from these model renders is expected. Its stored image dimensions and semantic identity were separately confirmed by the reference collection audit.

No artistic gate or human approval was entered in an AS1 ledger.
