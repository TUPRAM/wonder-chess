# Validation, evidence and release gates

## Layered test matrix

| Layer | Required scenarios | Pass establishes |
|---|---|---|
| Source/compiler | Strict numeric types, quantization, unique IDs, threshold membership, all weighted costs recruitable, relic compatibility/tradeoffs, full neutral schedule, identical generated/native/staged identity | Authoring consistency |
| Native combat | Six signature mechanics; favorable/unfavorable/mirrored formations; blocked pushes/charge destinations; full board; movement interruption; simultaneous release/defeat; delayed beam packets; stationary reset; deterministic replay | Executed mechanic behavior for those scenarios |
| Transactions | Full-bench merges, relic survivor/extras, incompatible equip, ownership, duplicate/reordered requests, phase locks, facing, draft survival, corrupt/incompatible save, exact resume | Authority and state lifecycle |
| Full tournaments | Real shops, all off-screen combats, leveling, elimination, ghosts, neutrals, results, restart and deterministic saved failures | Complete simulated flow for tested content |
| Packaged engine | Same candidate data; normal-speed lifecycle, inputs, camera, sound, effects, restart and clean machine | Shipped-engine execution |
| Human play | Recruitment/placement/scouting comprehension, explaining battle outcomes, enjoyable losses, build changes, repeat sessions and voluntary replay | Observed experience in the sampled population |
| Remote online | 2H6B → 4H4B → 8H0B across independent devices, seat authentication/reclaim, bot takeover, disconnect/server failure, latency/jitter/loss, private-state isolation | Actual remote multiplayer evidence |

Maintain identical combat outcomes for viewed and off-screen battles. Equal-investment scenarios run multiple seeds and mirrored orientations. Unit pick/win rates are interpreted alongside exposure, affordability and purchase opportunity. Investigate timeout-heavy compositions separately from aggregate results.

## Human study protocol

The first interaction study uses five external players. Let each recruit, place, orient, scout and complete selected combats after onboarding. Record task success without moderator intervention, time, misunderstood cues and the participant's explanation. Avoid teaching the expected answer during the measurement.

The visual slice study uses at least twelve participants with newcomer and genre-experienced coverage. Play at normal speed, include losses and early elimination, and repeat across days during solo beta. Record fatigue, meaningful decisions, build changes and voluntary replay choice separately from first-impression liking.

The comparative study uses at least thirty genre-familiar participants and counterbalances whether Wonder Chess or Auto Chess is played first. Record version, prior familiarity and session conditions. Compare tactical agency, creature appeal, battle clarity, usability and desire to replay. Report preferences and uncertainty with sample limitations. No automated or agent-operated test substitutes for those people.

Proposed preregistered targets: 80 percent novice preparation-task success, 80 percent principal-cause recognition, eight accessible strategic archetypes, combat timeout below two percent, median complete standard tournament 35–45 minutes, and zero unresolved critical crash/stall/economy/authority/required-ability defects. These targets are not current results.

## Release evidence and performance

Before a release candidate, run at least 1,000 seeded full native tournaments and 100 full packaged-engine tournaments using the same frozen content. Record source digest, engine/tool versions, executable/package hashes, command line, seed, start/end state, outcome and every failing seed. Human, technical and production acceptance remain separate.

The first performance target is the known Windows laptop at 1080p/60 FPS. Capture frame-time distributions, CPU/GPU work, memory, loading and hitches through menus, transitions, twenty deployed units, permitted summons, busy effects and concurrent off-screen fights. Targets are p95 ≤16.7 ms and p99 ≤25 ms in active gameplay, with no recurrent unexplained >100 ms stalls. Mark loading and intentional pauses explicitly. Set minimum specifications only after additional hardware evidence.

Build/install dependencies are candidates until actually used. A compile pass does not establish an Unreal import, visible quality, package lifecycle, frame-time target or external acceptance. Preserve raw evidence alongside summaries and retain honest failed/blocked/not-run statuses.

## Network and release progression

Solo gameplay is proven before online release. The intended online architecture uses OSS EOS sessions and an authoritative dedicated match server. Include the required source-engine toolchain and actual service registration in M6 work. Local multiclient tests are useful but do not establish independent-device networking.

Private rooms and an unranked quick-play path come first. Bot filling is disclosed. Reclaim authenticates the original seat; a temporary bot yields to exactly one authenticated controller. Shops, benches and draft choices stay private. Content/protocol mismatches are rejected before joining a live match. Server failure reports an explicit aborted match rather than fabricating a result. Ranked play follows reliability and human balance evidence.

At each milestone produce a playable or reviewable artifact, measured checks, defects, actual blockers and a precise next task. Reserve stabilization before beta/release. M7 freezes roster/content, verifies the package on a clean machine, retains a rollback package and defines support diagnostics. Paid services, asset purchases, public hosting and deployment are outside the current authorization. No production dates are promised before measured M2 pilot effort.
