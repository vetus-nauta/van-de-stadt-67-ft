#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
import rhino3dm as r
root=Path(__file__).resolve().parents[4]
src=root/'documentation/01-hull-and-geometry/3d/2-1.3dm'
f=r.File3dm.Read(str(src)); shift=[1294.16,19381.843773828055,24837.674386867988]
def xyz(p):return [(getattr(p,a)+shift[i])/1000 for i,a in enumerate('XYZ')]
# Actual native deck Brep outer trim edges; fixed source selection from G02 deck loop.
obj=f.Objects[478];edges=[6,11]
def cut(e,x):
 lo,hi=e.Domain.T0,e.Domain.T1;flo=xyz(e.PointAt(lo))[0]-x
 for _ in range(70):
  mid=(lo+hi)/2;fm=xyz(e.PointAt(mid))[0]-x
  if flo*fm<=0:hi=mid
  else:lo=mid;flo=fm
 return xyz(e.PointAt((lo+hi)/2))
xs=[-18.5,-18,-17.5,-17,-16,-15.1,-15,-14,-13,-12,-11,-10.5,-10,-9,-8,-7.798,-7,-6.5,-6,-5.5,-5,-4.798,-4,-3,-2]
sections=[]
for x in xs:
 p=[cut(obj.Geometry.Edges[i],x) for i in edges]
 sections.append({'x_m':x,'edge_points_m':p,'deck_plan_width_m':abs(p[0][1]-p[1][1]),'max_cabin_halfwidth_for_0_5m_plan_gap_m':min(abs(v[1]) for v in p)-.5})
out={'status':'MODEL_REFERENCE_NOT_CLEAR_PASSAGE_OR_AS_BUILT','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_object_index':478,'source_object_id':str(obj.Attributes.Id),'edge_indices':edges,'method':'Root bisection of X on native Brep edge parameter; no DXF alignment or mesh interpolation','coordinate_frame':'G02 work metres, X forward, Z0 drawing datum not floor','sections':sections}
out['outer_edges_m']=[{'edge_index':i,'points_m':[xyz(obj.Geometry.Edges[i].PointAt(obj.Geometry.Edges[i].Domain.T0+(obj.Geometry.Edges[i].Domain.T1-obj.Geometry.Edges[i].Domain.T0)*j/512)) for j in range(513)]} for i in edges]
# Cockpit-adjacent deck cutout is a continuous boundary with the existing cabin; do not label the whole loop cockpit.
out['deck_inner_edges_m']=[{'edge_index':i,'points_m':[xyz(obj.Geometry.Edges[i].PointAt(obj.Geometry.Edges[i].Domain.T0+(obj.Geometry.Edges[i].Domain.T1-obj.Geometry.Edges[i].Domain.T0)*j/256)) for j in range(257)]} for i in [0,1,2,3,4,5]]
(root/'experiments/EXP-002/01_support/basis/deck-sections.json').write_text(json.dumps(out,indent=2)+'\n')
for d in sections:print(d['x_m'],[(round(p[1],4),round(p[2],4)) for p in d['edge_points_m']])
