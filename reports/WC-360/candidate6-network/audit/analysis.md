Candidate6 actual two-process network acceptance: PASS

Two actual packaged processes over local loopback with separate human seat bindings and real scripted RPCs. This is not manual play, a second physical PC, normal-speed profiling, or visual/audio acceptance.

Paired evidence reader: PASS across 37 checks. The candidate6 packaged executable hashes match its immutable provenance manifest: True.

- Host PID 1104, human seat 0: completed round 23. Combat rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]. Recap rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23].
- Host: 42 requests; 37 accepted and 5 rejected actual replies. Reasons: {'Out-of-order command sequence': 1, 'Accepted': 37, 'Request ID reused with different payload': 1, 'Stale seat revision': 1, 'Unit is not owned': 1, 'Preparation is locked': 1}. Probes: {'out_of_order_sequence_rejected': 'PASS', 'original_idempotent_lock_request': 'PASS', 'duplicate_request_applies_once': 'PASS', 'changed_payload_same_request_rejected': 'PASS', 'stale_revision_rejected': 'PASS', 'foreign_unit_sale_rejected': 'PASS', 'combat_phase_buy_rejected': 'PASS'}.
- Host: actual maximum public JSON 32621 characters / 32621 UTF8 bytes; 0 oversized-bunch engine errors; 0 stale recap observations.
- Client PID 36464, human seat 1: completed round 23. Combat rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]. Recap rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23].
- Client: 53 requests; 48 accepted and 5 rejected actual replies. Reasons: {'Out-of-order command sequence': 1, 'Accepted': 48, 'Request ID reused with different payload': 1, 'Stale seat revision': 1, 'Unit is not owned': 1, 'Preparation is locked': 1}. Probes: {'out_of_order_sequence_rejected': 'PASS', 'original_idempotent_lock_request': 'PASS', 'duplicate_request_applies_once': 'PASS', 'changed_payload_same_request_rejected': 'PASS', 'stale_revision_rejected': 'PASS', 'foreign_unit_sale_rejected': 'PASS', 'combat_phase_buy_rejected': 'PASS'}.
- Client: actual maximum public JSON 32621 characters / 32621 UTF8 bytes; 0 oversized-bunch engine errors; 0 stale recap observations.

Payload lengths exclude protocol overhead; the actual engine log check is separate. Accepted replies include the deliberately replayed idempotent request and therefore do not equal distinct accepted mutations. Frame data is a 1280x720 accelerated 5x two-process workload and cannot pass the 1080p normal-speed performance gate.

Candidate5 remains preserved as a failure with 60 oversized bunches and missing combat rounds 2-16. This report describes the separately packaged candidate6 run only.
