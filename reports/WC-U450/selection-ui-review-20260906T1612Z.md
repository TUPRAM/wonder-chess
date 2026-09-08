# Actual selection-rejection review

Read-only review of `reports/WC-U430/20260906T161052Z/selection-ui`, completed 2026-09-06. The runtime source remained frozen. No game was launched by this reviewer.

The actual JSON report passed six checks with zero failed checks/captures. All three requested 1280 x 720 screenshots were opened for visual inspection. The process exited 0. Launch and exit evidence bind the same runtime DLL SHA256 `726fbefbcedafdace72c1006e4a60997432c6727fb81325b86925bd6ce031339` and the report records catalog digest `a0fc03fd31260f245a795233aa00d3959e7f80be37dcc7affe3500d4346fc101`.

The actual editor log corroborates request IDs 1 through 5: an accepted purchase, rejected invalid placement, accepted legal placement, rejected unowned sale, and accepted sale of the owned copy. The audit records selected unit 1 after both rejected commands, gold 9 retained during rejection, selection cleared after accepted placement/sale, and gold 10 after sale.

The Indonesian screenshots visibly show the invalid-deployment error, then the ownership error, with Liora retained in the selected bench/board position. The last capture shows her removed after sale, the bench empty, and the canonical one-gold sale credit. No fatal error or ensure matched the inspected log patterns.

This passes the focused actual native HUD/authoritative-reply fixture. It is an editor `-game` software-driven check, not packaged human play, a complete tournament, physical LAN or performance acceptance. The CSV is header-only because this launch did not request profiling.

Separate visual observations remain open: the single-species neutral preview occupies approximately 112 screen pixels vertically across most board width, and the gameplay detail still presents technical zero durations and an irrelevant maximum-targets value for the inspected movement skill. These do not invalidate the narrow command/selection result; they prevent treating this review as complete visual approval.
