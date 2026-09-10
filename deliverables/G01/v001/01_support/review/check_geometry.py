"""Independent G01 read-only check. Run from repo root with rhino venv python.
Same rhino3dm parser as author: independent code, not independent CAD engine.
No author extraction code is imported or executed.
"""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, argparse
import rhino3dm as r
root=Path('.')
parser=argparse.ArgumentParser()
parser.add_argument('--out-dir',default='.local/G01/review/recheck')
args=parser.parse_args()
out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
checks=[]
for row in csv.DictReader(open('documentation/registers/2026-09-10/documents.csv'), delimiter=';'):
 p=Path(row['path']); digest=hashlib.sha256(p.read_bytes()).hexdigest()
 checks.append({'id':row['document_id'],'sha256':digest,'matches_register':digest==row['sha256'],'bytes':p.stat().st_size})
m=r.File3dm.Read('documentation/01-hull-and-geometry/3d/2-1.3dm')
a=json.load(open('deliverables/G01/v001/01_support/rhino/inventory.json'))
objects=list(m.Objects)
counts=Counter(type(o.Geometry).__name__ for o in objects)
assert len(objects)==a['object_count'] and dict(counts)==a['types']
assert str(m.Settings.ModelUnitSystem)==a['settings']['ModelUnitSystem']
ids={str(o.Attributes.Id) for o in objects}
assert ids=={o['id'] for o in a['objects']}
# Independent denser edge evaluation and exact cached mesh vertices for chosen objects.
samples=[]
for idx in [0,3,42,133,144,198,232,234,239,264,333,334,335,336,338,339,340,343,344,400,478,484,490]:
 o=objects[idx]; g=o.Geometry; row={'index':idx,'id':str(o.Attributes.Id),'type':type(g).__name__}
 if isinstance(g,r.Curve):
  row['curve_endpoints']=[[p.X,p.Y,p.Z] for p in [g.PointAtStart,g.PointAtEnd]]
 if isinstance(g,r.Text): row.update(text=g.PlainText,origin=[g.Plane.Origin.X,g.Plane.Origin.Y,g.Plane.Origin.Z])
 if isinstance(g,r.Brep):
  row.update(faces=len(g.Faces),edges=len(g.Edges),solid=g.IsSolid)
  pts=[]
  for edge in g.Edges:
   for n in range(513):
    p=edge.PointAt(edge.Domain.T0+(edge.Domain.T1-edge.Domain.T0)*n/512)
    pts.append([p.X,p.Y,p.Z])
  meshpts=[]
  for f in g.Faces:
   mesh=f.GetMesh(r.MeshType.Render)
   if mesh:
    meshpts.extend([[v.X,v.Y,v.Z] for v in mesh.Vertices])
  for name,p in [('edge513',pts),('cached_mesh',meshpts)]:
   if p: row[name]={'min':[min(t[k] for t in p) for k in range(3)],'max':[max(t[k] for t in p) for k in range(3)]}
  author=a['objects'][idx]
  if meshpts:
   row['mesh_max_abs_difference_to_author']=max(abs(row['cached_mesh'][z][k]-author['cached_mesh_bounds'][z][k]) for z in ['min','max'] for k in range(3))
 samples.append(row)
report={'source_checks':checks,'parser_version':r.__version__,'archive_version':m.ArchiveVersion,'units':str(m.Settings.ModelUnitSystem),'absolute_tolerance_setting':m.Settings.ModelAbsoluteTolerance,'objects':len(objects),'layers':[{ 'name':l.Name,'count':sum(o.Attributes.LayerIndex==l.Index for o in objects)} for l in m.Layers],'types':dict(counts),'valid_objects':sum(o.Geometry.IsValid for o in objects),'brep_faces':sum(len(o.Geometry.Faces) for o in objects if isinstance(o.Geometry,r.Brep)),'faces_with_render_mesh':sum(f.GetMesh(r.MeshType.Render) is not None for o in objects if isinstance(o.Geometry,r.Brep) for f in o.Geometry.Faces),'solid_breps':sum(isinstance(o.Geometry,r.Brep) and o.Geometry.IsSolid for o in objects),'all_ids_and_counts_match_author':True,'samples':samples,'limits':'513 points per edge are not extrema guarantee. Cached meshes not native surface accuracy. Parser setting not survey tolerance. No yacht dimensions or as-built claim.'}
assert all(c['matches_register'] for c in checks)
(out/'independent-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['source_checks','samples']},ensure_ascii=False,indent=2))
