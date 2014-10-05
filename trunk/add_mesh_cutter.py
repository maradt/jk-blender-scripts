# add_mesh_gear.py (c) 2009, 2010 Michel J. Anders (varkenvarken)
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
    "name": "Cutter",
    "author": "John Kollman",
    "version": (2, 4, 2),
    "blender": (2, 5, 7),
    "api": 35853,
    "location": "View3D > Add > Mesh > Gears ",
    "description": "Adds a mesh Involute Gear to the Add Mesh menu",
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

Conversion to 2.50 also meant we could simply do away with our crude user
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

class AddInvoluteGear(bpy.types.Operator):
    '''Add a gear mesh.'''
    bl_idname = "mesh.primitive_cutter"
    bl_label = "Add Involute Gear"
    bl_options = {'REGISTER', 'UNDO'}

#    edge_length = FloatProperty(name="Edge Length",
#        description="Edge Length",
#        min=0.01,
#        max=2,
#        default=0.3)
    addendum = FloatProperty(name="Addendum",
        description="Addendum",
        min=0.01,
        max=2,
        default=0.603)
    dedendum = FloatProperty(name="Dedendum",
        description="Dedendum",
        min=0.01,
        max=2,
        default=0.603)
    pressure_angle =  FloatProperty(name="Pressure Angle",
        description="Pressure Angle",
        min=0.0,
        max=50,
        default=20)
    thick =  FloatProperty(name="Thickness",
        description="Thickness",
        min=0.01,
        max=10,
        default=0.1)
    width =  FloatProperty(name="Center Width",
        description="Width at Pitch",
        min=0.01,
        max=10,
        default=2.2)
    
    helix =  FloatProperty(name="Helix Angle",
        description="Helix Angle Degrees",
        min=0.0,
        max=90,
        #default=12)
        default=0)

    name = StringProperty(name="Object Name", 
        description="Object Name",
        default="Cutter")
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'pressure_angle')
        box.prop(self, 'width')
        box.prop(self, 'helix')
        box.prop(self, 'addendum')
        box.prop(self, 'dedendum')
        box = layout.box()

    def execute(self, context):
      #PitchDiameter = self.pitch_diameter
      #me.from_pydata(pnts,[],[])
      #N = 20               # number of teeth
      pi = 3.14159
      th = self.thick
      phi = float(self.pressure_angle) * pi/180.0
      pnts = []
      
      b = self.addendum
      a = self.dedendum

#      x = a*sin(phi);
#      y = a*cos(phi);
      x = a*tan(phi)
      y = a
      
      #t = self.tip - 2*x
      helix = self.helix
      m = self.width - 2*x

      x2 = b*tan(phi)
      y2 = b 

      pnts.append([-x,y,-th])
      pnts.append([x2,-y2,-th])
      pnts.append([-x-m-x-x2,-y2,-th])
      pnts.append([-x-m, y,-th])
      
      pnts.append([-x,y,th])
      pnts.append([x2,-y2,th])
      pnts.append([-x-m-x-x2,-y2,th])
      pnts.append([-x-m, y,th])


      print('point 1 : ',[-x,y,-th]);
      print('point 2 : ',[x2,-y2,-th]);

      print('point 3 : ',[-x-m-x-x2,-y2,-th]);
      print('point 4 : ',[-x-m, y,-th]);
#############################################      
#      pnts.append([m/2,y,-th/2])
#      pnts.append([x+m/2+x2,-y2,-th/2])
#      pnts.append([-x-m/2-x2,-y2,-th/2])
#      pnts.append([-m/2, y,-th/2])
      
#      pnts.append([m/2,y,th/2])
#      pnts.append([x+m/2+x2,-y2,th/2])
#      pnts.append([-x-m/2-x2,-y2,th/2])
#      pnts.append([-m/2, y,th/2])
################################################     
#      pnts.append([-x,y,-th/2])
#      pnts.append([x2,-y2,-th/2])
#      pnts.append([-x-m/2,-y2,-th/2])
#      pnts.append([-x-m/2, y,-th/2])
#      
#      pnts.append([-x,y,th/2])
#      pnts.append([x2,-y2,th/2])
#      pnts.append([-x-m/2,-y2,th/2])
#      pnts.append([-x-m/2, y,th/2])
      
      fcs =[]
      fcs.append([3,0,1,2])
      fcs.append([7,4,5,6])
      fcs.append([0,1,5,4])
      fcs.append([1,2,6,5])
      fcs.append([2,3,7,6])
      fcs.append([0,3,7,4])
      
      create_mesh_object(context,pnts,[],fcs,self.name)
      bpy.ops.object.mode_set(mode='EDIT', toggle=True)
      
      bpy.ops.mesh.normals_make_consistent(inside=False)
      
      bpy.ops.object.mode_set(mode='OBJECT', toggle=True)
      rot_axis = (0,1.0,0.0)
      bpy.ops.transform.rotate(value=(pi/180*helix),axis=rot_axis)
      return {'FINISHED'}

   
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

