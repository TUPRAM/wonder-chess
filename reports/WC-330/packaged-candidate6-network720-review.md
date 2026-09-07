# Candidate 6 — actual packaged 720p network visual review

Eight actual packaged combat screenshots were opened and inspected: host and client rounds 5, 8, 10 and 12. They come from the integration lane's `builds/Windows-Alpha-Candidate6/WonderChess.exe` local network run, at 1280×720 with the revised camera and revision-6 hero animations. The launch evidence specifies `-WCFast=5`; this review does not certify normal-speed motion, animation cadence or release timing.

Unchanged copies of the eight screenshots are in `packaged-candidate6-network720/`. `packaged-candidate6-network720-review-evidence.json` records their original paths, hashes and capture times, plus exact copies and hashes of the observed host/client session reports. The original launch files remain in `reports/WC-360/candidate6-network/host/launch.json` and its client counterpart.

**Normal battle framing passes this 720p sampled checkpoint.** The board, back-rank heads and ordinary front-rank pieces remain between the header and shop. Host and client round 8 show twelve combatants without the former header clipping. The limestone tiles are quiet behind the costume colors, and the edge pots, lamps and flags establish a coherent courtyard without competing with the units. The board/HUD arrangement is orderly and the principal panels are legible in these native-size images.

The cast remains readable as tabletop champions at this smaller scale. Ada's shield, the broad ochre Orc, turquoise rogue, pale-green archer, ivory harp user, coral priest and small differently equipped dwarfs retain useful identities. Family proportions, primary costume colors and weapon contours do more work than fine face detail, which is appropriate to this camera. Cyan and salmon base/health-bar treatments separate teams even when both teams have the same hero. Actual arrows/bolts or thin blue travel cues are visible in client round 8 and host round 12; this is evidence of rendered cues, not their timing or rules accuracy.

## Inspected captures

| Archived image | Actual scene | Readability finding |
|---|---|---|
| `host-round-05.png` | Ten-unit combat, five deployed human pieces | Three broad melee figures cluster near the center; team bars and separate bases keep them distinguishable. Backline archer and harp silhouettes remain apart. |
| `client-round-05.png` | Eleven-unit combat with repeated small dwarf figures | Slate helmet/hammer, red coat/hammer and mustard crossbow groupings remain distinct. Same-hero repetitions read as repetitions rather than missing or merged meshes. |
| `host-round-08.png` | Twelve-unit combat | Full back and front ranks remain clear of fixed HUD panels. A small indigo orb user is visible in the back rank; fine orb/frame detail is not resolvable. |
| `client-round-08.png` | Twelve-unit combat with a visible thin blue travel cue | The line remains narrow and does not wash out the clustered units; opposing team bases and health bars remain readable. |
| `host-round-10.png` | Twelve-unit combat and center melee cluster | The broad opposing bodies overlap naturally in depth, while base locations and main costume shapes remain distinguishable. No gross deformation or mesh disappearance is visible. |
| `client-round-10.png` | Twelve-unit combat with separated backline ranger | Small ranger and dwarf silhouettes remain visible, though hand and face detail is too small for precise inspection. |
| `host-round-12.png` | Combat after the local human is eliminated | **P2:** the elimination/spectator panel covers the lower board rows and part of a living foreground unit. See the defect below. |
| `client-round-12.png` | Twelve-unit combat, including two coral staff priests | Mira's coral mantle/staff and the repeated mustard crossbow users are identifiable; all ordinary units remain clear of the fixed panels. |

No missing character, T-pose, gross scale/orientation failure or detached visible weapon is apparent in these eight frames. They do not sample every animation state, continuous movement, LOD transitions or late Victory staff sweeps.

## Actual remaining defect

**P2 — elimination notice obscures ongoing spectated combat.** In `host-round-12.png`, the notice and its buttons occupy approximately y=449–511, inside the front board rows. A foreground indigo character around x=516, y=445 has its lower portion hidden by the panel. This is real pixel occlusion despite the geometry being inside the nominal board safe rectangle. Move the persistent notice/buttons into the existing shop area, collapse them, or provide a compact dismissal while spectating. The finding and exact screenshot were sent to the integration owner; this report does not claim a corrected build yet.

The top strip still says `VIEWING Captain 1` in this eliminated-host image, while the notice invites choosing a captain. The capture alone does not establish the intended automatic target selection, so spectating labels should be checked with the integration lane's actual interaction evidence.

## Geometry evidence and its boundary

Observed session snapshots at 07:17:28 UTC contain 36 host and 35 client projected-bounds samples: 180 and 165 component-bound evaluations respectively. All 345 recorded boxes project successfully and stay inside the defined rectangle x=223.33–1033.33, y=114.67–521.33. No sampled missing/invisible component is recorded. Host projected top/bottom extremes are 123.34/515.47 px; client extremes are 125.26/512.57 px.

These values project eight world-axis component-box corners. Individual records contain varying subsets of 2–12 units rather than proving every visible character in every screenshot. They support the corrected camera's geometric fit but cannot detect the spectator panel covering valid geometry, nor do they prove aesthetic quality. The archived session JSON and screenshot hashes preserve exactly the inspected boundary.

## Per-hero acceptance boundary

Eleven distinct hero definitions are visibly represented across the selected combat images: Ada, Mira, Rowan, Liora, Elin, Sylas, Borin, Tessa, Dagna, Rok and Kesh. Their actual 720p packaged crowded appearance has now been sampled and reviewed. Zura appears in shop portraits but was not observed as a living board character in these selected images; she remains pending a targeted crowded view. No shop portrait is counted as that evidence.

The readiness matrix records this 720p progress without promoting it to final acceptance. Current 1080p crowded presentation, all twelve heroes together including Zura's staff, complete skill cues at normal speed, moving-foot behavior, repeated-dwarf occlusion under sustained combat, LOD transitions and the fixed spectator notice remain separate work. Network correctness, complete matches, frame times and hardware measurements belong to the integration lane's reports; none are inferred from this visual review.

No art source, export, game Content or executable was changed in this review.

## Subsequent Shipping correction evidence

`shipping-spectator-fix-review.md` records five actual later Shipping images, including four post-elimination frames with the notice moved into the shop area and the scouting name corrected. The previous P2 is visually closed in those samples; this report's original failing screenshot remains unchanged. That later run failed its intended network startup and was stopped before match completion, so the correction evidence establishes pixels only, not network or full-match acceptance.
