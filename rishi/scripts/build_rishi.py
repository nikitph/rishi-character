import bpy, math, random, json, os
from mathutils import Vector
from math import sin, cos, pi
random.seed(21)
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
cols={}
for name in ['01 Anatomy','02 Face details','03 Jata and beard','04 Cloth','05 Mala','06 Hermitage objects','07 Stage']:
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); cols[name]=c
CURRENT='01 Anatomy'
def put(o,name,mat=None):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    cols[CURRENT].objects.link(o)
    if mat: o.data.materials.append(mat)
    if o.type=='MESH':
        for p in o.data.polygons:p.use_smooth=True
    return o

def material(name,color,rough=.6,noise=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes; p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
    if noise:
        t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=80;t.inputs['Detail'].default_value=3
        b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=noise;b.inputs['Distance'].default_value=.025
        m.node_tree.links.new(t.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
    return m
skin=material('Warm umber | aged skin',(.31,.145,.075),.62,.16)
hair=material('Silver ivory | hair',(.51,.48,.40),.73,.2)
hairD=material('Ash brown | jata shadows',(.19,.17,.135),.8,.28)
hairL=material('Silver | fine strands',(.68,.64,.53),.7)
cloth=material('Undyed bark ochre | handwoven cloth',(.34,.14,.045),.93,.42)
hem=material('Worn ochre | woven edges',(.51,.25,.09),.9,.3)
bead=material('Dark seeds | mala',(.095,.036,.014),.74,.6)
wood=material('Weathered wood',(.14,.067,.026),.9,.35)
pot=material('Earth | water vessel',(.29,.108,.045),.72,.2)
dark=material('Warm crease shadow',(.077,.027,.012),.9)
stone=material('Charcoal stone',(.095,.11,.102),.85,.45)
matte=material('Backdrop',(.027,.043,.04),.95)

def uv(name,loc,scale,mat,seg=40,rings=28):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
    o=put(bpy.context.object,name,mat);o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o

def mesh(name,verts,faces,mat,sub=0):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update()
    o=bpy.data.objects.new(name,m);cols[CURRENT].objects.link(o);o.data.materials.append(mat)
    for p in m.polygons:p.use_smooth=True
    if sub:
        s=o.modifiers.new('Soft sculpted surface','SUBSURF');s.levels=sub;s.render_levels=sub
    return o

def strand(name,pts,radius,mat,radii=None):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=10;c.bevel_depth=radius;c.bevel_resolution=3
    s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for i,(b,p) in enumerate(zip(s.bezier_points,pts)):
        b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO';b.radius=radii[i] if radii else 1
    o=bpy.data.objects.new(name,c);cols[CURRENT].objects.link(o);c.materials.append(mat);return o

def limb(name,a,b,r1,r2,mat):
    d=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
    o=uv(name,mid,(r1,r2,d.length/2+r1*.4),mat)
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o

def fuse(objects,name,voxel=.028):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=objects[0];o.name=name
    mod=o.modifiers.new('Unified sculpt volume','REMESH');mod.mode='VOXEL';mod.voxel_size=voxel;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=o.modifiers.new('Relax anatomy','SMOOTH');mod.factor=.65;mod.iterations=5;bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=o.modifiers.new('Sculpt surface','SUBSURF');mod.levels=1;mod.render_levels=1
    return o

# Slender seated body, shoulders relaxed.
parts=[uv('Pelvis',(0,.08,1.04),(.53,.35,.42),skin),uv('Abdomen',(0,.05,1.6),(.42,.28,.60),skin),uv('Rib cage',(0,.08,2.18),(.59,.30,.51),skin),uv('Neck',(0,.06,2.79),(.205,.205,.37),skin)]
for side in [-1,1]:
    parts += [uv('Deltoid',(side*.59,.055,2.40),(.235,.24,.27),skin),limb('Upper arm',(side*.62,.03,2.36),(side*.86,-.06,1.77),.165,.18,skin),uv('Elbow',(side*.86,-.06,1.76),(.145,.15,.18),skin),limb('Forearm',(side*.86,-.06,1.77),(side*1.00,-.53,1.28),.13,.14,skin),uv('Palm',(side*.98,-.63,1.20),(.15,.21,.075),skin)]
body=fuse(parts,'Body | unified sculpt')
# A coherent face volume: cranium, cheeks, muzzle, long nose, ears.
parts=[uv('Cranium',(0,.035,3.35),(.415,.35,.58),skin),uv('Jaw',(0,-.055,3.03),(.32,.28,.26),skin),uv('Chin',(0,-.17,2.94),(.20,.20,.14),skin),uv('Nose bridge',(0,-.326,3.35),(.077,.11,.23),skin),uv('Nose tip',(0,-.426,3.20),(.105,.10,.078),skin)]
for side in [-1,1]:
    parts += [uv('Cheekbone',(side*.25,-.225,3.25),(.16,.135,.16),skin),uv('Muzzle',(side*.09,-.282,3.10),(.12,.088,.1),skin),uv('Nostril wing',(side*.087,-.381,3.18),(.058,.07,.044),skin),uv('Brow plane',(side*.18,-.28,3.51),(.185,.08,.08),skin),uv('Ear',(side*.415,.00,3.27),(.093,.09,.18),skin),uv('Earlobe',(side*.424,-.012,3.13),(.067,.065,.082),skin)]
head=fuse(parts,'Head | elderly sage sculpt',.012)
CURRENT='02 Face details'
# Closed lids with raised upper and lower margins, age folds.
for side in [-1,1]:
    for name,z,dep,r in [('Closed eyelid',3.405,-.326,.011),('Upper lid',3.434,-.327,.017),('Under-eye fold',3.35,-.306,.009)]:
        strand(name,[(side*.075,dep+.004,z+.005),(side*.16,dep-.018,z-.021),(side*.245,dep+.006,z-.016),(side*.302,dep+.028,z+.01)],r,skin if name!='Closed eyelid' else dark,[.3,1,1,.2])
    uv('Nostril shadow',(side*.071,-.441,3.158),(.025,.010,.012),dark,24,16)
    strand('Ear helix',[(side*.42,-.07,3.13),(side*.463,-.068,3.24),(side*.447,-.055,3.40),(side*.396,-.055,3.38)],.014,skin,[.4,1,1,.3])
    strand('Ear concha',[(side*.43,-.085,3.20),(side*.421,-.091,3.28),(side*.438,-.080,3.33)],.012,dark,[.2,.8,.1])
    for j in range(3):
        strand('Crow foot',[(side*.29,-.283,3.40-j*.015),(side*.345,-.25,3.395-j*.033),(side*.363,-.213,3.38-j*.04)],.0045,dark,[.1,.6,.1])
    strand('Nasolabial fold',[(side*.122,-.363,3.17),(side*.171,-.326,3.11),(side*.179,-.292,3.038)],.006,dark,[.1,.65,.1])
    for j in range(8):
        x=.075+j*.028
        strand('Silver eyebrow',[(side*x,-.338+max(0,x-.17)*.24,3.51),(side*(x+.032),-.35+max(0,x-.17)*.27,3.548),(side*(x+.064),-.321+max(0,x-.17)*.25,3.534)],.013,hair,[.55,1,.05])
for j in range(3):
    z=3.64+j*.058
    strand('Forehead age line',[(-.24,-.254+j*.024,z),(-.12,-.308+j*.022,z+.009),(0,-.325+j*.022,z+.014),(.12,-.308+j*.022,z+.009),(.24,-.254+j*.024,z)],.004, dark,[.1,.4,.6,.4,.1])
strand('Resting mouth',[(-.137,-.35,3.066),(-.067,-.367,3.057),(0,-.373,3.061),(.067,-.367,3.057),(.137,-.35,3.066)],.009,dark,[.1,.7,1,.7,.1])
strand('Lower lip',[(-.1,-.347,3.044),(0,-.368,3.039),(.1,-.347,3.044)],.017,skin,[.2,1,.2])
# Fingers rest gently on the knees, individual mesh volumes and nail plates.
for side in [-1,1]:
    for j in range(4):
        x=side*(.88+j*.065);y=-.68
        strand('Resting finger',[(x,y,1.20),(x+side*.015,y-.14,1.18),(x+side*.01,y-.22+(abs(j-1.5)*.025),1.14)],.036,skin,[1,1,.65])
    strand('Relaxed thumb',[(side*.88,-.60,1.20),(side*.79,-.68,1.20),(side*.80,-.78,1.16)],.046,skin,[1,.85,.6])
    strand('Clavicle',[(side*.08,-.224,2.51),(side*.29,-.246,2.48),(side*.48,-.195,2.47)],.022,skin,[.1,1,.1])
CURRENT='03 Jata and beard'
# Sculpted beard locks are tapered organic ribbons/tubes with nested fine strands.
for i in range(27):
    u=(i-13)/13;x=.31*u;z=3.15-.12*(1-abs(u));endz=2.25+.34*abs(u)**1.4
    pts=[(x,-.22-.055*(1-abs(u)),z),(x*1.10,-.36,2.91),(x*.80+.02*sin(i),-.405,2.65),(x*.46+.025*sin(i*2),-.34,endz)]
    strand('Beard | layered silver lock',pts,.048,hair if i%4 else hairD,[.72,1,.70,.035])
    for k in range(3):
        off=(k-1)*.012
        p=[(a+off,b-.03,c+.006*sin(i+k)) for a,b,c in pts]
        strand('Beard | fine relief',p,.0045,hairL,[.25,1,.75,.01])
for side in [-1,1]:
    for j in range(8):
        strand('Moustache | flowing lock',[(side*.02,-.423,3.115+j*.005),(side*.11,-.408,3.102+j*.005),(side*.19,-.364,3.055),(side*.215,-.344,2.98-j*.008)],.015,hair,[.3,1,.75,.01])
    for j in range(6):
        strand('Temple silver locks',[(side*.36,.02+j*.035,3.68),(side*.403,-.02+j*.03,3.47),(side*.385,-.06+j*.03,3.21),(side*.31,-.20+j*.02,2.91)],.034,hairD if j>2 else hair,[.65,1,.8,.04])
# Hair cap swept up from a receding hairline into a braided jata crown.
for i in range(25):
    ang=2*pi*i/25
    pts=[]
    for k in range(9):
        t=k/8;rad=.39*(1-.64*t)
        z=3.62+.52*t
        pts.append((rad*sin(ang+.25*t),.06+rad*cos(ang+.25*t)*.84,z+.07*sin(t*pi)))
    strand('Jata | swept scalp lock',pts,.052,hairD if i%3 else hair,[.45]+[1]*7+[.7])
for i in range(10):
    a=2*pi*i/10
    pts=[]
    for k in range(24):
        t=k/23;ang=a+t*pi*2.0;rad=.24+.035*sin(t*pi)
        pts.append((rad*sin(ang),.08+rad*cos(ang)*.82,3.96+.43*t))
    strand('Jata | crown coil',pts,.064,hairD if i%3 else hair,[.55]+[1]*22+[.15])
strand('Jata binding',[(.278*sin(a),.08+.239*cos(a),4.03) for a in [2*pi*i/32 for i in range(33)]],.019,wood)
CURRENT='04 Cloth'
# A draped continuous lower garment, shaped to cross-legged volume with radial folds.
v=[];f=[];N=128;M=30
for j in range(M+1):
    t=j/M
    for i in range(N):
        a=2*pi*i/N
        r=.28+1.01*(sin(t*pi/2)**.75)
        x=r*cos(a);y=.045+.66*r*sin(a)
        z=1.25-.86*t+.16*sin(pi*t)+.055*sin(18*a+4*t)*sin(t*pi/2)+.025*sin(31*a-2*t)*t
        v.append((x,y,z))
for j in range(M):
    for i in range(N):
        a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
o=mesh('Lower wrap | radial woven folds',v,f,cloth,1);s=o.modifiers.new('Cloth thickness','SOLIDIFY');s.thickness=.025
strand('Lower wrap | worn hem',v[-N:]+[v[-N]],.025,hem)
# Two raised diagonal cloth folds suggest folded thighs without exposed disconnected limbs.
for side in [-1,1]:
    for j in range(5):
        strand('Lap drapery fold',[(side*.10,-.29,1.15-j*.04),(side*.49,-.51-j*.032,1.06-j*.053),(side*.95,-.41-j*.027,.86-j*.045),(side*1.18,-.22,.63-j*.025)],.020 if j%2 else .03,cloth,[.1,1,1,.1])
# Shoulder shawl: finite width textile strip, following the left shoulder to the right hip.
path=[(-.39,.19,2.67),(-.52,-.03,2.64),(-.46,-.30,2.43),(-.28,-.355,2.16),(-.07,-.36,1.91),(.16,-.345,1.63),(.32,-.33,1.34),(.40,-.40,1.15)]
v=[];f=[];W=16
for j,p in enumerate(path):
    for i in range(W+1):
        u=(i/W-.5);v.append((p[0]+u*.39,p[1]-.017*cos(u*8*pi),p[2]+u*.11))
for j in range(len(path)-1):
    for i in range(W):
        a=j*(W+1)+i;f.append((a,a+1,a+W+2,a+W+1))
o=mesh('Angavastra | shoulder drape',v,f,cloth,2);s=o.modifiers.new('Woven thickness','SOLIDIFY');s.thickness=.02
for side in [-1,1]:strand('Shoulder shawl | selvedge',[(p[0]+side*.19,p[1]-.008,p[2]+side*.055) for p in path],.014,hem)
CURRENT='05 Mala'
for i in range(49):
    a=2*pi*i/49;x=.32*sin(a);y=.055-.37*cos(a);z=2.50-.41*max(cos(a),0)
    uv('Mala | seed %02d'%i,(x,y-.025,z),(.036,.036,.040),bead,16,12)
strand('Mala | tassel',[(0,-.352,2.07),(0,-.354,1.99),(.012,-.35,1.95)],.018,wood)
for side in [-1,1]:
    for i in range(13):
        a=2*pi*i/13
        uv('Wrist mala',(side*.98+.102*cos(a),-.51+.056*sin(a),1.33+.075*sin(a)),(.027,.027,.027),bead,12,8)
CURRENT='06 Hermitage objects'
# Water pot as a closed lathed vessel with a dark mouth and simple loop handle.
def lathe(name,profile,center,mat):
    verts=[];faces=[];n=64
    for r,z in profile:
        for i in range(n):
            a=2*pi*i/n;verts.append((center[0]+r*cos(a),center[1]+r*sin(a),center[2]+z))
    for j in range(len(profile)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
    return mesh(name,verts,faces,mat,1)
lathe('Kamandalu | earthen vessel',[(0,0),(.18,0),(.26,.12),(.285,.28),(.23,.40),(.105,.48),(.10,.58),(.13,.60),(.13,.63),(.082,.63),(.078,.55),(.065,.47),(0,.46)],(1.60,-.05,.30),pot)
strand('Kamandalu | carrying loop',[(1.43,-.045,.68),(1.29,-.045,.91),(1.40,-.045,1.12),(1.66,-.045,1.09),(1.77,-.045,.84),(1.75,-.045,.70)],.023,wood)
strand('Danda | wooden staff',[(-1.59,.18,.29),(-1.51,.20,1.13),(-1.43,.23,2.07),(-1.39,.24,2.99),(-1.43,.24,3.77)],.037,wood,[1.1,1,.85,.85,.9])
for i in range(8):
    z=2.7+i*.028
    strand('Staff | fiber binding',[(-1.39+.044*cos(a),.24+.044*sin(a),z) for a in [2*pi*j/16 for j in range(17)]],.008,hem)
CURRENT='07 Stage'
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=2.02,depth=.23,location=(0,0,.155));o=put(bpy.context.object,'Stone dais',stone)
b=o.modifiers.new('Soft stone edges','BEVEL');b.width=.075;b.segments=4
bpy.ops.mesh.primitive_plane_add(size=200);put(bpy.context.object,'Studio ground',matte)
# Camera and soft studio illumination.
def camera(name,loc,target,lens):
    bpy.ops.object.camera_add(location=loc);o=put(bpy.context.object,name);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=lens;return o
hero=camera('Camera | portrait',(6,-12,6.1),(0,0,2.28),5.5)
front=camera('Camera | front',(0,-12,4.1),(0,0,2.3),5.3)
close=camera('Camera | face',(3,-10,4.7),(0,-.05,3.38),2.15)
for name,loc,energy,size,color in [('Key',(-4,-6,8),1100,5,(1,.79,.59)),('Fill',(5,-3,5),700,4,(.64,.80,1)),('Rim',(2,4,7),1500,3,(1,.86,.63))]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=put(bpy.context.object,name);o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.camera=hero;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.world.color=(.16,.16,.16);scene.render.resolution_x=1100;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
# All character curves become real mesh objects; preserve object-level editability.
for o in list(bpy.data.objects):
    if o.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
# Start in camera view, with materials available.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
scene['Design']='Composite forest rishi; scriptural motifs and artistic age cues, not a portrait of a named sage.'
scene['Status']='Static multi-part sculpt; not rigged, retopologized, or validated for printing.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Wise_Rishi.blend'))
for cam,file,size in [(hero,'rishi-hero.png',(1100,1300)),(close,'rishi-face.png',(1000,1000)),(front,'rishi-front.png',(1000,1200))]:
    scene.camera=cam;scene.render.resolution_x=size[0];scene.render.resolution_y=size[1];scene.render.filepath=os.path.join(ROOT,'renders',file);bpy.ops.render.render(write_still=True)
scene.camera=hero
meshes=[o for o in bpy.data.objects if o.type=='MESH']
report={'blender':bpy.app.version_string,'mesh_objects':len(meshes),'base_vertices':sum(len(o.data.vertices) for o in meshes),'base_faces':sum(len(o.data.polygons) for o in meshes),'finite_coordinates':all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co),'external_images':[i.filepath for i in bpy.data.images if i.source=='FILE'],'rigged':False,'retopologized':False,'watertight_print_verified':False}
with open(os.path.join(ROOT,'model-report.json'),'w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Wise_Rishi.blend'))
print('RISHI_COMPLETE',json.dumps(report))
