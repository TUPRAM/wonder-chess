# Actual routed Shipping two-process network check

Functional received-state/RPC audit: **PASS**. Process lifecycle complete: **True**.

Two actual Shipping game processes over local loopback with separate authenticated human controllers, six persistent bots and scripted real RPC inputs. This is not two physical PCs, manual play, an uncontended1080p performance run or packet capture.

The paired reader completed 35 checks with status PASS. UDP7780 was verified on the host's actual Shipping process before starting the client. Executable hashes still match the immutable startup-fixed provenance.

- host: PID38772, seat0, network mode2; completed round23. All combat rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23].
- host: 37 accepted / 5 rejected actual replies; probes {'out_of_order_sequence_rejected': 'PASS', 'original_idempotent_lock_request': 'PASS', 'duplicate_request_applies_once': 'PASS', 'changed_payload_same_request_rejected': 'PASS', 'stale_revision_rejected': 'PASS', 'foreign_unit_sale_rejected': 'PASS', 'combat_phase_buy_rejected': 'PASS'}.
- host: maximum actual public JSON 32622 characters / 32622 UTF8 bytes; 0 stale retained recaps.
- client: PID48568, seat1, network mode3; completed round23. All combat rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23].
- client: 48 accepted / 5 rejected actual replies; probes {'out_of_order_sequence_rejected': 'PASS', 'original_idempotent_lock_request': 'PASS', 'duplicate_request_applies_once': 'PASS', 'changed_payload_same_request_rejected': 'PASS', 'stale_revision_rejected': 'PASS', 'foreign_unit_sale_rejected': 'PASS', 'combat_phase_buy_rejected': 'PASS'}.
- client: maximum actual public JSON 32622 characters / 32622 UTF8 bytes; 0 stale retained recaps.

Both engine log oversized-bunch/error counts are **NOT_RUN**, not zero. Shipping provides received-state, real-RPC, frame and screenshot evidence through the game's explicit verification writer.

Root plans a separate headless100 regression during the initial network minute. This functional network run is not an uncontended performance measurement.
The optional concurrency.json inventory records any additional actual concurrent functional processes, including a root-owned restart run when present.

## Limits

- Current and maximum public JSON UTF8 byte lengths exclude replication and socket overhead.
- Both tracked bootstrap processes exited0. Inner process exits were observed but their captured ExitCode values are null/UNKNOWN; bootstrap exit0 is not substituted for an unavailable inner exit code.
- Accepted replies include an intentional idempotent duplicate; they are not a count of distinct mutations.
- Projected skeletal component bounds are conservative geometry, not proof of lack of pixel occlusion or satisfactory hero art.
- Native engine log error and oversized-bunch counts are unavailable for Shipping and remain null/NOT_RUN.
- The preserved earlier Shipping trial failed before client launch because positional startup URLs were disabled; this is a separate build and separate run.
