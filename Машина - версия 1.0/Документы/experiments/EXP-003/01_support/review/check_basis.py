"""Independent reading of native Rhino contours/roots, no author helper imported."""
from pathlib import Path
import json,hashlib
import rhino3dm as r
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
SRC=ROOT/'documentation/01-hull-and-geometry/3d/2-1.3dm'
B=json.loads((ROOT/'experiments/EXP-003/01_support/basis/bulwark-basis.json').read_text())
M=json.loads((ROOT/'deliverables/G02/v001/01_support/alignment/transform.json').read_text())['rhino_native_to_working']
f=r.File3dm.Read(str(SRC));assert hashlib.sha256(SRC.read_bytes()).hexdigest()==B['source_sha256']
def p(e,t):
 q=e.PointAt(t);v=[q.X,q.Y,q.Z,1]
 return [sum(M[a][b]*v[b] for b in range(4))/1000 for a in range(3)]
def atx(e,x):
 ts=[e.Domain.T0+(e.Domain.T1-e.Domain.T0)*i/256 for i in range(257)]
 intervals=[(a,b) for a,b in zip(ts,ts[1:]) if (p(e,a)[0]-x)*(p(e,b)[0]-x)<=0];assert len(intervals)==1
 a,b=intervals[0]
 for _ in range(50):
  t=(a+b)/2
  if (p(e,a)[0]-x)*(p(e,t)[0]-x)<=0:b=t
  else:a=t
 return p(e,(a+b)/2)
checks=[]
for c in B['contours']:
 obj=f.Objects[c['object_index']];assert str(obj.Attributes.Id)==c['object_id']
 for row in c['edges']:
  e=obj.Geometry.Edges[row['edge_index']];n=len(row['source_points_m']);errs=[]
  for i,(q,up) in enumerate(zip(row['source_points_m'],row['proposed_raised_points_m'])):
   actual=p(e,e.Domain.T0+(e.Domain.T1-e.Domain.T0)*i/(n-1))
   errs.extend(abs(actual[a]-q[a]) for a in range(3))
   assert max(abs(up[a]-q[a]-(.25 if a==2 else 0)) for a in range(3))<1e-12
  assert max(errs)<1e-9
  checks.append({'index':c['object_index'],'edge':row['edge_index'],'points':n,'max_difference_m':max(errs)})
for row in B['sections']:
 for obj,edge,key in [(142,1,'existing_top_outer_m'),(478,6,'deck_edge_m')]:
  q=atx(f.Objects[obj].Geometry.Edges[edge],row['x_m']);assert max(abs(q[a]-row[key][a]) for a in range(3))<1e-9
for row in B['openings']:
 q=atx(f.Objects[row['source_side_index']].Geometry.Edges[1],row['centre_proposed_m'][0])
 assert max(abs(q[a]+(.125 if a==2 else 0)-row['centre_proposed_m'][a]) for a in range(3))<1e-9
(OUT/'basis-check.json').write_text(json.dumps({'status':'PASS_NATIVE_CONTOURS_AND_VERTICAL_250MM_INCREMENT','contours_checked':checks,'sections_checked':len(B['sections']),'proposed_hole_centres_checked':len(B['openings']),'meaning_limit':'Geometric classification; no material, thickness, existing as-built or load verification'},indent=2)+'\n')
print('PASS native basis, 4 contours, 9 stations, 6 proposed centres')
