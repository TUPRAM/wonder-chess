# Playing the Wonder Chess alpha

You are one captain in an eight-seat tournament. Buy heroes, arrange your formation and develop race/class traits during preparation. Heroes fight automatically; the other captains' encounters continue while you watch yours.

## Launch and start

Open `WonderChess.exe` at the top of the delivered Windows package folder. Keep its adjacent folders and files together.

**Packaged launcher:** `builds/WonderChess-Alpha-Candidate/Windows/WonderChess.exe`. The accompanying handoff records the actual gameplay checks and remaining issues for this candidate. Manual acceptance remains incomplete; the package is not an accepted final alpha.

Unreal Editor, Blender and Visual Studio are not needed to run the packaged game. If Windows reports missing Microsoft Visual C++ runtime components, the package includes Microsoft's installer at `Windows/Engine/Extras/Redist/en-us/vc_redist.x64.exe` (relative to `builds/WonderChess-Alpha-Candidate`). Run that installer when needed, then launch the game again. The installer was included and its signature checked; installer execution and launch on a clean Windows machine have not been verified.

Select **Play Bot Tournament** for one human and seven persistent bots. The title lobby lists the bots and their policies. **How to play** opens a short introduction; it is optional.

For a guided first round, select **Guided practice | fixed shop seed**. Its disclosed fixed shop setup lets you buy Ada, deploy her, add Mira for the Human trait and buy two more Ada copies to see a merge. Follow the on-screen steps and inspect Ada's shield. The first preparation remains untimed until you press **Ready**. Later rounds use normal timers. Starting a normal tournament returns to ordinary independent shops.

## Build your team

Preparation is the time to change your team. The HUD shows gold, level, XP, deployment capacity and each action's cost.

1. Use a shop card's **Buy** button to purchase that hero. Purchases go to your eight-slot bench. Selecting a portrait inspects the hero; it does not buy it.
2. Select a bench hero, then click a legal cell in your half of your own board. You can also drag a hero between the bench and board. An occupied destination can swap heroes when the resulting formation is legal. Your level limits how many heroes you can deploy.
3. Collect **three identical heroes of the same star level** to merge automatically: three one-star copies make a two-star hero; three two-star copies make a three-star hero. A full bench can still allow a purchase when the shop explicitly shows a possible merge.
4. Select an owned hero and use **Sell selected hero** to sell it. **Reroll** replaces the shop for the displayed price. **Lock shop** preserves its current offers, including empty purchased slots. Use the XP button to progress toward a higher level and more deployment capacity.
5. Deploy different hero types sharing a race or class. Two qualifying types activate that trait; the left panel shows its count and numerical bonus. Bench heroes and duplicate copies do not add distinct trait types.

Inspect heroes to compare their star level, health, separate shield amount, armor, resistance, Physical/Magic/True damage, attack delivery and skill values. Combat inspection includes current combat modifiers.

Press **Ready** or **Space** when satisfied. The button changes to **READY - waiting**. There is no separate unready toggle; a successful preparation edit clears readiness. Combat starts when all living captains are ready or the preparation timer expires. You cannot buy, sell or reposition during combat.

## Scout, watch and finish

Select a captain in the standings to scout their public formation during preparation or watch their current encounter during combat. Use **Return to your board** to resume editing your team. Scouting preserves a pending selection and does not reveal another captain's shop or bench.

**Round recap** shows the encounter outcome, survivors, health damage, shield absorption, effective healing and captain damage. A ghost opponent is a copied formation; its donor does not lose health from that copied fight. Timeout and capped results carry their own labels.

If eliminated early, select another captain to spectate while the bots continue, or choose **Return to title** or **New solo tournament**. You do not need to ready after elimination. Final results show placements; **New tournament** starts a fresh match. In a two-human session, the host controls the tournament restart.

## Controls and options

| Input | Action |
| --- | --- |
| Left click | Inspect/select a hero, place a selected hero or activate a button |
| Left drag | Move a hero to a legal board/bench destination; adjust a volume slider |
| Right click or Escape | Cancel a selected hero; with nothing selected, open or close Options |
| Space | Ready during preparation |
| Tab / Enter | Move visible button focus / activate the focused button |
| Left / Right arrow | Adjust a focused volume slider |
| F9 | Save a screenshot of the current game view, including the HUD |

Options provide English/Indonesian labels, master/music/effects volume, reduced motion and window/borderless fullscreen switching. Click or drag along a volume track to set its level. Local preferences persist. Options pause an offline match; they do not pause a network match.

F9 writes `manual-<timestamp>.png` in the game's `Saved/Screenshots/<platform>` directory. To choose a directory when launching the executable directly, pass `-WCEvidenceDir="C:\path\to\screenshots"`. With `tools/unreal/launch_alpha.ps1`, use its `-EvidenceDirectory 'C:\path\to\screenshots'` option instead.

## Two humans and six bots

For two game processes on one PC:

1. Open the first process and select **Host LAN lobby | 2H6B**.
2. Open a second process and select **Join local host**. This button connects to `127.0.0.1:7777` on the same PC.
3. Once both humans are connected, the host selects **Start 2 humans + 6 bots**.

You can also open a lobby from PowerShell in the packaged `Windows` folder. On the host, run:

```powershell
.\WonderChess.exe -WCHost -Port=7777
```

In the second process on the same PC, run:

```powershell
.\WonderChess.exe -WCJoin=127.0.0.1:7777
```

For another PC on the local network, replace `127.0.0.1` with the host's literal IPv4 address and use the same port. The host starts the tournament after both humans reach the lobby. The explicit `-WCHost` and `-WCJoin` options are supported by this Shipping build; ordinary positional startup map/address arguments are not its launch interface.

Alternatively, use the source kit's launcher from the Wonder Chess workspace, supplying the actual packaged executable and host's literal IPv4 address. For example:

```powershell
.\tools\unreal\launch_alpha.ps1 -Mode Join -Executable 'C:\path\to\package\WonderChess.exe' -HostAddress '192.168.1.20'
```

Replace both example paths/addresses. The default port is `7777`; `-Port` selects another matching host/client port. The launcher can also create the host with `-Mode Listen -Executable 'C:\path\to\package\WonderChess.exe'`.

A departing non-host human is replaced by a bot that retains that seat's progress. Losing the host aborts the match and displays an explicit error with no winner. Returning the host to the title also ends that session. Joining an already-running tournament is unsupported; create a fresh lobby.

**Network evidence boundary:** the current verification setup is two separate game processes on one Windows PC. It does not establish compatibility across two physical PCs. Consult the accompanying handoff for the actual completed checks and remaining issues.
