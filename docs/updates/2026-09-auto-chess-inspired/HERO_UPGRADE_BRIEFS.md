# Wonder Chess — 24 hero upgrade briefs

Status: **planning proposal, 2026-09-06; no character, balance, animation or runtime edits performed by this document.**

The user selected **all 24 existing heroes as fully playable content for this update**, with **visual weapons and armor only**. The original twelve remain the first production wave because they already have authored models, imported animation and packaged evidence. The other twelve become full production obligations in this update; they are not merely gallery previews. This explicitly expands the old v3 twelve-hero delivery scope. Keep the original identities and stable IDs, and migrate the canonical profile, generated documents, runtime adapters, bot policies and tests together when implementation begins.

The source of character identity and numeric truth remains [units.json](../../../data/units.json), supported by the complete [character bible](../../CHARACTER_BIBLE_24.md), [twelve existing asset briefs](../../ALPHA_12_ASSET_BRIEFS.md), and [Blender production contract](../../BLENDER_PRODUCTION.md). This file proposes changes; it does not supersede their current implemented values silently. Do not duplicate numerical combat tables here. All revised values must be authored once in canonical data and rendered by the same stat evaluator used by the game.

## Decisions that apply to every hero

- **Short names:** use the first name in shop cards, board inspection, standings and gallery navigation. Keep the complete name and title in biography/search metadata. Stable unit IDs, asset directories, ability IDs and save references do not change. The working game title remains Wonder Chess; shortening hero names is not a game rebrand.
- **Role, race and class:** preserve the existing race/class assignment. Show plain class names Guardian, Warrior, Ranger, Mage, Priest and Rogue. Show race names directly. Roles are explanatory labels and do not add a third synergy system: the proposed player-facing role vocabulary is Tank, Melee, Ranged, Caster, Support, Healer and Control. Map Defender to Tank, Melee damage to Melee, Ranged damage to Ranged and Spell damage to Caster. Mira/Orla are Healer; Elin/Oren use Support rather than falsely claiming that their skills heal. The per-hero headers below record current canonical role text for traceability. All six races and all six classes have four distinct members in the complete 24-hero roster, so two- and four-member thresholds are reachable. Duplicate copies and star levels must not count as distinct members. The systems plan owns exact tier effects and balance.
- **One active skill:** keep the authored mechanical identity and a readable basic attack. Improvement means a clearer tactical decision, better valid-target behavior, stronger anticipation/release/recovery, or a justified mechanic change; it does not mean adding extra damage and control to every skill. Initial damage, duration, cooldown and range tuning starts from canonical data. New targeting proposals below are explicitly unimplemented and need tests before adoption.
- **Visual equipment:** improve each authored weapon, shield, focus, clothing and armor. These are fixed character identity assets. No loot inventory, gameplay equipment slots, item modifiers, recipes, item purchases or recommended gameplay items are introduced. Star presentation can add restrained trim, stitching and a small focus glow without changing equipment stats or logical footprint.
- **Gallery parity:** a hero page presents the actual game mesh, model-matched portrait, race/class, explanatory role, cost, rarity, current one-/two-/three-star stats, active description, cooldown/reach, tactical positioning, synergies, visual gear and biography. A star selector evaluates actual combat scaling; it must not invent stat multipliers. Preview Idle, Move, Attack, Active, Hit, Defeat and Victory. A Gear & Appearance section explains authored costume/props and does not resemble a functional equipment inventory.
- **Animation authority:** preserve the seven required clips at 60 FPS, in-place movement, and the canonical release/recovery timings aligned to the simulation. Notifies can emit presentation only. The full roster needs **168 hero/clip review cells**, including the existing 84; shared clips are acceptable only after each body, costume and prop combination is reviewed. Still samples cannot certify continuous playback.
- **Recognition:** test face and costume in the gallery, but prioritize body proportions, two or three large identity shapes, grip, material grouping and posture on the board. Use the accepted gameplay camera, 1920×1080 and 1280×720, 96-pixel portraits, both team orientations and crowded encounters. Keep one logical tile at every star.

## Preserve the existing work

The current twelve are not untouched kit scaffolds. [Implementation state](../../../reports/implementation_state.json), the [revision-six Unreal review](../../../reports/WC-330/unreal-visual-review-revision6.md), [84-clip matrix](../../../reports/WC-330/84-clip-review.md) and [packaged still review](../../../reports/WC-330/shipping-normal1080-taa-review.json) record actual modeled costume/equipment, four body families, imported clips and inspected poses. Those are existing evidence with defined limits, not a new acceptance claim from this planning pass.

Reuse `art-source/heroes/<stable_id>/`, their established exports, source collections, materials and measured import profiles. Ada's costume revision/reimport evidence already exists. Inspect the current source and accepted package before choosing any geometry replacement. Retain snapshots and source-controlled checkpoints; do not discard the existing faceted tabletop style simply because the reference uses a smoother surface treatment. Improve specific anatomy, grip, silhouette, material and motion defects. Existing reports leave continuous movement, precise release/audio alignment, some small gestures and fine contacts open. One prior conservative Rok screen-margin excursion also remains a useful camera regression case.

## Wave 1 — upgrade the twelve existing playable heroes

### 01. Ada Brightshield → **Ada**

**Stable ID:** `wc_u_human_guardian` · **Human / Guardian / Defender** · First reference asset.

**Current skill:** Sunward Guard gives Ada a temporary personal shield. **Proposed display skill:** **Sun Guard**. Preserve her role as the cheaper personal defensive anchor. Make remaining absorption, expiry and actual shield breaks readable in inspection and combat; distinguish absorption from healing. Anticipation raises the shield before the canonical release, a thin crest-shaped shell appears at release, and the shell visibly breaks or fades on the actual corresponding event. Do not add taunt, damage immunity or an ally shield merely because she looks protective; Tala owns group shielding.

**Model and gear:** refine the broad shoulder-to-waist taper, warm brown face and short black braid. Keep the ivory quilted coat, navy tabard, steel armor and one sun disk. Strengthen the kite shield's curved profile, grip thickness and shallow emblem bevel; improve the short broad sword's handle-to-hand contact. Preserve the face above the resting shield. Use controlled metal roughness against matte cloth, with gold confined to the authored crest and fasteners.

**Motion and effects:** measured planted steps; one clearly readable sword sweep; a supported shield raise; recoil that moves both the torso and attached shield; a noncombat terminal crouch; a modest shield salute. Audit shoulder elevation, shield/forearm intersections and repeated neighbor occlusion through continuous playback. The warm shield chime must identify protection without masking impact sounds.

**Hero test:** weaker refreshes cannot erase stronger absorption; overflow damages health correctly; UI absorption equals combat events; every shield pose stays readable in the front row.

### 02. Mira Dawnwell → **Mira**

**Stable ID:** `wc_u_human_priest` · **Human / Priest / Support**.

**Current skill:** Mend heals the ally with the lowest health percentage, including herself. **Proposed improvement:** make the triage decision explicit: preview an eligible injured recipient, release a directed pulse, and show effective healing separately from attempted overheal. Retain readiness when no valid injured target exists; define the displayed target as provisional until the canonical release snapshot. This is a targeting/feedback refinement, not resurrection, cleansing or an added periodic heal.

**Model and gear:** retain the olive face, auburn bun, cream layers, coral mantle and teal details. Thicken the open circular staff head so the hole survives 96-pixel rendering. Improve the square satchel's two clasps and strap routing without adding dangling potion simulation. Build broad cloth folds and a readable staff grip, with the face separated from the bright lantern.

**Motion and effects:** brisk balanced walking; a small point for basics; a visibly larger upward curve for Mend. The outgoing gold pulse ends as two rising leaflike arcs on the actual target. Keep healing distinct from Ada's shell and Elin's tempo chevrons. Review bun/staff clearance and the wide late Victory staff against neighbors.

**Hero test:** health-percentage ties, full-health readiness, self eligibility and capped effective healing; directed VFX must terminate on the same recipient as the event.

### 03. Rowan Emberwick → **Rowan**

**Stable ID:** `wc_u_human_mage` · **Human / Mage / Spell damage**.

**Current skill:** Ember Orb damages a small area around a captured location. **Proposed display skill:** **Ember Burst**. Preserve the faster, smaller burst niche relative to Zura. Add a quiet ground marker for the captured center and true radius, with one unambiguous arrival flash. The inspected skill diagram should teach that movement after release can escape the impact; it must not imply a homing explosion or persistent fire.

**Model and gear:** retain copper-brown skin, charcoal curls, thick round spectacles, angular collar, indigo coat and amber vest. Give the bronze orb bracket a clear asymmetrical outline and a convincing held support. Separate the coat tails, cuffs and belt book at gallery distance. Keep the emissive core small enough to expose the hand and frame.

**Motion and effects:** basics flick a compact spark; the active gathers both hands then pushes outward with visible follow-through. Animate orb presentation through sockets rather than physics. A low amber burst must leave feet, health bars and adjacent heroes visible. Distinguish a miss from a hit without a fabricated damage number.

**Hero test:** move the original target after release, defeat it in flight and verify the captured-area contract; one event per actual victim, no hidden fire ticks.

### 04. Liora Leafstep → **Liora**

**Stable ID:** `wc_u_elf_ranger` · **Elf / Ranger / Ranged damage**.

**Current skill:** Leafstep retreats while retaining attack range when a useful landing exists. **Proposed improvement:** make the reserved landing and reason for a blocked retreat legible. Revalidate the tactical improvement required by the contract, and return to the aiming stance facing the surviving target after movement. Preserve the skill's zero-damage positional identity and ordinary recovery; do not grant an unlisted free shot or immunity.

**Model and gear:** golden-brown face, gray-green eyes, pale hair fan, crescent bow and three separate short cloak panels remain defining shapes. Refine bow grip/draw contact, broad wooden limbs, quiver clearance and the narrow leg silhouette. The mint scarf should remain distinct from the moss costume without brightening the whole body.

**Motion and effects:** visible draw/hold/release; light lateral walk; a brief crouch and directed airborne step for the dash. The mint leaf trail fades rapidly and reveals the entire journey and destination. Verify continuous foot contact outside the deliberate magical slide.

**Hero test:** crowded rear row, corners, simultaneous reservations and target loss; no cooldown charge for a nonexistent useful landing; logical and displayed landing cells agree.

### 05. Elin Moonsong → **Elin**

**Stable ID:** `wc_u_elf_priest` · **Elf / Priest / Support**.

**Current skill:** Quickening Song increases adjacent allies' basic attack speed, including herself. **Proposed display skill:** **Quick Song**. Before placement, show the cells that would be in reach; at release, briefly identify the actual snapshotted recipients and their buff duration. Keep cooldowns unchanged. The improvement is learning which formation benefits and why moving into the circle later does not acquire the cast.

**Model and gear:** preserve the deep umber face, compact silver crown braid, crescent harp, teal tunic and pale sleeve ends. Increase the harp's useful negative space, retain a few thick stylized strings and improve supporting-hand contact. Strengthen broad sleeve planes without turning them into many fine leaves.

**Motion and effects:** a basic pluck remains compact; the active visibly plants both feet, opens the elbows and strikes a broad chord. Existing still reviews flagged small Attack/Active separation: verify the larger gesture in continuous crowded playback. Use a brief low teal ring and small tempo chevrons on recipients, with one audible chord rather than an endless aura loop.

**Hero test:** exact release recipients, Priest interaction with the positive buff, strongest-key refresh, no indefinite stacking and no shortened active cooldown.

### 06. Sylas Duskrun → **Sylas**

**Stable ID:** `wc_u_elf_rogue` · **Elf / Rogue / Disruption**.

**Current skill:** Backline Dash seeks a free cell beside the farthest enemy. **Proposed display skill:** **Backline Leap**. Expose the selected target and reserved landing during anticipation, with an explicit blocked outcome when the enemy formation leaves no valid cell. Preserve deterministic ties and the original dash-only payload. His tactical distinction is target selection across the formation, not an automatic assassination or hidden critical strike.

**Model and gear:** light bronze face, amber eyes, side-swept hair, dusk-blue single-shoulder mantle and paired curved blades. Improve the visible lower face and blade silhouette asymmetry. Keep the courier lantern and document case close to the body; they are cosmetic and grant no stealth, detection or inventory.

**Motion and effects:** quiet ready stance, quick narrow steps, separated alternating cuts, compressed leap anticipation and a clean directed launch. A blue ribbon and landing ring identify travel without concealing destination or implying invisibility. Keep the held blades clear of the document case during every turn.

**Hero test:** farthest-target ties, blocked cells, interrupted reservation cleanup, target defeat and clone timer preservation; the next basic remains a normal combat event.

### 07. Borin Stonebell → **Borin**

**Stable ID:** `wc_u_dwarf_guardian` · **Dwarf / Guardian / Defender**.

**Current skill:** Bell Stomp stuns adjacent enemies. **Proposed improvement:** a readable planted-foot windup and exact adjacent-cell ring must communicate an incoming interruption; the shared stun indicator starts and ends on authoritative ticks. Retain fixed control duration across stars and nonadditive refresh. His strength is local tempo control, not damage or knockback.

**Model and gear:** compact rectangular torso, open domed helmet, two large beard braids, slate armor, moss padding and bell-headed hammer. Refine the eye opening, beard/shoulder clearance and low supported hammer. Give the bell housing a strong outer rim without dense internal mechanics. Distinguish his rounded hammer from Dagna's rectangular forge head.

**Motion and effects:** low heavy idle, short deliberate stride, compact side impacts and a lifted foot followed by one firm stamp. A single amber ring and short low bell knock serve the cast. Maintain readable head/helmet placement when three stocky allies stand together.

**Hero test:** adjacent membership, cancellation of unreleased attacks, projectile persistence, fixed duration at all stars and refresh instead of summed stun time.

### 08. Tessa Brassbolt → **Tessa**

**Stable ID:** `wc_u_dwarf_ranger` · **Dwarf / Ranger / Ranged damage**.

**Current skill:** Heavy Bolt is a single stronger physical shot. **Proposed improvement:** separate normal fire and the deliberate charged shot through brace, timing, trail and a physical-damage indicator. Show range and windup clearly in the gallery, making exposure to interruptions an understandable cost. Keep the current single-target projectile; no hidden piercing, explosion or automatic retarget is added.

**Model and gear:** preserve freckles, copper hair, lifted forehead goggles, mustard jacket and horizontal crank crossbow. Improve both hand supports, housing bevels and the large decorative side wheel. Lower the crossbow outside attack anticipation so its width does not cover neighbors; leave the face above the stock.

**Motion and effects:** a compact basic brace/fire/reset, followed by a distinctly longer two-foot active brace. Existing reviews could not verify fine grip or shot release: add close and board-scale continuous checks. Use a compact bright bolt and physical impact flash; retain a fantasy crossbow sound.

**Hero test:** physical mitigation; no Ranger basic-only bonus on the active; target defeat in flight and interruption outcomes; camera framing through the full crossbow arc.

### 09. Dagna Anvilheart → **Dagna**

**Stable ID:** `wc_u_dwarf_warrior` · **Dwarf / Warrior / Melee damage**.

**Current skill:** Anvil Sweep damages adjacent enemies. **Proposed display skill:** **Hammer Sweep**. Improve target-area communication and attack-to-active contrast: the basic is a compact overhead action, the active is a low full sweep whose edge corresponds to the actual adjacent cells. Keep all victims hit once, with a single cast-level sound instead of a louder sound per victim. No incidental stun or knockback.

**Model and gear:** deep brown skin, high coiled black braid, brick-red workshop coat, square apron and broad forge hammer. Refine the hammer's beveled block shape, two-handed grip, shoulder armor separation and sturdy planted feet. Large cloth and leather folds are more useful than additional rune detail.

**Motion and effects:** heavy grounded steps and a weighted pivot that returns to the same logical cell. Keep torso twist, heel lift and recovery coherent through continuous playback. A low pale-gold sweep traces the real area without crossing a second row visually.

**Hero test:** diagonal neighbors exactly once, no self-hit, physical mitigation and source bonus once; no root displacement or visual radius inflation.

### 10. Rok Sunward → **Rok**

**Stable ID:** `wc_u_orc_warrior` · **Orc / Warrior / Melee damage**.

**Current skill:** Battle Tempo temporarily accelerates his basic attacks. **Proposed display skill:** **Battle Rhythm**. Improve the onset and end of the tempo window through a clear breath/foot plant, arm marks and timed status feedback. Preserve committed attack timing and unchanged ability cooldowns; show the modified basic cadence rather than speeding the entire character and every clip indiscriminately.

**Model and gear:** olive-green face, rounded tusks, topknot, circular ochre mantle, red sash and diagonal broad axe. Refine the broad rig's shoulder/hand anatomy, axe socket contact and mantle drape. His open off-hand is a deliberate balance shape. Keep the friendly determined expression and avoid extra spikes or trophies.

**Motion and effects:** weighty but open stance, compact alternating attacks and a readable rhythm change. Amber speed marks fade to a small buff icon instead of a full-body fire layer. Recheck the existing extreme-pose screen-margin case and crowd occlusion after any axe or mantle enlargement.

**Hero test:** attack-rate clamp, next interval calculation, no rewind of a committed strike, no cooldown acceleration, and correct stacking with the Warrior/Orc tier proposals.

### 11. Zura Stormcall → **Zura**

**Stable ID:** `wc_u_orc_mage` · **Orc / Mage / Spell damage**.

**Current skill:** Storm Ring releases a wider delayed magic burst around a captured location. **Proposed improvement:** make the longer commitment and wider coverage visually distinct from Rowan's faster burst. Display a thin radius edge during travel and one clear impact, then remove it. The storm must teach its snapshot location and lack of stun or damage over time, despite dramatic lightning imagery.

**Model and gear:** sage skin, modest tusks, three thick braids, cloud collar, storm-blue layered coat and open forked staff. Refine braid spacing and the staff's fork negative space. Keep the sky stone small and bounded in brightness. Improve coat clearance in crouches and the hand-to-staff relationship during the broad cast and Victory sweep.

**Motion and effects:** listening idle, small storm-mote basics, slow staff raise, circular intent gesture and firm release. Thin vertical streaks appear within a low blue boundary, with one capped thunder chord. Multi-Zura tests must preserve hero bodies, health bars and selection visibility.

**Hero test:** correct release snapshot, actual area edge, exactly one packet per victim, interruption before release and multiple overlapping storms without hidden stun or repeated damage.

### 12. Kesh Quickwind → **Kesh**

**Stable ID:** `wc_u_orc_rogue` · **Orc / Rogue / Disruption**.

**Current skill:** Closing Dash moves beside the current target within its authored distance limit. **Proposed display skill:** **Quickstep**. Show why this is a short chase rather than Sylas's farthest-enemy leap. Preview the reserved landing, keep the current target identity readable, and expose an unavailable/blocked reason without spending the skill when no improving landing exists. No bonus strike, slow or immunity is added.

**Model and gear:** jade face, short dark hair, pale tie, turquoise courier jacket, tall scarf loop and two short rounded blades. Refine the athletic broad-family proportions rather than uniformly shrinking Rok. Keep the map case and tan sash close to the torso and the scarf loop clear of the face.

**Motion and effects:** economical basics, grounded lead-shoulder glide and visible landing foot plant. A low pale-cyan streak and shorter wind accent distinguish him from Sylas. Control scarf follow-through with a small authored chain; no physics dependency.

**Hero test:** maximum range, already-adjacent behavior, blocked paths, same-tick movement and interrupt cleanup; displayed direction always agrees with the reserved destination.

## Wave 2 — turn the twelve existing expansion designs into playable heroes

These are new production obligations for this update. Their canonical designs already exist, but this document does not claim corresponding modeled/imported/verified assets. Reuse a rig family only after proportion, head and equipment deformation are measured. All receive the same gallery, combat, bot, animation and packaged acceptance as Wave 1.

### 13. Cass Vale → **Cass**

**Stable ID:** `wc_u_human_warrior` · **Human / Warrior / Melee damage**.

**Current skill:** Resolute Strike delivers one strong physical hit. **Proposed display skill:** **Firm Strike**. Emphasize a brief unmistakable windup followed by a concentrated single-target impact, preserving the contrast with Dagna's area sweep. The hero page should show that this is an ability packet and that armor/shields still counter it. Improve readability first; any magnitude or cooldown adjustment requires equal-investment tests against other Warriors.

**Model and gear:** medium-brown face, close hair, natural pale eyebrow streak, single squared shoulder plate, crimson coat and long diagonal sword. Build a short rigid-backed banner with a visible bracket and enough distance from the health-bar anchor. Refine two-handed support and clean brushed steel rather than ornate engravings.

**Motion and effects:** a low blade idle, short controlled cuts, measured forward active and delayed banner follow-through. Use a narrow warm-white trail with a compact physical impact; no armor break, splash or knockback. Victory raises the sword within a framed safe area rather than lifting the whole banner into UI.

**Hero test:** ability/basic bonus separation, interruption and shield absorption; banner and sword remain clear of faces, adjacent units and stat panels in all clips.

### 14. Neris Starbloom → **Neris**

**Stable ID:** `wc_u_elf_mage` · **Elf / Mage / Spell damage** (existing role label is imperfect for a nondamaging active; proposed explanatory role: **Control**).

**Current skill:** Starbind stuns one current target with no damage. **Proposed skill upgrade:** one projectile hits the current enemy with **magic damage followed by stun if the victim survives**. This gives her Mage class bonus a real damage component while preserving her primary interrupter identity. Proposed initial damage is **6,000 / 10,800 / 19,440 centipoints** at stars 1/2/3, equivalent to **60 / 108 / 194.4 HP** before source bonuses and resistance. These are **unimplemented, unbalanced proposal values**, not canonical stats or accepted outcomes. Keep the authored **1,250 ms stun at every star**, **radius 0**, **range 4 tiles**, **400 ms cast**, **200 ms projectile travel**, **300 ms recovery**, **3,500 ms first cast** and **9,500 ms cooldown** as the initial experiment inputs. Make the target and finite travel explicit; do not add automatic targeting of casting enemies in the first implementation.

The ordered effect contract must apply permitted source/Mage bonuses to magic damage exactly once, then resistance and shield absorption, resolve defeat, and apply stun only to a surviving valid target. A surviving shielded target may still be stunned even when its shield absorbs the damage: the status is a separate effect. A defeated target receives no stun. Control duration receives no Mage damage scaling. Implement a bounded composite effect list in the canonical ability schema and combat runtime; never insert hidden extra damage in a widget, animation notify or hero-ID branch.

**Model and gear:** cool brown face, midnight low hair knot, broken-circle headpiece, violet coat and open-hand star lens. Thicken the headpiece and silver lens ring to survive the bright lobby sky. The palm-held focus and flat chart case distinguish her from staff casters.

**Motion and effects:** a compact spark for basics, lens raised to eye level and both palms aligning for the active. A pale violet projectile ends in the shared stun indicator. Keep movement visibly possible outside stun; do not use lasting chains that imply another effect.

**Hero test:** ordered damage then survival check then stun, Mage bonus once, resistance/shield interactions, fully shield-absorbed hits, lethal hits, defeated targets in flight, existing interruption policy and constant duration at all stars. Test clustered interrupters for oppressive chains and compare against the original nondamaging control baseline.

### 15. Orla Hearthglow → **Orla**

**Stable ID:** `wc_u_dwarf_priest` · **Dwarf / Priest / Support**.

**Current skill:** Hearth Pulse heals herself and adjacent allies once. **Proposed display skill:** **Hearth Glow**. Improve the formation decision with a visible adjacency preview and an explicit one-shot pulse. Show effective healing per recipient and an aggregate cast total in inspection/replay information. Preserve the cost of grouping and the distinction from Mira's longer-range triage. Do not turn the lantern into a persistent regeneration aura.

**Model and gear:** warm dark face, silver side braids, rounded hood, rust coat, oatmeal apron and octagonal lantern. Build a deliberately rounded stocky silhouette distinct from Borin's rectangular plate. Use opaque warm lantern panes, thick handles and a supported carrying hand; avoid refractive glass.

**Motion and effects:** settled idle, modest light-mote basic, free arm opening while the lantern rises, then one low amber ring. Distinct warm bell cluster; cap total recipient audio. Defeat must lower the lantern without pushing it through knees or the board.

**Hero test:** self exactly once, adjacent snapshot, overheal excluded from totals, no continuing heal zone and correct Priest source scaling.

### 16. Tala Ironroot → **Tala**

**Stable ID:** `wc_u_orc_guardian` · **Orc / Guardian / Defender**.

**Current skill:** Shared Guard shields herself and adjacent allies. **Proposed improvement:** make group recipients and the smaller per-target protection distinct from Ada's personal guard. The cast projects short shield outlines onto actual recipients, then leaves compact individual absorption indicators. A placement preview explains how many allies can benefit; moving out afterward does not remove granted protection and moving in does not gain it.

**Model and gear:** deep moss face, tight braids, arched shoulders, bronze/leather armor, blue sash and rounded tower shield with a road emblem. Keep the travel pack low. Lower shield rest position so nearby support characters remain visible; the shape must not simply be a larger Ada shield.

**Motion and effects:** short mace basics, shield planted for the active and an outward free-hand cue. One low shared chime with quiet recipient ticks. Review overhead shoulders and shield turning against adjacent small allies.

**Hero test:** snapshot recipients, self once, source potency once, stronger-shield policy and independent expiry; no continuous aura or damage-sharing mechanic.

### 17. Pippa Oakstride → **Pippa**

**Stable ID:** `wc_u_halfling_warrior` · **Halfling / Warrior / Melee damage**.

**Current skill:** Stout Heart gives a short personal shield. **Proposed improvement:** preserve a mobile small Warrior's survival window rather than making a miniature Guardian. Give the shield an explicit short duration indicator and a clean break cue, with a fast return to the normal attacking stance. Damage, duration and cooldown start from canonical values; test investment-equivalent output and survival against Ada rather than adding a retaliatory proc by default.

**Model and gear:** adult freckled face, dense chestnut curls, apple-green quilted jacket, broad red scarf and round orchard buckler. Create a distinct adult Halfling proportion family instead of scaling a Dwarf or enlarging an infant-like head. The leaf-shaped club and circle shield carry identity above the crowd.

**Motion and effects:** full-foot quick steps, compact determined swings and a short contained hop/brace for the active. Keep logical position unchanged. A green-gold buckler-shaped outline remains proportional; audio is a wooden knock and warm chime.

**Hero test:** fixed duration at all stars, shield overflow and Halfling movement interaction; body/health anchor visibility beside Tala and Sora.

### 18. Finn Thistlearrow → **Finn**

**Stable ID:** `wc_u_halfling_ranger` · **Halfling / Ranger / Ranged damage**.

**Current skill:** Dulling Shot reduces a target's basic attack rate. **Proposed skill experiment:** choose the highest current basic-attack-rate enemy within range, falling back through deterministic distance and stable-ID ties. Show the selected enemy and rate change. Keep the effect restricted to attack tempo: no movement slow, cooldown delay or poison. This targeting proposal supplies a distinct answer to fast attackers, but needs counterplay and retarget tests before canonical adoption.

**Model and gear:** tan adult face, sandy curls, upward-tilted folded brim, river-blue vest and narrow triangular cape. Build a long upright bow, side quiver and readable hand spacing. Keep eyes visible under the brim; separate him from Liora through height, hat and vertical bow posture.

**Motion and effects:** compact bow basics; a visibly longer careful aim for the active. Blue descending chevrons communicate reduced tempo without immobilizing the target. Distinct descending two-note arrival sound.

**Hero test:** rate-based target ties, changing buffs during windup, strongest-key refresh, attack-rate floor and unchanged enemy movement/active cooldown.

### 19. Nella Quickpocket → **Nella**

**Stable ID:** `wc_u_halfling_rogue` · **Halfling / Rogue / Disruption**.

**Current skill:** Quick Feint stuns the current target briefly. **Proposed improvement:** strengthen her local interruption identity through an obvious off-hand feint and shared stun timeline, while keeping her lack of dash explicit. The gallery and tactics view should say that she must approach by ordinary movement; a Rogue icon must not suggest all Rogues teleport. Maintain the authored zero-damage stun unless a separate balance experiment justifies a change.

**Model and gear:** rich brown adult face, swept curls, plum festival jacket, teal cord and diamond cape. Make two broad fanlike batons distinct from the other Rogues' blades. Preserve anticipation visibility on a small body with broad gestures and thick prop tips.

**Motion and effects:** side-on ready stance, alternating short taps, off-hand false lead then one clear forward active. A compact gold star resolves into the common stun marker, with a short double-tap cue. No disappearance, injury effect or camera cut.

**Hero test:** interruption before release, no recall of released projectiles, fixed stun duration and role clarity at normal camera scale.

### 20. Milo Mistwhistle → **Milo**

**Stable ID:** `wc_u_halfling_mage` · **Halfling / Mage / Spell damage**.

**Current skill:** Mist Pop deals a small captured-area magic burst. **Proposed improvement:** make the repeated modest burst cadence distinguishable from Rowan's stronger burst and Zura's broad storm. Display the actual recharge and short low area mark; use a quick stir/flick rather than a grand windup. Any revised cadence must be authored in data and tested for total effective output, not sped up through animation playback alone.

**Model and gear:** adult mustached face, wavy hair, round sky-blue raincoat, high cream collar and thick spiral wand. The rigid folded umbrella disk is a cosmetic rear shape, not a shield or flight tool. Refine coat panel separation and side visibility of the spiral focus.

**Motion and effects:** curious but restrained idle, pale mote basics and one circular stir/flick. A blue-white cloudlet pops low and vanishes; retain a precise ground edge and low opacity rather than obscuring the battle. One rising whistle and soft pop.

**Hero test:** captured-area semantics, single damage event, no cloud ticks/blind/slow, repeated casts under Mage/Halfling combinations and crowd readability without bloom.

### 21. Sora Dawnscale → **Sora**

**Stable ID:** `wc_u_dragonkin_guardian` · **Dragonkin / Guardian / Defender**.

**Current skill:** Beacon Guard is a stronger personal shield. **Proposed display skill:** **Beacon Shield**. Preserve the expensive mixed-defense anchor role and make its cost-versus-protection difference legible in comparison with Ada. Show current resistance and remaining absorption accurately; do not imply immunity. Use a shield-facing vertical glint to identify her cast without a board-covering pillar.

**Model and gear:** pearl-gold scales, rounded muzzle, swept horns, short neck crest, pale armor, blue tabard and oval shield. Develop an actual Dragonkin head/neck proportion profile; a scaled human face under a scale texture is insufficient. Keep plantigrade feet and no wings or tail as authored. Build the gem and mace as restrained fixed props.

**Motion and effects:** tall steady idle, deliberate steps, compact mace strike and upward shield angle for the active. Low resonant chime; no mandatory roar. Inspect muzzle/neck/shoulder clearance in every clip and gallery turntable.

**Hero test:** Dragonkin resistance before damage, shield absorption/overflow, no immunity, and readable differences from Ada/Tala in mixed frontlines.

### 22. Varek Prismshot → **Varek**

**Stable ID:** `wc_u_dragonkin_ranger` · **Dragonkin / Ranger / Ranged damage**.

**Current skill:** Prism Shot fires one stronger magic shot; his basics also deal magic damage. **Proposed improvement:** make the damage type visible on both attack and skill descriptions, projectile treatment and combat inspection. This is the Ranger who pressures physical armor rather than another Tessa. Preserve finite projectile travel and a single target; crystalline appearance must not imply piercing, true damage or chaining.

**Model and gear:** blue-gray scales, short angular muzzle, outward blunt horn fins, dark-blue coat and forked short cloak. Create a prismatic bow with a dark supported grip and broad opaque facets. Use shaded dark/light planes for crystal identity without expensive refraction or full-white bloom. No hidden flight rig.

**Motion and effects:** low bow rest, deliberate bow alignment for the active and a narrow cyan projectile with compact impact sparkles. Keep both hands convincingly attached to the wide grip/limbs. Whole-body turn and Defeat must not sweep the bow across neighboring health bars.

**Hero test:** Ranger applies to magic basics but not the skill, correct resistance mitigation, target loss in flight and prism visibility with bloom disabled.

### 23. Iri Cinderstep → **Iri**

**Stable ID:** `wc_u_dragonkin_rogue` · **Dragonkin / Rogue / Disruption**.

**Current skill:** Prism Cut is a small true-damage hit. **Proposed display skill:** **Prism Cut** retained. Improve the counterplay explanation: the hit bypasses armor/resistance but shields still absorb it, and Iri has no dash. Give it a short recognizable anticipation glint and distinct true-damage icon. Keep its lower magnitude niche; expanding the roster is not a reason to inflate true damage until defensive compositions fail.

**Model and gear:** copper scales, soft-edged muzzle, close horns/neck crest, charcoal jacket, coral diagonal sash and paired crescent blades. Keep the slim low stance and visible joints. Small inset gems remain dark except on the active; do not create a constant glowing outline that hides the body.

**Motion and effects:** still balanced idle, compact alternating basics, one deliberate inward crescent preparation and short release. Thin white-violet impact with no injury detail, teleport or invulnerability. Inspect crest clearance during deep crouch and rapid turns.

**Hero test:** true damage bypasses armor/resistance only, applies permitted source bonuses once and still respects shields; equal-investment defensive counters remain worth testing.

### 24. Oren Skyward → **Oren**

**Stable ID:** `wc_u_dragonkin_priest` · **Dragonkin / Priest / Support**.

**Current skill:** Skyward Ward shields the ally with the lowest health percentage. **Proposed display skill:** **Sky Ward**. Proposed target-eligibility refinement: skip candidates for whom the new ward would be fully rejected by the existing stronger-shield policy, then select the lowest-health eligible ally using the same deterministic ties. If every candidate is ineligible, remain ready and continue basics. This avoids a visibly wasted support cast without adding healing or resurrection; exact eligibility and refresh semantics need canonical tests.

**Model and gear:** moss-gray scales, rounded muzzle/horns, white robes, deep-teal panels, short mantle and open hexagonal lantern staff. Preserve long vertical cloth planes and the compact map case. Build thick, readable lantern edges and controlled opaque glow, distinct from Mira's circle and Orla's carried octagon.

**Motion and effects:** balanced staff rest, small light-mote basics and a visible turn toward the selected recipient, followed by a free-palm lift. A brief gold connection ends in a hexagonal shield outline; use protection audio rather than Mira's heal cue. Keep staff clear of horns during raised poses.

**Hero test:** stronger-shield eligibility, health-percentage ties, self inclusion, all-ineligible readiness, exact expiry and no health restoration; compare alongside Mira and Tala in the same formation.

## Serialized production and review order

1. **Inventory and freeze the current evidence.** Record the actual source/export/import revisions and package being extended. Review existing heroes in the current game before setting geometry priorities. Preserve existing source paths and functional imports.
2. **Ada plus camera plus gallery prototype.** Refine one complete hero through body/face, gear, seven clips, portrait, actual stat/skill panel and crowded board. Demonstrate one reversible costume source revision and reimport. Capture both resolutions and continuous playback. This is the quality and framing reference; no other worker edits her binaries or shared rig/material files.
3. **Existing families and all twelve upgrades.** Complete Humans, Elves, Dwarves and Orcs in bounded per-hero ownership tasks. Improve the concrete grip/gesture/occlusion findings, verify each seven-clip set and run actual skill presentation before calling a hero accepted.
4. **Four additions using the existing families.** Cass, Neris, Orla and Tala extend Human/Elf/Dwarf/Orc coverage. Validate their special props and proposed target-selection semantics; do not assume reused skeleton names guarantee safe deformation.
5. **Halfling family and four heroes.** Start with Pippa's adult proportions, feet, scale and visibility; then Finn, Nella and Milo. Recheck small heroes beside the largest shields and staffs.
6. **Dragonkin family and four heroes.** Start with Sora's head/neck/armor calibration; then Varek, Iri and Oren. No wings, tails or flight expansion. Verify muzzle, horn, crest and focus clearances rather than disguising a human rig failure with effects.
7. **Whole-cast integration.** All 24 must recruit, merge, deploy, fight, lose, appear in bot decisions, render in the gallery and survive restart. Review **168 hero/clip cells continuously**, using still captures as indexed evidence rather than a substitute. Test all six race and six class families, both team orientations, current star variants, multiple similar bodies and concurrent effects.

One worker owns `data/units.json`; another may implement runtime logic only against an agreed versioned schema. Shared rigs/materials and generated manifests have one owner. Independent hero files can be authored in parallel after their family contract is frozen; never permit concurrent edits to the same `.blend`, `.uasset` or portrait export. Neris's composite ability and Finn/Oren's targeting proposals need bounded runtime change sets with deterministic fixtures and real combat tests, not separate ad hoc widget logic.

## Evidence and acceptance per hero

Each hero's review record must link: source revision; measured proportion/scale check; front/side/back and gallery view; 96-pixel portrait; equipment grip inspection; all seven continuous clips; source-to-Unreal import record; current packaged gameplay with actual skill release; updated model-matched portrait; two resolutions; defects and next action. Store these under the existing report conventions with per-hero identifiers. A thumbnail, animation file count or successful import is not finished-hero acceptance.

Acceptance requires recognizability, correct family anatomy, readable role, fitted costume, supported props, stable foot contact, no gross deformation, suitable game-camera VFX, matching canonical statistics and no clipped gallery animation across all star previews. The full cast may share quality materials and motion patterns, but cannot be twenty-four recolors of one body. Profiling must measure actual costs; the existing triangle/material targets are unprofiled design budgets until measured on the new 24-hero package.

The Auto Chess references inform interface function and readability. Use original Aurelune forms, palettes, portraits, equipment, icons, motions and sound. Do not trace the Exile's ice silhouette, copy reference models/textures, import outside skins, or reproduce the reference's gameplay items. The new gallery's visual gear view contains only Wonder Chess's authored character equipment.

## Principal design risks

- Doubling the recruitable set dilutes duplicate availability and changes the value of leveling, rerolls and two-/four-member traits. Art completion alone cannot validate the new economy or bots. Re-run equal-investment combat and full real tournaments using the new roster; do not simply turn on twelve definitions and reuse old balance acceptance.
- Neris's damage-plus-stun composite and Finn's target priority change combat value. Specify effect order, deterministic ties, event snapshot points and fallback behavior before implementation; watch for clustered control removing counterplay. Oren's no-waste targeting must agree with actual shield replacement rules.
- Many support and movement skills are intentionally nondamaging. Do not “improve” them by automatically adding unrelated damage, healing, taunts, status effects or a mana subsystem. Good feedback and a distinct tactical niche are valuable changes.
- A gallery close-up exposes fine face, hand, roughness and contact details that were previously small at the board camera. The existing sampled passes do not automatically certify gallery quality. Preserve the good silhouette work while budgeting actual close-view refinements.
- Race/class labels and short names must remain consistent across gallery, shop, localizations, bots, network messages, results and generated documents. Human-readable names never become stable identifiers.
- Cosmetic gear has no stats. New panels, star embellishments and monster rewards must not quietly reintroduce the gameplay equipment inventory the user explicitly excluded.
