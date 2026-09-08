# Focused negative native UI checks (proposal, not executed)

This proposal accompanies the first protocol-5 interaction checkpoint. It is not a passing test report. No runtime source changed while the owner compiles.

## Failed connection, retry and return

An opt-in `-WCFrontEndRecoveryAudit -WCJoin=127.0.0.1:<confirmed-unused-port> -WCRecoveryTarget=127.0.0.1:<actual-listening-test-host>` drives the existing native Mode controls. The host runs the same package/protocol with `-WCHost`, without automatic match start. Both processes use fresh evidence directories. A loopback test proves two local processes only; the physical-LAN gate remains separate.

The audit waits for a real Unreal network callback, never assigns bMatchAborted or invents an error. It records the actual error/detail, endpoint, elapsed time, package digest and protocol. On failure it verifies that no tournament exists, the Mode page shows that same error, pending state is false, the retained endpoint is editable, and Solo/Host/Join are enabled. It captures the actual native error panel.

It then puts the declared listening endpoint in the same editable view model and activates the real Join LAN button through focused Slate Enter. State for this opt-in fixture persists across world travel in a process-local map keyed by the GameInstance, not a production save or fake participant. Before travel it writes an intermediate evidence record. After travel it requires actual connected=2, a real assigned remote human seat, protocol/digest parity and no retained failure before calling retry successful. A bounded timeout writes FAIL/INCOMPLETE, with the failed attempt retained.

Finally the real Leave LAN lobby control returns the client to the title. The audit requires a fresh idle local world with no running tournament and captures it. Endpoint reachability, readiness and clocks are never inferred from button presence. If a host is unavailable, the retry is NOT_RUN/failed according to the observed attempt; the error-panel check can still have independent evidence.

## Selection after server rejection

An opt-in `-WCSelectionAudit -WCAutoStart -WCHumans=1` uses the actual native controller/HUD and normal command path during the first preparation. It does not run WCExercise simultaneously. A bounded audit hook in controller Tick, implemented in WCFrontEndAudit.cpp, survives removal of the lobby widget when the actual match starts.

1. Wait for real first preparation and authoritative private snapshot. Select an affordable actual offer and invoke the existing HUD Buy action. Wait for its accepted reply/private roster before continuing.
2. Select that real bench unit through the HUD action. Send an intentionally out-of-bounds cell action through the same handler. Require the server's exact rejection, unchanged gold/owned unit/location, and SelectedUnit still equal to the real unit. This is an intentionally invalid input test, not a claim that the invalid cell has a clickable on-screen target.
3. Select and move to a real free legal deployment cell through the HUD. Require matching accepted reply plus authoritative unit placement; selection clears only following that reply.
4. Re-select the same actual unit. Submit a deliberately unowned Sell target through the controller command API; require real server rejection and preservation of the useful selected owned unit. This separately exercises sale rejection without fabricating ownership.
5. Sell the actual selected unit through the HUD. Require accepted reply, authoritative removal and expected canonical sale credit, then selection cleared.

The audit records request ID, command, reply, before/after revision/sequence, selected ID, gold and owned placement for each step. It never assigns canonical economy or private snapshots. A challenge for a stale/wrong request reply may call the client reply handler explicitly, but that assertion must be labelled a client-handler injection, separate from actual server replies and normal match evidence; it must not silently inflate accepted-command counts. Prefer testing this in an isolated native automation fixture if the existing verification recorder cannot distinguish it.

These are focused software-driven interaction checks. They do not replace manual keyboard/mouse play, a complete 1H7B match, physical 2H6B, continuous animation or performance acceptance.

## Secondary UI coverage to add after the checkpoint

Role OR, cost OR and mixed four-group AND use real gallery view-model results compared to catalog fields. A real SScrollBox offset is sampled after layout, then detail/back is invoked and selection/offset are compared. Original icon widgets and partner portrait brushes are checked for actual geometry/resources, then visually inspected at 720p and 1080p. Merge previews must consume the shared economy result or a dry-run cloned seat; no parallel approximate merge algorithm is acceptable.
