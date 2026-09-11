"""Independent read-only Blender comparison and actual mesh-footprint extraction."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent;M=ROOT/'experiments/EXP-002/01_support/model'
def sig(o):return {'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world],'uuid':o.get('source_uuid')}
def points(o):return [list(o.matrix_world@v.co) for v in o.data.vertices]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'experiments/EXP-001/01_support/model/experiment.blend'))
ref={o.get('source_index'):sig(o) for o in bpy.data.objects if o.type=='MESH' and 'source_index' in o}
roof={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(('EXP_roof_','EXP_rooflight_lip_')) or o.name=='EXP_rounded_forward_roof_cap')}
structure={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH' and any(o.name.startswith(q) for q in ['EXP_transverse_frame','EXP_longitudinal_reserved_beam','EXP_mast_step_','EXP_mast_bearing_','EXP_mast_axis_','EXP_compression_post_','EXP_foundation_'])}
bpy.ops.wm.open_mainfile(filepath=str(M/'experiment.blend'))
nowref={o.get('source_index'):o for o in bpy.data.objects if o.type=='MESH' and 'source_index' in o}
assert len(ref)==len(nowref)==314
for i,s in ref.items():assert sig(nowref[i])==s,i
for n,s in (roof|structure).items():assert n in bpy.data.objects and sig(bpy.data.objects[n])==s,n
new=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('EXP002_')]
footprint=[];rake=[]
for o in new:
 if any(k in o.name for k in ['main_opaque_raked_coaming_','low_side_coaming_','low_front_opaque']):
  q=points(o);footprint.append({'name':o.name,'lower_edge':[q[0],q[1]]})
 if 'main_raked_glazing_' in o.name:
  q=points(o)
  for a,b in [(0,3),(1,2)]:
   if abs(q[b][1])>1.5:rake.append(abs(q[a][1])-abs(q[b][1]))
assert rake and min(rake)>0
low=[o for o in new if o.name.startswith(('EXP002_low_roof_','EXP002_low_side_coaming_','EXP002_low_side_glass_')) or o.name in ['EXP002_low_front_opaque','EXP002_low_front_glass']]
front=max(p[0] for o in low for p in points(o));assert abs(front+4.798)<1e-5
front_glass=points(bpy.data.objects['EXP002_low_front_glass'])
assert max(p[2] for p in front_glass)-min(p[2] for p in front_glass)>0
hard=[o for o in new if 'hardtop_' in o.name]
hard_geometry=[{'name':o.name,'points_m':points(o)} for o in hard]
low_windows=[{'name':o.name,'points_m':points(o)} for o in new if 'low_side_glass' in o.name or 'low_front_glass' in o.name]
# Plan coverage on actual sampled vertices of four source candidates, not whole cockpit.
roofpolys=[]
for o in hard:
 if 'hardtop_roof_' not in o.name:continue
 q=points(o)
 for face in o.data.polygons:roofpolys.append([q[i][:2] for i in face.vertices])
def inside(p,poly):
 signs=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):signs.append((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
 return all(v>=-1e-7 for v in signs) or all(v<=1e-7 for v in signs)
coverage=[]
for i in [52,58,212,457]:
 q=points(nowref[i]);n=sum(any(inside(v,poly) for poly in roofpolys) for v in q)
 coverage.append({'source_candidate_index':i,'vertices_under_roof_in_plan':n,'total_vertices':len(q),'all_sampled_vertices_covered':n==len(q),'candidate_z_min_max_m':[min(p[2] for p in q),max(p[2] for p in q)]})
cross=[p[2] for o in hard if 'hardtop_cross_frame' in o.name for p in points(o)]
assert abs(min(cross)-3.75)<1e-5
clearance_checks=[]
for row in json.loads((M/'hardtop-clearances.json').read_text()):
 q=points(nowref[row['source_index']]);gap=min(cross)-max(p[2] for p in q)
 assert abs(gap-row['conservative_vertical_gap_m'])<1e-5
 clearance_checks.append({'candidate':row['source_index'],'independent_gap_m':gap})
mainfront=[o for o in new if 'main_raked_glazing_' in o.name and all(abs(p[0]+7.798)<1e-5 for p in points(o))]
assert mainfront
fz=[p[2] for o in mainfront for p in points(o)]
assert abs(min(fz)-(2.03+2.797)/2)<1e-5 and abs(max(fz)-2.797)<1e-5
(OUT/'geometry-extracted.json').write_text(json.dumps({'footprint_edges':footprint,'hardtop_geometry':hard_geometry,'low_windows':low_windows},indent=2)+'\n')
result={'status':'PASS_EXPERIMENTAL_INHERITANCE_AND_SHAPE','original_reference_objects_unchanged':len(ref),'EXP001_roof_meshes_unchanged':len(roof),'EXP001_structure_meshes_unchanged':len(structure),'new_mesh_count':len(new),'main_side_glazing_outward_delta_y_min_max_m':[min(rake),max(rake)],'low_coachroof_front_x_m':front,'additional_extension_m':front-(-7.798),'low_glazing_objects':len(low_windows),'hardtop_objects':len(hard),'hardtop_min_crossframe_z_m':min(cross),'hardtop_gap_checks':clearance_checks,'main_front_glazing_z_min_max_m':[min(fz),max(fz)],'hardtop_source_candidate_vertex_coverage':coverage,'reference_objects_hidden':sum(any(c.hide_render for c in o.users_collection) for o in nowref.values())}
(OUT/'scene-check.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
