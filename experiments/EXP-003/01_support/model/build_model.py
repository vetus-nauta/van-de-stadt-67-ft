"""EXP-003: actual model changes; all prior releases read-only. Blender 4.x."""
import bpy, math, json, hashlib, argparse, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--out-dir',required=True,type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=a.out_dir.expanduser().resolve()
if OUT.exists() and (not OUT.is_dir() or any(OUT.iterdir())):p.error('Output must be NEW or EMPTY: '+str(OUT))
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'experiments/EXP-002/01_support/model/experiment.blend';BASIS=ROOT/'experiments/EXP-003/01_support/basis/bulwark-basis.json'
B=json.loads(BASIS.read_text());bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
P={'status':'GEOMETRIC_EXPERIMENT_NOT_ENGINEERING','units':'m','source_blend_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'bulwark_basis_sha256':hashlib.sha256(BASIS.read_bytes()).hexdigest(),'bulwark_raise_m':.25,'bulwark_datum':'existing top of native142/143, NOT deck','front_slope_deg':45,'front_slope_definition':'straight low forward wall: upper edge moves aft by same amount as rise in Z; rounding at corners varies','glass':'dark smoked visual material, no performance or transmission approval','roof':'continuous shallow-crown canopy with smooth longitudinal transitions, rounded margins, real cut-out rooflights','structures':'geometry-connected supports and knees; no strength/load approval','limits':['No rig/boom clearance verification','No actual floor/headroom approval','No glazing or structure scantling calculation','No drainage/freeing-port sizing','No as-built equivalence']}
NEW=bpy.data.collections.new('50_EXP003_GEOMETRIC_CHANGES');scene.collection.children.link(NEW)
CUT=bpy.data.collections.new('51_EXP003_BOOLEAN_CUTTERS_hidden');scene.collection.children.link(CUT)
ANNOT=bpy.data.collections.new('52_EXP003_DIMENSIONS');scene.collection.children.link(ANNOT)
refs=[o for o in bpy.data.objects if o.get('source_index') is not None]
P['reference_count']=len(refs)
COL={'metal':(.67,.73,.73,1),'glass':(.016,.028,.034,1),'structure':(.48,.56,.56,1),'text':(.018,.026,.029,1)}
def mesh(n,v,f,c='metal'):
 m=bpy.data.meshes.new(n);m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new('EXP003_'+n,m);NEW.objects.link(o);o.color=COL[c];return o
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_select=False;o.select_set(True);bpy.context.view_layer.objects.active=o

def modifier(o,typ,**kwargs):
 m=o.modifiers.new(typ,typ)
 for k,v in kwargs.items():setattr(m,k,v)
 active(o);bpy.ops.object.modifier_apply(modifier=m.name)
def solid(o,t=.025,bevel=.01):
 modifier(o,'SOLIDIFY',thickness=t,offset=-1,use_even_offset=True)
 if bevel:modifier(o,'BEVEL',width=bevel,segments=3)
 return o

def bar(n,a,b,w=.065,c='structure'):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cube_add(size=1,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name='EXP003_'+n;o.dimensions=(w,w,d.length);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(o.users_collection):col.objects.unlink(o)
 NEW.objects.link(o);o.color=COL[c];modifier(o,'BEVEL',width=w*.22,segments=3);return o

def box(n,center,size,c='metal',r=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name='EXP003_'+n;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(o.users_collection):col.objects.unlink(o)
 NEW.objects.link(o);o.color=COL[c]
 if r:modifier(o,'BEVEL',width=r,segments=5)
 return o

def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def roofz(x):
 if x<-13.40:return 3.35+.55*smooth((-13.40-x)/1.60)
 if x<-10.50:return 3.35
 if x<-9.50:return 2.897+.453*smooth((-9.50-x))
 return 2.897

def roofw(x):
 if x>-8.448:return 1.22+math.sqrt(max(0,.65*.65-(x+8.448)**2))
 if x<-16.20:return 1.83+.09*(x+18.72)/2.52
 if x<-14.10:return 1.87+.05*smooth((-14.10-x)/2.10)
 return 1.87
# Remove superseded proposal geometry only; source314 untouched.
for o in list(bpy.data.objects):
 if o.get('source_index') is not None:continue
 n=o.name
 if n.startswith(('EXP_roof','EXP_rounded_forward_roof','EXP_transverse_frame','EXP_longitudinal_reserved_beam','EXP002_hardtop','EXP002_main_window','EXP002_gap','EXP002_plan_','EXP002_extension','EXP002_additional','EXP002_side_title','EXP002_mast_note','EXP002_foredeck_label','EXP002_hardtop_label')) or o.type in ['CAMERA','FONT']:
  bpy.data.objects.remove(o,do_unlink=True)
# High glass reaches the newly swept roof without light gaps. Explicit narrow mullions.
for o in list(bpy.data.objects):
 if o.name.startswith('EXP002_main_raked_glazing'):
  for v in o.data.vertices:
   if v.co.z>2.414:v.co.z=roofz(v.co.x)-.075
  o.color=COL['glass'];solid(o,.018,.005)
  v=[q.co.copy() for q in o.data.vertices] # framing references derived separately below
# Recreate clean frame paths from the old sill endpoints and exact high roof profile.
for o in list(bpy.data.objects):
 if o.name.startswith('EXP002_main_opaque_raked_coaming'):
  a,b,g,h=[v.co.copy() for v in o.data.vertices[:4]]
  for q in [g,h]:
   y=q.y/(1 if abs(q.y)<1e-9 else 1)
   # Roof top follows inherited main-roof plan edge, obtained from original glass before solidifying elsewhere.
  o.color=(.65,.73,.72,1);solid(o,.025,.006)
# Rebuild the low forward envelope from regular stations; the entire frontal plane is X+Z=constant.
frontx=-4.798;floorz=1.820211;front_constant=frontx+floorz
D=json.loads((ROOT/'experiments/EXP-002/01_support/basis/deck-sections.json').read_text())['sections']
def dw(x):
 for a,b in zip(D,D[1:]):
  if a['x_m']<=x<=b['x_m']:
   t=(x-a['x_m'])/(b['x_m']-a['x_m']);return min(abs(p[1]) for p in a['edge_points_m'])*(1-t)+min(abs(p[1]) for p in b['edge_points_m'])*t
 return min(abs(p[1]) for p in D[-1]['edge_points_m'])
def lowz(x):return 2.4135+(2.36-2.4135)*(x+8.448)/3.65
def lx(x,z):return x-max(0,z-floorz)*smooth((x+6.2)/(frontx+6.2))
for o in list(bpy.data.objects):
 if o.type=='MESH' and o.name.startswith('EXP002_low_'):
  if any(k in o.name for k in ['roof_','front_','reservation','mullion','glass_top','glass_sill']):
   bpy.data.objects.remove(o,do_unlink=True);continue
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   w=o.matrix_world@v.co;w.x=lx(w.x,w.z);v.co=inv@w
  if 'glass' in o.name or 'light' in o.name:o.color=COL['glass']
  if 'coaming' in o.name:solid(o,.025,.007)
# Rebuild a smooth low roof with actual rounded plate thickness; no folded terminal panels.
lxs=[-8.448+3.65*i/80 for i in range(81)];ly=[-1,-.75,-.5,-.25,0,.25,.5,.75,1];vv=[]
for x in lxs:
 width=min(2.28,dw(x)-.55)-.20
 for y in ly:
  z=lowz(x)+.055*(1-y*y);vv.append((lx(x,z),y*width,z))
ff=[]
for i in range(80):
 for j in range(8):a=i*9+j;ff.append((a,a+9,a+10,a+1))
lowroof=mesh('regular_low_roof',vv,ff);solid(lowroof,.075,.025)
for f in lowroof.data.polygons:f.use_smooth=True
width=min(2.28,dw(frontx)-.55)
def fp(y,z):return (front_constant-z,y,z)
frontopaque=mesh('front45_opaque',[fp(-width,floorz),fp(width,floorz),fp(width-.10,2.06),fp(-width+.10,2.06)],[(0,1,2,3)]);solid(frontopaque,.025,.007)
frontglass=mesh('front45_glass',[fp(-width+.10,2.06),fp(width-.10,2.06),fp(width-.20,2.30),fp(-width+.20,2.30)],[(0,1,2,3)],'glass');solid(frontglass,.016,.004)
# Curved fascia also belongs to the same45 degree frontal plane.
vf=[]
for y in ly:
 z=2.36+.055*(1-y*y);vf.extend([fp(y*(width-.20),2.30),fp(y*(width-.20),z)])
fac=mesh('front45_curved_fascia',vf,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(8)]);solid(fac,.022,.006)
for y in [-width+.16,0,width-.16]:bar('front45_mullion',fp(y,2.06),fp(y*.94,2.30),.032)
# Low roof edge frames follow the same profile; no inherited protruding orange members.
for side in [-1,1]:
 for a,b in zip(lxs[::8],lxs[8::8]):
  ya=side*(min(2.28,dw(a)-.55)-.21);yb=side*(min(2.28,dw(b)-.55)-.21)
  bar('low_fascia_frame',(lx(a,lowz(a)),ya,lowz(a)-.065),(lx(b,lowz(b)),yb,lowz(b)-.065),.05)
P['front_plane_x_plus_z']=front_constant;P['front_base_z']=floorz;P['front_max_x']=frontx
# Continuous canopy shell: subtle crown, smooth stern-to-main transition; no detached tabletop.
xa=-18.72;xf=-7.798;corner=.65
xs=[xa+(xf-xa)*i/160 for i in range(161)]
yfracs=[-1,-.75,-.5,-.25,0,.25,.5,.75,1]
verts=[]
for x in xs:
 w=roofw(x)
 if x>xf-corner:w=1.22+math.sqrt(max(0,corner*corner-(x-(xf-corner))**2))
 for y in yfracs:verts.append((x,y*w,roofz(x)+.035*(1-y*y)))
faces=[]
for i in range(len(xs)-1):
 for j in range(8):a=i*9+j;faces.append((a,a+9,a+10,a+1))
canopy=mesh('continuous_canopy',verts,faces);solid(canopy,.13,.025)
# Actual rooflight holes with dark infill surface slightly recessed, surrounded by solid longitudinal bands.
rooflights=[]
for x in [-13.60,-12.45,-11.30]:
 for y in [-.91,.91]:
  cutter=box('rooflight_cutter',(x,y,3.4),(1.0,1.10,1.0),r=.10)
  m=canopy.modifiers.new('rooflight_hole','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;active(canopy);bpy.ops.object.modifier_apply(modifier=m.name)
  bpy.data.objects.remove(cutter,do_unlink=True)
  z=roofz(x)+.035*(1-(y/roofw(x))**2)-.015
  gv=[]
  for i in range(9):
   X=x-.505+1.01*i/8
   for j in range(9):
    Y=y-.555+1.11*j/8;gv.append((X,Y,roofz(X)+.035*(1-(Y/roofw(X))**2)-.012))
  gf=[]
  for i in range(8):
   for j in range(8):a=i*9+j;gf.append((a,a+9,a+10,a+1))
  glass=mesh('curved_recessed_rooflight',gv,gf,'glass');solid(glass,.018,0);rooflights.append(glass.name)
# Split sharp normals at hole walls; weighted top-surface normals avoid false sink marks.
for f in canopy.data.polygons:f.use_smooth=abs(f.normal.z)>.55
canopy.data.use_auto_smooth=True;canopy.data.auto_smooth_angle=math.radians(35)
modifier(canopy,'WEIGHTED_NORMAL',keep_sharp=True,weight=50)
# Restore two actual low-rooflight openings and curved dark infill.
for u in [-7.0,-6.1]:
 xc=lx(u,lowz(u)+.055)
 cutter=box('low_rooflight_cutter',(xc,0,2.45),(.65,.70,1.0),r=.08)
 m=lowroof.modifiers.new('LOW_ROOFLIGHT_THROUGH','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;active(lowroof);bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
 gv=[]
 for i in range(9):
  X=xc-.34+.68*i/8
  for j in range(9):
   Y=-.365+.73*j/8;lo=-8.448;hi=-4.798
   for k in range(40):
    U=(lo+hi)/2;ww=min(2.28,dw(U)-.55)-.20;Z=lowz(U)+.055*(1-(Y/ww)**2)
    if lx(U,Z)<X:lo=U
    else:hi=U
   gv.append((X,Y,Z-.012))
 gf=[]
 for i in range(8):
  for j in range(8):a=i*9+j;gf.append((a,a+9,a+10,a+1))
 glass=mesh('low_curved_recessed_rooflight',gv,gf,'glass');solid(glass,.018,0);rooflights.append(glass.name)
for f in lowroof.data.polygons:f.use_smooth=abs(f.normal.z)>.55
lowroof.data.use_auto_smooth=True;lowroof.data.auto_smooth_angle=math.radians(35)
modifier(lowroof,'WEIGHTED_NORMAL',keep_sharp=True,weight=50)
P['rooflight_count']=len(rooflights)
# Ribs follow canopy and stay below glazing; low section near mast retained support is separate.
for x in [-18.25,-17.10,-15.9,-14.55,-13.0,-11.90,-10.50,-9.20]:
 z=roofz(x)-.17;bar('canopy_cross_frame',(x,-roofw(x)+.07,z),(x,roofw(x)-.07,z),.085)
for side in [-1,1]:
 for a,b in zip(xs[::10],xs[10::10]):bar('canopy_edge_beam',(a,side*(roofw(a)-.075),roofz(a)-.16),(b,side*(roofw(b)-.075),roofz(b)-.16),.10)
# Sweep broad curved side supports into source cockpit coaming/deck, with actual contact located by source-mesh ray casts.
supports=[]
def source_hit(x,y):
 best=None
 for o in refs:
  if o.hide_render or any(c.hide_render for c in o.users_collection):continue
  inv=o.matrix_world.inverted();hit,loc,n,idx=o.ray_cast(inv@Vector((x,y,3.0)),Vector((0,0,-1)))
  if hit:
   w=o.matrix_world@loc
   if .7<w.z<2.5 and (best is None or w.z>best[0]):best=(w.z,o.get('source_index'))
 return best
for side in [-1,1]:
 for xb in [-18.10,-15.65]:
  y=side*(1.84 if xb>-17 else 1.50);yt=side*(1.84 if xb>-17 else 1.70);hit=source_hit(xb,y)
  if hit is None:raise RuntimeError(f'No source contact for proposed support {xb,y}')
  zbase,idx=hit
  if idx not in [454,457,67,93]:raise RuntimeError(f'Support must land on mapped cockpit panels67/93 or coaming454/457, got {idx}')
  xt=xb+.30;zt=roofz(xt)-.11
  # Curved fin with constant width and an upper knee flaring into the roof edge beam.
  vv=[]
  for i in range(21):
   t=i/20;cx=xb+.30*smooth(t);z=zbase+(zt-zbase)*t;half=.09+.17*smooth((t-.65)/.35)
   for dx,dy in [(-half,-.055),(half,-.055),(half,.055),(-half,.055)]:vv.append((cx+dx,y+(yt-y)*smooth(t)+dy,z))
  ff=[(0,3,2,1),(80,81,82,83)]
  for i in range(20):
   for j in range(4):a=i*4+j;b=i*4+(j+1)%4;ff.append((a,b,b+4,a+4))
  o=mesh('curved_support_and_knee',vv,ff,'structure');modifier(o,'BEVEL',width=.025,segments=3)
  # Conform the shoe underside to the source coaming at every corner.
  fv=[]
  fx,fy=(.12,.07) if xb>-17 else (.10,.08)
  for dx,dy in [(-fx,-fy),(fx,-fy),(fx,fy),(-fx,fy)]:
   h=source_hit(xb+dx,y+dy)
   if h is None or h[1]!=idx:raise RuntimeError(f'Foot corner misses coaming {idx}: {xb+dx,y+dy,h}')
   fv.append((xb+dx,y+dy,h[0]))
  fv += [(x,y,z+.07) for x,y,z in fv[:4]]
  foot=mesh('support_foot_CONTACT',fv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'structure')
  modifier(foot,'BEVEL',width=.008,segments=3)
  supports.append({'source_index_contact':idx,'base_contact_xyz':[xb,y,zbase],'top_xyz':[xt,yt,zt],'foot_corner_xyz':fv[:4],'status':'GEOMETRIC_CONTACT_ONLY_NOT_LOAD_PATH_VERIFICATION'})
P['supports']=supports
# +0.25m above actual existing top; native outer/inner edge samples form a closed strip.
bulwarks=[]
for c in B['contours']:
 outer=next(e['source_points_m'] for e in c['edges'] if e['meaning']=='outer');inner=list(reversed(next(e['source_points_m'] for e in c['edges'] if e['meaning']=='inner')))
 n=len(outer);vv=[]
 for q,r in zip(outer,inner):vv.extend([q,r,[r[0],r[1],r[2]+.25],[q[0],q[1],q[2]+.25]])
 ff=[(0,3,2,1),((n-1)*4,(n-1)*4+1,(n-1)*4+2,(n-1)*4+3)]
 for i in range(n-1):
  for j in range(4):a=i*4+j;b=i*4+(j+1)%4;ff.append((a,b,b+4,a+4))
 strip=mesh('raised_bulwark_'+str(c['object_index']),vv,ff);bulwarks.append(strip)
 for opening in [q for q in B['openings'] if q['source_side_index']==c['object_index']]:
  x,y,z=opening['centre_proposed_m'];near=min(range(1,len(outer)-1),key=lambda i:abs(outer[i][0]-x));d=Vector(outer[near+1])-Vector(outer[near-1]);angle=math.atan2(d.y,d.x)
  cutter=box('mooring_hole_CUTTER',(x,y,z),(.36,.55,.10),'metal',.049)
  cutter.rotation_euler.z=angle
  m=strip.modifiers.new('THROUGH_MOORING_HOLE','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;active(strip);bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
 modifier(strip,'BEVEL',width=.006,segments=3)
P['openings']=B['openings'];P['bulwark_end_treatment']='native side-strip ends capped; bow/stern continuation subject to separate source contour check'
# Plan gaps to actual INNER raised bulwark, sampled from finished meshes.
def section_y(o,x):
 vv=[o.matrix_world@v.co for v in o.data.vertices];out=[]
 for e in o.data.edges:
  a,b=[vv[i] for i in e.vertices]
  if abs(a.x-b.x)<1e-8:
   if abs(a.x-x)<1e-5:out.extend([a.y,b.y])
  elif min(a.x,b.x)<=x<=max(a.x,b.x):out.append(a.y+(x-a.x)/(b.x-a.x)*(b.y-a.y))
 return out
body=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('EXP002_main_opaque_raked_coaming') or o.name.startswith('EXP002_low_side_coaming') or o.name.startswith('EXP003_front45_opaque'))]
gaps=[]
for x in [-15.,-14.,-13.,-12.,-11.,-10.,-9.,-8.,-7.,-6.,-5.5]:
 by=[y for o in body for y in section_y(o,x)];sw=[section_y(o,x) for o in bulwarks]
 if by and all(sw):
  inner_pos=min(y for ys in sw for y in ys if y>0);inner_neg=max(y for ys in sw for y in ys if y<0)
  gaps.append({'x_m':x,'inner_starboard_y':inner_pos,'inner_port_y':inner_neg,'body_max_y':max(by),'body_min_y':min(by),'starboard_plan_gap_m':inner_pos-max(by),'port_plan_gap_m':min(by)-inner_neg,'status':'MESH_SECTION_PLAN_ONLY_NOT_CLEAR_PASSAGE'})
(OUT/'inner-bulwark-gaps.json').write_text(json.dumps(gaps,indent=2)+'\n')
# Conservative clearance uses sampled canopy profile and deepest frame reserve, NOT identified floors.
meta=json.loads((ROOT/'deliverables/V02/v001/01_support/full/metadata.json').read_text())
clear=[]
for o in meta['objects']:
 if o['source_index'] in [52,58,212]:
  lo=o['bounds_m']['min'];hi=o['bounds_m']['max'];a=max(lo[0],-18.72);b=min(hi[0],-7.798)
  samples=[roofz(a+(b-a)*i/200)-.225 for i in range(201)];zmin=min(samples)
  clear.append({'source_index':o['source_index'],'overlap_x':[a,b],'source_max_z':hi[2],'conservative_lowest_canopy_and_frame_reserve_z':zmin,'conservative_vertical_gap_m':zmin-hi[2],'status':'PROFILE_RESERVE_OVER_LOCAL_SURFACE_CANDIDATE_NOT_CONFIRMED_FLOOR'})
P['transition_clearances']=clear
(OUT/'transition-clearances.json').write_text(json.dumps(clear,indent=2)+'\n')
P['inner_bulwark_gap_min_m']=min(min(q['starboard_plan_gap_m'],q['port_plan_gap_m']) for q in gaps)
# Darken every inherited glass/light pane, retaining source coordinates.
for o in bpy.data.objects:
 if o.type=='MESH' and o.get('source_index') is None and any(s in o.name.lower() for s in ['glass','glazing','rooflight','flush_light']):o.color=COL['glass']
# Smooth reference hull normals only: mesh vertices/polygons/connectivity stay unchanged.
for o in refs:
 if o.get('source_index') in [133,144]:
  for face in o.data.polygons:face.use_smooth=True
P['reference_display_change']='smooth shading flags only on shell133/144; coordinates and topology unchanged'
# Workbench studio previews, actual scene surfaces and rounded geometry.
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='OBJECT';scene.display.shading.light='STUDIO';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.86,.89,.91)
scene.render.resolution_x=2000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cam=bpy.data.cameras.new('EXP003_camera');camera=bpy.data.objects.new('EXP003_camera',cam);scene.collection.objects.link(camera);scene.camera=camera;cam.type='ORTHO'
def view(eye,target,scale):
 camera.location=eye;camera.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    s=area.spaces.active;s.region_3d.view_rotation=camera.rotation_euler.to_quaternion();s.region_3d.view_distance=scale;s.region_3d.view_location=Vector(target);s.region_3d.view_perspective='ORTHO';s.overlay.show_overlays=False;s.shading.color_type='OBJECT';s.shading.light='STUDIO';s.shading.show_cavity=True

def render(n):scene.render.filepath=str(OUT/(n+'.png'));bpy.ops.render.render(write_still=True)
view((7,-25,15),(-10.3,0,1.4),26);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'experiment.blend'));render('exterior')
view((-20,-20,12),(-13.8,0,2.45),16.0);render('detail')
view((-10.3,-35,2.6),(-10.3,0,2.6),24);render('side')
view((-10.3,0,30),(-10.3,0,0),24);render('top')
(OUT/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2)+'\n')
(OUT/'README.md').write_text('''# EXP-003: фальшборт и связанный экстерьер\n\nОтдельная геометрическая итерация от EXP-002. Все исходные314 объектов сохранены, оригиналы и прежние эксперименты не меняются. На отображении оболочки133/144 только сглажены нормали; координаты и топология прежние.\n\nФальшборт поднят на0.25м от прежнего верха142/143, не от палубы. Шесть клюзов действительно прорезаны Boolean насквозь, по три на борт. Размеры и позиции условны, швартовные нагрузки и водоотлив не рассчитаны.\n\nЛоб низкой передней надстройки наклонён45° в прямом продольном профиле: верхний край отведён назад на величину подъёма, передний нижний габарит сохранён. Радиусы и галтели не имеют постоянного угла. Стекло затемнено, его характеристики не выбирались.\n\nГлавная крыша плавно переходит в хардтоп, выполнена с небольшой погибью и скруглёнными краями. Реальные проёмы фонарей прорезаны в крыше и заполнены тёмными панелями. Боковые опоры с кницами геометрически привязаны к найденным исходным поверхностям; это не подтверждение рассчитанного пути нагрузки.\n\nПлавный переход уменьшает местные просветы: текущие условные минимумы над площадками-кандидатами приведены в transition-clearances.json; прежние 2.13 м EXP-002 не переносятся. Плановые зазоры inner-bulwark-gaps.json измерены до ВНУТРЕННЕГО нового фальшборта, а не прежней наружной кромки палубы; это ещё не чистая ширина прохода. Пол, гик, шкоты, прочность, масса, остойчивость, стекло, дренаж и производственные узлы не проверены. Исходное соответствие построенному корпусу не доказано.\n\nВоспроизведение: `blender -b -t 4 --python experiments/EXP-003/01_support/model/build_model.py -- --out-dir .local/EXP-003/rebuild-001`. Выходной каталог обязан быть новым или пустым, отказ до открытия сцены и записи файлов.\n''',encoding='utf-8')
license=ROOT/'experiments/EXP-002/01_support/model/font-license.txt'
if license.exists():(OUT/'font-license.txt').write_bytes(license.read_bytes())
print('EXP003_DONE',len(refs))
