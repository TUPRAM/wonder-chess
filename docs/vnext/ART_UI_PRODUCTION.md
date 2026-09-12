# Mythic-storybook production contract

## Visual bible and reference gate

Use broad primary forms, clear silhouette breaks, deliberate asymmetry and expressive poses. Materials have readable identities: bark and leaves, glazed ceramic, weathered bronze, translucent membranes, contained magic and selected cloth. Surfaces carry painterly value grouping rather than uniformly noisy microdetail. Team/readiness/status readability survives grayscale and small gameplay scale.

Wondergrove is a carved stone tactical platform held within roots of an ancient sanctuary. Keep cells and the center low contrast. Place architectural storytelling, richer foliage and motion around the perimeter. Bench, shop frame, lobby and loading transitions share the same illustrated-field-guide language. Produce one excellent board before variations; later themes keep tactical geometry and visibility unchanged.

The first AS1 pilots are Bellback, Prism Organ and Thimblewake. They prove a grounded quadruped, floating assembly and articulated insect. Produce them serially through the shared Blender queue, with separate asset manifests and immutable checkpoints. Existing Ada artifacts and approvals do not establish these pilots. Read the applicable AS1 stage manual and direct dependencies only; never skip required human approval of reference, forms or release.

## Asset inventory and acceptance

| Group | Deliverables | Acceptance evidence |
|---|---|---|
| Each hero | Approved concept; front/side/back views; complete forms; topology; UVs/materials; rig/weights; sockets; motion; LODs; selection bounds; portraits/icons; skill effects and audio; gallery binding | Viewed reference and gameplay-scale frames; continuous motion review; export/import identity; performance; human gate |
| Seven neutral families | Original silhouettes, playable encounter variants, visual/audio tells, animation, boss skills and teaching compositions | Each wave and boss executed with exact data; comprehension test |
| Wondergrove board | Modular platform, cells, bench, roots, stonework, perimeter props, foliage, lighting, ambience, collision and camera limits | Whole game screen at target resolution; readable busy fight; performance trace |
| UI | Design tokens, type hierarchy, icon grid, cards, panels, buttons, focus/hover/disabled states, tooltips, settings and network states | Full keyboard and pointer task flows; text scale and localization |
| Effects | Distinct damage/heal/shield/stun/displacement/ground/transform/defeat grammar, pooled spawn and expiry | Authoritative timing alignment and overlapping effects review |
| Audio | Creature voices, cast cues, contacts, interface feedback, ambience, adaptive music and mix controls | Direct listening review in a full busy match; clipping and masking audit |
| Frontend | Lobby, model bestiary, learning sandbox, onboarding, loading, elimination, victory, restart | Complete package lifecycle and clean restart |

One rig family needs a method proof before a new production batch uses it. Artwork cannot pass because it has many files or polygons. Each technical pass cites source hashes, tool version, actual output and captures actually viewed. Candidate assets remain separate until their applicable human and measured-engine gates pass.

## Animation and effects

Use family-specific anticipation, weight, contacts and recovery. Required behavior coverage includes idle variety, locomotion, turning, attack start/release/recovery, cast, hit response, interruption, defeat and transition blends. Attack variations must share correct timing. Creature identity should be visible in the gait, not only in its mesh.

Combat events own release time, projectile identity and movement completion. Animation never creates a second damage authority. Review minimum/maximum attack rate, repeated casts, target changes, source defeat after release, displacement and interrupted motion. View continuous normal-speed motion before slow-motion inspection. Check slipping feet, hovering props, tail/wing overlap, clipping, culling, sudden scale changes and abrupt blends.

Important effect tells occupy clear world geometry with minimal persistent noise. Damage types are distinguishable by shape and motion in addition to color. Reduced-effects mode keeps the essential range, direction and timing information. Every transient visual/audio object has a lifecycle and ownership test.

## Screen layouts and interactions

Use responsive UMG/Slate and shared authoritative view models for the full frontend. A laboratory panel or proxy renderer is an implementation aid, not acceptance of this finished interface.

**Preparation:** a compact top bar carries round, phase and clock; economy sits beside the five-card shop at the bottom; compact traits sit left; standings and scouting controls sit right. The board and bench stay in the main unobstructed area. A selected hero opens a contextual panel alongside the board. At smaller widths, collapse secondary detail before covering placement cells.

**Placement:** show legal destinations and preview the selected hero's relevant guard arc, line, area or target relationship. Facing changes update the preview before commit. Provide click-source/click-destination alongside drag and drop. Reject feedback states the reason without discarding selection. Upgrade opportunities indicate exact owned copies rather than just glowing cards.

**Combat:** keep the board dominant. Show phase, opponent, compact standings and essential health/status cues. Scouting must clearly identify the viewed seat and provide a persistent return-to-own-board action. No private benches or shops appear in opponent views.

**Recap:** lead with one or two facts grounded in recorded events, followed by optional unit breakdown and replay inspection. A claim that another formation would win requires an actual replay comparison. A damage leaderboard alone is not an explanation.

**Bestiary:** animated hero model, race/class, ability geometry, strengths/counters, star comparison and a button into a controlled sandbox. Search by identity, trait, body family and behavior. Future unimplemented heroes, if shown in development tools, are explicitly design candidates and cannot be recruited.

**Settings and accessibility:** scalable text, keyboard focus navigation, remappable controls, pointer alternatives, volume buses, color-independent cues, reduced motion/effects and equivalent English/Indonesian content. Test actual long localized text and 125/150/200 percent text scale. A missing translation is a defect, not a reason to silently hide functionality.

## Production queue

Brief → approved reference → silhouette/blockout → accepted full forms → topology → materials and rig/skin → animation → optimization → Unreal integration → gameplay-camera review → package review. Maintain one Blender operation queue and one writer per binary. After two ineffective changes to a critical defect, change the modeling method or stop that asset stage while independent work continues.
