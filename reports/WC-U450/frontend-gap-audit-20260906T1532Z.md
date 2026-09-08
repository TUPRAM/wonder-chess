# Native frontend gap audit, 2026-09-06 15:32 UTC

Read-only assessment completed before the follow-up UI edits. Sources: adopted FRONTEND_AND_GALLERY.md, HERO_UPGRADE_BRIEFS.md, WC-U450 sequence, WCFrontEnd.cpp/.h, WCMatchHUD.cpp, WCMatchRuntime.cpp, WCNetworkSession.cpp, WCFrontEndAudit.cpp. No asset completion or physical input inferred.

Retained package evidence inspected directly: reports/WC-U430/20260906T150922Z/packaged-gallery1080/20260906T150926-{gallery,ada-synergies,ada-star2-active,halfling-story,no-results,seat-introduction-1500ms}.png and frontend-audit.json. That old package audit had 527 checks, 109 failures (108 missing expansion assets plus the approach mesh); it is not the current import state. The selected UI checks passed, but the whole audit failed.

| Requirement | Observed boundary / omission |
|---|---|
| Race/class icons | Absent from actual cards and detail. Current Card renders text race/class; no original icon motifs are loaded. Explicit contract requirement. |
| Skill icons | Absent from actual skill tab. The specific frontend contract requires original icons and active descriptions, but does not separately enumerate 24 skill icons; retain this distinction when sizing the requested improvement. |
| Card active description | Card shows the skill name, with descriptive tooltip on hover. A visible one-line active description is missing. Focus-triggered description needs actual keyboard review. |
| Synergy partners | Matching eligible partners, exact 2/4 values and matching-only recipients are coded and visible. Partners are text buttons; required partner portraits are absent. No optional trait-stat preview is implemented. |
| Tactics/story/appearance | Tactics reads authored placement/partner/counter/weakness/contrast. Story reads full name/title/region/faction/biography, visibly confirmed for Pippa. Dossier-specific visual gear description is absent; only a generic no-inventory explanation appears. |
| Filters/sorting | Race/class/cost/role use OR within a group and AND across groups. Short/full search and all four sorts are coded. Actual audit proves race/class combination and search, not role/cost combinations or sort order. |
| Retention | Detail/back saves/restores gallery scroll and SelectedId in source. Showcase persists locally outside audit. Actual scroll/back/selection and restart persistence assertions are missing. Rebuilding destroys focused widgets; full keyboard continuity needs review. |
| Errors/cancel/ready | Actual entry identities/readiness, cancellation, duplicate-start guard and initial-clock barrier are coded. Audit passes solo duplicate/cancel/barrier. Session failures already leave frontend and render Canvas MATCH ABORTED with Return to title; they are not wholly hidden. Controller Message changes do not trigger frontend rebuild, pending join lacks direct retry, and failed initial connections get a misleading match-aborted screen. Physical LAN and slow-client UI not established by the solo audit. |
| Bot policy | Introduction displays name/BOT/readiness but no difficulty policy. Public entryParticipants contains no policy field; the fallback bot focus text is bypassed whenever participants exist. |
| Shop upgrades | Result star, buy cost and full-bench merge allowance are coded. Prepurchase consumed-copy/survivor/destination path is missing. The confirmed transaction already describes absorbed copies/destination after the authoritative revision, but no card-to-destination travel animation exists. |
| Selection after rejection | Move (drag/click/bench/swap) and Sell immediately clear SelectedUnit. ClientReply has no request identity and does not restore selection. This is a concrete contract failure before the follow-up fix. |
| Trait hints | Clickable trait detail separates distinct deployed contributors from receiving copies, displays 2/4 and next tier, and highlights units. Hover/focus does not open equivalent detail; buy/replace effect preview is absent. |
| Localization | Several new frontend labels remain English when ID selected: tabs, clip labels, sort values, role/race labels and authored narrative text. EN/ID long-string layout and full keyboard/drag path remain manual acceptance work. |

The inspected 1080p samples show a readable six-column gallery, fixed Back/previous/next, complete Ada preview bounds and clear scrolling cues. This does not prove all 24 assets, all screens at 720p, continuous animation, audio, physical LAN, or a complete human match.

Follow-up implementation authorized by root: priority one connection/error/retry handling and request-correlated selection; next merge path, partner portraits and original icons. Asset production remains owned by its designated lanes.
