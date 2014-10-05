# add_mesh_helical_gear.py (c) 2014, John Kollman
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#  bl_info, name is key! not a comment
# ***** END GPL LICENCE BLOCK *****
"""
bl_info = {
    "name": "Helical Gear",
    "author": "John Kollman",
    "version": (2, 4, 2),
    "blender": (2, 5, 7),
    "api": 35853,
    "location": "View3D > Add > Mesh > Helical Gear ",
    "description": "Adds a mesh Helical Gear to the Add Mesh menu",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Add_Mesh/Add_Gear",
    "tracker_url": "https://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=21732",
    "category": "Add Mesh"}
"""

"""
What was needed to port it from 2.49 -> 2.50 alpha 0?

The basic functions that calculate the geometry (verts and faces) are mostly
unchanged (add_tooth, add_spoke, add_gear)

Also, the vertex group API is changed a little bit but the concepts
are the same:
=========
vertexgroup = ob.vertex_groups.new('NAME_OF_VERTEXGROUP')
vertexgroup.add(vertexgroup_vertex_indices, weight, 'ADD')
=========

Now for some reason the name does not 'stick' and we have to set it this way:
vertexgroup.name = 'NAME_OF_VERTEXGROUP'

Conversion to 2.50 also meant we could simply do away with our crude userK-LM503349/K-LM503310 ZXY
interface.
Just definining the appropriate properties in the AddGear() operator will
display the properties in the Blender GUI with the added benefit of making
it interactive: changing a property will redo the AddGear() operator providing
the user with instant feedback.

Finally we had to convert/throw away some print statements to print functions
as Blender nows uses Python 3.x

The code to actually implement the AddGear() function is mostly copied from
add_mesh_torus() (distributed with Blender).
"""

import bpy
import mathutils
from math import *
from bpy.props import *

def involute(phi):
   return tan(phi)-phi

def create_mesh_object(context, verts, edges, faces, name):
    scene = context.scene
    obj_act = scene.objects.active

    # Create new mesh
    mesh = bpy.data.meshes.new(name)

    # Make a mesh from a list of verts/edges/faces.
    mesh.from_pydata(verts, edges, faces)

    # Update mesh geometry after adding stuff.
    mesh.update()

    #import add_object_utils
    from bpy_extras import object_utils
    return object_utils.object_data_add(context, mesh, operator=None)

class AddHelicalGear(bpy.types.Operator):
    '''Add a gear mesh.'''
    #bl_idname = "mesh.primitive_involute_gear2"
    bl_idname = "mesh.primitive_helical_gear"
    bl_label = "Add Helical Gear"
    bl_options = {'REGISTER', 'UNDO'}

    pitch_radius= FloatProperty(name="Pitch Radius",
        description="Pitch Radius",
        min=0.1,
        max=100,
        default=10)
    pressure_angle =  FloatProperty(name="Pressure Angle",
        description="Pressure Angle",
        min=0.0,
        max=100.0,
        default=20.0)
    increment = IntProperty(name="Increments",
        description="Number of Increments in a Cut",
        min=6,
        max=60,
        default=15)
    teeth = IntProperty(name="Teeth",
        description="Number of Teeth",
        min=4,
        max=60,
        default=13)
    axis_angle = FloatProperty(name="Axis Angle",
        description="Axis Angle",
        min=0.0, 
        max=90.0,
        #default=30.0)
        default=20.0)

    addendum = FloatProperty(name="Addendum",
        description="Addendum",
        min=0.0,
        max=20.0,
        default=1.3)

    dedendum = FloatProperty(name="Dedendum",
        description="Dedendum",
        min=0.0,
        max=20.0,
        default=1.5)

    tooth_thick=  FloatProperty(name="Tooth Thickness",
        description="Circular Tooth Thickness at Pitch Circle (distance)",
        min=0.01,
        max=7.0,
        default=2.6)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'pitch_radius')
        box.prop(self, 'tooth_thick')
        box.prop(self, 'pressure_angle')
        box.prop(self, 'teeth')
        box.prop(self, 'addendum')
        box.prop(self, 'dedendum')
        box.prop(self, 'axis_angle')
        box.prop(self, 'increment')
        box = layout.box()


    def execute(self, context):
      #original_type = bpy.context.area.type
      pi = 3.14159
      rp = self.pitch_radius
      phi = self.pressure_angle * pi/180
      n = self.increment
      n_teeth = self.teeth
      theta = self.axis_angle * pi/180
      a = self.addendum
      b_ = self.dedendum
      ro = rp + a
      # tooth thick in radians
      tooth_thick = self.tooth_thick / rp

      # rotation axis
      #rot_axis = (sin(theta),0,cos(theta))
      rot_axis = (0,0,1.0)

      # points on the two corners of the cutter
    
      sce = context.scene
         
      if (theta) > 0:
         height =1 

#         bpy.ops.mesh.primitive_cone_add(vertices=50, radius=ro-height*tan(theta), depth=ro*tan(theta)-height, cap_end=True, view_align=False, enter_editmode=False, location=(0, 0, -(ro*tan(theta)-height)/2), rotation=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
#         smallcone_name = bpy.context.scene.objects.active.name
#         smallcone = sce.objects.get(smallcone_name)
         #bpy.ops.mesh.primitive_cone_add(vertices=50, radius=ro, depth=ro*tan(theta), cap_end=True, view_align=False, enter_editmode=False, location=(0, 0, -ro*tan(theta)/2), rotation=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

         #bpy.ops.mesh.primitive_cone_add(vertices=50, radius1=ro, radius2=ro-height*tan(theta), depth=height, end_fill_type='NGON', view_align=False, enter_editmode=False, location=(0, 0, height/2), rotation=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
         bpy.ops.mesh.primitive_cylinder_add(vertices=50, radius=ro, depth=4)
         #big_cone = sce.objects.get(bpy.context.scene.objects.active.name);



#         bpy.ops.object.modifier_add(type='BOOLEAN')
#         big_cone.modifiers[0].operation='DIFFERENCE'
#         big_cone.modifiers[0].object=smallcone
#         bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Boolean')
#         big_cone.select = False
#         smallcone.select = True
#         bpy.ops.object.delete(use_global=False)
         
#         big_cone.select = True
#         bpy.ops.transform.translate(value=(0,0,ro*tan(theta)), constraint_axis=(False, False, True))
#         bpy.ops.object.mode_set(mode='EDIT', toggle=True)
         #bpy.ops.mesh.normals_make_consistent(inside=False)
#         bpy.ops.object.mode_set(mode='OBJECT', toggle=True)   

      else:
         bpy.ops.mesh.primitive_cylinder_add(vertices=50, radius=ro, depth=4)

      #for i in bpy.context.scene.objects:  # last one is active
         #print(i.name, i.selected, " ->active object:", bpy.context.scene.objects.active.name)
         #print(i.name,  " ->active object:", bpy.context.scene.objects.active.name)


      blank = sce.objects.get(bpy.context.scene.objects.active.name);
      #blank = sce.objects.get('Cylinder');

#      bpy.ops.mesh.primitive_wedge_add(size_x=p0_x, size_y=p0_y, size_z =0.2 )
#      cutter = sce.objects.get('Wedge');

      # little bigger for backlash
      module_ = 2*rp/n_teeth

      # gap thickness in radians at the pressure circle
      # pitch is module * pi
      space_width_rad = 2*pi/n_teeth - tooth_thick 

      width_cutter = rp *tan(space_width_rad)

      bpy.ops.mesh.primitive_cutter(addendum=a, dedendum=b_, pressure_angle=20, thick=8, width=width_cutter, name="Cutter", helix=12*0)
      #cutter = sce.objects.get('Cutter');
      cutter = sce.objects.get(bpy.context.scene.objects.active.name);

      blank.select = False
      cutter.select = True
      bpy.ops.transform.rotate(value=(-theta),axis=(0,1,0))
      bpy.ops.transform.translate(value=(0,-rp,0), constraint_axis=(False,True, False))

      # maximum amount to move the rack
      a = 1;
      b=-(a+b_)*sin(phi)
      c = (a+b_)**2 /4 - ro**2 - (a+b_)*cos(phi)*rp + rp**2

      s_min = (-b - (b**2 - 4*a*c)**0.5)/(2*a)
      s_max = (-b + (b**2 - 4*a*c)**0.5)/(2*a)


      bpy.ops.transform.translate(value=(s_min,0,0), constraint_axis=(True,False, False))
      
      dx = (s_max-s_min)/n
      dphi=dx/rp;
      for j in range(1,(n_teeth+1)):
      #for j in range(1,3):
         bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) 
         for i in range(1,n+1):
            blank.select = False
            cutter.select = True
#            bpy.context.scene.objects.active= blank
            bpy.ops.transform.translate(value=(dx,0,0), constraint_axis=(True,False, False))
            blank.select = True 
            cutter.select = False
#            bpy.context.scene.objects.active= cutter
            bpy.ops.transform.rotate(value=(dphi),axis=rot_axis)
   
#            blank.select = False
#            cutter.select = False
            bpy.context.scene.objects.active= blank
            bpy.ops.object.modifier_add(type='BOOLEAN')
            blank.modifiers[0].operation='DIFFERENCE'
            blank.modifiers[0].object=cutter
            bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Boolean')
   
            #this redraws so we can see what is happening
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) 


         blank.select = True
         cutter.select = False
         bpy.ops.transform.rotate(value=(-dphi*n),axis=rot_axis)
         bpy.ops.transform.rotate(value=(2*pi/n_teeth),axis=rot_axis)
         blank.select = False 
         cutter.select = True
         bpy.ops.transform.translate(value=(-dx*n,0,0), constraint_axis=(True,False, False))

      bpy.ops.object.delete(use_global=False)
      blank.select = True

      r_base = rp * cos( phi )
      print('Base Radius: ',r_base) 
      #thick_at_base = 2 * r_base *( tooth_thick /(2*rp)  + involute(phi) )
      thick_at_base = 2 * ( tooth_thick /(2)  + involute(phi) )
      print('Tooth Thickness at Base Circle (rad): ',thick_at_base) 
      print('Tooth Thickness at Pitch Circle (rad): ', tooth_thick)
      print('Space Width at Pitch Circle (rad): ', space_width_rad) 

      return {'FINISHED'}

   
