"""blender --background --python this.py -- --bridge-dir DIR

Import reference OBJ, validate in metres, save new .blend, reopen and validate.
Requires modern Blender wm.obj_import. Does not edit user preferences or originals.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bridge-dir', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
folder = args.bridge_dir.resolve()
target = folder / 'vds67-reference.blend'
report_path = folder / 'blender-verification.json'
if target.exists() or report_path.exists():
    raise RuntimeError('Existing Blender outputs are never overwritten')
meta = json.loads((folder / 'metadata.json').read_text())
assert hashlib.sha256((folder / 'vds67-reference.obj').read_bytes()).hexdigest() == meta['obj_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.wm.obj_import(filepath=str(folder / 'vds67-reference.obj'),
                      forward_axis='Y', up_axis='Z', use_split_objects=True, use_split_groups=False)
for record in meta['objects']:
    obj = bpy.data.objects[record['name']]
    for key in ['source_uuid', 'source_index', 'role']:
        obj[key] = record[key]
    obj['usage'] = meta['status']
    obj['source_sha256'] = next(iter(meta['inputs_sha256'].values()))
    obj.color = {'shell': (0.25, 0.5, 0.7, 1), 'deck': (0.7, 0.7, 0.7, 1),
                 'roof': (0.8, 0.5, 0.2, 1)}[record['role']]
note = bpy.data.texts.new('READ_ME_REFERENCE_LIMITS')
note.write(json.dumps(meta, ensure_ascii=False, indent=2))


def verify():
    assert len(bpy.data.objects) == len(meta['objects'])
    assert bpy.context.scene.unit_settings.scale_length == 1.0
    rows = []
    for record in meta['objects']:
        obj = bpy.data.objects[record['name']]
        assert obj.type == 'MESH'
        assert obj['source_uuid'] == record['source_uuid']
        assert len(obj.data.vertices) == record['vertices']
        assert len(obj.data.polygons) == record['faces']
        points = [obj.matrix_world @ v.co for v in obj.data.vertices]
        measured = {key: [fn(v[a] for v in points) for a in range(3)]
                    for key, fn in [('min', min), ('max', max)]}
        delta = max(abs(measured[k][a] - record['bounds_m'][k][a])
                    for k in measured for a in range(3))
        assert delta < 0.00001, (record['name'], delta)
        rows.append({'name': record['name'], 'vertices': len(points), 'faces': len(obj.data.polygons),
                     'bounds_m': measured, 'max_bbox_coordinate_error_m': delta})
    return rows


before = verify()
bpy.ops.wm.save_as_mainfile(filepath=str(target))
bpy.ops.wm.open_mainfile(filepath=str(target))
after = verify()
assert before == after
report = {'status': 'PASS_IMPORT_SAVE_REOPEN', 'blender_version': bpy.app.version_string,
          'axis_import': {'forward_axis': 'Y', 'up_axis': 'Z'},
          'coordinate_check_tolerance_m': 0.00001,
          'scope': '8 objects, cached vertex/face counts, source UUID, metre bounding boxes before and after reopen',
          'not_checked': 'Exact CAD surfaces, manifoldness, visual rendering, hydrostatics and production suitability',
          'obj_sha256': meta['obj_sha256'], 'blend_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'objects': after}
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'objects': len(after), 'blend_sha256': report['blend_sha256']}))
