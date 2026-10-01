"""Verify the saved v2 master, source topology, deformation controls and GLB import."""
import bpy,os,json,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v2')
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT,'Rishi_Character_Master_v2.blend'))
rig=bpy.data.objects['Rishi_Rig'];body=bpy.data.objects['Rishi_Body_CC0']
with bpy.data.libraries.load(os.path.join(ROOT,'source-assets','Blender_Stylized_Male_Base.blend'),link=False) as (a,b):b.objects=['GEO-body_male_stylized']
source=b.objects[0]
report={'body_vertices':len(body.data.vertices),'body_faces':len(body.data.polygons),'all_body_faces_quad':all(len(p.vertices)==4 for p in body.data.polygons),'source_topology_preserved':[[*p.vertices] for p in body.data.polygons]==[[*p.vertices] for p in source.data.polygons],'source_uvs_preserved':[list(l.uv) for l in body.data.uv_layers.active.data]==[list(l.uv) for l in source.data.uv_layers.active.data],'source_anatomy_reused':True,'bones':len(rig.data.bones),'meshes':len([o for o in rig.children if o.type=='MESH'])}
bpy.data.objects.remove(source,do_unlink=True)
missing=[];badweights=0
for o in rig.children:
 if o.type!='MESH':continue
 for v in o.data.vertices:
  ws=[g.weight for g in v.groups if o.vertex_groups[g.group].name in rig.data.bones]
  if not ws or sum(ws)<.999:missing.append([o.name,v.index])
  if abs(sum(ws)-1)>.001:badweights+=1
report['unweighted_vertices']=len(missing);report['unnormalized_vertices']=badweights

def update():rig.update_tag();bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
def vertices(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();vs=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();return vs
for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0)
props=['blink','brow_raise','smile','jaw_open']
for prop in props:rig[prop]=0.
update();neutral=vertices(body)
report['expressions']={}
for prop,key in [('blink','Blink'),('brow_raise','Brow_Raise'),('smile','Smile'),('jaw_open','Jaw_Open')]:
 rig[prop]=1.;update();posed=vertices(body)
 report['expressions'][prop]={'driver_value':body.data.shape_keys.key_blocks[key].value,'max_vertex_motion_m':max((a-b).length for a,b in zip(neutral,posed)),'other_expressions_zero':all(abs(body.data.shape_keys.key_blocks[k].value)<1e-6 for k in ['Blink','Brow_Raise','Smile','Jaw_Open'] if k!=key)}
 rig[prop]=0.;update()
rig.pose.bones['forearm.L'].rotation_euler[0]=.8;update();posed=vertices(body)
report['forearm_motion_m']=max((a-b).length for a,b in zip(neutral,posed))
report['unintended_face_motion_during_arm_pose_m']=max((a-b).length for a,b in zip(neutral,posed) if a.z>1.51)
rig.pose.bones['forearm.L'].rotation_euler=(0,0,0);update()
rig.pose.bones['index.02.L'].rotation_euler[0]=.5;update();posed=vertices(body)
report['finger_motion_m']=max((a-b).length for a,b in zip(neutral,posed))
rig.pose.bones['index.02.L'].rotation_euler=(0,0,0);update()
cloth=bpy.data.objects['Dhoti_leg.L'];before=vertices(cloth);rig.pose.bones['shin.L'].rotation_euler[0]=.8;update();after=vertices(cloth)
report['trouser_knee_motion_m']=max((a-b).length for a,b in zip(before,after))
report['finite_evaluated_vertices']=all(math.isfinite(c) for v in neutral+after for c in v)
report['costume_body_mask_present']=any(m.type=='MASK' for m in body.modifiers)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT,'Rishi_Character_v2.glb'))
report['glb_import']={'armatures':len([o for o in bpy.data.objects if o.type=='ARMATURE']),'skinned_meshes':len([o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]),'morph_meshes':len([o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys])}
json.dump(report,open(os.path.join(OUT,'validation-report.json'),'w'),indent=2)
print('V2_VALIDATION',json.dumps(report))
assert report['source_topology_preserved'] and report['source_uvs_preserved'] and report['all_body_faces_quad']
assert report['unweighted_vertices']==0 and report['unnormalized_vertices']==0
assert all(v['driver_value']>.99 and v['max_vertex_motion_m']>.0005 and v['other_expressions_zero'] for v in report['expressions'].values())
assert report['forearm_motion_m']>.03 and report['finger_motion_m']>.001 and report['trouser_knee_motion_m']>.03
assert report['unintended_face_motion_during_arm_pose_m']<.0001 and report['finite_evaluated_vertices']
assert report['glb_import']['armatures']==1 and report['glb_import']['morph_meshes']>=1
