"""Independent comparison of decoded DWG JSON and DXF; not a second DWG engine."""
from pathlib import Path
from collections import Counter
import json,argparse,hashlib
import ezdxf
ap=argparse.ArgumentParser();ap.add_argument('--out-dir',default='.local/G01/review/recheck');args=ap.parse_args()
out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
p=Path('deliverables/G01/v001/01_support/dwg');j=json.loads((p/'lines-decoded.json').read_text());d=ezdxf.readfile(p/'lines-derived.dxf')
raw={format(o['handle'][2],'X'):o for o in j['OBJECTS'] if 'handle' in o}
missing=[];types=Counter();errors=[];line_delta=[];vertices_delta=[];poly=[];texts=[]
for e in d.modelspace():
 o=raw.get(e.dxf.handle)
 if o is None:missing.append(e.dxf.handle);continue
 types[e.dxftype()+' / '+o.get('entity','?')]+=1
 if e.dxftype()=='LINE':
  delta=max(abs(float(v)-float(w)) for key in ['start','end'] for v,w in zip(e.dxf.get(key),o[key]));line_delta.append(delta)
 if e.dxftype()=='TEXT':texts.append(e.dxf.text==o['text_value'])
 if e.dxftype()=='POLYLINE' and o['entity']=='POLYLINE_3D':
  vh=[format(x[-1],'X') for x in o['vertex']]; ev=list(e.vertices)
  if len(vh)!=len(ev): errors.append({'handle':e.dxf.handle,'vertex_count':[len(vh),len(ev)]})
  ds=[]
  for h,v in zip(vh,ev):
   rv=raw[h];loc=rv.get('point')
   if loc is None:errors.append({'vertex':h,'missing_point':True});continue
   ds.append(max(abs(float(a)-float(b)) for a,b in zip(v.dxf.location,loc)))
  vertices_delta.extend(ds);poly.append({'handle':e.dxf.handle,'vertex_count':len(ev),'max_delta':max(ds) if ds else None})
audit=d.audit()
report={'dwg_signature':Path('documentation/01-hull-and-geometry/lines/Linie teoretyczne VDS 67.DWG').read_bytes()[:6].decode(),'raw_objects':len(j['OBJECTS']),'modelspace_count':len(d.modelspace()),'raw_to_dxf_type_counts':dict(types),'missing_raw_handles_for_dxf_entities':missing,'header_comparison':{k:{'raw':j['HEADER'].get(k),'dxf':d.header.get('$'+k)} for k in ['INSUNITS','LUNITS','DIMSCALE','DIMLFAC']},'line_endpoint_comparisons':len(line_delta),'max_line_endpoint_abs_difference':max(line_delta),'text_comparisons':len(texts),'all_text_strings_equal':all(texts),'polyline3d_comparisons':poly,'max_vertex_abs_difference':max(vertices_delta) if vertices_delta else None,'errors':errors,'audit_errors':[{'code':str(x.code),'message':x.message} for x in audit.errors],'audit_fixes':[{'code':str(x.code),'message':x.message} for x in audit.fixes],'limits':'RawJSON and DXF use same LibreDWG decode. Equal handles/coordinates do not prove original completeness or correct physical units. No DWG source corruption conclusion.'}
assert not missing and not errors and all(texts)
(out/'independent-dwg-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='polyline3d_comparisons'},ensure_ascii=False,indent=2))
