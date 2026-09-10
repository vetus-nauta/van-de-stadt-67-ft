"""Independent review: re-read original Rhino mesh vertices vs exported OBJ, no author imports."""
from pathlib import Path
import collections, hashlib, json, zipfile
import rhino3dm as r
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).parent
src=ROOT/'documentation/01-hull-and-geometry/3d/2-1.3dm'
meta_path=FOLDER/'full/metadata.json'
meta=json.loads(meta_path.read_text())
obj_path=FOLDER/'full/vds67-reference.obj'
assert hashlib.sha256(obj_path.read_bytes()).hexdigest()==meta['obj_sha256']
for p,h in meta['inputs_sha256'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
model=r.File3dm.Read(str(src))
breps={i:o for i,o in enumerate(model.Objects) if isinstance(o.Geometry,r.Brep)}
assert len(model.Objects)==491 and len(breps)==314
assert {o['source_index'] for o in meta['objects']}==set(breps)
parsed={}; current=None
for line in obj_path.read_text().splitlines():
 if line.startswith('o '):
  current={'vertices':[],'faces':[]};parsed[line[2:]]=current
 elif line.startswith('v '):current['vertices'].append([float(x) for x in line.split()[1:]])
 elif line.startswith('f '):current['faces'].append([int(x) for x in line.split()[1:]])
assert len(parsed)==314
matrix=json.loads((ROOT/'deliverables/G02/v001/01_support/alignment/transform.json').read_text())['rhino_native_to_working']
offset=1; rows=[]; max_vertex_error=0; max_bbox_error=0
for rec in meta['objects']:
 original=breps[rec['source_index']]
 assert str(original.Attributes.Id)==rec['source_uuid']
 expected_vertices=[];expected_faces=[]
 for face in original.Geometry.Faces:
  mesh=face.GetMesh(r.MeshType.Render);assert mesh is not None
  start=len(expected_vertices)
  for p in mesh.Vertices:
   native=(p.X,p.Y,p.Z,1)
   expected_vertices.append([sum(a*b for a,b in zip(row,native))/1000 for row in matrix[:3]])
  for f in mesh.Faces:
   expected_faces.append([start+offset+i for i in (f[:3] if f[2]==f[3] else f)])
 actual=parsed[rec['name']]
 assert len(actual['vertices'])==len(expected_vertices)==rec['vertices']
 assert actual['faces']==expected_faces
 assert len(expected_faces)==rec['faces']
 err=max(abs(a-b) for p,q in zip(actual['vertices'],expected_vertices) for a,b in zip(p,q))
 assert err<1e-8
 bbox_error=max(abs(rec['bounds_m'][k][a]-fn(p[a] for p in expected_vertices)) for k,fn in [('min',min),('max',max)] for a in range(3))
 assert bbox_error<1e-10
 max_vertex_error=max(max_vertex_error,err);max_bbox_error=max(max_bbox_error,bbox_error)
 rows.append({'source_index':rec['source_index'],'source_uuid':rec['source_uuid'],'vertices':len(expected_vertices),'faces':len(expected_faces),'vertex_max_error_m':err})
 offset+=len(expected_vertices)
archives=[]
for path in sorted((ROOT/'.local/original-deliveries/2026-09-10').glob('attachments*.zip')):
 with zipfile.ZipFile(path) as z:
  members=[{'name':n,'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in z.namelist() if not n.endswith('/')]
  threed=[p for p in members if Path(p['name']).suffix.lower() in {'.3dm','.step','.stp','.iges','.igs','.obj','.blend','.stl','.fbx'}]
  assert len(threed)==1 and threed[0]['sha256']==hashlib.sha256(src.read_bytes()).hexdigest()
  archives.append({'archive':path.name,'members':members})
assert len(archives)==3
result={'status':'PASS_CACHED_BREP_EXPORT_ONLY','source_objects':len(model.Objects),'source_breps':len(breps),'source_brep_faces':sum(len(o.Geometry.Faces) for o in breps.values()),'exported_mesh_objects':len(parsed),'exported_vertices':sum(x['vertices'] for x in rows),'exported_mesh_faces':sum(x['faces'] for x in rows),'max_vertex_error_m':max_vertex_error,'max_bbox_error_m':max_bbox_error,'scope':'All UUIDs, every cached vertex and triangle/quad face index, all bounds; independent code using same rhino3dm engine. No source curves/text/points exported.','checked_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,obj_path,meta_path]},'archives':archives,'objects':rows}
(FOLDER/'review-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['objects','archives','checked_sha256']},ensure_ascii=False))
