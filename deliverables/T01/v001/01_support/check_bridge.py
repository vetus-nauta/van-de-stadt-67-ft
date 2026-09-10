"""Independent T01 check; run using the project rhino Python environment."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import rhino3dm as r

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BRIDGE = HERE / 'bridge'
source = ROOT / 'documentation/01-hull-and-geometry/3d/2-1.3dm'
frame_path = ROOT / 'deliverables/G02/v001/01_support/alignment/transform.json'
model = r.File3dm.Read(str(source))
assert len(model.Objects) == 491
assert model.Settings.ModelUnitSystem == r.UnitSystem.Millimeters
frame = json.loads(frame_path.read_text())['rhino_native_to_working']
assert [row[:3] for row in frame[:3]] == [[1,0,0],[0,1,0],[0,0,1]]
offset = [row[3] for row in frame[:3]]
meta = json.loads((BRIDGE / 'metadata.json').read_text())
for path, expected_sha in meta['inputs_sha256'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected_sha
assert hashlib.sha256((BRIDGE / 'vds67-reference.obj').read_bytes()).hexdigest() == meta['obj_sha256']

objects = {}
vertices = []
for line in (BRIDGE / 'vds67-reference.obj').read_text().splitlines():
    fields = line.split()
    if not fields or fields[0].startswith('#'):
        continue
    if fields[0] == 'o':
        name = fields[1]
        objects[name] = {'vertices': [], 'faces': [], 'offset': len(vertices)}
    elif fields[0] == 'v':
        vertex = [float(v) for v in fields[1:]]
        vertices.append(vertex)
        objects[name]['vertices'].append(vertex)
    elif fields[0] == 'f':
        objects[name]['faces'].append([int(i)-1-objects[name]['offset'] for i in fields[1:]])
    else:
        raise AssertionError(fields[0])
assert set(o['source_index'] for o in meta['objects']) == {133,144,478,198,333,334,335,336}
assert len(objects) == 8
rows = []
for record in meta['objects']:
    obj = model.Objects[record['source_index']]
    assert str(obj.Attributes.Id) == record['source_uuid']
    mesh_vertices, mesh_faces = [], []
    for face in obj.Geometry.Faces:
        mesh = face.GetMesh(r.MeshType.Render)
        start = len(mesh_vertices)
        for v in mesh.Vertices:
            mesh_vertices.append([(value + offset[a]) * .001 for a,value in enumerate((v.X,v.Y,v.Z))])
        for f in mesh.Faces:
            mesh_faces.append([start + int(i) for i in (f[:3] if f[2] == f[3] else f)])
    exported = objects[record['name']]
    assert exported['faces'] == mesh_faces
    assert len(exported['vertices']) == len(mesh_vertices) == record['vertices']
    assert len(mesh_faces) == record['faces']
    error = max(abs(a-b) for v,w in zip(mesh_vertices,exported['vertices']) for a,b in zip(v,w))
    assert error < 1e-9
    rows.append({'source_index': record['source_index'], 'source_uuid': record['source_uuid'],
                 'vertices': len(mesh_vertices), 'faces': len(mesh_faces), 'obj_max_coordinate_error_m': error})

with tempfile.TemporaryDirectory(prefix='vds67-independent-') as tmp:
    dump = Path(tmp) / 'scene.json'
    code = ('import bpy,json\n'
            'from pathlib import Path\n'
            'result={"units":bpy.context.scene.unit_settings.system,"scale":bpy.context.scene.unit_settings.scale_length,"objects":{}}\n'
            'for o in bpy.data.objects:\n'
            ' result["objects"][o.name]={"type":o.type,"uuid":o.get("source_uuid"),"vertices":[list(o.matrix_world @ v.co) for v in o.data.vertices],"faces":[list(p.vertices) for p in o.data.polygons]}\n'
            f'Path({str(dump)!r}).write_text(json.dumps(result))\n')
    script = Path(tmp) / 'read.py'
    script.write_text(code)
    proc = subprocess.run(['blender','--background',str(BRIDGE / 'vds67-reference.blend'),'--python',str(script)],capture_output=True,text=True,check=True)
    scene = json.loads(dump.read_text())
assert scene['units'] == 'METRIC' and scene['scale'] == 1.0
assert set(scene['objects']) == set(objects)
for record,row in zip(meta['objects'],rows):
    actual = scene['objects'][record['name']]
    exported = objects[record['name']]
    assert actual['type'] == 'MESH' and actual['uuid'] == record['source_uuid']
    assert actual['faces'] == exported['faces']
    assert len(actual['vertices']) == len(exported['vertices'])
    error = max(abs(a-b) for v,w in zip(actual['vertices'],exported['vertices']) for a,b in zip(v,w))
    assert error < 2e-6
    row['blend_max_coordinate_error_m'] = error
files = [source,frame_path,BRIDGE/'metadata.json',BRIDGE/'vds67-reference.obj',BRIDGE/'vds67-reference.blend',ROOT/'tools/cad/rhino_cached_mesh_to_obj.py',ROOT/'tools/cad/blender_reference_scene.py']
result = {'status':'PASS_REFERENCE_TRANSFER_ONLY','reviewer':'/root/tools_review',
          'method':'Original Rhino cached vertices and face topology compared against all OBJ vertices/faces; separately started Blender reads saved scene, checks every world-space vertex, face and UUID.',
          'limits':'Same rhino3dm source reader as author; distinct checking code. No validation of NURBS, tessellation accuracy, closed solid, physical hull or design feasibility.',
          'source_objects':len(model.Objects),'exported_objects':len(rows),'objects':rows,
          'checked_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(HERE/'bridge-independent-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'objects':len(rows),'vertices':sum(r['vertices'] for r in rows),'faces':sum(r['faces'] for r in rows)}))
