import bpy, math

def add_eyelid_surfaces(rig, scale=1.0):
    skin=bpy.data.materials['Warm umber | aged skin'];collection=bpy.data.collections['02 Face details']
    for side in [-1,1]:
        for upper in [True,False]:
            verts=[];closed=[];faces=[];N=32;M=8
            for j in range(M+1):
                row=j/M
                for i in range(N+1):
                    t=-1+2*i/N;envelope=math.sqrt(max(0,1-t*t));x=side*.17+.108*t
                    edge=(.060 if upper else -.052)*envelope
                    # Retracted lid is a very thin strip along the open-eye edge.
                    dz_open=edge*(1-.015*row)
                    dz_closed=edge*(1-row)
                    y_open=-.33-.046*envelope
                    y_closed=-.325-.080*math.sqrt(max(0,1-t*t-(dz_closed/.067)**2))
                    verts.append((x*scale,y_open*scale,(5.405+dz_open)*scale))
                    closed.append((x*scale,y_closed*scale,(5.405+dz_closed)*scale))
            for j in range(M):
                for i in range(N):
                    a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
            name=('Upper' if upper else 'Lower')+'_LidSurface.'+('L' if side>0 else 'R')
            me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
            o=bpy.data.objects.new(name,me);collection.objects.link(o);me.materials.append(skin)
            for p in me.polygons:p.use_smooth=True
            o.parent=rig;g=o.vertex_groups.new(name='head');g.add(list(range(len(verts))),1.,'REPLACE')
            mod=o.modifiers.new('Rishi skeletal deformation','ARMATURE');mod.object=rig
            o.shape_key_add(name='Basis');k=o.shape_key_add(name='Blink')
            for v,p in zip(k.data,closed):v.co=p
            d=k.driver_add('value').driver;d.type='AVERAGE';v=d.variables.new();v.name='expression';v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path='["blink"]'
    # Move rim centerlines toward the seam without flattening bevel thickness.
    for o in collection.objects:
        if not o.name.startswith(('Upper eyelid','Lower eyelid')):continue
        basis=o.data.shape_keys.key_blocks['Basis'];key=o.data.shape_keys.key_blocks['Blink'];upper=o.name.startswith('Upper')
        for b,k in zip(basis.data,key.data):
            t=max(0,min(1,(abs(b.co.x/scale)-.065)/.21));arch=math.sin(math.pi*t)
            k.co=b.co;k.co.z-=(.06 if upper else -.05)*arch*scale;k.co.y-=.024*arch*scale
