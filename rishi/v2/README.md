# Rishi 001 — version 0.2

The recurring rishi character now uses Blender's **Human Base Meshes v1.4.1 / Body Male – Stylized** as its actual anatomical mesh. The previous procedural body, head and separate fingers are replaced by the imported connected body, with its original quad topology and UVs preserved.

## Open and reuse

- **`Rishi_Character_Master_v2.blend`**: authoritative Blender master.
- `Rishi_Character_v2.glb`: portable skinned copy with expression morph targets.
- `renders/`: neutral, face, teaching gesture, closed-eye and bent-knee inspections.
- `poses.json` and `apply_pose.py`: saved static starting poses.
- `migration-report.json`: source topology and UV comparison.
- `validation-report.json`: checks performed on the reopened master and imported GLB.

For a new film shot, use **File → Link → Collection → RISHI_001_CHARACTER_V2**, then make a Library Override. Pose `Rishi_Rig` in Pose Mode. Its custom properties `blink`, `brow_raise`, `smile` and `jaw_open` control expressions. The body and finger bones use FK; `beard.01` and `beard.02` provide secondary posing. The legacy jaw bone is reserved; use the `jaw_open` property for the current facial deformation.

For a saved pose, open `apply_pose.py` in Blender's Text Editor, set `POSE` to an entry from `poses.json`, and run it with this master open. Keep shot files separate from the neutral master.

## What changed

- Imported the complete body, head, hands, feet and eye meshes from the CC0 base.
- Sculpted a leaner torso, gaunter cheeks, subtly aged facial features and a longer lower face without remeshing.
- Preserved the body's **12,502 vertices, 12,500 quad faces and original UV coordinates**.
- Refitted the original stable 55-bone skeleton to the new shoulders, elbows, wrists, finger joints, hips, knees and feet.
- Replaced the old facial pieces with expression shapes on the connected source face.
- Refitted hair, beard and prayer beads; rebuilt fitted eyebrow geometry and shoulder cloth; adjusted trousers and added a wrapped hip garment.
- Retained the source mesh under the costume. A non-destructive `Clothed body visibility` Mask modifier hides covered body regions to prevent garment breakthrough. Disable this modifier when editing the full body or removing the costume.

## Source and credits

Anatomical base: **Julien Kaspar**, *Body Male – Stylized*, described by Blender as based on Snow. The [Human Base Meshes bundle](https://www.blender.org/download/demo-files/) is distributed under **CC0**, as also stated in its embedded README. See [the local source manifest](../source-assets/source-manifest.json) for the version, download URL and archive hash.

The rishi's costume, hair, appearance and refitted rig are project customizations. The composite scriptural design references remain documented in [the original design notes](../README.md#scriptural-references-and-limits).

## Verification and limits

The checks compare source topology and UV coordinates, inspect skin weights, exercise individual expression controls and finger/arm/knee deformation, and reimport the GLB. Supplied renders cover specific poses; they do not prove every possible movement is clean.

This is a reusable character prototype. It is not a finished dialogue rig: it has no complete viseme set or finished teeth/tongue setup. The current rig is FK, with no IK controls, cloth simulation, hair dynamics or broad library of corrective shapes. Extreme poses and close-up acting require further polish.

The Blender master is authoritative. GLB carries skinning and morph targets, but not the Blender facial drivers or procedural shader bump nodes. Use the Blender master for film shots and edit the source body there.

## Rebuild

From the repository root, with Blender on your PATH:

```sh
blender -b --python rishi/scripts/migrate_to_human_base.py
blender -b --python rishi/scripts/validate_human_base.py
```

The migration reads the original v0.1 master and the imported base in `rishi/source-assets/`, then regenerates this v0.2 directory. The original v0.1 master remains intact.
