"""Independent scene audit; run blender -b -t 2 --python this_file.py.
Reads author scene; writes review JSON only. Does not save/mutate source scenes.
"""
import bpy,json,gzip,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
MODEL=ROOT/'experiments/EXP-001/01_support/model'
expected=json.loads(gzip.decompress((OUT/'expected-native-meshes.json.gz').read_bytes()))
def sig(o):
 return {'name':o.name,'uuid':o.get('source_uuid'),'vertices':[list(v.co) for v in o.data.vertices], 'faces':[list(p.vertices) for p in o.data.polygons], 'matrix':[list(r) for r in o.matrix_world]}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'deliverables/V02/v001/01_support/full/vds67-reference.blend'))
baseline={o.get('source_index'):sig(o) for o in bpy.data.objects if o.type=='MESH' and 'source_index' in o}
bpy.ops.wm.open_mainfile(filepath=str(MODEL/'experiment.blend'))
ref={o.get('source_index'):o for o in bpy.data.objects if o.type=='MESH' and 'source_index' in o}
assert len(ref)==len(baseline)==314
source_deltas=[]
for row in expected:
 o=ref[row['index']]
 assert sig(o)==baseline[row['index']],row['index']
 assert o.get('source_uuid')==row['uuid']
 assert len(o.data.vertices)==len(row['vertices']) and len(o.data.polygons)==len(row['faces'])
 # OBJ importer may reorder polygon vertex indices; face correspondence against V02 is exact above.
 delta=max(abs((o.matrix_world@v.co)[a]-row['vertices'][i][a]) for i,v in enumerate(o.data.vertices) for a in range(3))
 assert delta<1e-5,(row['index'],delta)
 source_deltas.append(delta)
P=json.loads((MODEL/'parameters.json').read_text())
assert abs(P['extension']['new_front_x']-P['extension']['existing_roof_forward_x']-3)<1e-9
new=[o for o in bpy.data.objects if o.type=='MESH' and 'source_index' not in o]
assert all(o.name.startswith('EXP_') for o in new)
def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
glass=[o for o in new if o.name.startswith('EXP_glass_vertical_')]
vertical_max=0;radius_errors=[]
for o in glass:
 p=points(o);assert len(p)==4
 for a,b in [(0,3),(1,2)]:
  e=math.hypot(p[a].x-p[b].x,p[a].y-p[b].y);vertical_max=max(vertical_max,e);assert e<1e-6
 for v in p:
  r=P['forward_corner_radius'];xf=P['extension']['new_front_x'];w=P['half_width']
  if v.x>xf-r+1e-5 and abs(v.y)>w-r+1e-5:
   d=math.hypot(v.x-(xf-r),abs(v.y)-(w-r));radius_errors.append(abs(d-r));assert abs(d-r)<1e-5
assert radius_errors
frontmost=max(p.x for o in glass for p in points(o))
assert abs(frontmost-P['extension']['new_front_x'])<1e-5
frames=[o for o in new if o.name.startswith('EXP_transverse_frame_')]
aft_frames=[o for o in frames if max(p.x for p in points(o))<-10.5]
low=min(p.z for o in aft_frames for p in points(o));assert abs(low-P['test_floor_z']-2.1)<1e-5
# Check actual rooflight X bounds clear of every transverse frame plan footprint.
lights=[o for o in new if o.name.startswith('EXP_roof_') and 'rooflight' in o.name]
light_overlaps=[]
for o in lights:
 p=points(o);lo=min(v.x for v in p);hi=max(v.x for v in p)
 for f in frames:
  q=points(f);flo=min(v.x for v in q);fhi=max(v.x for v in q)
  overlap=min(hi,fhi)-max(lo,flo)
  if overlap>1e-6:light_overlaps.append([o.name,f.name,overlap])
human=[o for o in new if o.name.startswith('EXP_human_')]
hz=[p.z for o in human for p in points(o)]
assert abs(min(hz)-1.0)<1e-6 and abs(max(hz)-3.0)<1e-6
# Independent vertical coverage through mast axis. All selected elements are proposed
# structure, not glass. Coverage proves geometric contact only, not load capacity.
struct=bpy.data.collections['11_CONCEPT_STRUCTURE_NOT_SIZED']
intervals=[]
for o in struct.objects:
 if o.type!='MESH':continue
 q=points(o)
 if min(v.x for v in q)-1e-6<=P['mast_x']<=max(v.x for v in q)+1e-6 and min(v.y for v in q)-1e-6<=0<=max(v.y for v in q)+1e-6:
  intervals.append((min(v.z for v in q),max(v.z for v in q),o.name))
intervals.sort();end=intervals[0][1];gaps=[]
for lo,hi,name in intervals[1:]:
 if lo>end+1e-6:gaps.append([end,lo,name])
 end=max(end,hi)
assert not gaps,gaps
result={'scope':'EXPERIMENTAL_GEOMETRY_ONLY_NOT_ENGINEERING_ACCEPTANCE','reference_objects_preserved':len(ref),'reference_mesh_and_world_transforms_identical_to_V02':True,'max_native_mesh_coordinate_delta_m':max(source_deltas),'reference_objects_hidden_in_collection':sum(any(c.hide_render for c in o.users_collection) for o in ref.values()),'new_mesh_objects':len(new),'glass_panels_checked':len(glass),'vertical_xy_delta_max_m':vertical_max,'radius_error_max_m':max(radius_errors),'new_front_x_m':frontmost,'extension_m':P['extension']['new_front_x']-P['extension']['existing_roof_forward_x'],'aft_lowest_frame_z_m':low,'conditional_aft_clearance_m':low-P['test_floor_z'],'rooflight_frame_plan_overlaps':light_overlaps,'rooflights_checked':len(lights),'human_z_min_max_m':[min(hz),max(hz)],'mast_axis_structure_z_coverage':intervals,'mast_axis_geometry_gaps':gaps,'mast_load_capacity':'NOT_CHECKED; lower support is a hypothetical zone'}
(OUT/'scene-check.json').write_text(json.dumps(result,indent=2)+'\n')
assert not light_overlaps,light_overlaps
print('EXPERIMENTAL SCENE CHECK PASS',len(ref),len(new))
