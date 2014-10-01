# add_mesh_gear.py (c) 2014, John Kollman
#
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
#
# ***** END GPL LICENCE BLOCK *****
"""
bl_info = {
    "name": "Involute Gear",
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

class AddInvoluteGear(bpy.types.Operator):
    '''Add a gear mesh.'''
    bl_idname = "mesh.primitive_involute_gear"
    bl_label = "Add Involute Gear"
    bl_options = {'REGISTER', 'UNDO'}

    verts_per_tooth = IntProperty(name="Vertices Per Tooth",
        description="Vertices Per Tooth",
        min=8,
        max=200,
        default=10)
    number_of_teeth = IntProperty(name="Number of Teeth",
        description="Number of teeth on the gear",
        min=2,
        max=265,
        default=36)
    base_circle_r=  FloatProperty(name="Base Circle Radius",
        description="Base Circle Radius",
        min=0.5,
        max=100,
        default=16.92)
    outside_circle_r=  FloatProperty(name="Outside Circle Radius",
        description="Outside Circle Radius",
        min=1.0,
        max=1000,
        default=18)
    tooth_thick=  FloatProperty(name="Tooth Thickness",
        description="At Base Circle in Radians",
        min=0.0010,
        max=100,
        #default=0.12)
        default=0.11708)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'verts_per_tooth')
        box.prop(self, 'number_of_teeth')
        box.prop(self, 'base_circle_r')
        box.prop(self, 'outside_circle_r')
        box.prop(self, 'tooth_thick')
        box = layout.box()


    def execute(self, context):
      N = self.number_of_teeth
      pntsOnTeeth = 2*ceil(self.verts_per_tooth/2)      # points on teeth if odd, will round up to even
      #pntsPolar = self.gearPointsPolar(N,pntsOnTeeth)

      # get the first point on the base circle
      #theta = self.tooth_thick/2
      Rb = self.base_circle_r
      Ro = self.outside_circle_r
      thick = self.tooth_thick
      pnts=[]
      delta_r = (Ro-Rb)/(pntsOnTeeth/2-1)

      # do 1 tooth, more readable to do 1 tooth 1st then duplicate
      for i in range(int(pntsOnTeeth/2)):
         Ra = Rb + delta_r*i # radius of the point	
         phi = atan(((Ra**2 - Rb**2)**0.5)/Rb)  
         alpha = involute(phi)
         theta = alpha - self.tooth_thick/2 # rotate 1/2 tooth thickness at base + angle for involute
         x = Ra*cos(theta)      # convert to cartesian
         y = Ra*sin(theta)	# convert to cartesian 
         pnts.append([x,y,0])   # append to points
         #pnts.append([x,-y,0])	# other side of tooth
         thick = 2*Ra*(self.tooth_thick/2 - involute(phi))
         pnts.append([x,y+thick,0])	# other side of tooth
         #print('Ra: ', Ra) 
         #print('alpha: ', alpha) 
      
      fcs=[]
      for i in range(int(pntsOnTeeth/2-1)):
         j = i * 2 
         fcs.append([j,j+2,j+1])
         fcs.append([j+2,j+3,j+1])

      nn = len(pnts)
      # duplicate tooth
      #theta_ = 2*pi/N
      for k in range(N-1):
         kk = k + 1;
         theta_ = 2*pi/N*kk
         for i in range(nn):
            x = pnts[i][0]
            y = pnts[i][1]
            theta = theta_ + atan(y/x);
            r = (x**2 + y**2)**0.5
            x2 = r*cos(theta)
            y2 = r*sin(theta)
            pnts.append([x2,y2,0])
      
         for i in range(int(pntsOnTeeth/2-1)):
            j = i * 2 + nn*kk
            fcs.append([j,j+2,j+1])
            fcs.append([j+2,j+3,j+1])
      # done duplicating teeth 
      
      # make center circle
      pnts.append([0,0,0])
      for i in range(N):
         a = i*nn
         b = i*nn +1
         c = len(pnts)-1
         fcs.append([a,b,c])
         a = i*nn + pntsOnTeeth 
         if (i==N-1):
            fcs.append([b,0,c])
         else:
            fcs.append([b,a,c])
     
      
      create_mesh_object(context,pnts,[],fcs,"myGear")
      # assume a pressure angle of 20 degrees
       
      #bpy.ops.mesh.primitive_circle_add(vertices=72,radius=Ra1,view_align=False, enter_editmode=False, location=(0,0,0), layers=(True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False))
 
      return {'FINISHED'}
       

   
