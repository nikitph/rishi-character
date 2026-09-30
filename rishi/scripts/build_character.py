import os
BASE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(BASE,'build_rishi.py')).read()
exec(src.split('# Slender seated body')[0])
# Softer sculptural materials, real closed curve caps.
for m in [skin,cloth,hem]:
    for n in m.node_tree.nodes:
        if n.type=='BUMP':n.inputs['Strength'].default_value*=.3
oldstrand=strand
def strand(name,pts,radius,mat,radii=None):
    o=oldstrand(name,pts,radius,mat,radii);o.data.use_fill_caps=True;return o
# Rest pose body. Full limbs exist beneath removable garments.
parts=[uv('Hips',(0,.06,3.05),(.46,.27,.39),skin),uv('Waist',(0,.055,3.56),(.37,.255,.48),skin),uv('Chest',(0,.07,4.08),(.53,.29,.49),skin),uv('Neck',(0,.06,4.78),(.195,.19,.35),skin)]
for side in [-1,1]:
    parts += [uv('Shoulder',(side*.55,.05,4.40),(.205,.215,.23),skin),limb('Upper arm',(side*.58,.05,4.40),(side*.99,.015,3.83),.14,.155,skin),uv('Elbow',(side*.99,.015,3.83),(.125,.13,.14),skin),limb('Forearm',(side*.99,.015,3.83),(side*1.32,-.025,3.22),.115,.125,skin),uv('Palm',(side*1.39,-.045,3.04),(.105,.075,.19),skin),limb('Thigh',(side*.26,.07,3.04),(side*.30,-.015,1.85),.21,.205,skin),uv('Knee',(side*.30,-.015,1.83),(.145,.16,.18),skin),limb('Calf',(side*.30,-.015,1.83),(side*.34,.025,.57),.13,.14,skin),uv('Ankle',(side*.34,.025,.48),(.103,.115,.18),skin),uv('Foot',(side*.34,-.18,.27),(.15,.32,.125),skin)]
body=fuse(parts,'Rishi_Body',.025)
# Reuse and refine the identity sculpt, excluding the seated hands.
section=src[src.index('# A coherent face volume'):src.index('# Fingers rest gently')]
section=section.replace("(.16,.135,.16)","(.135,.12,.135)").replace("(.185,.08,.08)","(.17,.06,.055)")
exec(section)
head.name='Rishi_Head'
# Replace closed eyes and segmented eyebrows with expressive open eye forms.
for o in list(cols['02 Face details'].objects):
    if any(s in o.name for s in ['Closed eyelid','Upper lid','Under-eye','Silver eyebrow']):bpy.data.objects.remove(o,do_unlink=True)
CURRENT='02 Face details'
sclera=material('Eyes | warm ivory',(.72,.63,.48),.28)
iris=material('Eyes | dark amber',(.095,.035,.008),.3)
pupil=material('Eyes | pupil',(.004,.003,.002),.22)
blinkparts=[];browparts=[]
for side in [-1,1]:
    eye=uv('Eye white', (side*.17,-.325,3.405),(.108,.067,.059),sclera,32,20);blinkparts.append((eye,'eye'))
    eye=uv('Iris',(side*.17,-.387,3.405),(.039,.013,.040),iris,32,20);blinkparts.append((eye,'eye'))
    eye=uv('Pupil',(side*.17,-.398,3.405),(.019,.006,.024),pupil,24,16);blinkparts.append((eye,'eye'))
    for upper in [True,False]:
        pts=[]
        for i in range(7):
            t=i/6;xx=side*(.065+.21*t);z=3.405+(.06 if upper else -.05)*sin(pi*t)
            pts.append((xx,-.338-.036*sin(pi*t),z))
        o=strand('Upper eyelid' if upper else 'Lower eyelid',pts,.016,skin,[.35,.8,1,1,1,.8,.35]);blinkparts.append((o,'upper' if upper else 'lower'))
    o=strand('Expressive silver brow',[(side*.066,-.321,3.51),(side*.14,-.345,3.54),(side*.22,-.324,3.535),(side*.30,-.266,3.51)],.023,hair,[.35,1,1,.1]);browparts.append(o)
    for j in range(6):
        x=.08+j*.029
        o=strand('Brow hair',[(side*x,-.348,3.525),(side*(x+.025),-.349,3.552),(side*(x+.047),-.33,3.54)],.004,hairL,[.1,1,.1]);browparts.append(o)
# Existing hair, reworked to more closely follow the scalp and vary in clumps.
section=src[src.index("CURRENT='03 Jata and beard'"):src.index("CURRENT='04 Cloth'")]
section=section.replace("z=3.62+.52*t", "z=3.69+.45*t")
exec(section)
# Replace the initial cylindrical crown with a rounded, interwoven jata bun.
for o in list(cols['03 Jata and beard'].objects):
    if o.name.startswith('Jata'):bpy.data.objects.remove(o,do_unlink=True)
CURRENT='03 Jata and beard'
uv('Jata | rounded bun core',(0,.11,4.04),(.245,.23,.30),hairD)
for i in range(23):
    a=2*pi*i/23
    front=max(0,-cos(a));startz=3.46+.29*front+.025*sin(i*2)
    pts=[(.36*sin(a),.045+.30*cos(a),startz),(.39*sin(a+.10),.045+.33*cos(a+.10),3.79),(.27*sin(a+.22),.085+.24*cos(a+.22),3.98),(.12*sin(a+.45),.11+.11*cos(a+.45),4.12)]
    strand('Jata | swept matted lock',pts,.037,hair if i%4 else hairD,[.30,1,1,.35])
    strand('Jata | silver ridge',[(x-.01,y-.013,z+.012) for x,y,z in pts],.006,hairL,[.1,1,.8,.1])
for i in range(15):
    a=2*pi*i/15;pts=[]
    for k in range(17):
        t=k/16;ang=a+t*2.5;theta=.12+pi*.90*t
        pts.append((.255*sin(theta)*cos(ang),.11+.238*sin(theta)*sin(ang),4.04+.30*cos(theta)))
    strand('Jata | interwoven crown',pts,.034,hair if i%3 else hairD,[.25]+[1]*15+[.25])
# Crease lines sit on the face surface instead of floating above it.
bpy.context.view_layer.update();ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());inv=head.matrix_world.inverted()
for o in cols['02 Face details'].objects:
    if any(n in o.name for n in ['Forehead age','Crow foot','Nasolabial']):
        o.data.bevel_depth*=.65
        for spline in o.data.splines:
            for bp in spline.bezier_points:
                p=bp.co;hit,co,no,idx=ev.ray_cast(inv@Vector((p.x,-2,p.z)),Vector((0,1,0)))
                if hit:bp.co.y=(head.matrix_world@co).y-.002
for c in ['02 Face details','03 Jata and beard']:
    for o in cols[c].objects:o.location.z+=2
head.location.z+=2
# Individual fingers with three articulated segments per finger.
CURRENT='01 Anatomy';fingerpaths={}
for side,suff in [(1,'L'),(-1,'R')]:
    for j,label in enumerate(['index','middle','ring','little']):
        x=side*(1.31+j*.059);z=2.94+abs(j-1)*.022;length=[.26,.29,.27,.22][j]
        pts=[(x,-.045,z),(x+side*.025,-.05,z-length*.37),(x+side*.045,-.065,z-length*.72),(x+side*.055,-.085,z-length)]
        fingerpaths[label+'.'+suff]=pts
        strand('Finger_'+label+'.'+suff,pts,.031 if j<3 else .027,skin,[1,.93,.82,.50])
    pts=[(side*1.30,-.065,3.12),(side*1.22,-.11,3.02),(side*1.19,-.12,2.93),(side*1.21,-.13,2.88)]
    fingerpaths['thumb.'+suff]=pts;strand('Finger_thumb.'+suff,pts,.041,skin,[1,.9,.75,.5])
# Topology structured along the leg: independent dhoti trouser volumes can bend at knees.
CURRENT='04 Cloth'
def ringsmesh(name,rings,n,mat,fold=.012):
    vs=[];fs=[]
    for j,(cx,cy,z,rx,ry) in enumerate(rings):
        for i in range(n):
            a=2*pi*i/n;r=1+fold*cos(12*a+j*.18)
            vs.append((cx+rx*cos(a)*r,cy+ry*sin(a)*r,z))
    for j in range(len(rings)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    o=mesh(name,vs,fs,mat,1);s=o.modifiers.new('Cloth thickness','SOLIDIFY');s.thickness=.012;return o
for side,suff in [(1,'L'),(-1,'R')]:
    rings=[]
    for j in range(33):
        t=j/32;z=3.12-2.40*t
        rad=.26+.04*sin(pi*t)-.115*t+.04*sin(3*pi*t)
        rings.append((side*(.235+.1*t),.055,z,rad,rad*1.1))
    ringsmesh('Dhoti_leg.'+suff,rings,64,cloth,.055)
ringsmesh('Dhoti_waist',[(0,.055,3.22,.43,.29),(0,.055,3.16,.455,.31),(0,.055,3.07,.47,.32),(0,.055,2.99,.48,.32)],96,cloth,.025)
# Waist tie and tucked central pleat, deliberately short for leg movement.
for k in range(3):strand('Waist cord',[(.46*sin(a),.055+.313*cos(a),3.18+k*.027) for a in [2*pi*i/48 for i in range(49)]],.011,hem)
for j in range(5):
    x=(j-2)*.034
    strand('Tucked front pleat',[(x,-.275,3.12),(x,-.30,2.96),(x*.7,-.28,2.73)],.029,cloth,[.8,1,.05])
# Shawl is skinned to the torso, hanging clear of the upper arms.
path=[(-.37,.19,4.64),(-.46,-.02,4.62),(-.40,-.30,4.40),(-.23,-.345,4.16),(-.03,-.33,3.91),(.16,-.30,3.65),(.28,-.30,3.36),(.31,-.34,3.15)]
v=[];f=[];W=16
for j,p in enumerate(path):
    for i in range(W+1):
        u=i/W-.5;v.append((p[0]+u*.34,p[1]-.018*cos(u*8*pi),p[2]+u*.11))
for j in range(len(path)-1):
    for i in range(W):a=j*(W+1)+i;f.append((a,a+1,a+W+2,a+W+1))
shawl=mesh('Angavastra_shawl',v,f,cloth,2);s=shawl.modifiers.new('Woven thickness','SOLIDIFY');s.thickness=.018
for side in [-1,1]:strand('Shawl selvedge',[(p[0]+side*.167,p[1]-.015,p[2]+side*.055) for p in path],.012,hem)
CURRENT='05 Mala'
for i in range(49):
    a=2*pi*i/49;x=.305*sin(a);y=.055-.37*cos(a);z=4.50-.43*max(cos(a),0)
    uv('Mala seed',(x,y-.028,z),(.031,.031,.034),bead,16,12)
# Build armature with stable human-readable bone names.
rigcoll=bpy.data.collections.new('00 CHARACTER RIG');bpy.context.scene.collection.children.link(rigcoll)
bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Rishi_Rig'
for c in list(rig.users_collection):c.objects.unlink(rig)
rigcoll.objects.link(rig);rig.show_in_front=True;rig.data.display_type='STICK'
bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0]);segments={}
def bone(name,a,b,parent=None):
    e=rig.data.edit_bones.new(name);e.head=a;e.tail=b
    if parent:e.parent=rig.data.edit_bones[parent]
    segments[name]=(Vector(a),Vector(b));return e
bone('root',(0,0,.1),(0,0,.5))
bone('pelvis',(0,.06,2.95),(0,.06,3.36),'root')
bone('spine',(0,.06,3.36),(0,.06,3.90),'pelvis')
bone('chest',(0,.06,3.90),(0,.06,4.51),'spine')
bone('neck',(0,.06,4.51),(0,.04,4.98),'chest')
bone('head',(0,.04,4.98),(0,.04,5.92),'neck')
bone('jaw',(0,-.08,5.20),(0,-.30,4.97),'head')
bone('beard.01',(0,-.24,5.04),(0,-.33,4.68),'head')
bone('beard.02',(0,-.33,4.68),(0,-.32,4.23),'beard.01')
for side,suff in [(1,'L'),(-1,'R')]:
    bone('clavicle.'+suff,(side*.05,.06,4.44),(side*.56,.05,4.40),'chest')
    bone('upper_arm.'+suff,(side*.56,.05,4.40),(side*.99,.015,3.83),'clavicle.'+suff)
    bone('forearm.'+suff,(side*.99,.015,3.83),(side*1.32,-.025,3.22),'upper_arm.'+suff)
    bone('hand.'+suff,(side*1.32,-.025,3.22),(side*1.41,-.045,2.94),'forearm.'+suff)
    for label in ['index','middle','ring','little','thumb']:
        pts=fingerpaths[label+'.'+suff]
        for j in range(3):bone(label+'.%02d.'%(j+1)+suff,pts[j],pts[j+1],('hand.'+suff) if j==0 else label+'.%02d.'%j+suff)
    bone('thigh.'+suff,(side*.26,.07,3.04),(side*.30,-.015,1.85),'pelvis')
    bone('shin.'+suff,(side*.30,-.015,1.85),(side*.34,.025,.50),'thigh.'+suff)
    bone('foot.'+suff,(side*.34,.025,.50),(side*.34,-.31,.25),'shin.'+suff)
    bone('toe.'+suff,(side*.34,-.31,.25),(side*.34,-.48,.25),'foot.'+suff)
bpy.ops.object.mode_set(mode='OBJECT')
# Convert hair and detail curves into smooth closed mesh components.
for o in list(bpy.data.objects):
    if o.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
        for p in o.data.polygons:p.use_smooth=True
# Explicit spatial weights, restricted to the intended anatomical chain.
def dist(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-t*d).length

def bind(o,names,rigid=False):
    groups={n:o.vertex_groups.new(name=n) for n in names}
    for v in o.data.vertices:
        p=o.matrix_world@v.co
        if rigid:groups[names[0]].add([v.index],1,'REPLACE');continue
        candidates=names
        if o==body:
            ax=abs(p.x);z=p.z;suff='L' if p.x>=0 else 'R'
            if z<2.85:candidates=['pelvis','thigh.'+suff,'shin.'+suff,'foot.'+suff,'toe.'+suff]
            elif ax>.60:candidates=['upper_arm.'+suff,'forearm.'+suff,'hand.'+suff]
            elif z>4.14 and ax>.39:candidates=['chest','clavicle.'+suff,'upper_arm.'+suff]
            else:candidates=['pelvis','spine','chest','neck']
        ds=sorted((dist(p,*segments[n]),n) for n in candidates)[:2]
        vals=[1/max(d,.045)**4 for d,n in ds];sm=sum(vals)
        for (_,n),w in zip(ds,vals):
            if w/sm>.0001:groups[n].add([v.index],w/sm,'REPLACE')
    mod=o.modifiers.new('Rishi skeletal deformation','ARMATURE');mod.object=rig
    # Deform before subdivision, but after any baked sculpt modifier.
    bpy.context.view_layer.objects.active=o
    while o.modifiers.find(mod.name)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    o.parent=rig

bodybones=['pelvis','spine','chest','neck']+[n+'.'+s for s in ['L','R'] for n in ['clavicle','upper_arm','forearm','hand','thigh','shin','foot','toe']]
for o in list(cols['01 Anatomy'].objects):
    if o==head:bind(o,['head'],True)
    elif o==body:
        for b in rig.data.bones:b.use_deform=b.name in bodybones
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        for b in rig.data.bones:b.use_deform=True
        bpy.context.view_layer.objects.active=o
        mod=next(m for m in o.modifiers if m.type=='ARMATURE')
        while o.modifiers.find(mod.name)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    elif o.name.startswith('Finger_'):
        label,suff=o.name[7:].split('.');bind(o,[label+'.%02d.'%j+suff for j in [1,2,3]])
for o in cols['02 Face details'].objects:bind(o,['head'],True)
for o in cols['03 Jata and beard'].objects:
    bind(o,['head','beard.01','beard.02'] if o.name.startswith('Beard') else ['head'],not o.name.startswith('Beard'))
for o in cols['04 Cloth'].objects:
    if o.name.startswith('Dhoti_leg'):
        suff=o.name[-1];bind(o,['pelvis','thigh.'+suff,'shin.'+suff])
    elif o.name.startswith(('Dhoti_waist','Waist','Tucked')):bind(o,['pelvis'],True)
    else:bind(o,['pelvis','spine','chest'])
for o in cols['05 Mala'].objects:bind(o,['chest'],True)
# Driver-backed expression controls. Values live on Rishi_Rig, usable across shots.
for prop in ['blink','brow_raise','smile','jaw_open']:
    rig[prop]=0.0;rig.id_properties_ui(prop).update(min=0.,max=1.,description='Rishi facial control: '+prop)
def drive(key,prop):
    f=key.driver_add('value');d=f.driver;d.type='AVERAGE';v=d.variables.new();v.name='expression';v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path='["'+prop+'"]'
for o,kind in blinkparts:
    o.shape_key_add(name='Basis');key=o.shape_key_add(name='Blink')
    for v in key.data:
        if kind=='eye':v.co.z*=.06
        else:v.co.z=3.405+(v.co.z-3.405)*.08
    drive(key,'blink')
exec(open(os.path.join(BASE,'eyelids.py')).read())
add_eyelid_surfaces(rig)
for o in browparts:
    o.shape_key_add(name='Basis');key=o.shape_key_add(name='Brow_Raise')
    for v in key.data:v.co.z+=.075
    drive(key,'brow_raise')
# Mouth shape keys on the head and lips: broad expressions, not a phoneme rig.
for o in [head]+[o for o in cols['02 Face details'].objects if 'mouth' in o.name or 'lip' in o.name]:
    o.shape_key_add(name='Basis');key=o.shape_key_add(name='Smile')
    for i,v in enumerate(key.data):
        p=o.matrix_world@o.data.vertices[i].co
        influence=max(0,1-abs(p.z-5.06)/.15)*max(0,1-abs(p.x)/.24)*max(0,min(1,(-p.y-.18)/.13))
        v.co.z+=.05*influence*min(1,abs(p.x)/.10)
    drive(key,'smile')
    key=o.shape_key_add(name='Jaw_Open')
    for i,v in enumerate(key.data):
        p=o.matrix_world@o.data.vertices[i].co
        influence=max(0,min(1,(5.10-p.z)/.15))*max(0,1-abs(p.x)/.4)
        v.co.z-=.105*influence;v.co.y-=.025*influence
    drive(key,'jaw_open')
# Props are independent, linked into the library but never welded to the body.
exec(src[src.index("CURRENT='06 Hermitage objects'"):src.index("CURRENT='07 Stage'")])
# Hide props in character showcase; usable separately in future scenes.
cols['06 Hermitage objects'].hide_render=True
for o in cols['06 Hermitage objects'].objects:o.hide_set(True)
# Master identity metadata.
rig['character_id']='RISHI_001';rig['asset_version']='0.1.0';rig['rig_notes']='FK rig; facial sliders in custom properties; beard secondary controls; neutral A-pose. Prototype weights require shot-specific review.'
# Use meters: convert complete rig and bound meshes to approximately 1.86 m crown height.
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
rig.scale=(.3,.3,.3)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# Children inherit scale compensation from applying the armature scale; bake each mesh transform.
for o in list(rig.children):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
rig.location.z=-.0435
# Stage, camera, static inspection poses. No baked animation clips are implied.
CURRENT='07 Stage'
bpy.ops.mesh.primitive_plane_add(size=200);put(bpy.context.object,'Studio ground',matte)
def camera(name,loc,target,scale):
    bpy.ops.object.camera_add(location=loc);o=put(bpy.context.object,name);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;return o
hero=camera('Camera | character',(3,-7,3),(0,0,1.0),2.25)
front=camera('Camera | front',(0,-7,1.6),(0,0,1),2.25)
facecam=camera('Camera | expressions',(1,-6,2.2),(0,-.02,1.64),.7)
for name,loc,energy,size,color in [('Key',(-3,-4,6),500,4,(1,.83,.68)),('Fill',(4,-3,4),350,3,(.70,.83,1)),('Rim',(1,3,5),650,2,(1,.87,.67))]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=put(bpy.context.object,name);o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.camera=hero;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.world.color=(.11,.11,.11)
scene.render.resolution_x=1050;scene.render.resolution_y=1400;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.unit_settings.system='METRIC'
# Asset marked collection, suitable for Link / Library Override and Asset Browser.
asset=bpy.data.collections.new('RISHI_001_CHARACTER');scene.collection.children.link(asset)
for name in ['00 CHARACTER RIG','01 Anatomy','02 Face details','03 Jata and beard','04 Cloth','05 Mala']:
    c=bpy.data.collections[name];scene.collection.children.unlink(c);asset.children.link(c)
asset.asset_mark();asset.asset_data.description='Rishi 001: stylized sage, FK body and fingers, expression sliders and beard controls. v0.1 prototype.'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
def reset():
    for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
    for p in ['blink','brow_raise','smile','jaw_open']:rig[p]=0.
    bpy.context.view_layer.update()
pose_records={}
def render(name,cam=hero):
    rig.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
    pose_records[name]={'bones':{p.name:list(p.rotation_euler) for p in rig.pose.bones},'expressions':{k:float(rig[k]) for k in ['blink','brow_raise','smile','jaw_open']}}
    scene.camera=cam;scene.render.filepath=os.path.join(ROOT,'renders',name+'.png');bpy.ops.render.render(write_still=True)
reset();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Rishi_Character_Master.blend'))
# Reload to rebuild fresh-scene driver dependencies before testing expressions.
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'Rishi_Character_Master.blend'))
rig=bpy.data.objects['Rishi_Rig'];scene=bpy.context.scene
hero=bpy.data.objects['Camera | character'];front=bpy.data.objects['Camera | front'];facecam=bpy.data.objects['Camera | expressions']
render('character-neutral')
render('character-face',facecam)
# Teaching gesture exercises clavicle, upper arm, elbow, fingers, head and beard.
rig.pose.bones['upper_arm.L'].rotation_euler[1]=-.35
rig.pose.bones['forearm.L'].rotation_euler[0]=1.15
rig.pose.bones['hand.L'].rotation_euler[1]=.25
rig.pose.bones['head'].rotation_euler[1]=-.13
rig.pose.bones['beard.01'].rotation_euler[0]=.07
for digit in ['middle','ring','little']:
    for j in [1,2,3]:rig.pose.bones[digit+'.%02d.L'%j].rotation_euler[0]=.30
rig['brow_raise']=.35;rig['smile']=.45;bpy.context.view_layer.update();render('character-teaching')
reset();rig['blink']=1.;rig['brow_raise']=.15;bpy.context.view_layer.update();render('character-blink',facecam)
# Flex a leg to inspect skin and dhoti deformation.
reset();rig.pose.bones['thigh.L'].rotation_euler[0]=-.55;rig.pose.bones['shin.L'].rotation_euler[0]=1.0;bpy.context.view_layer.update();render('character-knee-test',front)
reset();scene.camera=hero
with open(os.path.join(ROOT,'poses.json'),'w') as f:json.dump(pose_records,f,indent=2)
# Normalize all deform weights explicitly for predictable interchange.
for o in rig.children:
    if o.type!='MESH':continue
    for v in o.data.vertices:
        ws=[(g.group,g.weight) for g in v.groups if o.vertex_groups[g.group].name in rig.data.bones];total=sum(w for _,w in ws)
        if total and abs(total-1)>1e-6:
            for idx,w in ws:o.vertex_groups[idx].add([v.index],w/total,'REPLACE')
# Portable rest-pose copy. Blender remains the authoritative rig; drivers do not transfer.
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in rig.children:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'Rishi_Character.glb'),use_selection=True,export_format='GLB',export_animations=False,export_skins=True,export_morph=True,export_extras=True,export_all_influences=True)
# Validation against the evaluated rigged asset.
meshes=[o for o in rig.children if o.type=='MESH']
missing=[];unnormalized=0
for o in meshes:
    for v in o.data.vertices:
        weights=[g.weight for g in v.groups if o.vertex_groups[g.group].name in rig.data.bones]
        if not weights:missing.append(o.name);break
        if abs(sum(weights)-1)>.001:unnormalized+=1
report={'blender':bpy.app.version_string,'character_id':'RISHI_001','version':'0.1.0','mesh_objects':len(meshes),'bones':len(rig.data.bones),'vertices':sum(len(o.data.vertices) for o in meshes),'faces':sum(len(o.data.polygons) for o in meshes),'unweighted_objects':missing,'unnormalized_vertices':unnormalized,'finite_coordinates':all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co),'shape_key_meshes':sum(bool(o.data.shape_keys) for o in meshes),'expressions':['blink','brow_raise','smile','jaw_open'],'rendered_checks':['neutral','face','teaching','blink','knee flexion'],'production_status':'Prototype FK character. Requires animation retopology, extended deformation polish and dialogue rig for demanding film work.','glb_scope':'Rest pose, skinning and morph targets; Blender expression drivers and procedural bump materials are not portable.'}
with open(os.path.join(ROOT,'character-report.json'),'w') as f:json.dump(report,f,indent=2)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Rishi_Character_Master.blend'))
print('CHARACTER_COMPLETE',json.dumps(report))
