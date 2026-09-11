"""Read-only hull clearance for block-layout envelope; run Blender in repo root."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];S=Path(__file__).parent
src=R/'experiments/EXP-003/01_support/model/experiment.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
trees=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.get('source_index') in [133,144]:
  trees.append(BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons]))
# local wet aft wall inner face X=-15.37, Y=1.6-y, bow towards local x+.
cases={'wet_outer':[-15.47,-10.87,-1.7,1.7],'dry_cabinet_outer':[-10.87,-10.17,-1.7,1.7],'side_passage':[-15.47,-10.17,-2.4,-1.7]}
rows=[]
for name,(x0,x1,y0,y1) in cases.items():
 pts=[];missing=0;nx=math.ceil((x1-x0)/.1);ny=math.ceil((y1-y0)/.05)
 for i in range(nx+1):
  x=x0+(x1-x0)*i/nx
  for j in range(ny+1):
   y=y0+(y1-y0)*j/ny;hits=[]
   for tree in trees:
    q,normal,idx,dist=tree.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),10)
    if q is not None:hits.append(q.z)
   if hits:pts.append([x,y,max(hits)])
   else:missing+=1
 worst=max(pts,key=lambda p:p[2]);floor=math.ceil((worst[2]+.15)/.05)*.05
 rows.append({'zone':name,'bounds_xy_m':[x0,x1,y0,y1],'sample_count':len(pts),'no_hit_count':missing,'highest_sample_xyz_m':[round(v,6) for v in worst],'underfloor_reserve_m':.15,'minimum_uniform_floor_rounded_up_m':round(floor,2),'status':'SAMPLED_HULL_ONLY_NOT_INTERIOR_FIT'})
out={'source':str(src.relative_to(R)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'coordinate_note':'G02 historical mesh, not actual waterline/as-built. These floor limits are outputs, NOT selected floor levels.','cases':rows,'limits':['No frames or tank deductions','Missing seam hits disclosed','No roof/passage headroom established','Allowance 0.15m is provisional; plate normal thickness not calculated']}
(S/'shell-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
