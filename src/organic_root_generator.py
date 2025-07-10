bl_info = {
    "name": "Fibonacci Organic Root Generator",
    "author": "Francisco Santelices & Claude",
    "version": (9, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Add > Mesh > Fibonacci Root System",
    "description": "Advanced organic root generator with proper connections and growth direction",
    "category": "Add Mesh",
}

import bpy
import math
from mathutils import Vector
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import (
    FloatProperty, IntProperty, BoolProperty,
    EnumProperty, FloatVectorProperty, PointerProperty
)

# ============= PROPERTY GROUP =============
class FibonacciRootProperties(PropertyGroup):
    # Main Root Properties
    root_length: FloatProperty(
        name="Length",
        description="Length of main roots",
        default=5.0,
        min=0.1,
        max=20.0,
        update=lambda self, context: update_modifier(self, context)
    )

    root_count: IntProperty(
        name="Root Count",
        description="Number of main root branches",
        default=5,
        min=1,
        max=13,
        update=lambda self, context: update_modifier(self, context)
    )

    base_width: FloatProperty(
        name="Base Width",
        description="Width at the base of main roots",
        default=0.3,
        min=0.01,
        max=1.0,
        precision=3,
        update=lambda self, context: update_modifier(self, context)
    )

    # Growth Direction
    growth_direction: EnumProperty(
        name="Growth Direction",
        description="Main growth direction of roots",
        items=[
            ('DOWN', "Down", "Roots grow downward"),
            ('UP', "Up", "Roots grow upward"),
            ('RADIAL', "Radial", "Roots grow outward")
        ],
        default='DOWN',
        update=lambda self, context: update_modifier(self, context)
    )

    spread_angle: FloatProperty(
        name="Spread Angle",
        description="How much roots spread from center",
        default=30.0,
        min=0.0,
        max=90.0,
        update=lambda self, context: update_modifier(self, context)
    )

    # Deformation
    noise_scale: FloatProperty(
        name="Noise Scale",
        description="Scale of organic noise",
        default=2.0,
        min=0.1,
        max=20.0,
        update=lambda self, context: update_modifier(self, context)
    )

    roughness: FloatProperty(
        name="Roughness",
        description="Amount of organic deformation",
        default=0.5,
        min=0.0,
        max=2.0,
        update=lambda self, context: update_modifier(self, context)
    )

    # Fibonacci
    fibonacci_angle: FloatProperty(
        name="Fibonacci Angle",
        description="Golden angle for distribution",
        default=137.5,
        min=0.0,
        max=360.0,
        update=lambda self, context: update_modifier(self, context)
    )

    root_separation: FloatProperty(
        name="Root Separation",
        description="Distance between roots at base",
        default=0.2,
        min=0.0,
        max=2.0,
        update=lambda self, context: update_modifier(self, context)
    )

    # Individual Growth Controls
    enable_individual_growth: BoolProperty(
        name="Enable Individual Growth",
        description="Allow individual control of each root's growth",
        default=False,
        update=lambda self, context: update_modifier(self, context)
    )

    root_growth_1: FloatProperty(name="Root 1", default=1.0, min=0.0, max=1.5, update=lambda self, context: update_modifier(self, context))
    root_growth_2: FloatProperty(name="Root 2", default=1.0, min=0.0, max=1.5, update=lambda self, context: update_modifier(self, context))
    root_growth_3: FloatProperty(name="Root 3", default=1.0, min=0.0, max=1.5, update=lambda self, context: update_modifier(self, context))
    root_growth_4: FloatProperty(name="Root 4", default=1.0, min=0.0, max=1.5, update=lambda self, context: update_modifier(self, context))
    root_growth_5: FloatProperty(name="Root 5", default=1.0, min=0.0, max=1.5, update=lambda self, context: update_modifier(self, context))

    # Secondary Roots
    enable_secondary_roots: BoolProperty(
        name="Enable Secondary Roots",
        description="Add secondary roots",
        default=True,
        update=lambda self, context: update_modifier(self, context)
    )

    secondary_density: FloatProperty(
        name="Density",
        description="Number of secondary roots",
        default=20.0,
        min=0.0,
        max=100.0,
        update=lambda self, context: update_modifier(self, context)
    )

    secondary_length: FloatProperty(
        name="Length",
        description="Length of secondary roots",
        default=1.0,
        min=0.1,
        max=5.0,
        update=lambda self, context: update_modifier(self, context)
    )

    secondary_width: FloatProperty(
        name="Width",
        description="Width of secondary roots",
        default=0.08,
        min=0.001,
        max=0.5,
        update=lambda self, context: update_modifier(self, context)
    )

    secondary_angle: FloatProperty(
        name="Branch Angle",
        description="Angle of secondary roots from main root",
        default=45.0,
        min=0.0,
        max=90.0,
        update=lambda self, context: update_modifier(self, context)
    )

    # Tertiary Roots
    enable_tertiary_roots: BoolProperty(
        name="Enable Tertiary Roots",
        description="Add tertiary roots",
        default=True,
        update=lambda self, context: update_modifier(self, context)
    )

    tertiary_density: FloatProperty(
        name="Density",
        description="Number of tertiary roots",
        default=15.0,
        min=0.0,
        max=50.0,
        update=lambda self, context: update_modifier(self, context)
    )

    tertiary_length: FloatProperty(
        name="Length",
        description="Length of tertiary roots",
        default=0.3,
        min=0.01,
        max=2.0,
        update=lambda self, context: update_modifier(self, context)
    )

    tertiary_width: FloatProperty(
        name="Width",
        description="Width of tertiary roots",
        default=0.03,
        min=0.001,
        max=0.2,
        update=lambda self, context: update_modifier(self, context)
    )

    # Leaves
    enable_leaves: BoolProperty(
        name="Enable Leaves",
        description="Add leaves at tips",
        default=False,
        update=lambda self, context: update_modifier(self, context)
    )

    leaf_size: FloatProperty(
        name="Leaf Size",
        description="Size of leaves",
        default=0.3,
        min=0.01,
        max=1.0,
        update=lambda self, context: update_modifier(self, context)
    )

def update_modifier(self, context):
    """Update modifier when properties change"""
    obj = context.active_object
    if obj and "Fibonacci Roots" in obj.modifiers:
        obj.modifiers["Fibonacci Roots"].show_viewport = obj.modifiers["Fibonacci Roots"].show_viewport

# ============= GEOMETRY NODES CREATION =============
def create_root_geometry_nodes():
    """Create the geometry nodes tree"""
    tree_name = "FibonacciRootSystem"

    if tree_name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[tree_name])

    node_tree = bpy.data.node_groups.new(name=tree_name, type='GeometryNodeTree')
    nodes = node_tree.nodes
    links = node_tree.links

    nodes.clear()

    # Input/Output
    group_input = nodes.new('NodeGroupInput')
    group_input.location = (-2000, 0)

    group_output = nodes.new('NodeGroupOutput')
    group_output.location = (4500, 0)

    # Define interface
    node_tree.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Add inputs
    inputs = [
        ('Length', 'NodeSocketFloat', 5.0),
        ('Count', 'NodeSocketInt', 5),
        ('Base Width', 'NodeSocketFloat', 0.3),
        ('Noise Scale', 'NodeSocketFloat', 2.0),
        ('Roughness', 'NodeSocketFloat', 0.5),
        ('Fibonacci Angle', 'NodeSocketFloat', 137.5),
        ('Separation', 'NodeSocketFloat', 0.2),
        ('Spread Angle', 'NodeSocketFloat', 30.0),
        ('Growth Direction', 'NodeSocketInt', 0),  # 0=Down, 1=Up, 2=Radial
        ('Individual Growth', 'NodeSocketBool', False),
        ('Growth 1', 'NodeSocketFloat', 1.0),
        ('Growth 2', 'NodeSocketFloat', 1.0),
        ('Growth 3', 'NodeSocketFloat', 1.0),
        ('Growth 4', 'NodeSocketFloat', 1.0),
        ('Growth 5', 'NodeSocketFloat', 1.0),
        ('Enable Secondary', 'NodeSocketBool', True),
        ('Sec Density', 'NodeSocketFloat', 20.0),
        ('Sec Length', 'NodeSocketFloat', 1.0),
        ('Sec Width', 'NodeSocketFloat', 0.08),
        ('Sec Angle', 'NodeSocketFloat', 45.0),
        ('Enable Tertiary', 'NodeSocketBool', True),
        ('Ter Density', 'NodeSocketFloat', 15.0),
        ('Ter Length', 'NodeSocketFloat', 0.3),
        ('Ter Width', 'NodeSocketFloat', 0.03),
        ('Enable Leaves', 'NodeSocketBool', False),
        ('Leaf Size', 'NodeSocketFloat', 0.3),
    ]

    for name, socket_type, default in inputs:
        socket = node_tree.interface.new_socket(name=name, in_out='INPUT', socket_type=socket_type)
        socket.default_value = default

    # === MAIN ROOTS - GROWTH DIRECTION SYSTEM ===
    # Create initial line
    curve_line = nodes.new('GeometryNodeCurvePrimitiveLine')
    curve_line.location = (-1600, 0)
    
    # Growth direction switch nodes
    switch_down = nodes.new('GeometryNodeSwitch')
    switch_down.location = (-1800, -200)
    switch_down.input_type = 'VECTOR'
    
    switch_up = nodes.new('GeometryNodeSwitch')
    switch_up.location = (-1800, -300)
    switch_up.input_type = 'VECTOR'
    
    # Direction vectors
    # DOWN (0): (0, 0, -length)
    negate_length = nodes.new('ShaderNodeMath')
    negate_length.location = (-2000, -200)
    negate_length.operation = 'MULTIPLY'
    links.new(group_input.outputs['Length'], negate_length.inputs[0])
    negate_length.inputs[1].default_value = -1.0
    
    combine_down = nodes.new('ShaderNodeCombineXYZ')
    combine_down.location = (-1900, -200)
    combine_down.inputs['X'].default_value = 0
    combine_down.inputs['Y'].default_value = 0
    links.new(negate_length.outputs['Value'], combine_down.inputs['Z'])
    
    # UP (1): (0, 0, length)
    combine_up = nodes.new('ShaderNodeCombineXYZ')
    combine_up.location = (-1900, -300)
    combine_up.inputs['X'].default_value = 0
    combine_up.inputs['Y'].default_value = 0
    links.new(group_input.outputs['Length'], combine_up.inputs['Z'])
    
    # RADIAL (2): (length, 0, 0) - will be rotated later
    combine_radial = nodes.new('ShaderNodeCombineXYZ')
    combine_radial.location = (-1900, -400)
    links.new(group_input.outputs['Length'], combine_radial.inputs['X'])
    combine_radial.inputs['Y'].default_value = 0
    combine_radial.inputs['Z'].default_value = 0
    
    # Compare growth direction
    compare_down = nodes.new('ShaderNodeMath')
    compare_down.location = (-1700, -150)
    compare_down.operation = 'COMPARE'
    links.new(group_input.outputs['Growth Direction'], compare_down.inputs[0])
    compare_down.inputs[1].default_value = 0.0  # DOWN
    compare_down.inputs[2].default_value = 0.001
    
    compare_up = nodes.new('ShaderNodeMath')
    compare_up.location = (-1700, -250)
    compare_up.operation = 'COMPARE'
    links.new(group_input.outputs['Growth Direction'], compare_up.inputs[0])
    compare_up.inputs[1].default_value = 1.0  # UP
    compare_up.inputs[2].default_value = 0.001
    
    # Switch between directions
    links.new(compare_down.outputs['Value'], switch_down.inputs['Switch'])
    links.new(combine_down.outputs['Vector'], switch_down.inputs['True'])
    links.new(combine_up.outputs['Vector'], switch_down.inputs['False'])
    
    links.new(compare_up.outputs['Value'], switch_up.inputs['Switch'])
    links.new(switch_down.outputs['Output'], switch_up.inputs['False'])
    links.new(combine_radial.outputs['Vector'], switch_up.inputs['True'])
    
    links.new(switch_up.outputs['Output'], curve_line.inputs['End'])
    
    # Resample for smoothness
    resample = nodes.new('GeometryNodeResampleCurve')
    resample.location = (-1400, 0)
    resample.inputs['Count'].default_value = 50
    links.new(curve_line.outputs['Curve'], resample.inputs['Curve'])
    
    # Duplicate for multiple roots
    duplicate = nodes.new('GeometryNodeDuplicateElements')
    duplicate.location = (-1200, 0)
    duplicate.domain = 'SPLINE'
    links.new(resample.outputs['Curve'], duplicate.inputs['Geometry'])
    links.new(group_input.outputs['Count'], duplicate.inputs['Amount'])

    # === FIBONACCI DISTRIBUTION (AFTER DUPLICATION) ===
    # These calculations need to happen after duplication to work per-spline
    index = nodes.new('GeometryNodeInputIndex')
    index.location = (200, -200)
    
    # Convert angles to radians
    to_radians_fib = nodes.new('ShaderNodeMath')
    to_radians_fib.location = (200, -300)
    to_radians_fib.operation = 'RADIANS'
    links.new(group_input.outputs['Fibonacci Angle'], to_radians_fib.inputs[0])
    
    to_radians_spread = nodes.new('ShaderNodeMath')
    to_radians_spread.location = (200, -400)
    to_radians_spread.operation = 'RADIANS'
    links.new(group_input.outputs['Spread Angle'], to_radians_spread.inputs[0])
    
    # Calculate fibonacci angle for each root
    mult_angle = nodes.new('ShaderNodeMath')
    mult_angle.location = (400, -250)
    mult_angle.operation = 'MULTIPLY'
    links.new(index.outputs['Index'], mult_angle.inputs[0])
    links.new(to_radians_fib.outputs['Value'], mult_angle.inputs[1])
    
    # Create radial distribution with spread
    cos_node = nodes.new('ShaderNodeMath')
    cos_node.location = (600, -200)
    cos_node.operation = 'COSINE'
    links.new(mult_angle.outputs['Value'], cos_node.inputs[0])
    
    sin_node = nodes.new('ShaderNodeMath')
    sin_node.location = (600, -300)
    sin_node.operation = 'SINE'
    links.new(mult_angle.outputs['Value'], sin_node.inputs[0])
    
    # Apply spread angle
    mult_cos_spread = nodes.new('ShaderNodeMath')
    mult_cos_spread.location = (800, -200)
    mult_cos_spread.operation = 'MULTIPLY'
    links.new(cos_node.outputs['Value'], mult_cos_spread.inputs[0])
    links.new(to_radians_spread.outputs['Value'], mult_cos_spread.inputs[1])
    
    mult_sin_spread = nodes.new('ShaderNodeMath')
    mult_sin_spread.location = (800, -300)
    mult_sin_spread.operation = 'MULTIPLY'
    links.new(sin_node.outputs['Value'], mult_sin_spread.inputs[0])
    links.new(to_radians_spread.outputs['Value'], mult_sin_spread.inputs[1])
    
    # Combine into vector
    combine_fib = nodes.new('ShaderNodeCombineXYZ')
    combine_fib.location = (1000, -250)
    links.new(mult_cos_spread.outputs['Value'], combine_fib.inputs['X'])
    links.new(mult_sin_spread.outputs['Value'], combine_fib.inputs['Y'])
    combine_fib.inputs['Z'].default_value = 0
    
    # Scale by separation
    scale_sep = nodes.new('ShaderNodeVectorMath')
    scale_sep.location = (1200, -250)
    scale_sep.operation = 'SCALE'
    links.new(combine_fib.outputs['Vector'], scale_sep.inputs[0])
    links.new(group_input.outputs['Separation'], scale_sep.inputs['Scale'])

    # === INDIVIDUAL GROWTH (SIMPLIFIED) ===

    # Get growth values based on index
    modulo = nodes.new('ShaderNodeMath')
    modulo.location = (-1200, -100)
    modulo.operation = 'MODULO'
    links.new(index.outputs['Index'], modulo.inputs[0])
    modulo.inputs[1].default_value = 5.0 # Cycle through 5 growth values

    # Compare nodes to check which root index it is
    compare_0 = nodes.new('ShaderNodeMath')
    compare_0.operation = 'COMPARE'
    compare_0.location = (-800, 150)
    compare_0.inputs[1].default_value = 0.0 # Value2
    compare_0.inputs[2].default_value = 0.001 # Epsilon for exact comparison
    links.new(modulo.outputs['Value'], compare_0.inputs[0])

    compare_1 = nodes.new('ShaderNodeMath')
    compare_1.operation = 'COMPARE'
    compare_1.location = (-800, 100)
    compare_1.inputs[1].default_value = 1.0 # Value2
    compare_1.inputs[2].default_value = 0.001 # Epsilon for exact comparison
    links.new(modulo.outputs['Value'], compare_1.inputs[0])

    compare_2 = nodes.new('ShaderNodeMath')
    compare_2.operation = 'COMPARE'
    compare_2.location = (-800, 50)
    compare_2.inputs[1].default_value = 2.0 # Value2
    compare_2.inputs[2].default_value = 0.001 # Epsilon for exact comparison
    links.new(modulo.outputs['Value'], compare_2.inputs[0])

    compare_3 = nodes.new('ShaderNodeMath')
    compare_3.operation = 'COMPARE'
    compare_3.location = (-800, 0)
    compare_3.inputs[1].default_value = 3.0 # Value2
    compare_3.inputs[2].default_value = 0.001 # Epsilon for exact comparison
    links.new(modulo.outputs['Value'], compare_3.inputs[0])

    compare_4 = nodes.new('ShaderNodeMath')
    compare_4.operation = 'COMPARE'
    compare_4.location = (-800, -50)
    compare_4.inputs[1].default_value = 4.0 # Value2
    compare_4.inputs[2].default_value = 0.001 # Epsilon for exact comparison
    links.new(modulo.outputs['Value'], compare_4.inputs[0])

    # Switch nodes for each growth property
    switch_g1 = nodes.new('GeometryNodeSwitch')
    switch_g1.location = (-600, 150)
    switch_g1.input_type = 'FLOAT'
    links.new(group_input.outputs['Individual Growth'], switch_g1.inputs['Switch'])
    switch_g1.inputs['False'].default_value = 1.0
    links.new(group_input.outputs['Growth 1'], switch_g1.inputs['True'])

    switch_g2 = nodes.new('GeometryNodeSwitch')
    switch_g2.location = (-600, 100)
    switch_g2.input_type = 'FLOAT'
    links.new(group_input.outputs['Individual Growth'], switch_g2.inputs['Switch'])
    switch_g2.inputs['False'].default_value = 1.0
    links.new(group_input.outputs['Growth 2'], switch_g2.inputs['True'])

    switch_g3 = nodes.new('GeometryNodeSwitch')
    switch_g3.location = (-600, 50)
    switch_g3.input_type = 'FLOAT'
    links.new(group_input.outputs['Individual Growth'], switch_g3.inputs['Switch'])
    switch_g3.inputs['False'].default_value = 1.0
    links.new(group_input.outputs['Growth 3'], switch_g3.inputs['True'])

    switch_g4 = nodes.new('GeometryNodeSwitch')
    switch_g4.location = (-600, 0)
    switch_g4.input_type = 'FLOAT'
    links.new(group_input.outputs['Individual Growth'], switch_g4.inputs['Switch'])
    switch_g4.inputs['False'].default_value = 1.0
    links.new(group_input.outputs['Growth 4'], switch_g4.inputs['True'])

    switch_g5 = nodes.new('GeometryNodeSwitch')
    switch_g5.location = (-600, -50)
    switch_g5.input_type = 'FLOAT'
    links.new(group_input.outputs['Individual Growth'], switch_g5.inputs['Switch'])
    switch_g5.inputs['False'].default_value = 1.0
    links.new(group_input.outputs['Growth 5'], switch_g5.inputs['True'])

    # Combine growth values using a series of Mix nodes
    mix_g1_g2 = nodes.new('ShaderNodeMix')
    mix_g1_g2.location = (-400, 100)
    mix_g1_g2.data_type = 'FLOAT'
    links.new(compare_0.outputs['Value'], mix_g1_g2.inputs['Factor'])
    links.new(switch_g1.outputs['Output'], mix_g1_g2.inputs[0])
    links.new(switch_g2.outputs['Output'], mix_g1_g2.inputs[1])

    mix_g3_g4 = nodes.new('ShaderNodeMix')
    mix_g3_g4.location = (-400, 0)
    mix_g3_g4.data_type = 'FLOAT'
    links.new(compare_2.outputs['Value'], mix_g3_g4.inputs['Factor'])
    links.new(switch_g3.outputs['Output'], mix_g3_g4.inputs[0])
    links.new(switch_g4.outputs['Output'], mix_g3_g4.inputs[1])

    mix_g_combined = nodes.new('ShaderNodeMix')
    mix_g_combined.location = (-200, 50)
    mix_g_combined.data_type = 'FLOAT'
    links.new(compare_1.outputs['Value'], mix_g_combined.inputs['Factor'])
    links.new(mix_g1_g2.outputs['Result'], mix_g_combined.inputs[0])
    links.new(mix_g3_g4.outputs['Result'], mix_g_combined.inputs[1])

    final_growth_factor = nodes.new('ShaderNodeMix')
    final_growth_factor.location = (0, 0)
    final_growth_factor.data_type = 'FLOAT'
    links.new(compare_4.outputs['Value'], final_growth_factor.inputs['Factor'])
    links.new(mix_g_combined.outputs['Result'], final_growth_factor.inputs[0])
    links.new(switch_g5.outputs['Output'], final_growth_factor.inputs[1])

    # === ORGANIC NOISE DEFORMATION ===
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-600, -500)
    noise.noise_dimensions = '3D'
    links.new(group_input.outputs['Noise Scale'], noise.inputs['Scale'])
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.7
    
    position = nodes.new('GeometryNodeInputPosition')
    position.location = (-800, -500)
    links.new(position.outputs['Position'], noise.inputs['Vector'])
    
    # Center noise around 0
    subtract = nodes.new('ShaderNodeVectorMath')
    subtract.location = (-400, -500)
    subtract.operation = 'SUBTRACT'
    subtract.inputs[1].default_value = (0.5, 0.5, 0.5)
    links.new(noise.outputs['Color'], subtract.inputs[0])
    
    # Scale noise by roughness and position along spline
    spline_param = nodes.new('GeometryNodeSplineParameter')
    spline_param.location = (-600, -600)
    
    # Reduce noise at base, increase towards tip
    mult_noise_factor = nodes.new('ShaderNodeMath')
    mult_noise_factor.location = (-400, -600)
    mult_noise_factor.operation = 'MULTIPLY'
    links.new(spline_param.outputs['Factor'], mult_noise_factor.inputs[0])
    mult_noise_factor.inputs[1].default_value = 0.8
    
    # Add base noise strength
    add_base_noise = nodes.new('ShaderNodeMath')
    add_base_noise.location = (-200, -600)
    add_base_noise.operation = 'ADD'
    links.new(mult_noise_factor.outputs['Value'], add_base_noise.inputs[0])
    add_base_noise.inputs[1].default_value = 0.2
    
    # Final noise scaling
    scale_noise = nodes.new('ShaderNodeVectorMath')
    scale_noise.location = (-200, -500)
    scale_noise.operation = 'SCALE'
    links.new(subtract.outputs['Vector'], scale_noise.inputs[0])
    links.new(group_input.outputs['Roughness'], scale_noise.inputs['Scale'])

    # === FIBONACCI SPREAD APPLICATION ===
    # Apply fibonacci distribution with spread angle applied during offset calculation
    # This is simpler and more reliable than complex rotation nodes

    # === SET POSITION WITH ALL DEFORMATIONS ===
    add_offsets = nodes.new('ShaderNodeVectorMath')
    add_offsets.location = (600, -250)
    add_offsets.operation = 'ADD'
    links.new(scale_sep.outputs['Vector'], add_offsets.inputs[0])
    links.new(scale_noise.outputs['Vector'], add_offsets.inputs[1])

    # Apply individual growth factor to offset
    scale_offset_by_growth = nodes.new('ShaderNodeVectorMath')
    scale_offset_by_growth.location = (700, -100)
    scale_offset_by_growth.operation = 'SCALE'
    links.new(add_offsets.outputs['Vector'], scale_offset_by_growth.inputs[0])
    links.new(final_growth_factor.outputs['Result'], scale_offset_by_growth.inputs['Scale'])

    # Apply position offsets to each duplicated spline
    set_position = nodes.new('GeometryNodeSetPosition')
    set_position.location = (800, 0)
    links.new(duplicate.outputs['Geometry'], set_position.inputs['Geometry'])
    links.new(scale_offset_by_growth.outputs['Vector'], set_position.inputs['Offset'])

    

    # === TAPERING ===
    set_radius = nodes.new('GeometryNodeSetCurveRadius')
    set_radius.location = (1000, 0)
    links.new(set_position.outputs['Geometry'], set_radius.inputs['Curve'])
    
    # Create taper from base to tip
    spline_param_taper = nodes.new('GeometryNodeSplineParameter')
    spline_param_taper.location = (800, -200)
    
    # Invert for thick base, thin tip
    invert_taper = nodes.new('ShaderNodeMath')
    invert_taper.location = (1000, -200)
    invert_taper.operation = 'SUBTRACT'
    invert_taper.inputs[0].default_value = 1.0
    links.new(spline_param_taper.outputs['Factor'], invert_taper.inputs[1])
    
    # Power for more natural taper
    power_taper = nodes.new('ShaderNodeMath')
    power_taper.location = (1200, -200)
    power_taper.operation = 'POWER'
    links.new(invert_taper.outputs['Value'], power_taper.inputs[0])
    power_taper.inputs[1].default_value = 1.5  # Exponent for taper curve
    
    mult_width = nodes.new('ShaderNodeMath')
    mult_width.location = (1400, -200)
    mult_width.operation = 'MULTIPLY'
    links.new(group_input.outputs['Base Width'], mult_width.inputs[0])
    links.new(power_taper.outputs['Value'], mult_width.inputs[1])
    links.new(mult_width.outputs['Value'], set_radius.inputs['Radius'])
    
    # Convert to mesh
    to_mesh = nodes.new('GeometryNodeCurveToMesh')
    to_mesh.location = (1600, 0)
    
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle.location = (1400, -100)
    circle.inputs['Resolution'].default_value = 8
    links.new(set_radius.outputs['Curve'], to_mesh.inputs['Curve'])
    links.new(circle.outputs['Curve'], to_mesh.inputs['Profile Curve'])

    # === SECONDARY ROOTS - ORGANIC BRANCHING ===
    # Distribute points along the main roots (not just on faces)
    curve_to_points = nodes.new('GeometryNodeCurveToPoints')
    curve_to_points.location = (1600, -400)
    curve_to_points.mode = 'COUNT'
    links.new(set_radius.outputs['Curve'], curve_to_points.inputs['Curve'])
    links.new(group_input.outputs['Sec Density'], curve_to_points.inputs['Count'])
    
    # Random selection for organic distribution
    random_value = nodes.new('FunctionNodeRandomValue')
    random_value.location = (1400, -600)
    random_value.data_type = 'FLOAT'
    random_value.inputs['Min'].default_value = 0.0
    random_value.inputs['Max'].default_value = 1.0
    
    compare_random = nodes.new('ShaderNodeMath')
    compare_random.location = (1600, -600)
    compare_random.operation = 'LESS_THAN'
    links.new(random_value.outputs['Value'], compare_random.inputs[0])
    compare_random.inputs[1].default_value = 0.4  # 40% chance of branch
    
    # Don't branch too close to base or tip
    spline_param_branch = nodes.new('GeometryNodeSplineParameter')
    spline_param_branch.location = (1400, -700)
    
    # Create branching zone (0.2 to 0.8 along spline)
    greater_than = nodes.new('ShaderNodeMath')
    greater_than.location = (1600, -700)
    greater_than.operation = 'GREATER_THAN'
    links.new(spline_param_branch.outputs['Factor'], greater_than.inputs[0])
    greater_than.inputs[1].default_value = 0.2
    
    less_than = nodes.new('ShaderNodeMath')
    less_than.location = (1600, -800)
    less_than.operation = 'LESS_THAN'
    links.new(spline_param_branch.outputs['Factor'], less_than.inputs[0])
    less_than.inputs[1].default_value = 0.8
    
    # Combine conditions
    and_node = nodes.new('FunctionNodeBooleanMath')
    and_node.location = (1800, -700)
    and_node.operation = 'AND'
    links.new(greater_than.outputs['Value'], and_node.inputs[0])
    links.new(less_than.outputs['Value'], and_node.inputs[1])
    
    and_node2 = nodes.new('FunctionNodeBooleanMath')
    and_node2.location = (2000, -650)
    and_node2.operation = 'AND'
    links.new(and_node.outputs['Boolean'], and_node2.inputs[0])
    links.new(compare_random.outputs['Value'], and_node2.inputs[1])
    
    # Create secondary root curves with varying angles
    sec_curve = nodes.new('GeometryNodeCurvePrimitiveLine')
    sec_curve.location = (1800, -400)
    
    # Get tangent at branch points for natural growth direction
    curve_tangent = nodes.new('GeometryNodeInputTangent')
    curve_tangent.location = (1600, -900)
    
    # Mix tangent with normal for branching angle
    normal_sec = nodes.new('GeometryNodeInputNormal')
    normal_sec.location = (1600, -1000)
    
    # Random angle variation
    random_angle = nodes.new('FunctionNodeRandomValue')
    random_angle.location = (1800, -900)
    random_angle.data_type = 'FLOAT'
    random_angle.inputs['Min'].default_value = -0.5
    random_angle.inputs['Max'].default_value = 0.5
    
    # Mix tangent and normal for branch direction
    mix_vectors = nodes.new('ShaderNodeVectorMath')
    mix_vectors.location = (2000, -900)
    mix_vectors.operation = 'ADD'
    links.new(curve_tangent.outputs['Tangent'], mix_vectors.inputs[0])
    links.new(normal_sec.outputs['Normal'], mix_vectors.inputs[1])
    
    # Normalize and scale
    normalize_branch = nodes.new('ShaderNodeVectorMath')
    normalize_branch.location = (2200, -900)
    normalize_branch.operation = 'NORMALIZE'
    links.new(mix_vectors.outputs['Vector'], normalize_branch.inputs[0])
    
    scale_branch_dir = nodes.new('ShaderNodeVectorMath')
    scale_branch_dir.location = (2400, -900)
    scale_branch_dir.operation = 'SCALE'
    links.new(normalize_branch.outputs['Vector'], scale_branch_dir.inputs[0])
    links.new(group_input.outputs['Sec Length'], scale_branch_dir.inputs['Scale'])
    
    # Add some downward tendency
    add_gravity = nodes.new('ShaderNodeVectorMath')
    add_gravity.location = (2600, -900)
    add_gravity.operation = 'ADD'
    links.new(scale_branch_dir.outputs['Vector'], add_gravity.inputs[0])
    add_gravity.inputs[1].default_value = (0, 0, -0.3)
    
    links.new(add_gravity.outputs['Vector'], sec_curve.inputs['End'])
    
    # Instance secondary roots
    instance_sec = nodes.new('GeometryNodeInstanceOnPoints')
    instance_sec.location = (2200, -400)
    links.new(curve_to_points.outputs['Points'], instance_sec.inputs['Points'])
    links.new(sec_curve.outputs['Curve'], instance_sec.inputs['Instance'])
    links.new(and_node2.outputs['Boolean'], instance_sec.inputs['Selection'])
    links.new(curve_to_points.outputs['Rotation'], instance_sec.inputs['Rotation'])
    
    realize_sec = nodes.new('GeometryNodeRealizeInstances')
    realize_sec.location = (2400, -400)
    links.new(instance_sec.outputs['Instances'], realize_sec.inputs['Geometry'])
    
    # Add organic noise to secondary roots
    noise_sec = nodes.new('ShaderNodeTexNoise')
    noise_sec.location = (2400, -600)
    noise_sec.inputs['Scale'].default_value = 5.0
    
    position_sec = nodes.new('GeometryNodeInputPosition')
    position_sec.location = (2200, -600)
    links.new(position_sec.outputs['Position'], noise_sec.inputs['Vector'])
    
    set_pos_sec = nodes.new('GeometryNodeSetPosition')
    set_pos_sec.location = (2600, -400)
    links.new(realize_sec.outputs['Geometry'], set_pos_sec.inputs['Geometry'])
    
    # Taper secondary roots
    set_radius_sec = nodes.new('GeometryNodeSetCurveRadius')
    set_radius_sec.location = (2800, -400)
    links.new(set_pos_sec.outputs['Geometry'], set_radius_sec.inputs['Curve'])
    
    spline_param_sec = nodes.new('GeometryNodeSplineParameter')
    spline_param_sec.location = (2400, -800)
    
    invert_sec = nodes.new('ShaderNodeMath')
    invert_sec.location = (2600, -800)
    invert_sec.operation = 'SUBTRACT'
    invert_sec.inputs[0].default_value = 1.0
    links.new(spline_param_sec.outputs['Factor'], invert_sec.inputs[1])
    
    power_sec = nodes.new('ShaderNodeMath')
    power_sec.location = (2800, -800)
    power_sec.operation = 'POWER'
    links.new(invert_sec.outputs['Value'], power_sec.inputs[0])
    power_sec.inputs[1].default_value = 2.0  # Sharper taper
    
    mult_width_sec = nodes.new('ShaderNodeMath')
    mult_width_sec.location = (3000, -800)
    mult_width_sec.operation = 'MULTIPLY'
    links.new(group_input.outputs['Sec Width'], mult_width_sec.inputs[0])
    links.new(power_sec.outputs['Value'], mult_width_sec.inputs[1])
    links.new(mult_width_sec.outputs['Value'], set_radius_sec.inputs['Radius'])
    
    to_mesh_sec = nodes.new('GeometryNodeCurveToMesh')
    to_mesh_sec.location = (3200, -400)
    
    circle_sec = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle_sec.location = (3000, -500)
    circle_sec.inputs['Resolution'].default_value = 6
    links.new(set_radius_sec.outputs['Curve'], to_mesh_sec.inputs['Curve'])
    links.new(circle_sec.outputs['Curve'], to_mesh_sec.inputs['Profile Curve'])

    # === TERTIARY ROOTS (FINE ROOTS) ===
    # From secondary roots
    curve_to_points_ter = nodes.new('GeometryNodeCurveToPoints')
    curve_to_points_ter.location = (3400, -800)
    curve_to_points_ter.mode = 'COUNT'
    links.new(set_radius_sec.outputs['Curve'], curve_to_points_ter.inputs['Curve'])
    links.new(group_input.outputs['Ter Density'], curve_to_points_ter.inputs['Count'])
    
    # Very thin root curves
    ter_curve = nodes.new('GeometryNodeCurvePrimitiveLine')
    ter_curve.location = (3400, -1000)
    
    # Random directions for hair-like roots
    random_dir = nodes.new('FunctionNodeRandomValue')
    random_dir.location = (3200, -1100)
    random_dir.data_type = 'FLOAT_VECTOR'
    random_dir.inputs['Min'].default_value = (-1, -1, -1)
    random_dir.inputs['Max'].default_value = (1, 1, 0)  # Tend downward
    
    normalize_ter = nodes.new('ShaderNodeVectorMath')
    normalize_ter.location = (3400, -1100)
    normalize_ter.operation = 'NORMALIZE'
    links.new(random_dir.outputs['Value'], normalize_ter.inputs[0])
    
    scale_ter = nodes.new('ShaderNodeVectorMath')
    scale_ter.location = (3600, -1100)
    scale_ter.operation = 'SCALE'
    links.new(normalize_ter.outputs['Vector'], scale_ter.inputs[0])
    links.new(group_input.outputs['Ter Length'], scale_ter.inputs['Scale'])
    links.new(scale_ter.outputs['Vector'], ter_curve.inputs['End'])
    
    instance_ter = nodes.new('GeometryNodeInstanceOnPoints')
    instance_ter.location = (3800, -800)
    links.new(curve_to_points_ter.outputs['Points'], instance_ter.inputs['Points'])
    links.new(ter_curve.outputs['Curve'], instance_ter.inputs['Instance'])
    
    realize_ter = nodes.new('GeometryNodeRealizeInstances')
    realize_ter.location = (4000, -800)
    links.new(instance_ter.outputs['Instances'], realize_ter.inputs['Geometry'])
    
    # Very thin taper
    set_radius_ter = nodes.new('GeometryNodeSetCurveRadius')
    set_radius_ter.location = (4200, -800)
    links.new(realize_ter.outputs['Geometry'], set_radius_ter.inputs['Curve'])
    links.new(group_input.outputs['Ter Width'], set_radius_ter.inputs['Radius'])
    
    to_mesh_ter = nodes.new('GeometryNodeCurveToMesh')
    to_mesh_ter.location = (4400, -800)
    
    circle_ter = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle_ter.location = (4200, -900)
    circle_ter.inputs['Resolution'].default_value = 3
    links.new(set_radius_ter.outputs['Curve'], to_mesh_ter.inputs['Curve'])
    links.new(circle_ter.outputs['Curve'], to_mesh_ter.inputs['Profile Curve'])

    # === LEAVES AT TIPS ===
    # Simple disc leaves at the end of smallest branches
    leaf_mesh = nodes.new('GeometryNodeMeshUVSphere')
    leaf_mesh.location = (3200, 400)
    leaf_mesh.inputs['Segments'].default_value = 8
    leaf_mesh.inputs['Rings'].default_value = 4
    
    # Scale leaves
    scale_leaf = nodes.new('GeometryNodeTransform')
    scale_leaf.location = (3400, 400)
    links.new(leaf_mesh.outputs['Mesh'], scale_leaf.inputs['Geometry'])
    scale_leaf.inputs['Scale'].default_value = (1, 1, 0.3)  # Flat leaves
    
    # Instance leaves on tertiary root endpoints
    endpoint_selection = nodes.new('GeometryNodeInputNamedAttribute')
    endpoint_selection.location = (3600, 300)
    endpoint_selection.data_type = 'FLOAT'
    endpoint_selection.inputs['Name'].default_value = "spline_parameter"
    
    # Select tips using curve parameter
    compare_tips = nodes.new('ShaderNodeMath')
    compare_tips.location = (3800, 300)
    compare_tips.operation = 'GREATER_THAN'
    compare_tips.inputs[1].default_value = 0.95
    
    # Convert curves to points for leaf placement
    curve_to_points_leaves = nodes.new('GeometryNodeCurveToPoints')
    curve_to_points_leaves.location = (4000, 400)
    curve_to_points_leaves.mode = 'EVALUATED'
    links.new(set_radius_ter.outputs['Curve'], curve_to_points_leaves.inputs['Curve'])
    
    instance_leaves = nodes.new('GeometryNodeInstanceOnPoints')
    instance_leaves.location = (4200, 400)
    links.new(curve_to_points_leaves.outputs['Points'], instance_leaves.inputs['Points'])
    links.new(scale_leaf.outputs['Geometry'], instance_leaves.inputs['Instance'])
    instance_leaves.inputs['Scale'].default_value = (0.3, 0.3, 0.3)

    # === SWITCHES FOR FEATURES ===
    switch_secondary = nodes.new('GeometryNodeSwitch')
    switch_secondary.location = (3400, -400)
    switch_secondary.input_type = 'GEOMETRY'
    links.new(group_input.outputs['Enable Secondary'], switch_secondary.inputs['Switch'])
    links.new(to_mesh_sec.outputs['Mesh'], switch_secondary.inputs['True'])
    
    switch_tertiary = nodes.new('GeometryNodeSwitch')
    switch_tertiary.location = (4600, -800)
    switch_tertiary.input_type = 'GEOMETRY'
    links.new(group_input.outputs['Enable Tertiary'], switch_tertiary.inputs['Switch'])
    links.new(to_mesh_ter.outputs['Mesh'], switch_tertiary.inputs['True'])
    
    switch_leaves = nodes.new('GeometryNodeSwitch')
    switch_leaves.location = (4400, 400)
    switch_leaves.input_type = 'GEOMETRY'
    links.new(group_input.outputs['Enable Leaves'], switch_leaves.inputs['Switch'])
    links.new(instance_leaves.outputs['Instances'], switch_leaves.inputs['True'])

    # === FINAL JOIN ===
    join_all = nodes.new('GeometryNodeJoinGeometry')
    join_all.location = (4800, 0)
    links.new(to_mesh.outputs['Mesh'], join_all.inputs['Geometry'])
    links.new(switch_secondary.outputs['Output'], join_all.inputs['Geometry'])
    links.new(switch_tertiary.outputs['Output'], join_all.inputs['Geometry'])
    links.new(switch_leaves.outputs['Output'], join_all.inputs['Geometry'])

    # Merge close vertices
    merge_by_dist = nodes.new('GeometryNodeMergeByDistance')
    merge_by_dist.location = (5000, 0)
    merge_by_dist.inputs['Distance'].default_value = 0.01
    links.new(join_all.outputs['Geometry'], merge_by_dist.inputs['Geometry'])

    links.new(merge_by_dist.outputs['Geometry'], group_output.inputs['Geometry'])

    return node_tree

# ============= OPERATORS =============
class MESH_OT_add_fibonacci_root(Operator):
    """Add a Fibonacci root system"""
    bl_idname = "mesh.add_fibonacci_root_system"
    bl_label = "Add Fibonacci Root System"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create base object
        bpy.ops.mesh.primitive_plane_add(size=0.1, location=(0, 0, 0))
        obj = context.active_object
        obj.name = "Fibonacci_Root_System"
        
        # Check if the object has a mesh data block, if not, create one.
        if obj.data is None:
            obj.data = bpy.data.meshes.new(name="Fibonacci_Root_System_Mesh")

        # Now we can safely clear the geometry
        if hasattr(obj.data, 'clear_geometry'):
            obj.data.clear_geometry()

        # Add modifier
        modifier = obj.modifiers.new(name="Fibonacci Roots", type='NODES')
        modifier.node_group = create_root_geometry_nodes()

        # Update from properties
        MESH_OT_add_fibonacci_root.update_modifier_from_props(modifier, context.scene.fibonacci_roots_props)

        return {'FINISHED'}

    @staticmethod
    def update_modifier_from_props(modifier, props):
        """Update modifier inputs from properties"""
        if not modifier.node_group:
            return

        mapping = {
            'root_length': 'Length',
            'root_count': 'Count',
            'base_width': 'Base Width',
            'noise_scale': 'Noise Scale',
            'roughness': 'Roughness',
            'fibonacci_angle': 'Fibonacci Angle',
            'root_separation': 'Separation',
            'spread_angle': 'Spread Angle',
            'growth_direction': 'Growth Direction',
            'enable_individual_growth': 'Individual Growth',
            'root_growth_1': 'Growth 1',
            'root_growth_2': 'Growth 2',
            'root_growth_3': 'Growth 3',
            'root_growth_4': 'Growth 4',
            'root_growth_5': 'Growth 5',
            'enable_secondary_roots': 'Enable Secondary',
            'secondary_density': 'Sec Density',
            'secondary_length': 'Sec Length',
            'secondary_width': 'Sec Width',
            'secondary_angle': 'Sec Angle',
            'enable_tertiary_roots': 'Enable Tertiary',
            'tertiary_density': 'Ter Density',
            'tertiary_length': 'Ter Length',
            'tertiary_width': 'Ter Width',
            'enable_leaves': 'Enable Leaves',
            'leaf_size': 'Leaf Size'
        }

        for prop_name, socket_name in mapping.items():
            if hasattr(props, prop_name) and socket_name in modifier:
                value = getattr(props, prop_name)
                # Convert growth_direction enum to int
                if prop_name == 'growth_direction':
                    direction_map = {'DOWN': 0, 'UP': 1, 'RADIAL': 2}
                    value = direction_map.get(value, 0)
                modifier[socket_name] = value

class MESH_OT_update_fibonacci_root(Operator):
    """Update the active root system"""
    bl_idname = "mesh.update_fibonacci_root_system"
    bl_label = "Update Root System"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and "Fibonacci Roots" in obj.modifiers

    def execute(self, context):
        obj = context.active_object
        modifier = obj.modifiers["Fibonacci Roots"]
        props = context.scene.fibonacci_roots_props

        MESH_OT_add_fibonacci_root.update_modifier_from_props(modifier, props)

        return {'FINISHED'}

# ============= UI PANELS =============
class VIEW3D_PT_fibonacci_roots(Panel):
    """Main panel"""
    bl_label = "Fibonacci Root Generator"
    bl_idname = "VIEW3D_PT_fibonacci_roots"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        props = context.scene.fibonacci_roots_props

        # Main buttons
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("mesh.add_fibonacci_root_system", icon='ADD')
        row.operator("mesh.update_fibonacci_root_system", icon='FILE_REFRESH')

        obj = context.active_object
        if not (obj and "Fibonacci Roots" in obj.modifiers):
            layout.label(text="Select a Root System", icon='INFO')
            return

        # Main roots
        box = layout.box()
        box.label(text="Main Roots", icon='CURVE_DATA')
        col = box.column(align=True)
        col.prop(props, "root_length")
        col.prop(props, "root_count")
        col.prop(props, "base_width")

        # Growth Direction
        box = layout.box()
        box.label(text="Growth Direction", icon='DRIVER_DISTANCE')
        col = box.column(align=True)
        col.prop(props, "growth_direction", expand=True)
        col.prop(props, "spread_angle")

        # Fibonacci
        box = layout.box()
        box.label(text="Fibonacci Pattern", icon='FORCE_VORTEX')
        col = box.column(align=True)
        col.prop(props, "fibonacci_angle")
        col.prop(props, "root_separation")

        # Deformation
        box = layout.box()
        box.label(text="Organic Deformation", icon='MOD_NOISE')
        col = box.column(align=True)
        col.prop(props, "noise_scale")
        col.prop(props, "roughness")

        # Individual growth
        box = layout.box()
        row = box.row()
        row.prop(props, "enable_individual_growth", text="")
        row.label(text="Individual Growth", icon='GRAPH')

        if props.enable_individual_growth:
            col = box.column(align=True)
            for i in range(1, min(props.root_count + 1, 6)):
                col.prop(props, f"root_growth_{i}", slider=True)

        # Secondary roots
        box = layout.box()
        row = box.row()
        row.prop(props, "enable_secondary_roots", text="")
        row.label(text="Secondary Roots", icon='PARTICLES')

        if props.enable_secondary_roots:
            col = box.column(align=True)
            col.prop(props, "secondary_density")
            col.prop(props, "secondary_length")
            col.prop(props, "secondary_width")
            col.prop(props, "secondary_angle")

            # Tertiary roots (nested)
            box_ter = col.box()
            row_ter = box_ter.row()
            row_ter.prop(props, "enable_tertiary_roots", text="")
            row_ter.label(text="Tertiary Roots", icon='PARTICLES')

            if props.enable_tertiary_roots:
                col_ter = box_ter.column(align=True)
                col_ter.prop(props, "tertiary_density")
                col_ter.prop(props, "tertiary_length")
                col_ter.prop(props, "tertiary_width")


        # Leaves
        box = layout.box()
        row = box.row()
        row.prop(props, "enable_leaves", text="")
        row.label(text="Leaves", icon='OUTLINER_OB_CURVES')

        if props.enable_leaves:
            col = box.column(align=True)
            col.prop(props, "leaf_size")

# ============= MENU FUNCTION =============
def menu_func(self, context):
    self.layout.operator(
        MESH_OT_add_fibonacci_root.bl_idname,
        text="Fibonacci Root System",
        icon='OUTLINER_OB_CURVES'
    )

# ============= REGISTRATION =============
classes = (
    FibonacciRootProperties,
    MESH_OT_add_fibonacci_root,
    MESH_OT_update_fibonacci_root,
    VIEW3D_PT_fibonacci_roots,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.fibonacci_roots_props = PointerProperty(type=FibonacciRootProperties)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    del bpy.types.Scene.fibonacci_roots_props
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Clean up node groups
    if "FibonacciRootSystem" in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups["FibonacciRootSystem"])

