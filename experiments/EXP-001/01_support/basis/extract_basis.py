#!/usr/bin/env python3
"""Source object references; mm to G02 work metres, no source geometry mutation."""
import ast,csv,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
src=root/'deliverables/G01/v001/01_support/rhino/objects.csv'
trans=root/'deliverables/G02/v001/01_support/alignment/transform.json'
rows=list(csv.DictReader(src.open()))
shift=[row[3] for row in json.loads(trans.read_text())['rhino_native_to_working'][:3]]
ids=[133,144,190,191,198,212,325,328,329,331,332,333,334,335,336,338,339,340,343,344,362,363,368,369,370,371,372,373,374,375,376,377,478]
out={'status':'GEOMETRY_REFERENCES_NOT_AS_BUILT','coordinates':'G02 working metres; X increases toward bow; Z0 drawing datum, not floor','inputs_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,trans,root/'documentation/01-hull-and-geometry/3d/2-1.3dm']},'objects':[]}
for i in ids:
 r=rows[i];assert int(r['index'])==i
 key='cached_mesh_bounds' if r['cached_mesh_bounds'] else 'sample_bounds';b=ast.literal_eval(r[key]);o={'index':i,'object_id':r['id'],'source_name':r['name'],'bounds_method':key,'working_bounds_m':{k:[(b[k][j]+shift[j])/1000 for j in range(3)] for k in ['min','max']}}
 out['objects'].append(o)
(root/'experiments/EXP-001/01_support/basis/source-refs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
