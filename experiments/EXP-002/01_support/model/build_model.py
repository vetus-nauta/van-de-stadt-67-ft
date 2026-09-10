"""EXP-002 Blender concept: immutable EXP-001 roof plus raked coamings, low fore coachroof, open cockpit hardtop."""
import bpy, math, json, hashlib, argparse, sys, csv
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
parser=argparse.ArgumentParser(description='EXP-002 writes only to a new or empty directory.')
parser.add_argument('--out-dir',required=True,type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=args.out_dir.expanduser().resolve()
if OUT.exists() and (not OUT.is_dir() or any(OUT.iterdir())):parser.error(f'Output must be a new or empty directory: {OUT}')
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'experiments/EXP-001/01_support/model/experiment.blend'
DECK=ROOT/'experiments/EXP-002/01_support/basis/deck-sections.json'
D=json.loads(DECK.read_text());S=sorted(D['sections'],key=lambda q:q['x_m'])
P={'status':'VISUAL_EXPERIMENT_NOT_ENGINEERING_OR_AS_BUILT','units':'metres','coordinate_frame':'G02: X forwards, Z0 is drawing datum, NOT interior floor',
 'source_blend':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'deck_basis_sha256':hashlib.sha256(DECK.read_bytes()).hexdigest(),
 'upper_roof':'EXP-001 geometry retained exactly, including rooflights, step and frames',
 'existing_upper_roof_front_x':-7.798,'new_lower_coachroof_front_x':-4.798,'additional_forward_length_m':3.0,
 'main_cabin_aft_x':-15.109,'main_halfwidth_roof':1.87,'main_base_max_halfwidth':2.28,'plan_gap_design_offset':.55,
 'main_front_original_glazing_sill_z':2.03,'main_front_glazing_top_z':2.797,'main_front_new_glazing_sill_z':2.4135,
 'front_glazing_reduction':'opaque sill raised to midpoint of EXP001 front glazing; NOT a change to interior floor',
 'main_glazing_geometry':'sides rake outwards towards deck; roof perimeter unchanged; opaque base expands separately',
 'low_coachroof_start_x':-8.448,'low_coachroof_front_x':-4.798,'low_coachroof_top_z_aft':2.4135,'low_coachroof_top_z_front':2.36,'low_glazing_height_nominal_m':.24,'low_roof_structural_reservation_depth_m':.14,
 'hardtop':{'aft_x':-18.72,'front_x':-15.109,'halfwidth_aft':1.83,'halfwidth_front':1.98,'roof_top_z_aft':3.90,'roof_top_z_front':3.92,'lowest_reserved_frame_z':3.75,'support_status':'slender conceptual posts; foundations, strength, access and full cockpit coverage not established','sides':'OPEN'},
 'mast_x':-9.2,'mast_status':'PROVISIONAL_UNCHANGED_FROM_EXP001','floor_status':'NOT_IDENTIFIED; no change to actual or assumed interior floor in EXP002',
 'foredeck_reservations':'two flush hatch zones and windlass/chain path reservation only; no selected equipment or verified below-deck volume',
 'passage_status':'sampled plan distance to outer native deck edge only, NOT clear usable passage; exclude rails/toerail/handrails/obstructions/height/slope/door sweep; linear interpolation used between native section stations',
 'structural_status':'conceptual spatial reservations only; no scantlings, loads, glazing, mass or stability calculations'}
def interp(x,key):
 for a,b in zip(S,S[1:]):
  if a['x_m']<=x<=b['x_m']:
   t=(x-a['x_m'])/(b['x_m']-a['x_m']);return key(a)*(1-t)+key(b)*t
 return key(S[0] if x<S[0]['x_m'] else S[-1])
def deckw(x):return interp(x,lambda s:min(abs(p[1]) for p in s['edge_points_m']))
def deckz(x):return interp(x,lambda s:sum(p[2] for p in s['edge_points_m'])/2)
def basew(x):return min(2.28,deckw(x)-.55)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
REF=bpy.data.collections['00_REFERENCE_V02_LOCKED_UNMODIFIED_GEOMETRY'];OLD=bpy.data.collections['01_REFERENCE_REPLACED_PARTS_hidden_in_experiment']
UPPER=bpy.data.collections.new('10_EXP001_UPPER_ROOF_RETAINED');scene.collection.children.link(UPPER)
NEW=bpy.data.collections.new('30_EXP002_RAKED_COAMINGS_AND_LOW_COACHROOF');scene.collection.children.link(NEW)
HARD=bpy.data.collections.new('31_EXP002_OPEN_COCKPIT_HARDTOP');scene.collection.children.link(HARD)
RES=bpy.data.collections.new('32_EXP002_FOREDECK_RESERVATIONS');scene.collection.children.link(RES)
ANNOT=bpy.data.collections.new('40_EXP002_DIMENSIONS');scene.collection.children.link(ANNOT)
TOP=bpy.data.collections.new('41_EXP002_PLAN_GAPS');scene.collection.children.link(TOP)
keep=[];refs=[]
for o in list(bpy.data.objects):
 if o.get('source_index') is not None:
  refs.append(o)
  if o.get('source_index') in [343,383,389]:
   for c in list(o.users_collection):c.objects.unlink(o)
   OLD.objects.link(o)
  o.hide_select=True
 elif o.name.startswith(('EXP_roof_','EXP_rooflight_lip_')) or o.name=='EXP_rounded_forward_roof_cap':
  for c in list(o.users_collection):c.objects.unlink(o)
  UPPER.objects.link(o);o.hide_select=True;keep.append(o.name)
 elif any(o.name.startswith(q) for q in ['EXP_transverse_frame','EXP_longitudinal_reserved_beam','EXP_mast_step_','EXP_mast_bearing_','EXP_mast_axis_','EXP_compression_post_','EXP_foundation_']):
  o.hide_select=True;keep.append(o.name)
 else:bpy.data.objects.remove(o,do_unlink=True)
P['reference_object_count']=len(refs);P['reference_hidden_indices']=sorted(o.get('source_index') for o in OLD.objects);P['retained_exp001_objects']=keep
COLORS={'roof':(.82,.89,.86,1),'glass':(.08,.32,.39,1),'coaming':(.63,.79,.77,1),'frame':(.28,.44,.43,1),'structure':(.80,.47,.22,1),'reservation':(.79,.59,.30,1),'text':(.025,.05,.055,1),'gap':(.88,.59,.12,1)}
fontpath=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');FONT=bpy.data.fonts.load(str(fontpath)) if fontpath.exists() else None
if FONT:
 FONT.pack()
 font_license=Path('/usr/share/doc/fonts-dejavu-core/copyright')
 if font_license.exists():(OUT/'font-license.txt').write_bytes(font_license.read_bytes())
def mesh(name,verts,faces,kind='roof',c=NEW):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('EXP002_'+name,m);c.objects.link(o);o.color=COLORS[kind];o['status']='PROPOSED_NOT_ENGINEERED';return o
def box(name,lo,hi,kind='roof',c=NEW):
 x,y,z=lo;X,Y,Z=hi;return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],kind,c)
def bar(name,a,b,width=.04,kind='frame',c=NEW):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cube_add(size=1,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name='EXP002_'+name;o.dimensions=(width,width,d.length);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.color=COLORS[kind]
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);return o

def text(name,body,loc,size=.16,c=ANNOT,top=False):
 d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.align_x='CENTER'
 if FONT:d.font=FONT
 o=bpy.data.objects.new('EXP002_'+name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(0,0,0) if top else (math.pi/2,0,0);o.color=COLORS['text'];return o

def ztop(x):return 3.35 if x<=-10.5 else 2.897 if x>=-9.5 else 2.897+.453*(-9.5-x)
# The exact EXP001 perimeter, with fewer conceptual mullions around curved ends.
xa=-15.109;xf=-7.798;w=1.87;r=.65
per=[(xa,-w),(-14.2,-w),(-12.9,-w),(-11.6,-w),(-10.5,-w),(-9.5,-w),(xf-r,-w)]
for i in range(1,17):
 t=-math.pi/2+math.pi/2*i/16;per.append((xf-r+r*math.cos(t),-w+r+r*math.sin(t)))
per.append((xf,w-r))
for i in range(1,17):
 t=math.pi/2*i/16;per.append((xf-r+r*math.cos(t),w-r+r*math.sin(t)))
per.extend([(q,w) for q in [-9.5,-10.5,-11.6,-12.9,-14.2,xa]])
def main_points(x,y):
 by=y/w*basew(x);sill=2.4135
 # glazing lower edge 60% towards the outer base; roof remains exact.
 gy=y+.60*(by-y)
 return (x,by,deckz(x)+.10),(x,gy,sill),(x,y,ztop(x)-.10)
for i,a in enumerate(per):
 b=per[(i+1)%len(per)];A,G,T=main_points(*a);B,H,U=main_points(*b)
 mesh(f'main_opaque_raked_coaming_{i}',[A,B,H,G],[(0,1,2,3)],'coaming')
 mesh(f'main_raked_glazing_{i}',[G,H,U,T],[(0,1,2,3)],'glass')
 bar(f'main_window_lower_{i}',G,H,.045);bar(f'main_window_upper_{i}',T,U,.065)
 if i<7 or i>38 or i%8==0:bar(f'main_window_mullion_{i}',G,T,.052)
# Low coachroof overlapping beneath front of retained roof. Side footprint follows available deck.
lxa=-8.448;lxf=-4.798
stations=sorted(set([lxa,-7.798,-7.,-6.5,-6.,-5.5,-5.15,lxf]))
def lowz(x):return 2.4135+(2.36-2.4135)*(x-lxa)/(lxf-lxa)
def lowpoint(x,side,part):
 width=basew(x);z=deckz(x)+.10
 if part=='base':return (x,side*width,z)
 if part=='sill':return (x,side*(width-.10),lowz(x)-.30)
 return (x,side*(width-.20),lowz(x)-.06)
for side in [-1,1]:
 for j,(a,b) in enumerate(zip(stations,stations[1:])):
  A=lowpoint(a,side,'base');B=lowpoint(b,side,'base');G=lowpoint(a,side,'sill');H=lowpoint(b,side,'sill');T=lowpoint(a,side,'top');U=lowpoint(b,side,'top')
  mesh(f'low_side_coaming_{side}_{j}',[A,B,H,G],[(0,1,2,3)],'coaming')
  mesh(f'low_side_glass_{side}_{j}',[G,H,U,T],[(0,1,2,3)],'glass')
  bar(f'low_glass_sill_{side}_{j}',G,H,.035);bar(f'low_glass_top_{side}_{j}',T,U,.045)
  if j in [0,2,4,6]:bar(f'low_mullion_{side}_{j}',G,T,.040)
# front: low glazed band, opaque lower half; corners are modest chamfers.
width=basew(lxf);Z=lowz(lxf)
mesh('low_front_opaque',[(lxf,-width,deckz(lxf)+.10),(lxf,width,deckz(lxf)+.10),(lxf,width-.10,Z-.30),(lxf,-width+.10,Z-.30)],[(0,1,2,3)],'coaming')
mesh('low_front_glass',[(lxf,-width+.10,Z-.30),(lxf,width-.10,Z-.30),(lxf,width-.20,Z-.06),(lxf,-width+.20,Z-.06)],[(0,1,2,3)],'glass')
bar('low_front_glass_sill',(lxf,-width+.10,Z-.30),(lxf,width-.10,Z-.30),.045)
bar('low_front_glass_top',(lxf,-width+.20,Z-.06),(lxf,width-.20,Z-.06),.045)
for y in [0,-width+.16,width-.16]:bar('low_front_mullion',(lxf,y,Z-.30),(lxf,y*.96,Z-.06),.035)
# Low roof has a modest crown and two flush rooflight reservations, no walkability claim.
for j,(a,b) in enumerate(zip(stations,stations[1:])):
 wa=basew(a)-.20;wb=basew(b)-.20
 for side in [-1,1]:
  mesh(f'low_roof_{j}_{side}',[(a,0,lowz(a)+.055),(b,0,lowz(b)+.055),(b,side*wb,lowz(b)),(a,side*wa,lowz(a))],[(0,1,2,3)],'roof')
 for yfactor in [-1,1]:
  bar(f'low_longitudinal_reservation_{j}_{yfactor}',(a,yfactor*(wa-.06),lowz(a)-.14),(b,yfactor*(wb-.06),lowz(b)-.14),.08,'structure')
for x in [-7.45,-6.45,-5.5]:
 ww=basew(x)-.25;bar('low_transverse_reservation',(x,-ww,lowz(x)-.14),(x,ww,lowz(x)-.14),.085,'structure')
for x in [-6.9,-5.9]:
 box(f'low_flush_light_reservation_{x}',(x-.32,-.40,lowz(x)+.047),(x+.32,.40,lowz(x)+.061),'glass')
# Open cockpit hardtop, gently tapering to stern. Keep sides entirely open.
hxa=-18.72;hxf=xa
def hw(x):return 1.83+(1.98-1.83)*(x-hxa)/(hxf-hxa)
def hz(x):return 3.90+.02*(x-hxa)/(hxf-hxa)
hxs=[hxa,-17.8,-16.7,hxf]
for a,b in zip(hxs,hxs[1:]):
 for side in [-1,1]:mesh(f'hardtop_roof_{a}_{side}',[(a,0,hz(a)+.04),(b,0,hz(b)+.04),(b,side*hw(b),hz(b)),(a,side*hw(a),hz(a))],[(0,1,2,3)],'roof',HARD)
 for side in [-1,1]:bar('hardtop_side_beam',(a,side*hw(a),hz(a)-.08),(b,side*hw(b),hz(b)-.08),.10,'frame',HARD)
for x in [hxa,-17.,hxf]:bar('hardtop_cross_frame',(x,-hw(x),hz(x)-.10),(x,hw(x),hz(x)-.10),.10,'frame',HARD)
for x in [-18.25,-15.50]:
 for side in [-1,1]:
  y=side*(hw(x)-.16);bar('hardtop_support_FOUNDATION_UNKNOWN',(x,y,1.68),(x+.12,y,hz(x)-.10),.07,'structure',HARD)
# Proposed flush reservations on original foredeck, NOT actual equipment.
for name,x,hx,hy in [('forepeak_hatch',-3.65,.42,.47),('anchor_locker_hatch',-2.15,.33,.35)]:
 z=deckz(x)+.12;box(name+'_RESERVED',(x-hx,-hy,z),(x+hx,hy,z+.035),'reservation',RES)
box('windlass_ZONE_NOT_SELECTED',(-1.44,-.23,1.93),(-.88,.23,2.07),'reservation',RES)
bar('chain_path_RESERVED',(-.88,0,1.94),(-.12,0,1.94),.04,'reservation',RES)
# Distances use actual straight bottom edges of constructed coaming panels, not design envelope alone.
def actualbasew(x):
 hits=[]
 for o in NEW.objects:
  if o.name.startswith(('EXP002_main_opaque_raked_coaming','EXP002_low_side_coaming','EXP002_low_front_opaque')):
   a,b=[v.co for v in o.data.vertices[:2]]
   if abs(a.x-b.x)<1e-7:
    if abs(x-a.x)<1e-5:hits.extend([abs(a.y),abs(b.y)])
   elif min(a.x,b.x)-1e-5<=x<=max(a.x,b.x)+1e-5:
    t=(x-a.x)/(b.x-a.x);hits.append(abs(a.y+t*(b.y-a.y)))
 return max(hits) if hits else None
# Hardtop clearance against local horizontal-object bounds, NOT accepted floor surfaces.
metadata=json.loads((ROOT/'deliverables/V02/v001/01_support/full/metadata.json').read_text())
clearances=[]
for o in metadata['objects']:
 if o['source_index'] in [52,58,212]:
  lo=o['bounds_m']['min'];hi=o['bounds_m']['max']
  clearances.append({'source_index':o['source_index'],'source_z_max_m':hi[2],'reference_x_interval_m':[lo[0],hi[0]],'overlap_x_interval_m':[max(lo[0],hxa),min(hi[0],hxf)],'minimum_reserved_underside_z_m':3.75,'conservative_vertical_gap_m':3.75-hi[2],'status':'LOCAL_SURFACE_CANDIDATE_NOT_CONFIRMED_FLOOR_OR_WALKABLE_ROUTE'})
P['hardtop']['conditional_clearances']=clearances
P['hardtop']['support_bottom_z']=1.68
P['hardtop']['support_bottom_status']='ILLUSTRATIVE_ENDPOINT_NOT_VERIFIED_CONTACT_WITH_SOURCE_STRUCTURE'
P['hardtop']['coverage']='longitudinally covers surface52 and58 bounding intervals; source212 extends 0.116m forwards beyond canopy towards main cabin; full 3D cockpit coverage and routes not certified'
P['hardtop']['rig_limit']='boom, sheets, running rigging and visibility conflicts are unresolved'
# Dimensions/labels. Plan clearances computed against native-edge section samples only.
passages=[]
for s in S:
 x=s['x_m']
 if xa<=x<=lxf:
  d=min(abs(p[1]) for p in s['edge_points_m']);bw=actualbasew(x);passages.append({'x_m':x,'deck_halfwidth_min_m':d,'base_halfwidth_m':bw,'design_envelope_halfwidth_m':basew(x),'plan_gap_each_side_m':d-bw,'status':'OUTER_EDGE_PLAN_ONLY_NOT_CLEAR_PASSAGE'})
for x in [-14.,-10.5,-7.798,-6.5,-4.798]:
 edge=deckw(x);bw=actualbasew(x);gap=edge-bw;z=4.1
 for side in [-1,1]:
  bar('plan_gap_measure',(x,side*bw,z),(x,side*edge,z),.022,'gap',TOP)
  for y in [side*bw,side*edge]:bar('plan_gap_tick',(x-.10,y,z),(x+.10,y,z),.022,'gap',TOP)
 text('gap_label',f'{gap:.2f} м',(x,-edge-.42,z),.31,TOP,True)
text('plan_title','EXP-002 / зазоры в плане до НАРУЖНОЙ кромки палубы',(-10.5,4.35,4.1),.37,TOP,True)
text('plan_limit','Не чистая ширина прохода: ограждения и препятствия не вычтены',(-10.5,-4.20,4.1),.32,TOP,True)
text('foredeck_label','Форпик / якорный отсек / лебёдка: резерв',(-3.00,3.40,4.1),.28,TOP,True)
text('hardtop_label','Открытый кокпит под хардтопом',(-16.6,3.40,4.1),.28,TOP,True)
for x in [xf,lxf]:bar('extension_witness',(x,-3.,2.65),(x,-3.,3.2),.02,'text',ANNOT)
bar('additional_extension',(xf,-3.,3.12),(lxf,-3.,3.12),.02,'text',ANNOT)
text('extension_label','ЕЩЁ 3.00 м / НИЗКАЯ НАДСТРОЙКА',((xf+lxf)/2,-3.01,3.34),.26)
text('side_title','EXP-002 / наклонные борта, низкая носовая надстройка, хардтоп',(-10.3,-3.01,6.5),.35)
text('mast_note','Условная ось мачты',(-9.2,-3.01,6.12),.22)
TOP.hide_render=True;TOP.hide_viewport=True;ANNOT.hide_render=True;ANNOT.hide_viewport=True
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.89,.92,.94)
scene.render.resolution_x=1800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cam=bpy.data.cameras.new('EXP002_camera');camera=bpy.data.objects.new('EXP002_camera',cam);scene.collection.objects.link(camera);scene.camera=camera;cam.type='ORTHO'
def view(eye,target,scale):
 camera.location=eye;camera.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    s=area.spaces.active;s.region_3d.view_rotation=camera.rotation_euler.to_quaternion();s.region_3d.view_distance=scale;s.region_3d.view_location=Vector(target);s.region_3d.view_perspective='ORTHO';s.overlay.show_overlays=False;s.shading.color_type='OBJECT';s.shading.light='STUDIO';s.shading.show_cavity=True

def render(n):scene.render.filepath=str(OUT/(n+'.png'));bpy.ops.render.render(write_still=True)
view((7,-25,16),(-10.3,0,1.3),26);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'experiment.blend'));render('exterior')
view((-20,-21,15),(-11,0,2.4),19.8);render('detail')
ANNOT.hide_render=False;scene.display.shading.show_shadows=False;view((-10.3,-35,2.7),(-10.3,0,2.7),24);render('side');ANNOT.hide_render=True
TOP.hide_render=False;view((-10.3,0,30),(-10.3,0,0),25);render('top')
TOP.hide_render=True;scene.display.shading.show_shadows=True;view((7,-25,16),(-10.3,0,1.3),26)
(OUT/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2)+'\n')
(OUT/'hardtop-clearances.json').write_text(json.dumps(clearances,ensure_ascii=False,indent=2)+'\n')
(OUT/'passages.json').write_text(json.dumps(passages,ensure_ascii=False,indent=2)+'\n')
(OUT/'reference-inventory.json').write_text(json.dumps([{'name':o.name,'source_index':o.get('source_index'),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'hidden':o in list(OLD.objects)} for o in refs],indent=2)+'\n')
(OUT/'README.md').write_text('''# EXP-002: классическая наклонная надстройка и хардтоп\n\nВерхняя крыша, наклонная ступень, фонари и силовые резервы EXP-001 сохранены геометрически. EXP-001 и исходные файлы не изменялись. Все 314 исходных mesh объектов V02 находятся в отдельной заблокированной подоснове; заменяемые только скрыты. Дополнительно скрыты исходные 343, 383, 389 для показа нового сопряжения комингсов: это предложение переделки, не существующее исполнение.\n\nНижнее основание главной рубки расширено к палубе, стекло боков наклонено. Сплошной передний комингс поднят на половину высоты прежнего лобового стекла: с Z=2.03 до Z=2.4135 м, стекло сверху остаётся до Z=2.797 м. **Это подъём наружной непрозрачной части, а не установленное изменение пола внутри.**\n\nДополнительная низкая надстройка идёт ещё на 3.00 м: X=-7.798 → -4.798 м. Она сужается к носу вслед за реальной палубой. Низкая полоса остекления по бокам и впереди, небольшой поперечный свод крыши, условные поперечные связи. В носу показаны лишь резервы люков форпика, якорного отсека и лебёдки; их объём и оборудование не подтверждены.\n\nХардтоп отдельно поднят до Z=3.90…3.92 м (плюс местный свод 0.04 м); нижний предел условных поперечных рам Z=3.75 м. По максимальным отметкам площадок-кандидатов 52/58/212 условные зазоры соответственно около 2.50/2.23/2.13 м. Эти площадки не признаны чистыми полами; см. hardtop-clearances.json. Опоры снизу заканчиваются условно на Z=1.68 м, контакт с существующим набором не доказан. Конфликты с гиком, шкотами и такелажем пока не проверены. Хардтоп X=-18.72…-15.109 м перекрывает выбранную основную зону кокпита; боковые стороны открыты. Тонкие опоры и связи условны: фундамент, прочность, проходы и покрытие всех крайних мест ещё проверяются.\n\n`passages.json` содержит плановые расстояния от пересечений фактических прямолинейных нижних рёбер новых комингсов до внешних кромок исходной палубы 478/edges6,11. Проектный запас огибающей 0.55 м. Между исходными сечениями палубы для построения применяется линейная интерполяция; таблица измеряет итоговые рёбра модели в исходных сечениях отдельно от проектной огибающей. **Это не чистая ширина прохода:** релинги, комингс/фальшборт, поручни, местные препятствия, высота, уклон палубы и открывание дверей не вычтены. Протопчины — сохраняемые наружные полосы исходной палубы.\n\nМачта по-прежнему условно X=-9.2 м. Пол, реальные высоты прохода, узлы сопряжения, сечения, стекло, нагрузки, масса и остойчивость не установлены. Стекло не несёт нагрузку мачты. Это самостоятельный геометрический эксперимент, не рабочий чертёж.\n\nВоспроизведение: `blender -b -t 4 --python experiments/EXP-002/01_support/model/build_model.py -- --out-dir .local/EXP-002/rebuild-001`. Каталог должен быть новым или пустым, иначе скрипт отказывает до открытия сцены и записи файлов. Генератор использует Blender 4.0.2, точную сохранённую основу EXP-001 и таблицу сечений EXP-002.\n\nФайлы: `experiment.blend`, `exterior.png`, `detail.png`, `side.png`, `top.png`, параметры, реестр подосновы и плановые зазоры. Цвет исходного корпуса серый, предлагаемой надстройки светло-бирюзовый, стекла тёмный, силовых/технических резервов охристый.\n''',encoding='utf-8')
print('EXP002_DONE',len(refs))
