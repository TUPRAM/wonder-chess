"""Export temporary centimeter-valued copies while keeping authored meter data intact."""
import bpy
from mathutils import Matrix

def scale_translation_curves(action,factor):
    count=0
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    if curve.data_path.endswith('location'):
                        for key in curve.keyframe_points:
                            key.co.y*=factor;key.handle_left.y*=factor;key.handle_right.y*=factor;count+=1
                        curve.update()
    return count

def export_normalized_copy(path,objects,animation,raw_export):
    scene=bpy.context.scene;old_units=scene.unit_settings.scale_length
    if abs(old_units-1)>1e-8:raise RuntimeError('Expected meter authoring scene before centimeter-copy export')
    if any(any(abs(v-1)>1e-8 for v in ob.scale) for ob in objects):raise RuntimeError('Apply source object scale before normalized skeletal export')
    original_names={ob:ob.name for ob in objects};copies={};data=[];action_copy=None
    selected=list(bpy.context.selected_objects);active=bpy.context.view_layer.objects.active
    try:
        for ob in objects:ob.name='WC_EXPORT_SOURCE_'+original_names[ob]
        for original in objects:
            copied=original.copy();copied.data=original.data.copy();data.append(copied.data)
            scene.collection.objects.link(copied);copied.name=original_names[original]
            copied.hide_set(False);copied.hide_viewport=False;copied.hide_render=False;copies[original]=copied
            copied.data.transform(Matrix.Scale(100,4))
            copied.location=original.location*100;copied.scale=(1,1,1)
            if copied.type=='ARMATURE':
                source_action=original.animation_data.action if original.animation_data else None
                copied.animation_data_clear()
                if animation and source_action:
                    action_copy=source_action.copy();scale_translation_curves(action_copy,100)
                    copied.animation_data_create();copied.animation_data.action=action_copy
                    copied.animation_data.action_slot=action_copy.slots[0]
                else:
                    for bone in copied.pose.bones:bone.location=(0,0,0);bone.rotation_euler=(0,0,0);bone.scale=(1,1,1)
        for original,copied in copies.items():
            if original.parent in copies:copied.parent=copies[original.parent]
            for modifier in copied.modifiers:
                if modifier.type=='ARMATURE' and modifier.object in copies:modifier.object=copies[modifier.object]
        scene.unit_settings.scale_length=.01;scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
        raw_export(path,list(copies.values()),animation)
    finally:
        for copied in copies.values():bpy.data.objects.remove(copied,do_unlink=True)
        for copied_data in data:
            if isinstance(copied_data,bpy.types.Mesh):bpy.data.meshes.remove(copied_data)
            elif isinstance(copied_data,bpy.types.Armature):bpy.data.armatures.remove(copied_data)
        if action_copy is not None:bpy.data.actions.remove(action_copy)
        for original,name in original_names.items():original.name=name
        scene.unit_settings.scale_length=old_units
        bpy.ops.object.select_all(action='DESELECT')
        for ob in selected:
            if ob.name in bpy.data.objects:ob.select_set(True)
        bpy.context.view_layer.objects.active=active
        scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
