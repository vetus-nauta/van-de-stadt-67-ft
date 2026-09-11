import ezdxf,json,csv
from pathlib import Path
from collections import Counter
L=ezdxf.readfile('deliverables/G01/v001/01_support/dwg/lines-derived.dxf');O=ezdxf.readfile('deliverables/G02/v001/01_support/cad/lines-oda-noaudit.dxf')
assert Counter(e.dxftype() for e in L.modelspace())==Counter(e.dxftype() for e in O.modelspace())
assert {e.dxf.handle for e in L.modelspace()}=={e.dxf.handle for e in O.modelspace()}
r={'modelspace_count':len(O.modelspace()),'INSUNITS':[L.header['$INSUNITS'],O.header['$INSUNITS']],'blocks':[]}
for h,old,n in [('4C21','*X27',37),('4C22','*X28',53)]:
 a=L.entitydb[h];b=O.entitydb[h];assert a.dxf.name=='*X';assert not L.blocks.get(a.dxf.name)
 x=L.blocks.get(old);y=O.blocks.get(b.dxf.name);assert x.block_record_handle==y.block_record_handle
 xx={e.dxf.handle:e for e in x};yy={e.dxf.handle:e for e in y};assert xx.keys()==yy.keys();assert len(xx)==n
 for k in xx:
  e,f=xx[k],yy[k];assert e.dxftype()==f.dxftype()=='LINE';assert e.dxf.start==f.dxf.start and e.dxf.end==f.dxf.end
 r['blocks'].append({'insert':h,'old_definition':old,'oda_definition':b.dxf.name,'identical_lines':n})
rows=[]
for a in L.modelspace().query('POLYLINE'):
 b=O.entitydb[a.dxf.handle];p=list(a.points_in_wcs());q=list(b.points_in_wcs());assert len(p)==len(q)
 delta=max((v-w).magnitude for v,w in zip(p,q));rows.append({'handle':a.dxf.handle,'flags':[a.dxf.flags,b.dxf.flags],'smooth_type':[a.dxf.smooth_type,b.dxf.smooth_type],'wcs_max_delta':delta})
r['polyline_differences']=[x for x in rows if x['flags'][0]!=x['flags'][1] or x['smooth_type'][0]!=x['smooth_type'][1] or x['wcs_max_delta']>1e-8];assert len(r['polyline_differences'])==12
for d in (L,O):
 e=d.entitydb['6387'];assert e.is_2d_polyline and tuple(e.dxf.elevation)==(0,0,0) and tuple(e.dxf.extrusion)==(0,0,1)
audit=O.audit();assert not audit.errors and not audit.fixes;r['oda_audit']={'errors':len(audit.errors),'fixes':len(audit.fixes)}
anchor_checks=[]
for row in csv.DictReader(Path('deliverables/G02/v001/01_support/alignment/anchors.csv').open()):
 pts=sorted(list(O.entitydb[row['dwg_handle']].points_in_wcs()),key=lambda p:p.z)
 wanted=[float(row['dwg_'+a]) for a in 'xyz']; z=wanted[2]
 if row['role']=='HOLDOUT_SECTION':
  a,b=next((a,b) for a,b in zip(pts,pts[1:]) if a.z<=z<=b.z and b.z>a.z)
  v=a+(b-a)*((z-a.z)/(b.z-a.z))
 else:v=min(pts,key=lambda p:sum((p[i]-wanted[i])**2 for i in range(3)))
 delta=max(abs(v[i]-wanted[i]) for i in range(3));assert delta<1e-8;anchor_checks.append({'id':row['id'],'raw_oda_vertex_or_interpolation_delta':delta})
r['raw_oda_anchors']=anchor_checks
print(json.dumps(r))
