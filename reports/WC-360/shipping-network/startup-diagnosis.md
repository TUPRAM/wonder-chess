Shipping CLI network startup: FAILED STARTUP MODE

The actual Shipping host started as NM_Standalone with one requested human; no UDP7780 listener formed during the35-second check. No client was launched. This attempt does not establish Shipping2H6B networking and did not exercise the in-game Host/Join UI.

Installed UE5.7 GameInstance.cpp lines641-644 intentionally discard the startup URL in a Shipping nonserver build unless the target allows map overrides. FUrlConfig::Init in CoreMisc.cpp lines312-326 independently accepts Port= without that guard. Thus the missing listener is explained by standalone map startup, not by a verified rejection of the port argument.

Root explicitly authorized cleanup of the exact owned failed-trial processes after identity checks. PIDs40076/42484 were stopped; the cleanup is ABORTED_FAILED_STARTUP_CLEANUP, not a normal exit or completed network run. Evidence is preserved. Root owns a scoped CLI route through existing Host/Join APIs and will package and test it separately.
