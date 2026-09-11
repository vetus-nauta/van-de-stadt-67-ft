"""Blender 4.x: reproducible, non-engineered EXP-001 on unchanged V02 reference meshes."""
import bpy, math, json, hashlib, argparse, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
parser=argparse.ArgumentParser(description='Build EXP-001 in a NEW or EMPTY output directory; released files are never overwritten.')
parser.add_argument('--out-dir', required=True, type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=args.out_dir.expanduser().resolve()
if OUT.exists() and (not OUT.is_dir() or any(OUT.iterdir())):
 parser.error(f'Output must be a new or empty directory: {OUT}')
OUT.mkdir(parents=True, exist_ok=True)
SOURCE=ROOT/'deliverables/V02/v001/01_support/full/vds67-reference.blend'
META=ROOT/'deliverables/V02/v001/01_support/full/metadata.json'
P={
 'status':'PROPOSED_VISUAL_EXPERIMENT_NOT_ENGINEERING_OR_AS_BUILT',
 'units':'metres', 'coordinates':'G02 working XYZ; bow towards increasing X; z=0 drawing datum, not approved waterline',
 'reference_blend':str(SOURCE.relative_to(ROOT)), 'reference_blend_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'reference_metadata_sha256':hashlib.sha256(META.read_bytes()).hexdigest(),
 'extension':{'value':3.0,'status':'OWNER_REQUEST_WITH_ASSUMED_DATUM','datum':'forward extremity of roof cached mesh, not lower sloping front','existing_roof_forward_x':-10.798,'new_front_x':-7.798,'lower_front_existing_x':-9.100,'alternative_if_from_lower_front_x':-6.100},
 'cabin_aft_x':-15.109,'half_width':1.87,'forward_corner_radius':0.65,
 'mast_x':-9.2,'mast_status':'PROVISIONAL_VISUAL_MARKER_NOT_SURVEYED_OR_RELOCATED','mast_basis':'../basis/basis.md: approximate visual Sailplan range -9.4 to -8.8m, use -9.2m within that range',
 'forward_roof_top_z':2.897,'forward_roof_height_status':'PROPOSED_FLAT_DATUM_FROM_EXISTING_REAR_MAXIMUM_NOT_PRESERVED_FORWARD_PROFILE','aft_roof_top_z':3.35,'conceptual_roof_zone_depth':0.25,
 'slope_start_aft_of_mast_x':-9.5,'slope_finish_x':-10.5,
 'glazing_sill_z':2.03,'glazing_orientation':'vertical to working horizontal plane, curved corners in plan; not normal to curved hull surface',
 'test_floor_z':1.0,'test_floor_status':'HYPOTHETICAL_SECTION_ONLY_NOT_IDENTIFIED_IN_SOURCE',
 'rear_clearance_to_lowest_roof_zone':2.10,'front_clearance_to_lowest_roof_zone':1.647,
 'human_height':2.0,'structural_member_status':'VOLUMETRIC_RESERVATIONS_NO_LOAD_OR_SCANTLING_CALCULATIONS',
 'mast_load_path':'reserved mast platform -> central compression post / transverse frame -> unknown structural foundation; glass not in load path',
 'rooflights':'two longitudinal glazed strips interrupted at transverse frames, mast platform and roof step',
 'no_claims':['actual interior headroom','structural feasibility','mast relocation approval','glazing scantlings','as-built correspondence','sailing clearances or stability']}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
bpy.context.preferences.filepaths.save_version=0
# Retain all 314 source objects and their mesh data; only move collections/visibility.
REF=bpy.data.collections.new('00_REFERENCE_V02_LOCKED_UNMODIFIED_GEOMETRY');scene.collection.children.link(REF)
OLD=bpy.data.collections.new('01_REFERENCE_REPLACED_PARTS_hidden_in_experiment');scene.collection.children.link(OLD)
NEW=bpy.data.collections.new('10_EXPERIMENT_NEW_CABIN');scene.collection.children.link(NEW)
STRUCT=bpy.data.collections.new('11_CONCEPT_STRUCTURE_NOT_SIZED');scene.collection.children.link(STRUCT)
SECTION=bpy.data.collections.new('20_SECTION_HYPOTHETICAL_FLOOR');scene.collection.children.link(SECTION)
ANNOT=bpy.data.collections.new('21_SIDE_DIMENSIONS');scene.collection.children.link(ANNOT)
replaced=set(range(184,199))|set(range(328,330))|set(range(331,338))|set(range(344,378))|{338,339,340}
source_inventory=[]
for o in list(bpy.data.objects):
 if o.type!='MESH':continue
 for c in list(o.users_collection):c.objects.unlink(o)
 (OLD if o.get('source_index') in replaced else REF).objects.link(o)
 o.hide_select=True;o.color=(.53,.60,.64,1) if o.get('role')=='shell' else (.73,.77,.78,1)
 source_inventory.append({'name':o.name,'source_index':o.get('source_index'),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'hidden_replaced':o.get('source_index') in replaced})
OLD.hide_render=True;OLD.hide_viewport=True
P['hidden_reference_indices']=sorted([x['source_index'] for x in source_inventory if x['hidden_replaced']])
P['retained_reference_mesh_objects']=len(source_inventory)
COLORS={'roof':(.83,.89,.87,1),'glass':(.09,.38,.48,1),'sill':(.37,.63,.64,1),'frame':(.25,.42,.43,1),'structure':(.91,.49,.17,1),'floor':(.58,.49,.37,1),'human':(.83,.25,.17,1),'text':(.05,.09,.12,1)}
def link(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);return o
def mesh(name,verts,faces,kind='roof',c=NEW):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('EXP_'+name,m);c.objects.link(o);o.color=COLORS[kind];o['status']='PROPOSED_NOT_ENGINEERED';return o
def box(name,lo,hi,kind='roof',c=NEW):
 x,y,z=lo;X,Y,Z=hi
 return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],kind,c)
def bar(name,a,b,width=.055,kind='frame',c=NEW):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cube_add(size=1,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name='EXP_'+name;o.dimensions=(width,width,d.length);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.color=COLORS[kind];link(o,c);return o
def text(name,body,loc,size=.16,c=ANNOT):
 d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.align_x='CENTER';o=bpy.data.objects.new(name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);o.color=COLORS['text'];return o
xa=P['cabin_aft_x'];xf=P['extension']['new_front_x'];w=P['half_width'];r=P['forward_corner_radius'];front=P['forward_roof_top_z'];rear=P['aft_roof_top_z'];depth=P['conceptual_roof_zone_depth'];s0=P['slope_start_aft_of_mast_x'];s1=P['slope_finish_x'];mast=P['mast_x']
def ztop(x):return rear if x<=s1 else front if x>=s0 else front+(rear-front)*(s0-x)/(s0-s1)
# Perimeter: aft corners square, forward two 650mm radius corners, vertical glazing.
per=[(xa,-w),(xf-r,-w)]
for i in range(1,17):
 t=-math.pi/2+(math.pi/2)*i/16;per.append((xf-r+r*math.cos(t),-w+r+r*math.sin(t)))
per.append((xf,w-r))
for i in range(1,17):
 t=(math.pi/2)*i/16;per.append((xf-r+r*math.cos(t),w-r+r*math.sin(t)))
per.extend([(xa,w)])
# Subdivide long sides for explicit window mullions at slope boundaries.
expanded=[]
for i,a in enumerate(per):
 b=per[(i+1)%len(per)];expanded.append(a)
 if abs(a[1]-b[1])<1e-6 and abs(a[0]-b[0])>2:
  xs=[q for q in [-14.2,-12.9,-11.6,s1,s0,mast,xf-r] if min(a[0],b[0])+1e-6<q<max(a[0],b[0])-1e-6]
  for q in sorted(xs,reverse=b[0]<a[0]):expanded.append((q,a[1]))
per=expanded
for i,(x,y) in enumerate(per):
 X,Y=per[(i+1)%len(per)];zt=ztop(x)-.10;ZT=ztop(X)-.10
 mesh(f'glass_vertical_{i:02}',[(x,y,2.03),(X,Y,2.03),(X,Y,ZT),(x,y,zt)],[(0,1,2,3)],'glass')
 mesh(f'sill_{i:02}',[(x,y,1.77),(X,Y,1.77),(X,Y,2.03),(x,y,2.03)],[(0,1,2,3)],'sill')
 bar(f'upper_edge_{i:02}',(x,y,zt),(X,Y,ZT),.09)
 bar(f'sill_edge_{i:02}',(x,y,2.03),(X,Y,2.03),.055)
 if i%4==0 or abs(y)==w:
  bar(f'window_mullion_{i:02}',(x,y,2.00),(x,y,zt),.060)
# roof field, with two actual distinct glass strips; orange structural reservations beneath.
xs=sorted(set([xa,-14.2,-12.9,-11.6,s1,s0,mast-.24,mast+.24,xf-r]))
ys=[-w,-1.40,-.36,.36,1.40,w]
for j,(a,b) in enumerate(zip(xs,xs[1:])):
 for k,(c,d) in enumerate(zip(ys,ys[1:])):
  light=(k in [1,3] and not(a<mast+.25 and b>mast-.25) and not(a<s0 and b>s1))
  inset=.065 if light else 0
  aa,bb,cc,dd=a+inset,b-inset,c+inset,d-inset
  mesh(f'roof_{j}_{k}_'+('rooflight' if light else 'solid'),[(aa,cc,ztop(aa)),(bb,cc,ztop(bb)),(bb,dd,ztop(bb)),(aa,dd,ztop(aa))],[(0,1,2,3)],'glass' if light else 'roof')
  if light:
   # infill lips keep skylight fully framed, no continuous light cutting cross frames.
   for h,v in enumerate([(a,c,a+.065,d),(b-.065,c,b,d),(a,c,b,c+.065),(a,d-.065,b,d)]):
    A,C,B,D=v;mesh(f'rooflight_lip_{j}_{k}_{h}',[(A,C,ztop(A)),(B,C,ztop(B)),(B,D,ztop(B)),(A,D,ztop(A))],[(0,1,2,3)],'roof')
# Rounded forward roof cap above curved glass.
cap=[(x,y,front) for x,y in per if x>=xf-r-1e-6]
cap.sort(key=lambda p:math.atan2(p[1],p[0]-(xf-r)))
mesh('rounded_forward_roof_cap',cap,[tuple(range(len(cap)))],'roof')
for x in xs:
 z=ztop(x)
 box(f'transverse_frame_at_{x:.3f}',(x-.055,-w,z-depth),(x+.055,w,z-.10),'structure',STRUCT)
for y in [-w+.055,0,w-.055]:
 for a,b in zip(xs,xs[1:]):
  mesh(f'longitudinal_reserved_beam_{y}_{a}',[(a,y-.065,ztop(a)-depth),(b,y-.065,ztop(b)-depth),(b,y+.065,ztop(b)-depth),(a,y+.065,ztop(a)-depth),(a,y-.065,ztop(a)-.10),(b,y-.065,ztop(b)-.10),(b,y+.065,ztop(b)-.10),(a,y+.065,ztop(a)-.10)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'structure',STRUCT)
box('mast_bearing_TRANSFER_RESERVATION',(mast-.28,-.32,front-.10),(mast+.28,.32,front-.02),'structure',STRUCT)
box('mast_step_RESERVATION',(mast-.28,-.32,front-.02),(mast+.28,.32,front+.16),'structure',STRUCT)
bar('mast_axis_PROVISIONAL_NOT_FULL_RIG',(mast,0,front+.16),(mast,0,6.2),.16,'structure',STRUCT)
bar('compression_post_SUPPORT_UNVERIFIED',(mast,0,0.25),(mast,0,front-.25),.16,'structure',STRUCT)
box('foundation_ZONE_UNKNOWN',(mast-.4,-.55,.12),(mast+.4,.55,.30),'structure',STRUCT)
# Cutaway supplementary geometry, no invented floor is visible in exterior.
box('HYPOTHETICAL_floor_z1',(xa,-1.6,.94),(xf,1.6,1.00),'floor',SECTION)
def human(x,y):
 z=1.;box('human_leg_A',(x-.19,y-.06,z),(x-.07,y+.06,z+.94),'human',SECTION);box('human_leg_B',(x+.07,y-.06,z),(x+.19,y+.06,z+.94),'human',SECTION)
 bar('human_torso',(x,y,z+.86),(x,y,z+1.61),.27,'human',SECTION)
 bar('human_arm_A',(x-.25,y,z+1.55),(x-.31,y,z+1.02),.085,'human',SECTION);bar('human_arm_B',(x+.25,y,z+1.55),(x+.31,y,z+1.02),.085,'human',SECTION)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=.17,location=(x,y,z+1.83));o=bpy.context.object;o.name='EXP_human_head_TOP_EXACTLY_2m_above_test_floor';o.color=COLORS['human'];link(o,SECTION)
human(-12.0,-.75)
bar('mast_SECTION_display_shortened',(mast,0,front+.16),(mast,0,4.10),.16,'structure',SECTION)
# Vertical dimensions live in section scene; X/Z schematic tied to exact parameters.
for x,bottom,top,label in [(-13.35,1.,3.10,'2.10 m CLEAR / ASSUMED FLOOR'),(-8.30,1.,front-depth,'1.647 m / LOW FRONT')]:
 bar('dimension_clearance',(x,-2.14,bottom),(x,-2.14,top),.018,'text',SECTION)
 for z in [bottom,top]:bar('dimension_tick',(x-.12,-2.14,z),(x+.12,-2.14,z),.018,'text',SECTION)
 text('clearance_label',label,(x,-2.40,3.65 if x>-10 else top+.30),.13,SECTION)
text('floor_label','FLOOR z=1.00: HYPOTHETICAL / NOT SOURCE GEOMETRY',(-11.5,-2.2,.48),.16,SECTION)
text('human_label','2.00 m',(-12.,-2.2,.76),.17,SECTION)
text('mast_label','MAST POSITION PROVISIONAL',(-9.2,-2.2,4.30),.15,SECTION)
text('section_label','CONCEPT SECTION / STRUCTURE NOT SIZED',(-11.5,-2.2,4.85),.22,SECTION)
# Extension dimension in the side image.
for x in [-10.798,xf]:bar('extension_witness',(x,-2.25,3.65),(x,-2.25,4.1),.018,'text',ANNOT)
bar('extension_dimension',(-10.798,-2.25,4.0),(xf,-2.25,4.0),.018,'text',ANNOT)
text('extension_label','3.00 m FROM EXISTING ROOF EDGE',((-10.798+xf)/2,-2.27,4.17),.18)
text('side_label','EXP-001  /  PROPOSED CABIN  /  SOURCE HULL',(-11.,-2.27,6.6),.26)
SECTION.hide_render=True;SECTION.hide_viewport=True;ANNOT.hide_render=True;ANNOT.hide_viewport=True
if scene.world is None: scene.world=bpy.data.worlds.new('EXP_background')
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.89,.92,.94)
scene.render.resolution_x=1800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cam=bpy.data.cameras.new('EXP_camera');camera=bpy.data.objects.new('EXP_camera',cam);scene.collection.objects.link(camera);scene.camera=camera;cam.type='ORTHO'
def view(eye,target,scale):
 camera.location=eye;camera.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    s=area.spaces.active;s.region_3d.view_rotation=camera.rotation_euler.to_quaternion();s.region_3d.view_distance=scale;s.region_3d.view_location=Vector(target);s.region_3d.view_perspective='ORTHO';s.overlay.show_overlays=False;s.shading.color_type='OBJECT';s.shading.light='STUDIO';s.shading.show_cavity=True

def render(name):
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
view((7,-25,16),(-10.3,0,1.0),26);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'experiment.blend'));render('exterior')
view((-21,-20,14),(-11.4,0,2.5),16);render('roof-detail')
ANNOT.hide_render=False;view((-10,-35,2.5),(-10,0,2.5),24);render('side');ANNOT.hide_render=True
# Section: original geometry and near-side glass suppressed, retained in main .blend.
REF.hide_render=True;SECTION.hide_render=False
bpy.data.objects['EXP_mast_axis_PROVISIONAL_NOT_FULL_RIG'].hide_render=True
scene.display.shading.show_shadows=False
for o in NEW.objects:
 o.hide_render=not(o.name.startswith('EXP_roof_') or o.name=='EXP_rounded_forward_roof_cap')
view((-11.4,-35,2.60),(-11.4,0,2.60),10.0);render('section')
# Restore exterior main scene, never save section visibility over default file.
REF.hide_render=False;SECTION.hide_render=True
bpy.data.objects['EXP_mast_axis_PROVISIONAL_NOT_FULL_RIG'].hide_render=False
scene.display.shading.show_shadows=True
for o in NEW.objects:o.hide_render=False
view((7,-25,16),(-10.3,0,1.0),26)
(OUT/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2)+'\n')
(OUT/'reference-inventory.json').write_text(json.dumps(source_inventory,indent=2)+'\n')
(OUT/'README.md').write_text('''# EXP-001: экспериментальная рубка\n\n`experiment.blend` — самостоятельная копия полной V02 сцены. Все 314 исходных mesh объектов сохранены, заблокированы от выбора. Заменяемые элементы рубки находятся в скрытой коллекции `01_REFERENCE_REPLACED_PARTS_hidden_in_experiment`; их геометрия не изменена. Бирюзовые элементы — предложение; оранжевые — условные силовые зоны и условная ось мачты.\n\n3 м отложены от передней кромки старой крыши X=-10.798 м. От нижнего лба это другая величина. Переднее вертикальное остекление закруглено в плане R=0.65 м; верх передней крыши Z=2.897 м — предложенный плоский уровень по максимальному габариту прежней кормовой крыши. Это не точное сохранение переднего профиля: прежние передние поверхности 335/336 имеют максимум около 2.777 м. За условной мачтой к корме крыша поднимается наклонным уступом до Z=3.35 м.\n\nПол в исходниках не идентифицирован. Только в разрезе задан тестовый Z=1.00 м. До нижней границы условных балок получается 2.10 м сзади и 1.647 м спереди. **Свободный проход двухметрового человека во всей рубке не подтверждён.** Передняя низкая зона требует другого пола либо использования для сидения/рабочей поверхности; это ещё не принятое решение.\n\nМачта — условный короткий маркер, не полноценный рангоут. Её ось и опора требуют привязки. Показанный путь нагрузки вниз не доказывает существование подходящего фундамента. Старые бортовые комингсы 383/389 сохранены и местами перекрывают предложенное стекло: их переработка и сопряжение ещё не выполнены. Сечения, шаг рам, стекло, отверстия, масса, остойчивость, проходы, двери и доступ пока не рассчитаны. Остекление и фонари не несут нагрузку мачты.\n\nПовтор: `blender -b -t 4 --python experiments/EXP-001/01_support/model/build_model.py -- --out-dir .local/EXP-001/rebuild-001` из репозитория. Скрипт читает неизменяемую V02 основу и пишет только в явно указанный новый или пустой каталог. Непустой каталог отклоняется до чтения сцены и записи файлов; для следующего запуска укажите другое имя каталога. Метаданные, параметры и перечень 314 объектов рядом. Внешний вид `exterior.png`, детали крыши `roof-detail.png`, боковой вид `side.png`, условный разрез `section.png`.\n''',encoding='utf-8')
print('EXP001_DONE',len(source_inventory))
