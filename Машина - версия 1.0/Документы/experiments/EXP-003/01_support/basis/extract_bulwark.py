#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
import rhino3dm as r
root=Path(__file__).resolve().parents[4]
src=root/'documentation/01-hull-and-geometry/3d/2-1.3dm'
f=r.File3dm.Read(str(src));shift=[1294.16,19381.843773828055,24837.674386867988]
def xyz(p):return [(getattr(p,a)+shift[i])/1000 for i,a in enumerate('XYZ')]
def atx(e,x):
 lo,hi=e.Domain.T0,e.Domain.T1;flo=xyz(e.PointAt(lo))[0]-x
 assert flo*(xyz(e.PointAt(hi))[0]-x)<=0
 for _ in range(70):
  m=(lo+hi)/2;fm=xyz(e.PointAt(m))[0]-x
  if flo*fm<=0:hi=m
  else:lo=m;flo=fm
 return xyz(e.PointAt((lo+hi)/2))
records=[]
for n in [142,143]:
 o=f.Objects[n];es=[]
 for i in [1,3]:
  e=o.Geometry.Edges[i];p=[xyz(e.PointAt(e.Domain.T0+(e.Domain.T1-e.Domain.T0)*j/512)) for j in range(513)]
  es.append({'edge_index':i,'meaning':'outer' if i==1 else 'inner','source_points_m':p,'proposed_raised_points_m':[[v[0],v[1],v[2]+.25] for v in p]})
 records.append({'object_index':n,'object_id':str(o.Attributes.Id),'source_name':o.Attributes.Name,'edges':es})
rows=[]
for x in [-18.72,-18,-15,-12,-10,-7,-4,-2.5,-1]:
 a=atx(f.Objects[142].Geometry.Edges[1],x);b=atx(f.Objects[478].Geometry.Edges[6],x)
 rows.append({'x_m':x,'existing_top_outer_m':a,'deck_edge_m':b,'top_above_deck_edge_m':a[2]-b[2],'proposed_top_m':[a[0],a[1],a[2]+.25]})
openings=[]
for zone,x in [('aft',-18),('midships',-12),('bow',-2.5)]:
 for n in [142,143]:
  a=atx(f.Objects[n].Geometry.Edges[1],x)
  openings.append({'zone':zone,'source_side_index':n,'centre_proposed_m':[a[0],a[1],a[2]+.125],'length_m':.36,'height_m':.10,'corner_radius_m':.05,'status':'PROPOSED_VISUAL_ENVELOPE_NOT_FITTING_SELECTED','orientation':'along local sheer tangent, through raised bulwark; position to review with cleats and rope lead'})
out={'status':'SOURCE_GEOMETRY_PLUS_OWNER_REQUEST_EXPERIMENT','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'coordinate_frame':'G02 work metres','raise_m':.25,'raise_direction':'global vertical Z, not normal to deck','contours':records,'sections':rows,'openings':openings,'scope_limit':'Existing bulwark geometric identification, not material/thickness verification; new holes are visual proposals and require load/rope/drainage detailing'}
(root/'experiments/EXP-003/01_support/basis/bulwark-basis.json').write_text(json.dumps(out,indent=2)+'\n')
for row in rows:print(row['x_m'],round(row['existing_top_outer_m'][1],4),round(row['existing_top_outer_m'][2],4),round(row['top_above_deck_edge_m'],4))
