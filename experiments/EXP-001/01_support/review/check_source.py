"""Independent read of original Rhino cached meshes and EXP-001 references.
Run from repo root with .local/cad-tools/rhino/venv/bin/python.
Only review outputs are written. No author extraction script is imported.
"""
import json,hashlib,gzip
from pathlib import Path
import rhino3dm as r
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
source=ROOT/'documentation/01-hull-and-geometry/3d/2-1.3dm'
refs=json.loads((ROOT/'experiments/EXP-001/01_support/basis/source-refs.json').read_text())
mat=json.loads((ROOT/'deliverables/G02/v001/01_support/alignment/transform.json').read_text())['rhino_native_to_working']
for path,h in refs['inputs_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
model=r.File3dm.Read(str(source)); assert len(model.Objects)==491
assert model.Settings.ModelUnitSystem==r.UnitSystem.Millimeters
expected=[]; checked=[]
for i,obj in enumerate(model.Objects):
 if not isinstance(obj.Geometry,r.Brep):continue
 points=[]; faces=[]
 for f in obj.Geometry.Faces:
  m=f.GetMesh(r.MeshType.Render); assert m is not None
  offset=len(points)
  for p in m.Vertices:
   n=[p.X,p.Y,p.Z,1.]
   points.append([sum(mat[a][b]*n[b] for b in range(4))/1000 for a in range(3)])
  for f in m.Faces:faces.append([offset+k for k in (f[:3] if f[2]==f[3] else f)])
 bb={key:[fn(p[a] for p in points) for a in range(3)] for key,fn in [('min',min),('max',max)]}
 expected.append({'index':i,'uuid':str(obj.Attributes.Id),'vertices':points,'faces':faces,'bounds_m':bb})
 for ref in refs['objects']:
  if ref['index']==i:
   assert ref['object_id']==str(obj.Attributes.Id)
   delta=max(abs(bb[k][a]-ref['working_bounds_m'][k][a]) for k in bb for a in range(3))
   assert delta<1e-10,(i,delta)
   checked.append({'index':i,'max_difference_m':delta})
assert len(expected)==314
assert len(checked)==len(refs['objects'])
(OUT/'expected-native-meshes.json.gz').write_bytes(gzip.compress((json.dumps(expected,separators=(',',':'))+'\n').encode(),mtime=0))
(OUT/'source-check.json').write_text(json.dumps({'status':'PASS','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'brep_objects_with_meshes':len(expected),'basis_objects_checked':checked,'mesh_accuracy':'Original cached meshes, unknown tessellation tolerance; no exact NURBS claim.'},indent=2)+'\n')
print('PASS: 314 Breps,',len(checked),'basis bounds, original SHA and native units')
