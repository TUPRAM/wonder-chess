# Blood Drummer pose and drumming — 2026-10-14

The owner found Blood Drummer's pose and animation poor. Seen in the running game (lab clip recordings with
`tools/unreal/frame_inspect.py`, before and after):

- **Before.** At rest both drumsticks pointed sideways through the drum. The attack was a boxing punch combo
  with a drum beat laid over it: the body twisted until the drum swung sideways, and the frame report found both
  sticks passing through his torso (3–4 cm from the spine). In the cast he beat at face height with the sticks
  pointing up.
- **After.** At rest and while walking the sticks continue the forearms and hang at his sides, as in the
  reference art. Attacks keep the idle body upright while both arms beat the drum in turn; each stick head is
  aimed at its own spot on the drum skin and flicks up between beats. On each down-beat the stick end lands
  within 3–6 cm of its spot, and both sticks stay at least 20 cm from the spine. The cast keeps the ground stomp
  for the legs, with the upper-body bend reduced by 60%, and drums the same way. A one-against-one fight against
  Hammerer shows continuous drumming through the attacks, then the stun, the cast and drumming again.

Changes: two new held-item options in `WCHeroPresentation.cpp`, `rest_forearm` (hold an item along the forearm)
and `strike` (aim an item's tip at a spot on another item during listed clips, lifted with the arm's beat), and
Blood Drummer's entry in `hero_presentation.json` (attack body clip, beat targets, strike spots, cast
straightening). No model or animation asset changed; no Meshy work.

Not covered: the stun reaction (hands to the face) and the defeat fall are the original library clips, and the
drum still sits tilted slightly sideways on his body. Candidate presentation, not owner-approved.

## Wild stance — 2026-10-17

The owner wanted the arms and shoulders away from the body and a wilder, beast-like pose. A new `stance` option in
`hero_presentation.json` lays bone turns over chosen clips before the arm reaches are solved: for Blood Drummer the
shoulders shrug up and forward, the upper arms are held 40° out from the body with bent elbows, the back leans
forward with the head kept level, the legs stand wider and the knees bend 18°, and the whole pose heaves slowly with
the breath. It applies to idle, walk, run, attack, cast, stun and celebration, not the defeat fall. With
`plant_feet` the hips come down by however far the bent knees lift the lower foot, so the feet stay exactly where
the clips put them (checked in all four recorded clips). The drumming follows the stance with flared elbows and a
bigger beat (28 cm).

The drumsticks are now placed once each frame's bones are final (`PlaceStrikes`, on the skeleton's
bones-finalised hook). Before, they were placed from the previous frame's hand, and a quick wrist turn of the arm
reach could flick a stick sideways for a frame or two (up to 145° in one frame during the cast); the largest
frame-to-frame turn is now 23°, and the sticks stay at least 12 cm from the spine.

The wild stance appears as the right-hand column of the `middle-*.gif` comparisons below.

The owner found the wild stance too wide and asked for the middle of the two versions, so every stance angle and
drumming value is now halfway: arms 20° out, shoulders up 10° and forward 7°, elbows bent 14°, lean 9°, legs 4°
wider, knees bent 9°, breath 2.5°, beat 21 cm with snap 1.7, hands at ±33 cm. The feet stay where the clips put
them, the largest frame-to-frame stick turn is 16°, and the stick ends stop within 1 cm of their spots (about 4 cm
above the skin), where the 2026-10-14 version went up to 6 cm past. GIFs (before, middle, wild): `middle-idle.gif`,
`middle-attack.gif`, `middle-cast.gif`, `middle-walk.gif`.

## Fist grip and drum collision — 2026-10-17

The owner asked for collision on the model and a better finger grip on the drumsticks. Close-ups (the frame
recorder now takes `-WCRecBone=<bone>` / `frame_inspect.py --bone` to centre on a hand) showed that the handle ran
along the outside of a fixed, tightly closed fist, and that the arms swung through the drum while walking.

- **Grip.** The handle is seated in the fist again: along the line from the little-finger knuckle to the index
  knuckle, 4 cm out from the knuckles towards the curled fingers and 2.1 cm back towards the wrist (grip `wrap.seat`).
  At load each finger joint then bends from straight until the next joint, or the fingertip, touches a 4.5 cm
  cylinder round the handle (`wrap.radius`: the 2 cm handle plus half a finger). The bends come out at 46–78° at the
  knuckles, 44–64° in the middle and 32–44° at the tips; the thumb, whose base the handle passes, keeps its curl.
- **Wrist.** Instead of the stick turning inside the hand, the hand turns (grip `wrist`): at rest the stick is cocked
  down and forward from the forearm (up to 40°); while drumming the wrist starts straight and aims the stick at its
  strike spot (up to 90°). Measured slip of the stick inside the fist: 0° at rest and walking, at most 2° in the
  attack, at most 18° for a frame at the top of a cast flick.
- **Collision.** The drum is a solid cylinder (`solid` on the drum item, 45 cm across, 29 cm tall, following its
  tilted skin). Hands and forearms are pushed out of it, with a 6 cm margin, before the wrists aim; held sticks are
  turned away from it except when striking. Measured: no hand inside the drum in any clip, sticks at most brushing
  the rim (under 1.5 cm, less than the handle's own thickness), stick ends within 2 mm of their strike spots.
- **Drum level.** The drum had been turned 14° sideways on his body, which made the left stick cut under the raised
  side of the skin; it now hangs level (`rotation` 0).
- The beat targets moved 6 cm forward and lower (`[±33, 8, 124]`) so the seated sticks still reach the skin.

Images: `grip-before-after.jpg` (the fist from four sides, fixed finger bend above, wrapped below) and
`grip-attack.gif` (upper body while drumming).

## Images

Stills of the original against the 2026-10-14 version: `attack-before-after.jpg`, `idle-cast-before-after.jpg`,
`walk-and-duel-after.jpg`. The motion GIFs of the superseded steps (2026-10-14 against the original, the wild
stance, a fight against Hammerer) were not committed; they are kept locally in
`support/runs/frames/blood-drummer-gifs-20261017/`. All candidate presentation, not owner-approved.
