# Rishi 001 — reusable Blender character

A stylized, elderly forest sage for recurring Blender films. This is a **version 0.1 character prototype**, not a finished feature-film animation asset.

## Files

- `Rishi_Character_Master.blend` — authoritative character, neutral A-pose, FK skeleton, facial controls, separate clothing and hair, stage cameras and lights.
- `Rishi_Character.glb` — portable rest-pose character with skeleton and morph targets. Blender remains the preferred animation environment.
- `Wise_Rishi.blend` — earlier static seated design study, not the animation master.
- `renders/character-*.png` — neutral, facial, expression and deformation inspection renders.
- `character-report.json` — generated geometry and weighting checks.
- `scripts/build_character.py` — reproducible character builder; uses helpers from `build_rishi.py`.

## Reusing the character in a film

1. In a shot file, use **File → Link**, select `Rishi_Character_Master.blend`, then **Collection → RISHI_001_CHARACTER**.
2. Make a **Library Override** to pose the linked rig in that shot. This retains a shared source for the character's identity.
3. Select `Rishi_Rig`, switch to Pose Mode and rotate the named bones. `root` moves the whole character. Limbs and fingers use FK controls. `beard.01` and `beard.02` provide secondary posing.
4. In the rig object's Custom Properties, adjust `blink`, `brow_raise`, `smile` and `jaw_open` from 0 to 1. Keyframe properties as needed. Blender drivers connect these sliders to the corresponding shape keys.
5. Keep the master in its neutral pose. Save each film scene as a separate shot file, and keep changes to the character's identity in the master.

The `RISHI_001_CHARACTER` collection is marked as an asset. Add this folder as a Blender asset library if desired. Props are separate in `06 Hermitage objects`; they are hidden in the master showcase and can be brought into shots independently. There is no baked motion or automatic cloth/hair simulation.

## Character identity

- Slender, elderly body; gentle face, long nose, high forehead and age folds.
- Warm brown skin, silver beard and eyebrows, matted hair tied in a high crown.
- Earth/ochre wrap and shoulder cloth; simple dark prayer beads.
- Bare feet, unadorned appearance; optional staff and water vessel.
- Open, attentive eyes for acting; closed-eye control for contemplation.

The model is a composite interpretation, not an identified historical person or a portrait of a particular rishi. Its age, proportions, silver palette and visual simplification are artistic choices. A prayer mala is a traditional design cue, not a universal scriptural requirement. No sect-specific forehead marking is imposed.

## Scriptural references and limits

- **Bhagavata Purana 7.12.21:** matted hair, uncut hair/moustache, waterpot, staff, bark covering and fire-colored garments are described for a vanaprastha. This is a specific ascetic prescription, not a universal definition of every rishi. https://vedabase.io/en/library/sb/7/12/21/
- **Valmiki Ramayana, Aranya Kanda 7:** Sutikshna's hermitage, ascetic presence, welcome and concern for living beings inform the character's composed, kindly demeanor. https://valmikiramayan.net/utf8/aranya/sarga7/aranya_7_prose.htm

The costume simplifies bark/fire-colored garments into animation-friendly stylized cloth. The character omits literal dirt and the animal skin for a clean recurring film design. Wisdom and character must ultimately also be conveyed through performance, dialogue and decisions.

## Current limits

- This is a working prototype FK rig with initial skin weights. Rendered checks cover the supplied poses; they do not prove every possible motion will deform cleanly.
- The body/head are procedural sculpt meshes. Full animation retopology, extensive corrective shapes, shoulder/hip stress testing, IK and animator control shapes remain future production work.
- The face has broad expression controls, not a complete dialogue/viseme system. The mouth has no finished teeth, tongue or oral cavity. Do not treat it as ready for close-up speech.
- Cloth and beard follow bones. Extreme leg, shoulder and head motion can require corrective posing or mesh work. There is no cloth collision or dynamics.
- The GLB carries skinned geometry and morph targets, but not Blender expression drivers or procedural bump materials. It is a portability copy, not an equivalent replacement for the Blender master.
- Not validated as a watertight 3D print.

## Rebuild

From this folder's parent:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python rishi/scripts/build_character.py
```

Rebuilding replaces generated master, export and character renders. Keep shot files elsewhere. Built with Blender 5.2.1 LTS.

## Inspection poses

`poses.json` stores the neutral, teaching gesture, closed-eye and bent-knee test poses. Open `scripts/apply_pose.py` in Blender's Text Editor, set `POSE` to one of the keys in that file, and run it with the master open. These are static starting poses, not motion clips. The script changes the current rig pose; save film shots separately.
