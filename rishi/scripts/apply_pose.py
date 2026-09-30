"""Run in Blender's Text Editor with the master open; choose POSE below."""
import bpy, json, os
POSE = 'character-teaching'
path = os.path.join(os.path.dirname(bpy.data.filepath), 'poses.json')
with open(path) as file:
    poses = json.load(file)
rig = bpy.data.objects['Rishi_Rig']
for name, rotation in poses[POSE]['bones'].items():
    bone = rig.pose.bones[name]
    bone.rotation_mode = 'XYZ'
    bone.rotation_euler = rotation
for name, value in poses[POSE]['expressions'].items():
    rig[name] = value
rig.update_tag()
bpy.context.scene.frame_set(bpy.context.scene.frame_current)
bpy.context.view_layer.update()
print('Applied pose:', POSE)
