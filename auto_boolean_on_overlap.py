bl_info = {
    "name": "Auto Boolean on Overlap",
    "blender": (3, 0, 0),
    "category": "Object",
    "version": (1, 0),
    "author": "Your Name",
    "description": "Automatically applies a Boolean modifier when two objects overlap",
}

import bpy
from mathutils import Vector

def check_overlap(obj1, obj2):
    # Get the bounding box of both objects
    obj1_bbox = [obj1.matrix_world @ Vector(corner) for corner in obj1.bound_box]
    obj2_bbox = [obj2.matrix_world @ Vector(corner) for corner in obj2.bound_box]
    
    obj1_min = Vector(map(min, zip(*obj1_bbox)))
    obj1_max = Vector(map(max, zip(*obj1_bbox)))
    
    obj2_min = Vector(map(min, zip(*obj2_bbox)))
    obj2_max = Vector(map(max, zip(*obj2_bbox)))
    
    # Check if the bounding boxes intersect
    return all([
        obj1_min.x <= obj2_max.x and obj1_max.x >= obj2_min.x,
        obj1_min.y <= obj2_max.y and obj1_max.y >= obj2_min.y,
        obj1_min.z <= obj2_max.z and obj1_max.z >= obj2_min.z
    ])

def apply_boolean(obj1, obj2, operation='UNION'):
    # Apply a boolean modifier
    mod = obj1.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = operation
    mod.object = obj2
    # Apply the modifier
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.object.modifier_apply(modifier="Boolean")

class OBJECT_OT_auto_boolean(bpy.types.Operator):
    """Apply boolean on overlap"""
    bl_idname = "object.auto_boolean"
    bl_label = "Auto Boolean on Overlap"
    bl_options = {'REGISTER', 'UNDO'}
    
    boolean_operation: bpy.props.EnumProperty(
        name="Boolean Operation",
        description="Choose the type of boolean operation",
        items=[
            ('UNION', "Union", "Combine objects"),
            ('INTERSECT', "Intersect", "Keep only overlapping parts"),
            ('DIFFERENCE', "Difference", "Subtract the second object from the first")
        ],
        default='UNION'
    )
    
    def execute(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) != 2:
            self.report({'WARNING'}, "Select exactly two objects")
            return {'CANCELLED'}
        
        obj1, obj2 = selected_objects
        if check_overlap(obj1, obj2):
            apply_boolean(obj1, obj2, self.boolean_operation)
            self.report({'INFO'}, f"Applied {self.boolean_operation} Boolean operation")
        else:
            self.report({'WARNING'}, "Objects do not overlap")
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_auto_boolean.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_auto_boolean)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_auto_boolean)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
