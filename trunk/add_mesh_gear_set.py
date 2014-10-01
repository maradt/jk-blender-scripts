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
    "name": "Involute Gear Set",
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

class AddInvoluteGear(bpy.types.Operator):
    '''Add a gear mesh.'''
    bl_idname = "mesh.primitive_gear_set"
    bl_label = "Add Involute Gear Set"
    bl_options = {'REGISTER', 'UNDO'}

#    pitch_radius1= FloatProperty(name="Pitch Radius 1",
#        description="Pitch Radius 1",
#        min=0.1,
#        max=100,
#        #default=2.1284) # matches gear on Radio shack motor
#        default=17.0)
    base_radius1 = FloatProperty(name="Base Radius 1",
        description="Base Radius 1",
        min=0.1,
        max=100,
        #default=2.1284) # matches gear on Radio shack motor
        default=16.92)
    outside_radius1= FloatProperty(name="Outside Radius 1",
        description="Outside Radius 1",
        min=0.1,
        max=100,
        #default=2.1284) # matches gear on Radio shack motor
        default=18.7)
#    pitch_radius2= FloatProperty(name="Pitch Radius 2",
#        description="Pitch Radius 2",
#        min=0.1,
#        max=100,
#        default=5)    
    pressure_angle =  FloatProperty(name="Pressure Angle",
        description="Pressure Angle",
        min=0.0,
        max=100.0,
        default=20.0)  
    verts_per_tooth = IntProperty(name="Vertices Per Tooth",
        description="Vertices Per Tooth",
        min=8,
        max=200,
        default=10)
    teeth1 = IntProperty(name="Teeth 1",
        description="Number of Teeth 1",
        min=4,
        max=60,
        #default=8) # matches gear on Radio shack motor 
        default=36)  
    teeth2 = IntProperty(name="Teeth 2",
        description="Number of Teeth 2",
        min=4,
        max=60,
        #default=8) # matches gear on Radio shack motor 
        default=24)  
    tooth_thick1=  FloatProperty(name="Tooth Thickness",
        description="Tooth Thickness at Base Circle (radians)",
        min=0.01,
        max=7.0,
        #default=0.7241) # matches gear on Radio shack motor
        #default=0.12) # matches gear on Radio shack motor
        default=0.11708) # matches gear on Radio shack motor
#    backlash =  FloatProperty(name="Backlash",
#        description="Backlash (mili rad)",
#        min=0.0,
#        max=100.0,
#        default=0.0)
#    undercut=  FloatProperty(name="Undercut",
#        description="Undercut",
#        min=0.0,
#        max=5,
#        default=0.1)
#    bevel=  FloatProperty(name="Bevel",
#        description="Bevel Angle",
#        min=0.0,
#        max=45,
#        default=0)
    #rack_b =  BoolProperty(name="Rack",
    #    description="Rack",
    #    default=False)
#    hob_b =  BoolProperty(name="Hob",
#        description="Hob",
#        default=False)
#    cut_b =  BoolProperty(name="Cut",
#        description="Cut",
#        default=False)
    #outside_circle_r1=  FloatProperty(name="Outside Circle Radius 1",
    #    description="Outside Circle Radius 1",
    #    min=1.0,
    #    max=1000,
    #    default=6)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        #box.prop(self, 'pitch_radius1')
        box.prop(self, 'verts_per_tooth')
        box.prop(self, 'teeth1')
        box.prop(self, 'base_radius1')
        box.prop(self, 'outside_radius1')
        box.prop(self, 'tooth_thick1')
        box.prop(self, 'pressure_angle')
        box.prop(self, 'teeth2')
        #box.prop(self, 'bevel')
        #box.prop(self, 'outside_circle_r1')
        #box.prop(self, 'pitch_radius2')
        #box.prop(self, 'backlash')
        #box.prop(self, 'axis_angle')
        #box.prop(self, 'undercut')
        #box.prop(self, 'rack_b')
        #box.prop(self, 'hob_b')
        #box.prop(self, 'cut_b')
        box = layout.box()


    def execute(self, context):
      phi = self.pressure_angle * pi/180
      N1 = self.teeth1
      N2 = self.teeth2
      inc = self.verts_per_tooth
      tooth_thick1 = self.tooth_thick1
      ro1 = self.outside_radius1
      Rb1 = self.base_radius1;
     
      # space width of gear 1 and the pitch 
      #space_width_rad1 = 2*pi - tooth_thick1*N1

#      print('This is inc')
#      print(inc)
#      print('This is N1')
#      print(N1)
#      print('This is base radius 1')
#      print(r_base1)
#      print('This is outside circle radius 1')
#      print(ro1)
#      print('This is tooth thick 1')
      #print(thick_at_base1)

      #bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N1, base_circle_r=Rb1, outside_circle_r=ro1, tooth_thick=tooth_thick1, internal_b=False, bevel_angle=self.bevel*pi/180, undercut=self.undercut);
      bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N1, base_circle_r=Rb1, outside_circle_r=ro1, tooth_thick=tooth_thick1);
      
      bpy.ops.transform.rotate(value=pi/N1,axis=[0,0,1])

      # Radius of pitch circle 
      Ra1 = ((tan(phi) * Rb1)**2 + Rb1**2)**(0.5);
      #print('pi = ', pi);
      print('Ra1 = ', Ra1);
      # Thickness of tooth 1 at pitch circle
      #tooth_thick1a = tooth_thick1 - 2*involute(phi); # radians
      tooth_thick1a = 2*(tooth_thick1/2-involute(phi)) #tooth_thick1 - 2*involute(phi); # radians
      print('Tooth Thickness of Gear 1 at pitch circle in Radians: ', tooth_thick1a);
      # ratio of N1 to N2 dictates ratio of Ra1 Ra2
      GRatio = N2/N1;
      Ra2 = GRatio * Ra1;  # Radius of pitch circle for Gear 2
      Rb2 = (Ra2**2/((tan(phi))**2+1))**0.5;
      print('Rb2 = ', Rb2);
      # Gap between teeth in Gear 1 at pitch circle
      gap1a = 2*pi/N1 - tooth_thick1a; # in radians
      print('Gap Thickness of Gear 1 at pitch circle in Radians: ', gap1a);
      gap1a_ = gap1a * Ra1; # in length
      tooth_thick2a_ =  gap1a_;      # gap thickness one in length is tooth thickness 2 in length on pitch circle (no backlash)
      tooth_thick2a = tooth_thick2a_/Ra2; # tooth thick 2 at pitch circle 
      #print('Tooth Thickness of Gear 2 at pitch circle in Radians: ', tooth_thick2a);
      tooth_thick2  = tooth_thick2a + 2*involute(phi); 
      ro2 = Ra2*1.05;
       
      #tooth_thick2 = self.tooth_thick1;
      #bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N2, base_circle_r=Rb2, outside_circle_r=ro1, tooth_thick=tooth_thick2, internal_b=False, bevel_angle=self.bevel*pi/180, undercut=self.undercut)
      bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N2, base_circle_r=Rb2, outside_circle_r=ro2, tooth_thick=tooth_thick2)
      bpy.ops.transform.rotate(value=pi,axis=[0,0,1])
      bpy.ops.transform.translate(value=(Ra1+Ra2,0,0), constraint_axis=(True,False, False))
      
      bpy.ops.mesh.primitive_circle_add(vertices=72,radius=Ra1,view_align=False, enter_editmode=False, location=(0,0,0), layers=(True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False))
      #N2 = N1 / rp1 * rp2
      #r_base2 = rp2 * cos( phi )
      #r_base2 = rp2 - (ro1 - rp1)

      #tooth_thick2 =  rp1*space_width_rad1/rp2
      #ctooth_thick2 = space_width_rad1*rp1/rp2
      #tooth_thick2 = rp2*ctooth_thick2
      #space_width_rad2 = 2*pi/N2 - tooth_thick2
      
      #thick_at_base2 = 2 *r_base2* ( tooth_thick2 /(2*rp2)  + involute(phi) )
      #tooth_thick2=space_width_rad1;

      #print('N2: ', N2);

      #ro2 = rp2 + (rp1  - r_base1)
      #bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N2, base_circle_r=r_base2, outside_circle_r=ro2, tooth_thick=thick_at_base2/ro2-self.backlash/2000, internal_b=False, bevel_angle=self.bevel*pi/180, undercut=self.undercut)
      #bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N2, base_circle_r=r_base2, outside_circle_r=ro2, tooth_thick=tooth_thick2, internal_b=False, bevel_angle=self.bevel*pi/180, undercut=self.undercut)
      #bpy.ops.transform.translate(value=(rp2+rp1,0,0), constraint_axis=(True,False, False))
      #bpy.ops.transform.rotate(value=(-self.bevel*2*pi/180,),axis=[0,1,0])
     
      #alpha_2 = acos(r_base2/rp2) 
      #theta_2 = (tan(alpha_2)-alpha_2)

      #theta_12b = theta_2 * rp1/rp2

      #bpy.ops.transform.rotate(value=(-(theta_2+theta_12b),),axis=[0,0,1])

#      adden_1 = ro1-rp1
#      deden_1 = rp1 - r_base1
#
#      adden_2 = ro2-rp2
#      deden_2 = rp2 - r_base2
#
#      print('!!!!! GEAR 1 !!!!!')
#      print('thick at base: ', thick_at_base1*rp1)
#      print('!!!!! GEAR 2 !!!!!')
#      print('thick at base: ', thick_at_base2*rp2)

###########################################
###########################################



#      print('!!!!! GEAR 1 !!!!!')
#      print('Pithc Radius 1: ', rp1)
#      print('Addendum Gear 1: ', adden_1);
#      print('Dedendum Gear 1: ', deden_1);
#      print('!!!!! GEAR 2 !!!!!')
#      print('Pithc Radius 2: ', rp2)
#      print('Addendum Gear 2: ', adden_2);
#      print('Dedendum Gear 2: ', deden_2);
#
#      print('bpy.ops.mesh.primitive_involute_gear2(pitch_radius=rp1, pressure_angle=phi, increment=inc, teeth=N1, axis_angle=0, addendum=adden_1, dedendum=deden_1, tooth_thick=tooth_thick1*rp1)')
#      print('bpy.ops.mesh.primitive_involute_gear2(pitch_radius=rp2, pressure_angle=phi, increment=inc, teeth=N2, axis_angle=0, addendum=adden_2, dedendum=deden_2, tooth_thick=tooth_thick2*rp2)')
#      
#      print('bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N1, base_circle_r=r_base1, outside_circle_r=ro1, tooth_thick=thick_at_base1, internal_b=False, bevel_angle=self.bevel*pi/180, undercut=self.undercut)')
#      print('bpy.ops.mesh.primitive_involute_gear(verts_per_tooth=inc, number_of_teeth=N2, base_circle_r=r_base2, outside_circle_r=ro2, tooth_thick=thick_at_base2-self.backlash/1000, internal_b=False, bevel_angle=self.bevel*pi/180, undercut=self.undercut)')
#      if self.cut_b:
#         bpy.ops.mesh.primitive_involute_gear2(pitch_radius=rp1, pressure_angle=phi, increment=inc, teeth=N1, axis_angle=0, addendum=adden_1, dedendum=deden_1, tooth_thick=tooth_thick1*rp1)
#         bpy.ops.mesh.primitive_involute_gear2(pitch_radius=rp2, pressure_angle=phi, increment=inc, teeth=N2, axis_angle=0, addendum=adden_2, dedendum=deden_2, tooth_thick=tooth_thick2*rp2)
#         bpy.ops.transform.translate(value=(rp2+rp1,0,0), constraint_axis=(True,False, False))
#      if self.rack_b:
#         width_cutter = rp1 *tan(space_width_rad1)
#         bpy.ops.mesh.primitive_cutter(addendum=adden_1, dedendum=deden_1, pressure_angle=20, thick=4, width=width_cutter-self.backlash/1000, name="Cutter")
#         #dist_ = 2*pi*rp1/N1
#         pitch_ =2*pi*rp1/N1
#         print('Distance between rack teeth :', pitch_)
#         bpy.ops.object.editmode_toggle()
#         bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(pitch_, 0, 0), "constraint_axis":(True, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
#      if self.hob_b:
#         pitch_ =rp1/N1
#         width_cutter = rp1 *tan(space_width_rad1)
#         bpy.ops.mesh.primitive_hob(addendum=adden_1, dedendum=deden_1, pressure_angle=20, width=width_cutter-self.backlash/1000, helix=0, pitch=pitch_, number_of_teeth=N1, name="Hob")
      return {'FINISHED'}

   
