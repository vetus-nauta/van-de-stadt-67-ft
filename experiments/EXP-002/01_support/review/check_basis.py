"""Independent source-edge scan with bracketed roots; no author functions used."""
import json,hashlib
from pathlib import Path
import rhino3dm as r
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
src=ROOT/'documentation/01-hull-and-geometry/3d/2-1.3dm'
basis=json.loads((ROOT/'experiments/EXP-002/01_support/basis/deck-sections.json').read_text())
assert hashlib.sha256(src.read_bytes()).hexdigest()==basis['source_sha256']
f=r.File3dm.Read(str(src));deck=f.Objects[478]
assert str(deck.Attributes.Id)==basis['source_object_id']
mat=json.loads((ROOT/'deliverables/G02/v001/01_support/alignment/transform.json').read_text())['rhino_native_to_working']
def xyz(edge,t):
 p=edge.PointAt(t);v=[p.X,p.Y,p.Z,1]
 return [sum(mat[a][b]*v[b] for b in range(4))/1000 for a in range(3)]
checks=[]
for row in basis['sections']:
 x=row['x_m'];pts=[]
 for ei in [6,11]:
  edge=deck.Geometry.Edges[ei];a,b=edge.Domain.T0,edge.Domain.T1
  samples=[a+(b-a)*i/512 for i in range(513)]
  intervals=[(p,q) for p,q in zip(samples,samples[1:]) if (xyz(edge,p)[0]-x)*(xyz(edge,q)[0]-x)<=0]
  assert len(intervals)==1,(x,ei,len(intervals))
  lo,hi=intervals[0]
  for _ in range(50):
   mid=(lo+hi)/2
   if (xyz(edge,lo)[0]-x)*(xyz(edge,mid)[0]-x)<=0:hi=mid
   else:lo=mid
  pts.append(xyz(edge,(lo+hi)/2))
 delta=max(abs(pts[j][a]-row['edge_points_m'][j][a]) for j in range(2) for a in range(3));assert delta<1e-9
 width=abs(pts[0][1]-pts[1][1]);assert abs(width-row['deck_plan_width_m'])<1e-9
 checks.append({'x_m':x,'points_m':pts,'max_difference_m':delta,'roots_per_edge':1})
sample_checks=[]
for group in ['outer_edges_m','deck_inner_edges_m']:
 for row in basis[group]:
  edge=deck.Geometry.Edges[row['edge_index']];pts=row['points_m'];a,b=edge.Domain.T0,edge.Domain.T1
  error=max(abs(xyz(edge,a+(b-a)*i/(len(pts)-1))[axis]-point[axis]) for i,point in enumerate(pts) for axis in range(3))
  assert error<1e-9
  sample_checks.append({'edge_index':row['edge_index'],'sample_count':len(pts),'max_difference_m':error})
(OUT/'basis-check.json').write_text(json.dumps({'status':'PASS_NATIVE_EDGE_POINTS_ONLY','scope':'25 discrete positions, no claim of clear passage or as-built dimensions','checks':checks,'sampled_edges_checked':sample_checks},indent=2)+'\n')
print('PASS',len(checks),'positions, 50 bracketed single roots')
