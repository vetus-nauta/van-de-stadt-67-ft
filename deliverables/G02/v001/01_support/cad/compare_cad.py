#!/usr/bin/env python3
"""Compare independent DWG decoders via untouched DXFs, before audit mutation."""
import argparse, collections, csv, hashlib, json, math, pathlib, re
import ezdxf
from ezdxf import bbox
p=argparse.ArgumentParser();p.add_argument('--oda',required=True);p.add_argument('--g01',required=True);p.add_argument('--log',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
def clean(o):
 if isinstance(o,dict):return {k:clean(v) for k,v in o.items()}
 if isinstance(o,list):return [clean(v) for v in o]
 if isinstance(o,float) and not math.isfinite(o):return None
 return o
def dump(n,o):(out/n).write_text(json.dumps(clean(o),ensure_ascii=False,indent=2,default=str,allow_nan=False)+'\n')
def norm(x):
 if isinstance(x,(str,int,float,bool,type(None))):return x
 try:return [norm(v) for v in x]
 except TypeError:return str(x)
def geometry(e):
 t=e.dxftype();keys={'LINE':['start','end','extrusion'],'ARC':['center','radius','start_angle','end_angle','extrusion'],'TEXT':['text','insert','align_point','height','rotation','width','oblique','halign','valign','extrusion'],'LWPOLYLINE':['elevation','flags','const_width','extrusion'],'POLYLINE':['elevation','flags','smooth_type','extrusion'],'INSERT':['insert','xscale','yscale','zscale','rotation','extrusion']}[t]
 r={k:norm(e.dxf.get(k,e.DXFATTRIBS.get(k).default)) for k in keys}
 if t=='POLYLINE':r['vertices']=[{k:norm(v.dxf.get(k,v.DXFATTRIBS.get(k).default)) for k in ['location','flags','bulge','start_width','end_width']} for v in e.vertices]
 if t=='LWPOLYLINE':r['vertices']=norm(e.get_points())
 return r
def delta(x,y):
 if isinstance(x,dict) and isinstance(y,dict):return max([delta(x[k],y[k]) for k in x] or [0]) if x.keys()==y.keys() else math.inf
 if isinstance(x,list) and isinstance(y,list):return max([delta(v,w) for v,w in zip(x,y)] or [0]) if len(x)==len(y) else math.inf
 if isinstance(x,(int,float)) and isinstance(y,(int,float)):return abs(x-y)
 return 0 if x==y else math.inf
ds=[ezdxf.readfile(a.g01),ezdxf.readfile(a.oda)]; inv=[]
for path,d in zip([a.g01,a.oda],ds):
 inv.append({'sha256':hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest(),'model_count':len(d.modelspace()),'types':dict(collections.Counter(e.dxftype() for e in d.modelspace())),'model_handles':sorted(e.dxf.handle for e in d.modelspace()),'header':{k:norm(d.header.get(k)) for k in ['$ACADVER','$INSUNITS','$MEASUREMENT','$LUNITS','$DIMSCALE','$DIMLFAC','$EXTMIN','$EXTMAX']},'blocks':[{'name':b.name,'handle':b.block_record_handle,'count':len(b),'entity_handles':[e.dxf.handle for e in b]} for b in d.blocks]})
rows=[]
poly=[]
for e in ds[0].modelspace():
 other=ds[1].entitydb.get(e.dxf.handle); diff=math.inf if other is None or other.dxftype()!=e.dxftype() else delta(geometry(e),geometry(other));rows.append({'handle':e.dxf.handle,'type':e.dxftype(),'layer_g01':e.dxf.layer,'layer_oda':other.dxf.layer if other else None,'differing_fields':','.join(k for k in geometry(e) if other is not None and delta(geometry(e)[k],geometry(other)[k])>1e-8),'geometry_max_abs_delta':float(diff),'pass_tolerance_1e-8':bool(diff<=1e-8)})
for e in ds[0].modelspace().query('POLYLINE'):
 other=ds[1].entitydb[e.dxf.handle];poly.append({'handle':e.dxf.handle,'raw_flags':[e.dxf.flags,other.dxf.flags],'smooth_type':[e.dxf.smooth_type,other.dxf.smooth_type],'wcs_points_delta':delta(norm(e.points_in_wcs()),norm(other.points_in_wcs())),'note':'ezdxf.points_in_wcs sequence only; elevation=0 special case retains raw Z, not proof of CAD curve equivalence'})
with (out/'comparison.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
missing=sorted(set(re.findall(r'Object handle not found \d+/0x([0-9A-Fa-f]+)',pathlib.Path(a.log).read_text())))
miss=[]
for h in missing:
 e=ds[1].entitydb.get(h.upper());miss.append({'handle':h.upper(),'oda_present':e is not None,'oda_type':e.dxftype() if e else None})
res={'ezdxf_version':ezdxf.__version__,'inputs':dict(zip(['g01','oda'],inv)),'comparison_scope':'1241 modelspace entities: core geometry, TEXT contents/placement, INSERT transform; excludes styles, proxy payloads, metadata and semantics; tolerance in drawing coordinate units','tolerance':1e-8,'same_model_handle_set':inv[0]['model_handles']==inv[1]['model_handles'],'model_geometry_pass':int(sum(r['pass_tolerance_1e-8'] for r in rows)),'model_geometry_fail':[r for r in rows if not r['pass_tolerance_1e-8']],'max_finite_coordinate_delta':max(r['geometry_max_abs_delta'] for r in rows if math.isfinite(r['geometry_max_abs_delta'])),'polyline_wcs':poly,'missing_handle_warnings':miss,'block_reference_findings':[]}
for h in ['4C21','4C22']:
 es=[d.entitydb[h] for d in ds]; b=ds[1].blocks[es[1].dxf.name]; old=next(z for z in ds[0].blocks if z.block_record_handle==b.block_record_handle)
 res['block_reference_findings'].append({'insert':h,'g01_name':es[0].dxf.name,'oda_name':es[1].dxf.name,'g01_block_same_record':old.name,'block_record':b.block_record_handle,'line_count':len(b),'same_member_handles':set(e.dxf.handle for e in b)==set(e.dxf.handle for e in old),'geometry_delta':max(delta(geometry(e),geometry(ds[1].entitydb[e.dxf.handle])) for e in old)})
for d,i in zip(ds,inv):
 aud=d.audit();i['audit_errors']=[str(x) for x in aud.errors];i['audit_fixes']=[{'code':int(x.code),'message':x.message} for x in aud.fixes]
dump('comparison.json',res)
print(json.dumps(clean({k:v for k,v in res.items() if k not in ['inputs','comparison_scope']}),ensure_ascii=False,indent=2))
