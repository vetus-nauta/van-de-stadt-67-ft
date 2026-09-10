"""Use actual exported mesh bottom edges and direct native Rhino curve intersections."""
from pathlib import Path
import json,hashlib
import rhino3dm as r
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
source=ROOT/'documentation/01-hull-and-geometry/3d/2-1.3dm'
model=r.File3dm.Read(str(source));edges=model.Objects[478].Geometry.Edges
mat=json.loads((ROOT/'deliverables/G02/v001/01_support/alignment/transform.json').read_text())['rhino_native_to_working']
g=json.loads((OUT/'geometry-extracted.json').read_text());bottom=[v['lower_edge'] for v in g['footprint_edges']]
def cp(e,t):
 p=e.PointAt(t);v=[p.X,p.Y,p.Z,1]
 return [sum(mat[a][b]*v[b] for b in range(4))/1000 for a in range(3)]
def native_at_x(x,idx):
 e=edges[idx];lo,hi=e.Domain.T0,e.Domain.T1
 assert (cp(e,lo)[0]-x)*(cp(e,hi)[0]-x)<0
 for _ in range(55):
  mid=(lo+hi)/2
  if (cp(e,lo)[0]-x)*(cp(e,mid)[0]-x)<=0:hi=mid
  else:lo=mid
 return cp(e,(lo+hi)/2)
def foot(x):
 ys=[]
 for a,b in bottom:
  if min(a[0],b[0])-1e-6<=x<=max(a[0],b[0])+1e-6:
   if abs(b[0]-a[0])<1e-6:ys.extend([a[1],b[1]])
   else:
    t=max(0,min(1,(x-a[0])/(b[0]-a[0])));ys.append(a[1]+t*(b[1]-a[1]))
 assert ys,x
 return min(ys),max(ys)
def gaps(x):
 l,h=foot(x);p=native_at_x(x,6);n=native_at_x(x,11)
 return {'x_m':x,'footprint_y_min_max_m':[l,h],'native_edge_points_m':[p,n],'gaps_port_starboard_m':[abs(n[1])-abs(l),p[1]-h]}
rows=json.loads((ROOT/'experiments/EXP-002/01_support/model/passages.json').read_text())
checks=[]
for row in rows:
 q=gaps(row['x_m']);q['author_row']=row;q['author_gap_difference_m']=abs(min(q['gaps_port_starboard_m'])-row['plan_gap_each_side_m']);assert q['author_gap_difference_m']<1e-5;checks.append(q)
dense=[gaps(-15.109+(-4.798+15.109)*i/300) for i in range(301)]
minimum=min(min(q['gaps_port_starboard_m']) for q in dense)
# Footprint only. No allowance for frames, rails, posts, open doors or walking height.
result={'scope':'BARE_COAMING_PLAN_GAPS_NOT_USABLE_PASSAGE','native_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Read actual coaming lower mesh edges; exact direct native edge roots; independent of author interpolation','author_stations_checked':checks,'dense_sample_count':len(dense),'dense_minimum_plan_gap_m':minimum,'dense_minimum_is_sampled_not_exact_global':True}
(OUT/'passage-check.json').write_text(json.dumps(result,indent=2)+'\n');print('Sampled native/mesh plan minimum:',minimum,'m')
