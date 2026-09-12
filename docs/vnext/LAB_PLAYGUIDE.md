# Playing the six-creature laboratory

This is the first interactive `wonder_vnext` combat laboratory. It uses the authoritative C++ combat implementation with six new creatures, facing, stars, compatible relics and deterministic replay. The simple 3D bodies are gameplay proxies. The complete tournament interface, finished Wondergrove arena, animation, audio and onboarding are later work.

From the repository root, double-click **Launch Wonder vNext.cmd**. The launcher identifies the actual packaged candidate; it does not open the legacy alpha. Alternatively:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/unreal/launch_vnext_lab.ps1
```

## Formation controls

The board starts with a six-creature mirror formation. Team A owns the lower four rows and team B the upper four. Each team can deploy up to ten pieces; each piece occupies one logical cell.

1. Select a creature in the right-hand palette, then click an empty cell to place it on that team.
2. Click an existing piece to inspect it. Click an empty cell on the same half to move the selection. Choose a palette entry again to place another piece.
3. Change the selected piece's star level and initial facing in the panel. A direction is relative to that team's deployment side: both teams' Forward points toward the opponent.
4. Use **Next relic** to cycle compatible relics, or **Unequip** to remove one. A team can equip three distinct relics, one per piece. This lab control creates combat fixtures; it does not reproduce tournament relic acquisition.
5. Remove the selected piece with **Remove selected**, or right-click a piece. **Clear both formations** empties the board. **Six-creature mirror preset** restores the starting scenario.

The selected Bellback shows its eligible protection sector and the chosen ally when one exists. Reefglass shows its initial tide lane. The inspector evaluates star level and relic changes against the same definitions used by combat.

## Run and compare

Use **Start** to run automatic combat. Formation editing is locked during the fight. **Pause / Resume** controls the simulation clock, and **Step 1 tick** advances one authoritative tick. **Reset to formation** returns to preparation. **Replay same seed** repeats the recorded starting formation and seed. Each completed result writes its event/result signature to the engine log; the automated lab exercise compares those signatures. Edit the seed field before a new run to vary deterministic choices.

The lab displays important recent combat events and the final result. A replay agreement verifies repeatability for that fixture; it does not show that the fixture is balanced or enjoyable. A claimed improvement from changing placement needs a new combat comparison.

## Six decisions to investigate

| Creature | Try this | Change one thing to investigate its counter |
|---|---|---|
| Bellback | Put a vulnerable ally immediately behind its guarded sector and attack from the front. | Approach from a side or move the protected ally out of the sector. |
| Cragstoat | Leave a short, open approach so completed movement can build charge momentum. | Put it directly into contact or obstruct its approach and landing space. |
| Grandmother Root | Protect a stationary healer while the fight remains near its grove. | Use concentrated pressure or Reefglass displacement to disrupt the setup. |
| Snapvine | Leave an enemy backliner exposed along the selected attack line. | Add a defender along that line to intercept the strike. |
| Prism Organ | Place enemies on crossing row and column lanes. | Stagger the formation and pressure the setup before release. |
| Reefglass | Align enemies along its facing and leave legal push destinations. | Stagger targets, change facing, or block destinations to compare the actual outcome. |

These are experiments, not guaranteed wins. Keep investment, stars, relics and seed equal when comparing a placement change. Switch both sides as well: an interesting interaction should survive a mirrored test rather than depend on one favorable spawn.

## Early playtest record

Record the package identity, seed, both formations, stars and relics before the session. Ask the participant to explain the important action after watching it, before supplying the expected explanation. Record their words, the relevant event and whether they want another attempt.

The first five-player milestone also requires recruitment and scouting tasks. This laboratory cannot close those tasks because the successor tournament frontend is unfinished. Combat comprehension can be tested now; the missing preparation flows need their own playable implementation and session.

Useful observations include an action the player did not notice, a preview they misunderstood, an input they could not discover, an outcome they could explain, and a formation change they chose independently. Do not infer enjoyment from a long session or from an automated test pass.
