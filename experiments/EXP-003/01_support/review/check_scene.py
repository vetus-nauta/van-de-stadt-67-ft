"""Independent comparison, native-loop interpolation and BVH aperture/contact tests."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent;M=ROOT/'experiments/EXP-003/01_support/model'
if '--scene-dir' in sys.argv:M=Path(sys.argv[sys.argv.index('--scene-dir')+1])
def pts(o):return [o.matrix_world@v.co for v in o.data.vertices]
def sig(o):return {'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world],'uuid':o.get('source_uuid')}
def tree(objects):
 v=[];f=[]
 for o in objects:
  offset=len(v);v+=pts(o);f += [[offset+i for i in face.vertices] for face in o.data.polygons]
 return BVHTree.FromPolygons(v,f,all_triangles=False)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'experiments/EXP-002/01_support/model/experiment.blend'))
base={o.get('source_index'):sig(o) for o in bpy.data.objects if o.type=='MESH' and 'source_index' in o}
bpy.ops.wm.open_mainfile(filepath=str(M/'experiment.blend'))
refs={o.get('source_index'):o for o in bpy.data.objects if o.type=='MESH' and 'source_index' in o}
assert len(base)==len(refs)==314
for i,old in base.items():assert sig(refs[i])==old,i
P=json.loads((M/'parameters.json').read_text());B=json.loads((ROOT/'experiments/EXP-003/01_support/basis/bulwark-basis.json').read_text())
strips=[o for o in bpy.data.objects if o.name.startswith('EXP003_raised_bulwark_')]
assert len(strips)==2
raise_checks=[]
def interp_curve(points,x):
 points=sorted(points,key=lambda v:v[0])
 for a,b in zip(points,points[1:]):
  if a[0]<=x<=b[0]:
   t=(x-a[0])/(b[0]-a[0]);return Vector([a[j]+t*(b[j]-a[j]) for j in range(3)])
 raise AssertionError(x)
for c in B['contours']:
 o=next(o for o in strips if str(c['object_index']) in o.name);bt=tree([o])
 outer=next(e['source_points_m'] for e in c['edges'] if e['meaning']=='outer')
 inner=next(e['source_points_m'] for e in c['edges'] if e['meaning']=='inner')
 for x in [-18,-15,-12,-10,-7,-4,-2.5]:
  mid=(interp_curve(outer,x)+interp_curve(inner,x))/2
  hit=bt.ray_cast(mid+Vector((0,0,.5)),Vector((0,0,-1)),.7)
  assert hit[0] is not None
  increment=hit[0].z-mid.z
  assert abs(increment-.25)<.001,(c['object_index'],x,increment)
  raise_checks.append({'source_side_index':c['object_index'],'x_m':x,'actual_increment_m':increment})
apertures=[]
for opening in B['openings']:
 strip=next(o for o in strips if str(opening['source_side_index']) in o.name)
 t=tree([strip]);centre=Vector(opening['centre_proposed_m'])
 row=next(q for q in B['contours'] if q['object_index']==opening['source_side_index'])
 outer=next(q['source_points_m'] for q in row['edges'] if q['meaning']=='outer')
 k=min(range(1,len(outer)-1),key=lambda i:abs(outer[i][0]-centre.x))
 tangent=Vector(outer[k+1])-Vector(outer[k-1]);tangent.z=0;tangent.normalize();normal=Vector((-tangent.y,tangent.x,0))
 def hit(dx,dz):
  c=centre+tangent*dx+Vector((0,0,dz));return t.ray_cast(c-normal*.20,normal,.40)[0] is not None
 clear=[not hit(dx,dz) for dx in [-.08,0,.08] for dz in [-.015,0,.015]]
 solid=[hit(0,dz) for dz in [-.09,.09]]
 assert all(clear) and all(solid),(opening,clear,solid)
 apertures.append({'zone':opening['zone'],'side_source':opening['source_side_index'],'interior_9_rays_clear':all(clear),'upper_lower_solid_control_rays_hit':all(solid)})
contacts=[]
feet=[o for o in bpy.data.objects if o.type=='MESH' and 'support_foot_CONTACT' in o.name]
assert len(feet)==4
for row in P['supports']:
 point=Vector(row['base_contact_xyz']);src=refs[row['source_index_contact']];near=tree([src]).find_nearest(point)
 assert near[0] is not None and near[3]<1e-5,(row,near)
 foot=min(feet,key=lambda o:(sum(pts(o),Vector())/len(pts(o))-point).length)
 actual_foot_distance=tree([foot]).find_nearest(point)[3]
 assert actual_foot_distance<.001,(foot.name,actual_foot_distance)
 corner_checks=[]
 for corner in row.get('foot_corner_xyz',[]):
  d=tree([src]).find_nearest(Vector(corner));assert d[0] is not None and d[3]<1e-5,(row,corner,d)
  corner_checks.append({'xyz':corner,'source_distance_m':d[3]})
 contacts.append({'source_index':row['source_index_contact'],'xyz':list(point),'source_distance_m':near[3],'actual_shoe_mesh_at_base_distance_m':actual_foot_distance,'foot_corner_contacts':corner_checks})
overhead=[o for o in bpy.data.objects if o.type=='MESH' and any(q in o.name for q in ['continuous_canopy','canopy_cross_frame','canopy_edge_beam'])]
roof_tree=tree(overhead);headroom=[]
for idx in [52,58,212]:
 measures=[];misses=0
 for point in pts(refs[idx]):
  hit=roof_tree.ray_cast(point+Vector((0,0,.00001)),Vector((0,0,1)),5)
  if hit[0] is not None:measures.append({'source_xyz_m':list(point),'underside_xyz_m':list(hit[0]),'vertical_gap_m':hit[0].z-point.z})
  else:misses+=1
 assert measures
 headroom.append({'candidate_index':idx,'status':'SURFACE_CANDIDATE_NOT_CONFIRMED_FLOOR; SAMPLED_VERTICES_NOT_GLOBAL_MIN','ray_hit_count':len(measures),'ray_miss_count':misses,'minimum':min(measures,key=lambda q:q['vertical_gap_m']),'by_x_metre':[{'x_floor_m':k,'min_gap_m':min(q['vertical_gap_m'] for q in measures if math.floor(q['source_xyz_m'][0])==k)} for k in sorted({math.floor(q['source_xyz_m'][0]) for q in measures})]})
angles=[]
for name in ['EXP003_front45_opaque','EXP003_front45_glass','EXP003_front45_curved_fascia']:
 o=bpy.data.objects.get(name);assert o is not None,name
 q=pts(o);face=max(o.data.polygons,key=lambda p:p.area)
 n=(q[face.vertices[1]]-q[face.vertices[0]]).cross(q[face.vertices[2]]-q[face.vertices[0]]).normalized()
 angle=math.degrees(math.atan2(abs(n.x),abs(n.z)))
 assert abs(angle-45)<.01 and n.x*n.z>0,(name,angle,list(n))
 angles.append({'object':name,'largest_planar_face_angle_to_horizontal_deg':angle})
def section_y(o,x):
 v=pts(o);ys=[]
 for edge in o.data.edges:
  a,b=[v[i] for i in edge.vertices]
  if abs(a.x-b.x)<1e-8:
   if abs(a.x-x)<1e-5:ys.extend([a.y,b.y])
  elif min(a.x,b.x)<=x<=max(a.x,b.x):ys.append(a.y+(x-a.x)/(b.x-a.x)*(b.y-a.y))
 return ys
body=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('EXP002_main_opaque_raked_coaming','EXP002_low_side_coaming','EXP003_front45_opaque'))]
gaps=[]
for row in json.loads((M/'inner-bulwark-gaps.json').read_text()):
 x=row['x_m'];by=[y for o in body for y in section_y(o,x)];sy=[y for o in strips for y in section_y(o,x)]
 pos=min(y for y in sy if y>0);neg=max(y for y in sy if y<0)
 gp,gs=min(by)-neg,pos-max(by)
 assert abs(gp-row['port_plan_gap_m'])<1e-6 and abs(gs-row['starboard_plan_gap_m'])<1e-6
 gaps.append({'x_m':x,'port_gap_m':gp,'starboard_gap_m':gs})
# Export actual geometry for separate checks of rake/passages/junctions.
new=[o for o in bpy.data.objects if o.type=='MESH' and 'source_index' not in o]
interesting=[{'name':o.name,'vertices':[list(p) for p in pts(o)],'faces':[list(f.vertices) for f in o.data.polygons]} for o in new if any(q in o.name for q in ['front','coaming','bulwark','support','canopy','beam','frame','roof'])]
(OUT/'geometry-extracted.json').write_text(json.dumps(interesting,separators=(',',':'))+'\n')
result={'status':'PASS_SOURCE_GEOMETRY_APERTURE_RAYS_AND_SOURCE_CONTACTS','reference_objects_preserved':len(refs),'reference_display_note':P.get('reference_display_change'),'aperture_checks':apertures,'actual_bulwark_raise_checks':raise_checks,'support_source_contacts':contacts,'overhead_clearance_samples':headroom,'front_face_angles':angles,'actual_inner_bulwark_plan_gaps':gaps,'limits':'Aperture sampling checks actual voids, not fitting load or manufacturing geometry. Contact distances only, no strength or verified underlying structural continuity.'}
(OUT/'scene-check.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
