# Actual routed Shipping two-process network check

Functional received-state/RPC audit: **PASS**. Process lifecycle complete: **True**.

Two actual Shipping game processes over local loopback with separate authenticated human controllers, six persistent bots and scripted real RPC inputs. This is not two physical PCs, manual play, an uncontended1080p performance run or packet capture.

The paired reader completed 35 checks with status PASS. Listener ownership and the entire packaged payload have separate checks in network-analysis.json.

- host: PID67348, seat0, network mode2; completed round33. All combat rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33].
- host: 48 accepted / 5 rejected actual replies; probes {'out_of_order_sequence_rejected': 'PASS', 'original_idempotent_lock_request': 'PASS', 'duplicate_request_applies_once': 'PASS', 'changed_payload_same_request_rejected': 'PASS', 'stale_revision_rejected': 'PASS', 'foreign_unit_sale_rejected': 'PASS', 'combat_phase_buy_rejected': 'PASS'}.
- host: maximum actual public JSON 79240 characters / 79240 UTF8 bytes; 0 stale retained recaps.
- client: PID66296, seat1, network mode3; completed round33. All combat rounds observed: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33].
- client: 48 accepted / 5 rejected actual replies; probes {'out_of_order_sequence_rejected': 'PASS', 'original_idempotent_lock_request': 'PASS', 'duplicate_request_applies_once': 'PASS', 'changed_payload_same_request_rejected': 'PASS', 'stale_revision_rejected': 'PASS', 'foreign_unit_sale_rejected': 'PASS', 'combat_phase_buy_rejected': 'PASS'}.
- client: maximum actual public JSON 64424 characters / 64424 UTF8 bytes; 0 stale retained recaps.
- client: latest process snapshot subsequently returned to namespace0 / phase-1, aborted=True, after the host's planned exit. Completed round33 results remain retained in the audited match namespace. The current error message is recorded exactly in network-analysis.json.

Both engine log oversized-bunch/error counts are **NOT_RUN**, not zero. Shipping provides received-state, real-RPC, frame and screenshot evidence through the game's explicit verification writer.

Concurrent workload is recorded at launch. Two rendered processes and automatic captures confound uncontended performance measurement.
The optional concurrency.json inventory records any additional actual concurrent functional processes, including a root-owned restart run when present.

## Limits

- Current and maximum public JSON UTF8 byte lengths exclude replication and socket overhead.
- Lifecycle records distinguish bootstrap and inner process observations. An unavailable inner exit code remains unknown; bootstrap success does not replace it.
- Accepted replies include an intentional idempotent duplicate; they are not a count of distinct mutations.
- Projected skeletal component bounds are conservative geometry, not proof of lack of pixel occlusion or satisfactory hero art.
- Native engine log error and oversized-bunch counts are unavailable for Shipping and remain null/NOT_RUN.
- Prior package evidence is retained separately and does not certify this payload.
