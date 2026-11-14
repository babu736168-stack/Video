# The Great Laddoo Heist: detailed edition

Same story as `great_laddoo_heist.md`, rebuilt around the detailed characters from the anatomy sheets.

Video: `output/great_laddoo_heist_v2.mp4` (1280×720, 24 fps, about 2 min 7 s, with sound).

## What is new
- **Detailed characters.** Every character is assembled from the detailed parts on the anatomy sheets: smooth outlines, gradient shading, striped fur, glossy eyes, gloves, sneakers, saree, bangles and more.
- **Jointed motion.** Arms and legs rotate about their joints. Walking, running and tiptoeing alternate the legs, lift the feet and swing the arms in opposition, with a body bounce and a lean in the direction of travel.
- **Real expressions.** Eyes switch between open, wide, angry, sly, happy, closed, winking and dizzy (spirals). Mouths open and close with the dialogue, and heads tilt as the characters talk.
- **Lit kitchen.** Sunlight streams in through the window, with a soft vignette, a darker floor and contact shadows under every character.
- **Props that follow the hands.** The frying pan, plate of laddoos, fork, cheese, broom, mousetrap and pot all move with the character's arm or head.

## Acting and camera (latest update)
- **Bigger characters.** All four are about 35% larger in frame, with stride, shadows and props scaled to match.
- **Lifelike acting.** Everyone breathes and shifts weight while resting. The cat and dog sleep curled up with tucked paws, a tilted head and slow breathing and snoring. The cat stretches, yawns and rolls upright when he wakes, and the dog leaps up startled when the pan hits him. Walking now includes hip sway, a body roll and a counter-tilting head. While someone speaks, their hands and head move and their eyebrows rise.
- **Cinematic camera.** A shot list with hard cuts between angles, slow push-ins, tracking shots that follow the characters, close-ups on reactions, tilted dutch angles on dramatic moments, camera shake on every impact, a light handheld drift and a soft vignette.

## Movement and activities (latest update)
- **Real elbows and knees.** Every arm and leg is now two bones solved with inverse kinematics. Elbows bend when a character reaches, gestures or puts hands on hips. Knees flex on each step, and a lifted foot bends the knee. Feet stay planted on the floor while the body bobs and sways.
- **More to do.** The dog twitches and woofs in his sleep as he dreams. The mouse washes his face at the hole, and glances back over his shoulder when carrying a laddoo. The cat looks nervously over his shoulder while sneaking, and staggers around dizzy after bumping his head.
- **New ending.** After the broom chase, Dadi returns with the plate of laddoos. The cat trudges in with his head hung, apologises, and is forgiven with a laddoo, which he eats happily. The story is now about eight seconds longer, and the closing fanfare moves to the new "THE END".

## Code
| File | What it does |
|---|---|
| `src/charart.py` | Drawing toolkit: splines, gradients, shading, tapered limbs |
| `src/cat_v2.py`, `mouse_v2.py`, `dog_v2.py`, `dadi_v2.py` | The detailed character parts |
| `src/expr_v2.py` | Expression variants (eyes, mouths) |
| `src/rig_v2.py` | Cut-out rigs: joints, pose blending, squash and lean |
| `src/kitchen_v2.py` | Poses for every story moment, the lit world, cards, and the parallel renderer |

Render it with `cd src && python3 kitchen_v2.py` (about 5 to 10 minutes on 4 cores).
