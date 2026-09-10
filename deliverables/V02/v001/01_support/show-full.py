from pathlib import Path
import bpy
from mathutils import Vector
base=Path('/home/alexey/Groot/van-de-stadt-67-ft')
out=base/'deliverables/V02/v001/01_support'
bpy.ops.wm.open_mainfile(filepath=str(base/'deliverables/V02/v001/01_support/full/vds67-reference.blend'))
scene=bpy.context.scene
center=Vector((-10.3,0,0.7))
eye=Vector((8,-25,15))
rotation=(center-eye).to_track_quat('-Z','Y')
for o in bpy.context.selected_objects:o.select_set(False)
for o in bpy.data.objects:
 if o.type=='MESH':
  o.color={'shell':(.52,.59,.64,1),'deck':(.72,.75,.77,1),'roof':(.62,.67,.71,1)}.get(o.get('role'),(.65,.65,.65,1))
for obj in bpy.data.objects:
 if obj.get('source_index') in [362,363]: obj.color=(.12,.2,.26,1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   s=area.spaces.active;s.region_3d.view_rotation=rotation;s.region_3d.view_distance=32;s.region_3d.view_location=center;s.region_3d.view_perspective='ORTHO'
   s.overlay.show_overlays=False;s.shading.color_type='OBJECT';s.shading.light='STUDIO';s.shading.show_cavity=True
cam=bpy.data.cameras.new('Exterior_view_camera');obj=bpy.data.objects.new('Exterior_view_camera',cam);scene.collection.objects.link(obj);obj.location=eye;obj.rotation_euler=rotation.to_euler();cam.type='ORTHO';cam.ortho_scale=27;scene.camera=obj
if scene.world is None: scene.world=bpy.data.worlds.new("Exterior background")
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.86,.88,.9)
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'exterior.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'exterior.blend'))
bpy.ops.render.render(write_still=True)
