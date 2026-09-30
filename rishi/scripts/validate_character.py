import bpy, os, json, math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'Rishi_Character_Master.blend'))
rig=bpy.data.objects['Rishi_Rig'];meshes=[o for o in rig.children if o.type=='MESH']
def update():
    rig.update_tag();bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
def worldverts(o):
    dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];e.to_mesh_clear();return v
allcoords=[v for o in meshes for v in worldverts(o)]
report={'height_m':max(v.z for v in allcoords)-min(v.z for v in allcoords),'floor_min_z':min(v.z for v in allcoords),'asset_marked':bool(bpy.data.collections['RISHI_001_CHARACTER'].asset_data),'linked_character_meshes':len(meshes),'bone_count':len(rig.data.bones),'finite_evaluated_coordinates':all(math.isfinite(c) for v in allcoords for c in v)}
checks={}
eye=bpy.data.objects['Eye white'];open_eye=worldverts(eye)
for prop,keyname in [('blink','Blink'),('brow_raise','Brow_Raise'),('smile','Smile'),('jaw_open','Jaw_Open')]:
    rig[prop]=1.;update()
    ks=[o.data.shape_keys.key_blocks[keyname] for o in meshes if o.data.shape_keys and keyname in o.data.shape_keys.key_blocks]
    checks[prop]={'targets':len(ks),'all_driven_to_one':all(abs(k.value-1)<1e-5 for k in ks)}
    if prop=='blink':checks[prop]['max_eye_vertex_motion_m']=max((a-b).length for a,b in zip(open_eye,worldverts(eye)))
    rig[prop]=0.;update()
report['expression_drivers']=checks
body=bpy.data.objects['Rishi_Body'];before=worldverts(body)
rig.pose.bones['forearm.L'].rotation_euler[0]=.7;update();after=worldverts(body)
report['forearm_pose_max_vertex_motion_m']=max((a-b).length for a,b in zip(before,after))
rig.pose.bones['forearm.L'].rotation_euler=(0,0,0);update()
report['pose_file_entries']=list(json.load(open(os.path.join(ROOT,'poses.json'))))
# Independent importer checks that the export contains usable skin/morph data.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,'Rishi_Character.glb'))
report['glb_import']={'armatures':len([o for o in bpy.data.objects if o.type=='ARMATURE']),'skinned_meshes':len([o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]),'morph_meshes':len([o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys])}
with open(os.path.join(ROOT,'validation-report.json'),'w') as file:json.dump(report,file,indent=2)
print('VALIDATION',json.dumps(report))
assert all(v['targets'] and v['all_driven_to_one'] for v in checks.values()),'Expression driver failure'
assert checks['blink']['max_eye_vertex_motion_m']>.005
assert report['forearm_pose_max_vertex_motion_m']>.01
assert report['glb_import']['armatures']==1
assert report['finite_evaluated_coordinates']
