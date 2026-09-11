#!/usr/bin/env python3
"""Export selected original cached render meshes; never remesh or edit the 3dm.

Run with the project's rhino Python environment. Output must be a new directory.
This is a visual reference, not an exact NURBS model or a closed engineering body.
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

import rhino3dm as r

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'documentation/01-hull-and-geometry/3d/2-1.3dm'
FRAME = ROOT / 'deliverables/G02/v001/01_support/alignment/transform.json'
SOURCE_SHA = '814ecb9ae6afa27963f288d52df8db9e67d5c43bf967131b89b5ff40f1c3caa8'
SELECTION = {
    133: ('shell', '47cc8bdb-89af-4af9-9312-275b5b3d047c'),
    144: ('shell', '190edc86-b6f9-43b0-8e00-276eaca1a3ee'),
    478: ('deck', '57a33295-b699-4ce5-9558-477c26fcf4ae'),
    198: ('roof', 'c1dc5a1b-98b3-41de-8720-1da63fbf38bd'),
    333: ('roof', 'addd62c5-1935-49d0-8fec-d90ba0764cf9'),
    334: ('roof', 'fc6d1e31-1b75-4851-8701-ee610eeeed81'),
    335: ('roof', '1737ac2c-6ff8-4b4e-95f8-ee30b013543a'),
    336: ('roof', '5077b506-30cd-4ab9-9784-91394139c4cc'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(vertices):
    return {name: [fn(p[a] for p in vertices) for a in range(3)]
            for name, fn in [('min', min), ('max', max)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.out_dir.exists():
        parser.error('Output directory must not exist; existing artifacts are never overwritten')
    assert sha(SOURCE) == SOURCE_SHA, 'Original revision changed; review selection first'
    frame = json.loads(FRAME.read_text())
    matrix = frame['rhino_native_to_working']
    model = r.File3dm.Read(str(SOURCE))
    assert model and model.Settings.ModelUnitSystem == r.UnitSystem.Millimeters
    lines = ['# VDS67 cached render meshes only; not production geometry',
             '# units: metres; axes unchanged from G02 Rhino working frame',
             '# z=0 is drawing datum, not an approved waterline']
    offset = 1
    records = []
    for index, (role, expected_uuid) in SELECTION.items():
        obj = model.Objects[index]
        assert str(obj.Attributes.Id) == expected_uuid
        vertices, faces = [], []
        assert isinstance(obj.Geometry, r.Brep)
        for face in obj.Geometry.Faces:
            mesh = face.GetMesh(r.MeshType.Render)
            assert mesh is not None, f'Missing original cached mesh: {index}'
            local_offset = len(vertices)
            for p in mesh.Vertices:
                native = [p.X, p.Y, p.Z, 1.0]
                vertices.append([sum(matrix[a][b] * native[b] for b in range(4)) / 1000
                                 for a in range(3)])
            for f in mesh.Faces:
                ids = f[:3] if f[2] == f[3] else f
                assert len(set(ids)) == len(ids)
                faces.append([v + local_offset for v in ids])
        name = f'{role}_{index}_{expected_uuid}'
        lines.append('o ' + name)
        lines.extend('v ' + ' '.join(format(c, '.12g') for c in p) for p in vertices)
        lines.extend('f ' + ' '.join(str(v + offset) for v in face) for face in faces)
        offset += len(vertices)
        records.append({'name': name, 'source_index': index, 'source_uuid': expected_uuid,
                        'role': role, 'vertices': len(vertices), 'faces': len(faces),
                        'bounds_m': bounds(vertices), 'source_brep_is_solid': obj.Geometry.IsSolid})
    args.out_dir.mkdir(parents=True)
    output = args.out_dir / 'vds67-reference.obj'
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    metadata = {
        'status': 'VISUAL_REFERENCE_ONLY_NOT_EXACT_CAD_NOT_AS_BUILT',
        'inputs_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [SOURCE, FRAME, Path(__file__)]},
        'rhino3dm_distribution_version': importlib.metadata.version('rhino3dm'),
        'units': 'metres', 'native_units': 'millimetres',
        'rhino_native_to_working_mm': matrix,
        'working_mm_to_rhino_native': frame['working_to_rhino_native'],
        'coordinate_conversion': 'apply 4x4 matrix to native mm, then divide XYZ by 1000',
        'axis_meaning': 'Same XYZ orientation as G02; X longitudinal, Y transverse, Z vertical by interpretation',
        'datum': frame['origin_definition'],
        'mesh_method': 'Original cached render mesh vertices and triangle/quad faces; no remeshing, welding or closure',
        'limits': ['Tessellation accuracy unknown; source NURBS and trims are not transferred',
                   'Open reference surfaces; no volume, hydrostatics or manufacturing dimensions certified',
                   'Object roles inherited from analytical selections, not approved semantic CAD assemblies',
                   'No complete interior, structural frame or proposed alterations in this export'],
        'objects': records, 'obj_sha256': sha(output),
    }
    (args.out_dir / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'objects': len(records), 'vertices': sum(o['vertices'] for o in records),
                      'faces': sum(o['faces'] for o in records), 'obj_sha256': sha(output)}))


if __name__ == '__main__':
    main()
