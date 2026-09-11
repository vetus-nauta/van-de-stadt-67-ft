#!/usr/bin/env python3
"""All original Brep cached meshes, not just the T01 selected envelope.
Uses the checked export path; curves, annotation and points are excluded.
"""
import rhino_cached_mesh_to_obj as exporter
model = exporter.r.File3dm.Read(str(exporter.SOURCE))
exporter.SELECTION = {
    i: ('brep', str(obj.Attributes.Id))
    for i, obj in enumerate(model.Objects)
    if isinstance(obj.Geometry, exporter.r.Brep)
}
exporter.main()
