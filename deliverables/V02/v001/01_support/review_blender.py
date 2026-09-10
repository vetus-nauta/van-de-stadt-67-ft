"""Independent .blend read: compare all retained cached vertices and polygon indices to OBJ."""
from pathlib import Path
import json, hashlib
import bpy
F=Path(__file__).parent
meshfile=F/'full/vds67-reference.blend';objfile=F/'full/vds67-reference.obj'
meta=json.loads((F/'full/metadata.json').read_text())
expected={};count=0
for line in objfile.read_text().splitlines():
 if line.startswith('o '):cur={'v':[],'f':[],'offset':count+1};expected[line[2:]]=cur
 elif line.startswith('v '):cur['v'].append([float(a) for a in line.split()[1:]]);count+=1
 elif line.startswith('f '):cur['f'].append([int(a)-cur['offset'] for a in line.split()[1:]])
bpy.ops.wm.open_mainfile(filepath=str(meshfile))
assert len(bpy.data.objects)==314
err=0
for rec in meta['objects']:
 o=bpy.data.objects[rec['name']];ex=expected[rec['name']]
 assert o['source_uuid']==rec['source_uuid']
 assert len(o.data.vertices)==len(ex['v'])==rec['vertices']
 assert [list(p.vertices) for p in o.data.polygons]==ex['f']
 for v,p in zip(o.data.vertices,ex['v']):
  q=o.matrix_world@v.co
  err=max(err,max(abs(a-b) for a,b in zip(q,p)))
assert err<1e-5
result={'status':'PASS_INDEPENDENT_BLEND_REREAD','objects':314,'vertices':count,'max_vertex_error_m':err,'blender_version':bpy.app.version_string,'blend_sha256':hashlib.sha256(meshfile.read_bytes()).hexdigest(),'obj_sha256':hashlib.sha256(objfile.read_bytes()).hexdigest(),'scope':'All UUIDs, every vertex transformed to world metres, all polygon index lists. No geometric healing, NURBS verification, volume or as-built assertion.'}
(F/'review-blender.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
