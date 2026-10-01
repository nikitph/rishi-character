"""Migrate Rishi 001 onto Blender's CC0 stylized human topology, without remeshing."""
import bpy, math, os, json, hashlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from math import sin, cos, pi, exp
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'v2');os.makedirs(os.path.join(OUT,'renders'),exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'Rishi_Character_Master.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['Rishi_Rig']
for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0)
for name in ['blink','brow_raise','smile','jaw_open']:rig[name]=0.
rig.update_tag();bpy.context.view_layer.update()
# Retain accessories and presentation; replace all primitive-based anatomy and face surfaces.
keep_brows=[o for o in bpy.data.collections['02 Face details'].objects if o.name.startswith(('Expressive silver brow','Brow hair'))]
for cname in ['01 Anatomy','02 Face details']:
 for o in list(bpy.data.collections[cname].objects):
  if o not in keep_brows:bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(os.path.join(ROOT,'source-assets','Blender_Stylized_Male_Base.blend'),link=False) as (a,b):
 b.objects=['GEO-body_male_stylized','GEO-body_male_stylized.eye.L','GEO-body_male_stylized.eye.R']
new=list(b.objects)
for o in new:
 bpy.data.collections['01 Anatomy'].objects.link(o)
 o.animation_data_clear();o.hide_set(False);o.hide_viewport=False;o.hide_render=False
bpy.context.view_layer.update()
body=next(o for o in new if o.name=='GEO-body_male_stylized');body.name='Rishi_Body_CC0'
eyes=[o for o in new if o!=body]
original=[list(body.matrix_world@v.co) for v in body.data.vertices]
original_faces=[list(p.vertices) for p in body.data.polygons]
original_uv=[list(v.uv) for v in body.data.uv_layers.active.data]

def gauss(x,center,width):return exp(-((x-center)/width)**2)
def age(p):
 x,y,z=p;ax=abs(x)
 # Reduce youthful chest bulk, keeping the continuous quad surface.
 torso=gauss(z,1.21,.23)*exp(-(ax/.185)**8)
 x*=1-.10*torso;y*=1-.16*torso
 # Leaner arms around their existing bone axes, not a change in arm pose.
 if ax>.18 and .95<z<1.43:
  a=Vector((math.copysign(.185,x),-.005,1.385));b=Vector((math.copysign(.39,x),-.008,.963));d=b-a
  t=max(0,min(1,(Vector((x,y,z))-a).dot(d)/d.length_squared));c=a+t*d
  w=.10*sin(pi*t)
  x=c.x+(x-c.x)*(1-w);y=c.y+(y-c.y)*(1-w)
 # Gaunt cheeks, longer lower face, a slightly lowered nose tip and softer brow.
 front=max(0,min(1,(-y-.055)/.07))
 cheek=gauss(ax,.067,.034)*gauss(z,1.568,.037)*front
 y+=.008*cheek;x*=1-.035*gauss(z,1.51,.075)*front
 z-=.010*gauss(z,1.493,.055)*front
 nose=gauss(x,0,.024)*gauss(z,1.584,.027)*max(0,min(1,(-y-.145)/.025))
 y-=.006*nose;z-=.004*nose
 # Age folds remain sculpted into the imported facial topology.
 y+=.0018*gauss(abs(x),.020+.35*(1.58-z),.004)*gauss(z,1.555,.035)*front
 y+=.0014*gauss(z,1.607+.10*(abs(x)-.042),.004)*gauss(abs(x),.046,.030)*front
 z-=.0025*gauss(z,1.649,.012)*gauss(abs(x),.043,.031)*front
 # Broad, shallow forehead furrows carved into the existing vertices.
 for zz in [1.692,1.715,1.737]:
  y+=.0013*gauss(z,zz,.0035)*gauss(x,0,.085)*front
 return Vector((x,y,z+.004))
for o in new:
 world=o.matrix_world.copy()
 for v in o.data.vertices:v.co=age(world@v.co)
 o.parent=None;o.matrix_world=Matrix.Identity(4);o.data.materials.clear()
 for p in o.data.polygons:p.use_smooth=True
skin=bpy.data.materials['Warm umber | aged skin']
body.data.materials.append(skin)
for n in skin.node_tree.nodes:
 if n.type=='BUMP':n.inputs['Strength'].default_value=.055;n.inputs['Distance'].default_value=.006
# Source eye topology is reused; iris and pupil use the existing front polygons.
def mat(name,color,rough):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m
white=mat('V2 Eye | warm sclera',(.60,.50,.36),.3)
iris=mat('V2 Eye | amber brown',(.10,.038,.012),.25)
pupil=mat('V2 Eye | pupil',(.003,.002,.001),.20)
for o in eyes:
 for m in [white,iris,pupil]:o.data.materials.append(m)
 center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 # Source poles and iris are centered on the full eye bounding box.
 cx=(min(v.co.x for v in o.data.vertices)+max(v.co.x for v in o.data.vertices))/2
 cz=(min(v.co.z for v in o.data.vertices)+max(v.co.z for v in o.data.vertices))/2
 for poly in o.data.polygons:
  p=sum((o.data.vertices[i].co for i in poly.vertices),Vector())/len(poly.vertices)
  r=math.hypot(p.x-cx,p.z-cz)
  if p.y<center.y-.020:poly.material_index=2 if r<.010 else 1 if r<.019 else 0
# Fit the original hair, clothes and jewelry to the new rest body.
def interp(z):
 anchors=[(0,0),(.17,.14),(.8565,.965),(.9215,1.035),(1.1865,1.326),(1.3485,1.445),(1.60,1.66)]
 for (a,b),(c,d) in zip(anchors,anchors[1:]):
  if z<=c:return b+(z-a)*(d-b)/(c-a)
 return z+.06
bvh=BVHTree.FromPolygons([v.co for v in body.data.vertices],original_faces,all_triangles=False)
def surface(x,z,front=True):
 hit,normal,index,dist=bvh.ray_cast(Vector((x,-2 if front else 2,z)),Vector((0,1 if front else -1,0)))
 return hit
accessories=[]
for cname in ['02 Face details','03 Jata and beard','04 Cloth','05 Mala']:
 for o in list(bpy.data.collections[cname].objects):
  if o.type!='MESH':continue
  world=o.matrix_world.copy()
  # Retire shape keys from the old facial surface, recreate only brow controls below.
  if o.data.shape_keys:o.shape_key_clear()
  o.animation_data_clear()
  for m in list(o.modifiers):
   if m.type=='ARMATURE':o.modifiers.remove(m)
   elif m.type=='SOLIDIFY':m.thickness=.002
  for v in o.data.vertices:
   p=world@v.co
   if cname in ['02 Face details','03 Jata and beard']:
    p=Vector((p.x*.92,p.y*1.20-.017,p.z+.057))
    if o.name.startswith(('Expressive silver brow','Brow hair')):
     hit=surface(p.x,p.z)
     if hit:p.y=hit.y-.004
   else:
    p=Vector((p.x*1.18,p.y*1.20-.005,interp(p.z)))
    if o.name.startswith(('Angavastra','Shawl')):
     hit=surface(p.x,p.z,p.y<.015)
     if hit:p.y=hit.y+(-.009 if p.y<.015 else .009)
   v.co=p
  o.parent=None;o.matrix_world=Matrix.Identity(4);o.vertex_groups.clear();accessories.append(o)
# Seat each necklace bead just above the chest or back, preserving its rounded geometry.
for o in bpy.data.collections['05 Mala'].objects:
 center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 hit=surface(center.x,center.z,center.y<0)
 if hit:
  target=hit.y+(-.011 if center.y<0 else .011);delta=target-center.y
  for v in o.data.vertices:v.co.y+=delta
# Refit trouser surfaces radially to the actual legs. Cover the hip join with a wrapped dhoti.
cloth=bpy.data.materials['Undyed bark ochre | handwoven cloth'];hem=bpy.data.materials['Worn ochre | woven edges']
for material in [cloth,hem,bpy.data.materials['Silver ivory | hair'],bpy.data.materials['Ash brown | jata shadows'],bpy.data.materials['Silver | fine strands']]:
 if material.use_nodes:
  for n in material.node_tree.nodes:
   if n.type=='BUMP':n.inputs['Distance'].default_value=.002;n.inputs['Strength'].default_value=.12
for o in list(accessories):
 if o.name.startswith(('Angavastra','Shawl','Dhoti_waist','Waist cord','Tucked','Expressive silver brow','Brow hair')):
  accessories.remove(o)
  if o in keep_brows:keep_brows.remove(o)
  bpy.data.objects.remove(o,do_unlink=True)
for o in accessories:
 if not o.name.startswith('Dhoti_leg'):continue
 side=1 if o.name.endswith('L') else -1
 for v in o.data.vertices:
  p=v.co;origin=Vector((side*.095,.012,p.z));d=p-origin;d.z=0
  if d.length<.001:continue
  direction=d.normalized()
  if p.z<.765:
   hit,no,idx,length=bvh.ray_cast(origin,direction,.22)
   if hit:
    target=max(d.length,(hit-origin).length+.016)
    p.x=origin.x+direction.x*target;p.y=origin.y+direction.y*target
  else:
   t=max(0,min(1,(p.z-.765)/.25));p.x=origin.x*(1-.40*t)+d.x*(1-.50*t);p.y=origin.y-.04*t+d.y*(1-.30*t)

def clothmesh(name,vs,fs):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.data.collections['04 Cloth'].objects.link(o);me.materials.append(cloth)
 for p in me.polygons:p.use_smooth=True
 s=o.modifiers.new('Soft woven surface','SUBSURF');s.levels=1;s.render_levels=2
 s=o.modifiers.new('Fabric thickness','SOLIDIFY');s.thickness=.002
 accessories.append(o);return o
vs=[];fs=[];N=96;M=24
for j in range(M+1):
 t=j/M;z=1.055-.285*t;rx=.125+.065*sin(t*pi/2);ry=.097+.018*sin(t*pi/2)
 for i in range(N):
  a=2*pi*i/N;fold=.002*sin(18*a+2*t)*sin(t*pi/2)
  vs.append(((rx+fold)*cos(a),(-.041+.029*t)+(ry+fold)*sin(a),z+.015*sin(3*a)*t))
for j in range(M):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
clothmesh('Dhoti_hipwrap',vs,fs)
# A continuous broad shoulder cloth, fitted with clearance rather than shrinkwrapped through skin.
# Rows are center x/z and front/back/over-shoulder guide y.
controls=[(-.05,1.045,.13),(-.09,1.20,.13),(-.13,1.34,.12),(-.145,1.418,.08),(-.145,1.447,.012),(-.145,1.415,-.07),(-.13,1.34,-.13),(-.085,1.235,-.15),(-.015,1.13,-.15),(.060,1.025,-.16)]
def catmull(a,b,c,d,t):return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
vs=[];fs=[];rows=90;cols=20
for j in range(rows+1):
 u=j/rows*(len(controls)-1);idx=min(int(u),len(controls)-2);t=u-idx
 p=catmull(Vector(controls[max(0,idx-1)]),Vector(controls[idx]),Vector(controls[idx+1]),Vector(controls[min(len(controls)-1,idx+2)]),t)
 for i in range(cols+1):
  cross=i/cols-.5;x=p.x+cross*.095;z=p.y+cross*.012;y=p.z
  if not 3.25<u<4.75:
   front=u>4;hit=surface(x,z,front)
   if hit:y=hit.y+(-1 if front else 1)*(.011+.003*(1+cos(cross*6*pi)))
   if z<1.10:y=min(y,-.145) if front else max(y,.090)
  else:
   z+=.013*cos(cross*pi)
  vs.append((x,y,z))
for j in range(rows):
 for i in range(cols):a=j*(cols+1)+i;fs.append((a,a+1,a+cols+2,a+cols+1))
clothmesh('Angavastra_refitted',vs,fs)
# Rounded, tapered eyebrow geometry follows the new brow ridge at its centerline.
for side in [-1,1]:
 curve=bpy.data.curves.new('Silver eyebrow','CURVE');curve.dimensions='3D';curve.resolution_u=16;curve.bevel_depth=.0038;curve.bevel_resolution=4;curve.use_fill_caps=True
 spline=curve.splines.new('BEZIER');spline.bezier_points.add(4)
 for i,(x,z) in enumerate([(.014,1.67),(.027,1.676),(.045,1.678),(.063,1.673),(.078,1.661)]):
  hit=surface(side*x,z);y=hit.y-.004 if hit else -.14
  p=spline.bezier_points[i];p.co=(side*x,y,z);p.radius=[.3,.9,1,.7,.03][i];p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new('Eyebrow_refitted.'+('L' if side>0 else 'R'),curve);bpy.data.collections['02 Face details'].objects.link(o);curve.materials.append(bpy.data.materials['Silver ivory | hair'])
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 for p in o.data.polygons:p.use_smooth=True
 keep_brows.append(o);accessories.append(o)

# Refit the existing stable bone names to the imported anatomical landmarks.
rig.location=(0,0,0);rig.rotation_euler=(0,0,0);rig.scale=(1,1,1)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
segments={}
def fit(name,a,b,roll=None):
 e=rig.data.edit_bones[name];e.head=a;e.tail=b
 if roll is not None:e.align_roll(Vector(roll))
 segments[name]=(Vector(a),Vector(b))
fit('root',(0,0,.02),(0,0,.16));fit('pelvis',(0,.012,.90),(0,.012,1.06));fit('spine',(0,.012,1.06),(0,.005,1.25));fit('chest',(0,.005,1.25),(0,0,1.405));fit('neck',(0,0,1.405),(0,-.01,1.52));fit('head',(0,-.01,1.52),(0,-.01,1.785));fit('jaw',(0,-.028,1.575),(0,-.12,1.49));fit('beard.01',(0,-.145,1.54),(0,-.17,1.40));fit('beard.02',(0,-.17,1.40),(0,-.145,1.285))
# Finger centerlines estimated from the source finger cross sections, retaining its relaxed pose.
vs=[Vector(p) for p in original]
fingers=[('index',-.055,1.0,.726),('middle',-.023,1.0,.711),('ring',.008,1.0,.718),('little',.034,.9,.747)]
for side,suff in [(1,'L'),(-1,'R')]:
 fit('clavicle.'+suff,(side*.035,0,1.405),(side*.185,-.002,1.385))
 fit('upper_arm.'+suff,(side*.185,-.002,1.385),(side*.30,-.016,1.196))
 fit('forearm.'+suff,(side*.30,-.016,1.196),(side*.390,-.01,.960))
 fit('hand.'+suff,(side*.390,-.01,.960),(side*.417,-.006,.849),(side,0,0))
 for label,y,length,tip in fingers:
  zs=[.851 if label!='little' else .828,.809 if label!='little' else .804,(tip+.809)/2,tip+.006]
  pts=[]
  for z in zs:
   samples=[p for p in vs if p.x>.3 and abs(p.y-y)<.014 and abs(p.z-z)<.009]
   x=sum(p.x for p in samples)/len(samples) if samples else .415
   pts.append((side*x,y,z+.004))
  for i in range(3):fit(label+'.%02d.'%(i+1)+suff,pts[i],pts[i+1],(side,0,0))
 pts=[(side*.391,-.047,.912),(side*.370,-.071,.865),(side*.361,-.081,.836),(side*.363,-.085,.82)]
 for i in range(3):fit('thumb.%02d.'%(i+1)+suff,pts[i],pts[i+1],(side,0,0))
 fit('thigh.'+suff,(side*.088,.025,.949),(side*.089,-.015,.524));fit('shin.'+suff,(side*.089,-.015,.524),(side*.096,.012,.10));fit('foot.'+suff,(side*.096,.012,.10),(side*.097,-.105,.036));fit('toe.'+suff,(side*.097,-.105,.036),(side*.098,-.165,.028))
bpy.ops.object.mode_set(mode='OBJECT')
# Bind continuous source body, including original fingers. Facial shapes keep head weights stable.
body.vertex_groups.clear()
for b in rig.data.bones:b.use_deform=b.name not in ['root','jaw','beard.01','beard.02']
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
for b in rig.data.bones:b.use_deform=True
# Use strictly head weights above neck to avoid unwanted arm/neck influences on the face.
g=body.vertex_groups.get('head') or body.vertex_groups.new(name='head')
ids=[v.index for v in body.data.vertices if v.co.z>1.51 or (v.co.z>1.46 and v.co.y<-.07)]
for group in body.vertex_groups:group.remove(ids)
g.add(ids,1,'REPLACE')
hide=body.vertex_groups.new(name='COSTUME_HIDDEN_SURFACE');hide.add([v.index for v in body.data.vertices if .155<v.co.z<1.045 and abs(v.co.x)<.27],1.,'REPLACE')
mask=body.modifiers.new('Clothed body visibility | disable to view full source mesh','MASK');mask.vertex_group=hide.name;mask.invert_vertex_group=True
sub=body.modifiers.new('Preserved quad topology | smooth surface','SUBSURF');sub.levels=1;sub.render_levels=2

def dist(p,a,b):
 d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-t*d).length

def bind(o,names):
 o.vertex_groups.clear();gs={n:o.vertex_groups.new(name=n) for n in names}
 for v in o.data.vertices:
  scores=sorted((dist(v.co,*segments[n]),n) for n in names)[:2]
  ws=[1/max(d,.01)**4 for d,n in scores];total=sum(ws)
  for (_,n),w in zip(scores,ws):gs[n].add([v.index],w/total,'REPLACE')
 o.parent=rig
 m=o.modifiers.new('Rishi skeletal deformation','ARMATURE');m.object=rig
 bpy.context.view_layer.objects.active=o
 while o.modifiers.find(m.name)>0:bpy.ops.object.modifier_move_up(modifier=m.name)
for o in eyes:bind(o,['head'])
for o in accessories:
 name=o.name
 if name.startswith('Beard'):names=['head','beard.01','beard.02']
 elif o in bpy.data.collections['03 Jata and beard'].objects.values() or o in keep_brows:names=['head']
 elif name.startswith('Dhoti_leg'):names=['pelvis','thigh.'+name[-1],'shin.'+name[-1]]
 elif name.startswith(('Dhoti_waist','Dhoti_hipwrap','Waist','Tucked')):names=['pelvis']
 elif name.startswith('Mala'):names=['chest']
 else:names=['pelvis','spine','chest']
 bind(o,names)
# The hip wrap follows each upper leg below the belt instead of remaining rigid at the pelvis.
wrap=bpy.data.objects['Dhoti_hipwrap'];wrap.vertex_groups.clear()
wg={n:wrap.vertex_groups.new(name=n) for n in ['pelvis','thigh.L','thigh.R']}
for v in wrap.data.vertices:
 leg=max(0,min(1,(1.045-v.co.z)/.19));leg=leg*leg*(3-2*leg)
 left=.5+.5*math.tanh(v.co.x/.028)
 for name,w in [('pelvis',1-leg),('thigh.L',leg*left),('thigh.R',leg*(1-left))]:
  if w>1e-7:wg[name].add([v.index],w,'REPLACE')

# Facial controls now deform the source facial mesh rather than floating primitive pieces.
body.shape_key_add(name='Basis')
def driver(key,prop):
 d=key.driver_add('value').driver;d.type='AVERAGE';v=d.variables.new();v.name='control';v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path='["'+prop+'"]'
for keyname,prop in [('Blink','blink'),('Brow_Raise','brow_raise'),('Smile','smile'),('Jaw_Open','jaw_open')]:
 key=body.shape_key_add(name=keyname,from_mix=False)
 for i,k in enumerate(key.data):
  p=body.data.shape_keys.key_blocks['Basis'].data[i].co.copy();x,y,z=p;front=max(0,min(1,(-y-.055)/.055))
  if prop=='blink':
   eyeX=.042 if x>=0 else -.042;dx=x-eyeX;dz=z-1.634
   # Elliptical influence around each eyelid; inner rims meet at a slightly lowered seam.
   w=exp(-((dx/.039)**6+(dz/.040)**6))*front*max(0,min(1,(abs(x)-.010)/.012))
   if abs(dx)<.050 and abs(dz)<.060:
    k.co.z+=(-.004-dz)*w*.95
    k.co.y-=.010*w*max(0,1-abs(dz)/.05)
  elif prop=='brow_raise':
   w=gauss(abs(x),.046,.041)*gauss(z,1.669,.028)*front;k.co.z+=.012*w
  elif prop=='smile':
   w=gauss(abs(x),.037,.027)*gauss(z,1.540,.024)*front;k.co.z+=.010*w;k.co.x+=math.copysign(.004*w,x)
  elif prop=='jaw_open':
   w=max(0,min(1,(1.545-z)/.04))*gauss(x,0,.077)*front*gauss(z,1.50,.09)
   k.co.z-=.018*w;k.co.y+=.006*w
 driver(key,prop)
for o in keep_brows:
 o.shape_key_add(name='Basis');key=o.shape_key_add(name='Brow_Raise')
 for v in key.data:v.co.z+=.012
 driver(key,'brow_raise')
# Normalize and audit every deform vertex.
for o in [body]+eyes+accessories:
 for v in o.data.vertices:
  ws=[(g.group,g.weight) for g in v.groups if o.vertex_groups[g.group].name in rig.data.bones];s=sum(w for _,w in ws)
  if s:
   for idx,w in ws:o.vertex_groups[idx].add([v.index],w/s,'REPLACE')
rig['asset_version']='0.2.0';rig['character_id']='RISHI_001';rig['base_asset']='Blender Human Base Meshes 1.4.1 / Body Male - Stylized / Julien Kaspar / CC0';rig['rig_notes']='Refitted FK body and fingers; continuous-mesh expression shapes; beard secondary controls. Prototype facial acting; no finished viseme set.'
asset=bpy.data.collections['RISHI_001_CHARACTER'];asset.name='RISHI_001_CHARACTER_V2';asset.asset_data.description='Rishi 001 v0.2: CC0 Blender stylized human base, preserved quad topology and UVs, refitted rig and costume.'
# Cameras suit the imported body's true proportions.
for name,loc,target,scale in [('Camera | character',(2.6,-6,2.3),(0,0,.99),2.22),('Camera | front',(0,-6,1.3),(0,0,.99),2.2),('Camera | expressions',(.75,-5,1.9),(0,-.02,1.62),.65)]:
 o=bpy.data.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.ortho_scale=scale
scene.camera=bpy.data.objects['Camera | character'];scene.render.resolution_x=1050;scene.render.resolution_y=1400;scene.cycles.samples=32
scene['Source']='Human Base Meshes v1.4.1, CC0, Julien Kaspar; sculpted without topology changes.'
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
path=os.path.join(OUT,'Rishi_Character_Master_v2.blend');bpy.ops.wm.save_as_mainfile(filepath=path)
# Reload to evaluate newly created driver dependencies in the same way as a reopened film shot.
bpy.ops.wm.open_mainfile(filepath=path);rig=bpy.data.objects['Rishi_Rig'];body=bpy.data.objects['Rishi_Body_CC0'];scene=bpy.context.scene
pose_records={}
def reset():
 for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0)
 for k in ['blink','brow_raise','smile','jaw_open']:rig[k]=0.
 rig.update_tag();bpy.context.view_layer.update()
def render(name,cam='Camera | character'):
 rig.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
 scene.camera=bpy.data.objects[cam];scene.render.filepath=os.path.join(OUT,'renders',name+'.png')
 pose_records[name]={'bones':{p.name:list(p.rotation_euler) for p in rig.pose.bones},'expressions':{k:float(rig[k]) for k in ['blink','brow_raise','smile','jaw_open']}}
 bpy.ops.render.render(write_still=True)
reset();render('rishi-v2-neutral');render('rishi-v2-face','Camera | expressions')
rig.pose.bones['forearm.L'].rotation_euler[0]=1.05;rig.pose.bones['head'].rotation_euler[1]=-.10;rig['brow_raise']=.4;rig['smile']=.4;render('rishi-v2-teaching')
reset();rig['blink']=1.;render('rishi-v2-blink','Camera | expressions')
reset();rig.pose.bones['thigh.L'].rotation_euler[0]=-.5;rig.pose.bones['shin.L'].rotation_euler[0]=.85;render('rishi-v2-knee','Camera | front')
reset();scene.camera=bpy.data.objects['Camera | character']
json.dump(pose_records,open(os.path.join(OUT,'poses.json'),'w'),indent=2)
# Reuse the same pose loader with the master in the new directory.
import shutil
shutil.copy2(os.path.join(ROOT,'scripts','apply_pose.py'),os.path.join(OUT,'apply_pose.py'))
p=open(os.path.join(OUT,'apply_pose.py')).read().replace("'character-teaching'","'rishi-v2-teaching'")
open(os.path.join(OUT,'apply_pose.py'),'w').write(p)
report={'version':'0.2.0','source':'Blender Human Base Meshes v1.4.1 / Body Male - Stylized','author':'Julien Kaspar','license':'CC0','body_vertices':len(body.data.vertices),'body_faces':len(body.data.polygons),'body_quad_faces':sum(len(p.vertices)==4 for p in body.data.polygons),'topology_matches_source':original_faces==[list(p.vertices) for p in body.data.polygons],'uv_coordinates_match_source':original_uv==[list(v.uv) for v in body.data.uv_layers.active.data],'bones':len(rig.data.bones),'mesh_objects':len([o for o in rig.children if o.type=='MESH']),'unweighted_body_vertices':sum(not any(g.weight>0 for g in v.groups) for v in body.data.vertices),'expressions':list(body.data.shape_keys.key_blocks.keys()),'status':'Refitted character prototype; tested poses only, not a production dialogue rig.'}
json.dump(report,open(os.path.join(OUT,'migration-report.json'),'w'),indent=2)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in rig.children:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'Rishi_Character_v2.glb'),use_selection=True,export_format='GLB',export_animations=False,export_skins=True,export_morph=True,export_extras=True,export_all_influences=True)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.ops.wm.save_as_mainfile(filepath=path)
print('MIGRATION_COMPLETE',json.dumps(report))
