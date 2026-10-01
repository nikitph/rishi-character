# Blender human base selected for the Rishi revision

`Blender_Stylized_Male_Base.blend` contains the **Body Male - Stylized** collection from Blender's Human Base Meshes v1.4.1 bundle, authored by **Julien Kaspar** and described by the source as based on **Snow**.

The main body has 12,502 vertices and 12,500 quad faces, with a UV map. Two separate eye meshes are included. There is no armature and no expression shape-key set. This is an imported modeling foundation; it is not a completed replacement for `Rishi_Character_Master.blend`.

The source mesh topology and UVs are unchanged. The collection was recentered, and stale object drivers referring to nonexistent mask modifiers were removed.

## Source and license

- [Official demo-files page](https://www.blender.org/download/demo-files/): Human Base Meshes v1.4.1, CC0.
- [Official archive](https://download.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip).
- [Bundle documentation](https://developer.blender.org/docs/release_notes/3.6/asset_bundles/).
- The bundle's embedded README says all provided assets are public domain under CC0. An additional inherited text block discusses the separate Rain Rig under CC-BY 4.0; the selected collection is the male Snow-derived base, and the bundle contains no armatures. Creator credit is retained here for provenance.
- `source-manifest.json` records the archive SHA-256 and inspected mesh counts.

## How this changes the character workflow

Use the supplied body, head, hands, feet, eyes and UV topology. Sculpt the rishi's elderly proportions and facial identity while preserving useful edge loops. Refit the existing beard, jata, clothes and beads to the new surface. Fit and test an animation rig against the imported anatomy, then create facial expressions on its connected facial topology. A base mesh reduces foundational modeling work; it does not itself supply the finished character performance rig.

The existing v0.1 master remains available as a visual design reference. The imported foundation has now been used for [the v0.2 character migration](../v2/README.md).
