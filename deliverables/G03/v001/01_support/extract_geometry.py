"""Read-only Blender mesh sampling; run blender -b --python this_file. Outputs only G03 support."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
SOURCE=ROOT/'experiments/EXP-003/01_support/model/experiment.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
refs=[o for o in bpy.data.objects if o.type=='MESH' and o.get('source_index') is not None]
def geom(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];fs=[list(f.vertices) for f in o.data.polygons]
 return vs,fs
def bv(o):
 vs,fs=geom(o);return BVHTree.FromPolygons(vs,fs)
cache=[(o,bv(o)) for o in refs]
shell=[(o,b) for o,b in cache if o['source_index'] in [133,144]]
def hit(b,x,y):
 hits=[];z=5
 for _ in range(12):
  q,n,i,d=b.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),10)
  if q is None:break
  if abs(n.z)>.5:hits.append({'z':round(q.z,6),'normal_z':round(n.z,4)})
  z=q.z-.0001
 return hits
xs=[-14.87,-11.27,-15,-14.5,-14,-13.7,-13.5,-13,-12.5,-12.25,-12,-11.7,-11.5,-11.2,-11,-10.5,-10,-9.5]
levels=[-1.25,-1,-.75,-.70,-.5,-.4,-.35,0,.25,.5,.75,1,1.25,1.5]
sections=[]
for x in xs:
 widths=[]
 for z in levels:
  ys=[]
  for o,b in shell:
   for y,dy in [(-5,1),(5,-1)]:
    q,n,i,d=b.ray_cast(Vector((x,y,z)),Vector((0,dy,0)),10)
    if q is not None:ys.append(q.y)
  vals=sorted(set(round(y,6) for y in ys));widths.append({'z_m':z,'shell_y_hits_m':vals,'outer_width_m':round(vals[-1]-vals[0],6) if len(vals)>1 else None})
 surfaces=[]
 for y in [0,-.75,.75,-1.2,1.2,-1.25,1.25,-1.3,-1.75,1.75,-2.05,-2.25,2.25]:
  for o,b in cache:
   hs=hit(b,x,y)
   for q in hs:
    if .4<=q['z']<=2.8:surfaces.append({'y_m':y,'source_index':o['source_index'],'source_uuid':o.get('source_uuid',o.get('source_id','')),'name':o.name,**q})
 bottoms=[]
 for y in [0,-.75,.75,-1.2,1.2,-1.25,1.25,-1.3,-1.75,1.75,-2.05]:
  for o,b in shell:
   q,n,i,dist=b.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),10)
   if q is not None:bottoms.append({"y_m":y,"source_index":o["source_index"],"z_m":round(q.z,6)})
 roofs=[]
 for o in bpy.data.objects:
  if o.type=='MESH' and ('EXP003_continuous_canopy' in o.name or 'EXP003_canopy_cross_frame' in o.name):
   b=bv(o)
   for y in [0,-1.25,1.25]:
    for q in hit(b,x,y):roofs.append({'y_m':y,'object':o.name,**q})
 sections.append({'x_m':x,'widths_by_z':widths,'shell_bottom_at_y':bottoms,'horizontal_source_intersections':surfaces,'proposal_roof_intersections':roofs})
inputs=['experiments/EXP-003/01_support/model/experiment.blend','experiments/EXP-003/01_support/model/parameters.json','deliverables/G02/v001/01_support/alignment/transform.json','deliverables/G02/v001/01_support/alignment/sections-working.json','deliverables/G02/v001/01_support/alignment/curves-working.json']
d={'status':'CONCEPT_NUMERICAL_BASIS_NOT_AS_BUILT','units':'m','coordinate_system':'G02 working = EXP003 world; X forward, Y transverse, Z up; origin native line234, not actual waterline','source_count':len(refs),'method':'BVH ray intersections of retained cached Rhino meshes and EXP003 roof meshes; samples are not exact Brep or structural scantlings','inputs_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},'sections':sections}
curves=json.loads((ROOT/'deliverables/G02/v001/01_support/alignment/curves-working.json').read_text())
for section in sections:
 x=section['x_m'];hits=[]
 for edge in curves['groups']['deck']:
  points=edge['points_mm']
  for a,b in zip(points,points[1:]):
   if min(a[0],b[0])<=x*1000<max(a[0],b[0]):
    t=(x*1000-a[0])/(b[0]-a[0]);hits.append({'source_index':edge['object_index'],'edge_index':edge['edge_index'],'y_m':round((a[1]+t*(b[1]-a[1]))/1000,6),'z_m':round((a[2]+t*(b[2]-a[2]))/1000,6)})
 section['deck_edge_intersections']=hits
 def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
 z=3.35+.55*smooth((-13.4-x)/1.6) if x<-13.4 else (3.35 if x<-10.5 else (2.897+.453*smooth(-9.5-x) if x<-9.5 else 2.897))
 section['roof_profile_edge_top_m']=round(z,6)
 section['roof_conservative_frame_bottom_m']=round(z-.225,6)
d['proposed_planes_not_source']={'engine_room_floor_z_m':-.7,'upper_salon_floor_z_m':1.10,'upper_salon_floor_total_depth_m':.18,'engine_room_ceiling_z_m':.92,'engine_room_geometric_height_m':1.62,'side_passage_floor_z_m':-.55,'shell_inward_side_allowance_m':.10,'deck_downward_structure_lining_allowance_m':.18,'status':'PROPOSED_SCENARIO_NOT_SCANTLINGS_OR_AS_BUILT','notes':['0.10 side reserve is horizontal reduction each side, not normal shell thickness','0.18 floor depth combines provisional structure and lining; load capacity uncalculated','Do not use EXP003 roof as engine-room ceiling if upper salon floor is present','Roof profile conservative -0.225 follows EXP003 clearance method, not measured continuous bottom surface']}
# Check full candidate footprints on a 0.10 m longitudinal grid and <=0.05 m transverse grid.
checks=[]
for label,y0,y1,floor in [('ER',-1.2,1.2,-.70),('passage',-2.05,-1.30,-.35)]:
 points=[]
 for i in range(37):
  x=-14.87+3.6*i/36
  for j in range(49 if label=='ER' else 16):
   n=48 if label=='ER' else 15;y=y0+(y1-y0)*j/n
   hh=[]
   for o,b in shell:
    q,normal,index,dist=b.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),10)
    if q is not None:hh.append(q.z)
   if hh:points.append({'x_m':round(x,5),'y_m':round(y,5),'shell_z_m':round(max(hh),6)})
 worst=max(points,key=lambda p:p['shell_z_m'])
 checks.append({'zone':label,'bounds_xy_m':[-14.87,-11.27,y0,y1],'tested_floor_z_m':floor,'underfloor_reserve_m':.15,'sample_count':len(points),'grid_x_step_m':.1,'grid_y_step_m':.05,'highest_shell_point':worst,'min_floor_minus_shell_m':round(floor-worst['shell_z_m'],6),'required_min_constant_floor_z_m':round(worst['shell_z_m']+.15,6),'status':'CLASH_WITH_150MM_RESERVE','points':points})
d['candidate_footprint_checks']=checks
bchecks=[]
for label,y0,y1 in [('B_ER',-1.0,1.0),('B_passage',-1.85,-1.10),('B2_ER',-.92,.92),('B2_passage',-1.77,-1.02),('B3_ER_with_walls',-1.05,1.05),('B3_passage',-1.75,-1.05)]:
 points=[]
 for i in range(43):
  x=-15.47+4.2*i/42
  for j in range(41):
   y=y0+(y1-y0)*j/40
   for o,b in shell:
    q,n,idx,dist=b.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),10)
    if q is not None:points.append({'x':round(x,4),'y':round(y,4),'z':round(q.z,6)})
 worst=max(points,key=lambda p:p['z']);stations=[]
 for xx in [-15.47,-14,-12.5,-11.27]:
  pp=[p for p in points if abs(p['x']-xx)<.051]
  if pp:stations.append(max(pp,key=lambda p:p['z']))
 bchecks.append({'zone':label,'bounds_xy_m':[-15.47,-11.27,y0,y1],'max_shell_point':worst,'min_floor_with_150mm_reserve':round(worst['z']+.15,6),'sample_count':len(points),'representative_max_shell_at_station':stations,'conservative_roof_bottom_m':3.125,'minimum_roof_halfwidth_m':1.87,'assumed_side_structure_reserve_m':.10,'reserved_inner_halfwidth_m':1.77,'passage_width_m':round(y1-y0,3) if 'passage' in label else None})
d['alternative_B_checks']=bchecks

(OUT/'geometry-basis.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('GEOMETRY DONE',len(sections))
