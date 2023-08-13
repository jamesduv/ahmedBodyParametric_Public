import os
import gmsh
import numpy as np

class ahmed_stl_generator_v3_sym():
    def __init__(self,  is_freestream                   = False,
                        slant_angle_deg                 = 5,
                        gmsh_body_mesh_size             = 5,
                        gmsh_legs_mesh_size             = 5,
                        gmsh_domain_mesh_size           = None,
                        domain_multiplier_width         = 20,
                        domain_multiplier_height        = 20,
                        domain_multiplier_after_body    = 25,
                        domain_multiplier_before_body   = 25,
                        save_path_base                  = None ):

        '''Generator for freestream ahmed body, additional stl mesh-fineness 
        controls added for body, front of body, and domain separately.

        All dimensions in millimeters

        ARGS:
            is_freestream           : if True, move body away from ground plane using domain_multiplier_height
            slant_angle_deg         : slant angle in degrees
            gmsh_body_mesh_size     : mesh fineness on body
            gmsh_legs_mesh_size     : mesh fineness on legs
            gmsh_domain_mesh_size   : mesh fineness for domain
            domain_multiplier_width : control domain extent on sides of body
            domain_multiplier_height: control domain extent above, and below if is_freestream = True
            domain_multiplier_after_body    : control domain extent in wake behind body
            domain_multiplier_before_body   : control domain extent in front of body
            save_path_base          : path to directory for saving individual component .stl files 
        '''

        #if freestream, set leg height to 0 so body bottom of body lies on z=0
        if is_freestream:
            self.body_dims          = get_body_dims_mm( slant_angle_deg = slant_angle_deg,
                                                        h_legs      = 0)
        else:
            self.body_dims          = get_body_dims_mm( slant_angle_deg = slant_angle_deg,)
        self.is_freestream          = is_freestream
        self.slant_angle_deg        = slant_angle_deg

        self.gmsh_mesh_size         = gmsh_body_mesh_size   #remove once depricated

        self.gmsh_body_mesh_size    = gmsh_body_mesh_size
        self.gmsh_legs_mesh_size    = gmsh_legs_mesh_size
        self.gmsh_domain_mesh_size  = gmsh_domain_mesh_size
        self.domain_multiplier_before_body = domain_multiplier_before_body
        self.domain_multiplier_after_body  = domain_multiplier_after_body
        self.domain_multiplier_height   = domain_multiplier_height
        self.domain_multiplier_width    = domain_multiplier_width

        self.inlet_x    = -1* (self.body_dims['l_overall'] * (1+domain_multiplier_before_body))
        self.outlet_x   = self.body_dims['l_overall']* domain_multiplier_after_body
        if self.is_freestream:
            self.bottom_z   = -1 * self.body_dims['h_overall'] * domain_multiplier_height
        else:
            self.bottom_z   = 0
        self.top_z      = self.body_dims['h_overall'] * domain_multiplier_height
        self.symmetry_y = 0
        self.side_y     = -0.5 * self.body_dims['w_overall'] * domain_multiplier_width

        if save_path_base is None:
            save_path_base = os.environ['AHMED_SLANT_PATH']

        case_path = os.path.join(save_path_base, 'slant_angle_{:1.2f}'.format(slant_angle_deg))
        save_path   = os.path.join(case_path, 'geometry')
        if not os.path.exists(case_path):
            os.mkdir(case_path)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        self.save_path = save_path

    def generate_domain(self):
        '''Generate and save all domain .stl files'''

        self.generate_inlet()
        self.generate_outlet()
        self.generate_bottom()
        self.generate_top()
        self.generate_symmetry_plane()
        self.generate_side()

    def generate_side(self,):
        '''Generate side wall .stl with domain mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make corner points
        # inlet lower
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z )

        # outlet lower
        p1      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z )

        # outlet upper
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z )

        # inlet upper
        p3      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'slipWallSide.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_symmetry_plane(self,):
        '''Generate symmetry plane .stl with domain mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make corner points
        # inlet lower
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.bottom_z )

        # outlet lower
        p1      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.bottom_z,  )

        # outlet upper
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.top_z,  )

        # inlet upper
        p3      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'symmetryMesh.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_top(self):
        '''Generate top wall .stl with domain mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make corner points
        # inlet inner corner
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.top_z )

        # inlet outer corner
        p1      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        # outlet outer corner
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        # outlet inner corner
        p3      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'slipWallTop.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_bottom(self):
        '''Generate bottom wall .stl with domain mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make corner points
        # inlet inner corner
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.bottom_z )

        # inlet outer corner
        p1      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        # outlet outer corner
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        # outlet inner corner
        p3      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.bottom_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        if self.is_freestream:
            fn_local = 'slipWallBottom.stl'
        else:
            fn_local = 'wallBottom.stl'
        fn_mesh = os.path.join(self.save_path, fn_local)
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_outlet(self):
        '''Generate outlet .stl with domain mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make points
        # lower inner corner
        p0      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.bottom_z )

        # lower outer corner
        p1      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        # upper outer corner
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        # inner upper corner
        p3      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop_outlet  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane_outlet = gmsh.model.occ.add_plane_surface([loop_outlet])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'outletMesh.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_inlet(self):
        '''Generate inlet .stl with domain mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ###make points
        #inlet lower inner corner
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.bottom_z )

        #inlet lower outer corner
        p1      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        #inlet upper outer corner
        p2      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        #inlet inner upper corner
        p3      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.symmetry_y, 
                                            z   = self.top_z, )

        ###make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop_inlet   = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane_inlet  = gmsh.model.occ.add_plane_surface([loop_inlet])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'inletMesh.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_legs(self):
        '''Generate leg .stl with legs mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ahm = self.body_dims
        front_circle_neg = gmsh.model.occ.addCircle(    x   = -(ahm['l_overall'] - ahm['dl_legs_front']), 
                                                    y   = -(0.5*ahm['w_overall'] - ahm['dw_legs_outer']), 
                                                    z   = self.bottom_z,
                                                    r   = ahm['r_legs'])

        front_leg_neg    = gmsh.model.occ.extrude(   dimTags = [(1,front_circle_neg),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['h_legs'] )

        rear_circle_neg = gmsh.model.occ.addCircle( x   = -ahm['dl_legs_back'], 
                                                y   = -(0.5*ahm['w_overall'] - ahm['dw_legs_outer']), 
                                                z   = self.bottom_z,
                                                r   = ahm['r_legs'])

        rear_leg_neg    = gmsh.model.occ.extrude(   dimTags = [(1,rear_circle_neg),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['h_legs'] )

        # get all points, set mesh size
        points = gmsh.model.occ.getEntities(0)
        gmsh.model.occ.mesh.setSize(points, self.gmsh_legs_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)
        fn_mesh = os.path.join( self.save_path, 'wallLegsMesh.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_body(self):
        '''Generate ahmed body mesh components for single case, defined by parameters
        in self.body_dims'''

        ahm = self.body_dims
        
        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        # extrude the body
        llc         = [0, -0.5*ahm['w_overall'], ahm['h_legs']]
        rectangle   = gmsh.model.occ.add_rectangle( x    = llc[0],
                                                    y   = llc[1],
                                                    z   = llc[2],
                                                    dx  = -ahm['l_overall'], 
                                                    dy  = 0.5*ahm['w_overall'])

        body        = gmsh.model.occ.extrude(   dimTags = [(2,rectangle),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['dh_body'] )

        # manually make wedge to cut slant
        if self.slant_angle_deg != 0:
            w0  = gmsh.model.occ.add_point( x   = 0, 
                                            y   = 0, 
                                            z   = ahm['h_overall'],)
            w1  = gmsh.model.occ.add_point( x   = 0, 
                                            y   = 0, 
                                            z   = ahm['h_overall']-ahm['dz_cut'],)

            w2  = gmsh.model.occ.add_point( x   = -ahm['dx_cut'], 
                                            y   = 0, 
                                            z   = ahm['h_overall'],)

            line_w01 = gmsh.model.occ.add_line(w0, w1)
            line_w12 = gmsh.model.occ.add_line(w1, w2)
            line_w20 = gmsh.model.occ.add_line(w2, w0)

            loop_wedge  = gmsh.model.occ.add_curve_loop([line_w01, line_w12, line_w20])
            plane_wedge = gmsh.model.occ.add_plane_surface([loop_wedge])
            wedge_cut   = gmsh.model.occ.extrude(   dimTags     = [(2,plane_wedge)], 
                                                    dx          = 0, 
                                                    dy          = -0.5*ahm['w_overall'], 
                                                    dz          = 0 )
            
            body_cut    = gmsh.model.occ.cut(   objectDimTags   = [body[1]],
                                                toolDimTags     = [wedge_cut[1]],
                                                removeObject    = True,
                                                removeTool      = True      )

        # ### front - top-down cut
        # write both halves of symmetry plane
        # place points 4 and 5 beyond end of body to avoid conincident lines 
        yc_circle = (0.5*ahm['w_overall']) - ahm['r_front']
        cen_yx1   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   = -yc_circle, 
                                                z   = ahm['h_overall'],  )
        cen_yx2   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   = yc_circle, 
                                                z   = ahm['h_overall'], )

        f0      = gmsh.model.occ.add_point( x   = -(ahm['l_overall'] - ahm['r_front']), 
                                            y   = -0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall'], )
        f1      = gmsh.model.occ.add_point( x   = -ahm['l_overall'], 
                                            y   = -yc_circle, 
                                            z   = ahm['h_overall'],  )

        f2      = gmsh.model.occ.add_point( x   = -ahm['l_overall'], 
                                            y   = yc_circle, 
                                            z   = ahm['h_overall'],  )
        f3      = gmsh.model.occ.add_point( x   = -(ahm['l_overall'] - ahm['r_front']), 
                                            y   = 0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall'], )
        f4      = gmsh.model.occ.add_point( x   = -(ahm['l_overall']+1), 
                                            y   = 0.5*ahm['w_overall'],
                                            z   = ahm['h_overall'],  )
        f5      = gmsh.model.occ.add_point( x   = -(ahm['l_overall']+1), 
                                            y   = -0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall'],  )

        # start from f0, create line segments
        line_f01 = gmsh.model.occ.add_circle_arc(f0, cen_yx1, f1)
        line_f12 = gmsh.model.occ.add_line(f1, f2)
        line_f23 = gmsh.model.occ.add_circle_arc(f2, cen_yx2, f3)
        line_f34 = gmsh.model.occ.add_line(f3, f4)
        line_f45 = gmsh.model.occ.add_line(f4, f5)
        line_f50 = gmsh.model.occ.add_line(f5, f0)

        # create loop, plane, volume
        loop_front_top = gmsh.model.occ.add_curve_loop([line_f01, line_f12, line_f23,
                                                        line_f34, line_f45, line_f50])
        plane_front_top = gmsh.model.occ.add_plane_surface([loop_front_top])
        volume_cut_top  = gmsh.model.occ.extrude(   dimTags     = [(2,plane_front_top)], 
                                                    dx          = 0, 
                                                    dy          = 0, 
                                                    dz          = -ahm['h_overall'] )

        # cut 
        body_cut_2    = gmsh.model.occ.cut( objectDimTags   = [body[1]],
                                            toolDimTags     = [volume_cut_top[1]],
                                            removeObject    = True,
                                            removeTool      = True      )

 
        # ### front - side-inward cut
        # draw sketch on -y face, extrude all the way through full body width
        # place points 4 and 5 beyond end of body to avoid conincident lines
        zcen_1 = ahm['h_legs']+ ahm['r_front']
        zcen_2  = ahm['h_overall'] - ahm['r_front']
        y_c2 = -0.5*ahm['w_overall']
        
        
        cen_xz1   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   =  y_c2, 
                                                z   = zcen_1,  )
        cen_xz2   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   = y_c2, 
                                                z   = zcen_2,  )

        s0 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall'] - ahm['r_front']), 
                                        y   = y_c2, 
                                        z   = ahm['h_legs'] )
        s1 = gmsh.model.occ.add_point(  x   = -ahm['l_overall'], 
                                        y   = y_c2, 
                                        z   = zcen_1)
        s2 = gmsh.model.occ.add_point(  x   = -ahm['l_overall'], 
                                        y   = y_c2, 
                                        z   = zcen_2)
        s3 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall'] - ahm['r_front']), 
                                        y   = y_c2, 
                                        z   = ahm['h_overall'])
        s4 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall']+1), 
                                        y   = y_c2, 
                                        z   = ahm['h_overall'] )
        s5 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall']+1), 
                                        y   = y_c2, 
                                        z   = ahm['h_legs'] )

        # #start from s0, create line segments
        line_s01 = gmsh.model.occ.add_circle_arc(s0, cen_xz1, s1)
        line_s12 = gmsh.model.occ.add_line(s1, s2)
        line_s23 = gmsh.model.occ.add_circle_arc(s2, cen_xz2, s3)
        line_s34 = gmsh.model.occ.add_line(s3, s4)
        line_s45 = gmsh.model.occ.add_line(s4, s5)
        line_s50 = gmsh.model.occ.add_line(s5, s0)

        loop_front_side = gmsh.model.occ.add_curve_loop([line_s01, line_s12, line_s23,
                                                        line_s34, line_s45, line_s50])
        plane_front_side = gmsh.model.occ.add_plane_surface([loop_front_side])
        volume_cut_side  = gmsh.model.occ.extrude(  dimTags     = [(2,plane_front_side)], 
                                                    dx          = 0, 
                                                    dy          = ahm['w_overall'], 
                                                    dz          = 0 )

        body_cut_3    = gmsh.model.occ.cut(   objectDimTags   = [body[1]],
                                            toolDimTags     = [volume_cut_side[1]],
                                            removeObject    = True,
                                            removeTool      = True      )

        # get all points, set mesh size
        points = gmsh.model.occ.getEntities(0)
        gmsh.model.occ.mesh.setSize(points, self.gmsh_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)
        fn_vtk = os.path.join( self.save_path, 'body_full.vtk')
        fn_msh = os.path.join( self.save_path, 'body_full.msh')
        gmsh.write(fn_vtk)
        gmsh.write(fn_msh)

        gmsh.finalize()

    def body_surface_stl_separate(self):

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")
        fn_read = os.path.join(self.save_path, 'body_full.msh')

        gmsh.open(fn_read)
        surfaces = gmsh.model.getEntities(2)

        n_surf = len(surfaces)
        for iSurf in np.arange(n_surf):
            gmsh.clear()
            gmsh.open(fn_read)
            volumes = gmsh.model.getEntities(3)
            n_volumes = len(volumes)
            for iVol in np.arange(n_volumes):
                gmsh.model.removeEntities( [volumes[iVol]], recursive=False)

            for iRemove in np.arange(n_surf):
                if iRemove != iSurf:
                    gmsh.model.removeEntities( [surfaces[iRemove]], recursive=True)

            gmsh.model.mesh.generate(2)

            fn_save = os.path.join(self.save_path, 'wallAhmed_{:1.0f}.stl'.format(iSurf))
            gmsh.write(fn_save)
        gmsh.finalize()

########################################################################################################################

class ahmed_stl_generator_v4_nonsym():
    def __init__(self,  slant_angle_deg                 = 5,
                        is_freestream                   = True,
                        gmsh_body_mesh_size             = 5,
                        gmsh_legs_mesh_size             = 5,
                        gmsh_domain_mesh_size           = None,
                        domain_multiplier_width         = 20,
                        domain_multiplier_height        = 20,
                        domain_multiplier_after_body    = 25,
                        domain_multiplier_before_body   = 25,
                        save_path_base                  = None ):

        '''Generator for non-symmetric ahmed body, free-stream or grounded.
        Additional stl mesh-fineness controls added for body, front of body, and domain separately.

        Non-symmetric, freestream generator

        ARGS:
            is_freestream           : if True, move body away from ground plane using domain_multiplier_height
            slant_angle_deg         : slant angle in degrees
            gmsh_body_mesh_size     : mesh fineness on body
            gmsh_legs_mesh_size     : mesh fineness on legs
            gmsh_domain_mesh_size   : mesh fineness for domain
            domain_multiplier_width : control domain extent on sides of body
            domain_multiplier_height: control domain extent above, and below if is_freestream = True
            domain_multiplier_after_body    : control domain extent in wake behind body
            domain_multiplier_before_body   : control domain extent in front of body
            save_path_base          : path to directory for saving individual component .stl files   
        '''
        if is_freestream:
            self.body_dims          = get_body_dims_mm( slant_angle_deg = slant_angle_deg,
                                                        h_legs      = 0)
        else:
            self.body_dims          = get_body_dims_mm( slant_angle_deg = slant_angle_deg,)
        self.is_freestream          = is_freestream
        self.slant_angle_deg        = slant_angle_deg

        self.gmsh_mesh_size         = gmsh_body_mesh_size   #remove once depricated
        self.gmsh_body_mesh_size    = gmsh_body_mesh_size
        self.legs_mesh_size         = gmsh_legs_mesh_size
        self.gmsh_domain_mesh_size  = gmsh_domain_mesh_size
        self.domain_multiplier_before_body = domain_multiplier_before_body
        self.domain_multiplier_after_body  = domain_multiplier_after_body
        self.domain_multiplier_height   = domain_multiplier_height
        self.domain_multiplier_width    = domain_multiplier_width

        self.inlet_x    = -1* (self.body_dims['l_overall'] * (1+domain_multiplier_before_body))
        self.outlet_x   = self.body_dims['l_overall']* domain_multiplier_after_body
        self.bottom_z   = -1 * self.body_dims['h_overall'] * domain_multiplier_height
        self.top_z      = self.body_dims['h_overall'] * domain_multiplier_height
        self.side_y     = self.body_dims['w_overall'] * domain_multiplier_width

        if save_path_base is None:
            save_path_base = os.environ['AHMED_SLANT_PATH']

        case_path = os.path.join(save_path_base, 'slant_angle_{:1.2f}'.format(slant_angle_deg))
        save_path   = os.path.join(case_path, 'geometry')
        if not os.path.exists(case_path):
            os.mkdir(case_path)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        self.save_path = save_path

    def generate_domain(self):
        self.generate_inlet()
        self.generate_outlet()
        self.generate_bottom()
        self.generate_top()
        self.generate_side_positive()
        self.generate_side_negative()

    def generate_side_positive(self,):
        '''Generate side wall .stl with domain mesh size'''
        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make points
        # inlet lower
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z )

        # outlet lower
        p1      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z )

        # outlet upper
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z )

        # inlet upper
        p3      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'slipWallSidePos.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_side_negative(self,):
        '''Generate side wall .stl with domain mesh size'''
        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make points
        # inlet lower
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.bottom_z )

        # outlet lower
        p1      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.bottom_z )

        # outlet upper
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.top_z )

        # inlet upper
        p3      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'slipWallSideNeg.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    
    def generate_top(self):
        '''Generate top wall .stl with domain mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make points
        # inlet negative corner
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.top_z )

        # inlet positive corner
        p1      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        # outlet positive corner
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        # outlet negative corner
        p3      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'slipWallTop.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_bottom(self):
        '''Generate bottom wall .stl with default mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make points
        # inlet negative corner
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.bottom_z )

        # inlet positive corner
        p1      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        # outlet positive corner
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        # outlet negative corner
        p3      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.bottom_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane = gmsh.model.occ.add_plane_surface([loop])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        if self.is_freestream:
            fn_local = 'slipWallBottom.stl'
        else:
            fn_local = 'wallBottom.stl'

        fn_mesh = os.path.join(self.save_path, fn_local)
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_outlet(self):
        '''Generate outlet .stl with domain mesh size'''
        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ### make points
        # lower negative corner
        p0      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.bottom_z )

        # lower positive corner
        p1      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        # upper positive corner
        p2      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        # upper negative corner
        p3      = gmsh.model.occ.add_point( x   = self.outlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.top_z, )

        ### make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop_outlet  = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane_outlet = gmsh.model.occ.add_plane_surface([loop_outlet])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'outletMesh.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_inlet(self):
        '''Generate inlet .stl with domain mesh size'''
        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ###make points
        #inlet lower negative corner
        p0      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.bottom_z )

        #inlet lower positive corner
        p1      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.bottom_z,  )

        #inlet upper positive corner
        p2      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = self.side_y, 
                                            z   = self.top_z,  )

        #inlet upper negative corner
        p3      = gmsh.model.occ.add_point( x   = self.inlet_x, 
                                            y   = -1*self.side_y, 
                                            z   = self.top_z, )

        ###make lines
        line_p01 = gmsh.model.occ.add_line(p0, p1)
        line_p12 = gmsh.model.occ.add_line(p1, p2)
        line_p23 = gmsh.model.occ.add_line(p2, p3)
        line_p30 = gmsh.model.occ.add_line(p3, p0)

        ### make curve loop and plane
        loop_inlet   = gmsh.model.occ.add_curve_loop([line_p01, line_p12, line_p23, line_p30])
        plane_inlet  = gmsh.model.occ.add_plane_surface([loop_inlet])

        #get all points, set mesh size
        if self.gmsh_domain_mesh_size is not None:
            points = gmsh.model.occ.getEntities(0)
            gmsh.model.occ.mesh.setSize(points, self.gmsh_domain_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)

        fn_mesh = os.path.join(self.save_path, 'inletMesh.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_legs(self):
        '''Generate leg .stl with body mesh size'''

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        ahm = self.body_dims
        front_circle_neg = gmsh.model.occ.addCircle(    x   = -(ahm['l_overall'] - ahm['dl_legs_front']), 
                                                    y   = -(0.5*ahm['w_overall'] - ahm['dw_legs_outer']), 
                                                    z   = self.bottom_z,
                                                    r   = ahm['r_legs'])

        front_leg_neg    = gmsh.model.occ.extrude(   dimTags = [(1,front_circle_neg),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['h_legs'] )

        rear_circle_neg = gmsh.model.occ.addCircle( x   = -ahm['dl_legs_back'], 
                                                y   = -(0.5*ahm['w_overall'] - ahm['dw_legs_outer']), 
                                                z   = self.bottom_z,
                                                r   = ahm['r_legs'])

        rear_leg_neg    = gmsh.model.occ.extrude(   dimTags = [(1,rear_circle_neg),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['h_legs'] )


        front_circle_pos = gmsh.model.occ.addCircle(    x   = -(ahm['l_overall'] - ahm['dl_legs_front']), 
                                                    y   = 0.5*ahm['w_overall'] - ahm['dw_legs_outer'], 
                                                    z   = self.bottom_z,
                                                    r   = ahm['r_legs'])

        front_leg_pos    = gmsh.model.occ.extrude(   dimTags = [(1,front_circle_pos),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['h_legs'] )

        rear_circle_pos = gmsh.model.occ.addCircle( x   = -ahm['dl_legs_back'], 
                                                y   = 0.5*ahm['w_overall'] - ahm['dw_legs_outer'], 
                                                z   = self.bottom_z,
                                                r   = ahm['r_legs'])

        rear_leg_pos    = gmsh.model.occ.extrude(   dimTags = [(1,rear_circle_pos),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['h_legs'] )

        #get all points, set mesh size
        points = gmsh.model.occ.getEntities(0)
        gmsh.model.occ.mesh.setSize(points, self.gmsh_legs_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)
        fn_mesh = os.path.join( self.save_path, 'wallLegsMesh.stl')
        gmsh.write(fn_mesh)
        gmsh.finalize()

    def generate_body(self):
        '''Generate an ahmed body mesh components for single case, defined by parameters
        in self.body_dims'''

        ahm = self.body_dims
        
        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")

        #extrude the body
        llc         = [0, -0.5*ahm['w_overall'], ahm['h_legs']]
        rectangle   = gmsh.model.occ.add_rectangle( x    = llc[0],
                                                    y   = llc[1],
                                                    z   = llc[2],
                                                    dx  = -ahm['l_overall'], 
                                                    dy  = ahm['w_overall'])

        body        = gmsh.model.occ.extrude(   dimTags = [(2,rectangle),], 
                                                dx      = 0,
                                                dy      = 0,
                                                dz      = ahm['dh_body'] )

        #manually make wedge
        if self.slant_angle_deg != 0:
            w0  = gmsh.model.occ.add_point( x   = 0, 
                                            y   = -0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall'],)
            w1  = gmsh.model.occ.add_point( x   = 0, 
                                            y   = -0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall']-ahm['dz_cut'],)

            w2  = gmsh.model.occ.add_point( x   = -ahm['dx_cut'], 
                                            y   = -0.5*ahm['w_overall'],
                                            z   = ahm['h_overall'],)

            line_w01 = gmsh.model.occ.add_line(w0, w1)
            line_w12 = gmsh.model.occ.add_line(w1, w2)
            line_w20 = gmsh.model.occ.add_line(w2, w0)

            loop_wedge  = gmsh.model.occ.add_curve_loop([line_w01, line_w12, line_w20])
            plane_wedge = gmsh.model.occ.add_plane_surface([loop_wedge])
            wedge_cut   = gmsh.model.occ.extrude(   dimTags     = [(2,plane_wedge)], 
                                                    dx          = 0, 
                                                    dy          = ahm['w_overall'], 
                                                    dz          = 0 )
            
            body_cut    = gmsh.model.occ.cut(   objectDimTags   = [body[1]],
                                                toolDimTags     = [wedge_cut[1]],
                                                removeObject    = True,
                                                removeTool      = True      )

        # ### front - top-down cut
        # write both halves of symmetry plane
        # place points 4 and 5 beyond end of body to avoid conincident lines 
        yc_circle = (0.5*ahm['w_overall']) - ahm['r_front']
        cen_yx1   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   = -yc_circle, 
                                                z   = ahm['h_overall'],  )
        cen_yx2   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   = yc_circle, 
                                                z   = ahm['h_overall'], )

        f0      = gmsh.model.occ.add_point( x   = -(ahm['l_overall'] - ahm['r_front']), 
                                            y   = -0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall'], )
        f1      = gmsh.model.occ.add_point( x   = -ahm['l_overall'], 
                                            y   = -yc_circle, 
                                            z   = ahm['h_overall'],  )

        f2      = gmsh.model.occ.add_point( x   = -ahm['l_overall'], 
                                            y   = yc_circle, 
                                            z   = ahm['h_overall'],  )
        f3      = gmsh.model.occ.add_point( x   = -(ahm['l_overall'] - ahm['r_front']), 
                                            y   = 0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall'], )
        f4      = gmsh.model.occ.add_point( x   = -(ahm['l_overall']+1), 
                                            y   = 0.5*ahm['w_overall'],
                                            z   = ahm['h_overall'],  )
        f5      = gmsh.model.occ.add_point( x   = -(ahm['l_overall']+1), 
                                            y   = -0.5*ahm['w_overall'], 
                                            z   = ahm['h_overall'],  )

        # #start from f0, create line segments
        line_f01 = gmsh.model.occ.add_circle_arc(f0, cen_yx1, f1)
        line_f12 = gmsh.model.occ.add_line(f1, f2)
        line_f23 = gmsh.model.occ.add_circle_arc(f2, cen_yx2, f3)
        line_f34 = gmsh.model.occ.add_line(f3, f4)
        line_f45 = gmsh.model.occ.add_line(f4, f5)
        line_f50 = gmsh.model.occ.add_line(f5, f0)

        #create loop, plane, volume
        loop_front_top = gmsh.model.occ.add_curve_loop([line_f01, line_f12, line_f23,
                                                        line_f34, line_f45, line_f50])
        plane_front_top = gmsh.model.occ.add_plane_surface([loop_front_top])
        volume_cut_top  = gmsh.model.occ.extrude(   dimTags     = [(2,plane_front_top)], 
                                                    dx          = 0, 
                                                    dy          = 0, 
                                                    dz          = -ahm['h_overall'] )

        #cut 
        body_cut_2    = gmsh.model.occ.cut( objectDimTags   = [body[1]],
                                            toolDimTags     = [volume_cut_top[1]],
                                            removeObject    = True,
                                            removeTool      = True      )

 
        # ### front - side-inward cut
        # draw sketch on -y face, extrude all the way through full body width
        # place points 4 and 5 beyond end of body to avoid conincident lines
        zcen_1 = ahm['h_legs']+ ahm['r_front']
        zcen_2  = ahm['h_overall'] - ahm['r_front']
        y_c2 = -0.5*ahm['w_overall']
        
        
        cen_xz1   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   =  y_c2, 
                                                z   = zcen_1,  )
        cen_xz2   = gmsh.model.occ.add_point(   x   = -(ahm['l_overall'] - ahm['r_front']), 
                                                y   = y_c2, 
                                                z   = zcen_2,  )

        s0 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall'] - ahm['r_front']), 
                                        y   = y_c2, 
                                        z   = ahm['h_legs'] )
        s1 = gmsh.model.occ.add_point(  x   = -ahm['l_overall'], 
                                        y   = y_c2, 
                                        z   = zcen_1)
        s2 = gmsh.model.occ.add_point(  x   = -ahm['l_overall'], 
                                        y   = y_c2, 
                                        z   = zcen_2)
        s3 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall'] - ahm['r_front']), 
                                        y   = y_c2, 
                                        z   = ahm['h_overall'])
        s4 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall']+1), 
                                        y   = y_c2, 
                                        z   = ahm['h_overall'] )
        s5 = gmsh.model.occ.add_point(  x   = -(ahm['l_overall']+1), 
                                        y   = y_c2, 
                                        z   = ahm['h_legs'] )

        # #start from s0, create line segments
        line_s01 = gmsh.model.occ.add_circle_arc(s0, cen_xz1, s1)
        line_s12 = gmsh.model.occ.add_line(s1, s2)
        line_s23 = gmsh.model.occ.add_circle_arc(s2, cen_xz2, s3)
        line_s34 = gmsh.model.occ.add_line(s3, s4)
        line_s45 = gmsh.model.occ.add_line(s4, s5)
        line_s50 = gmsh.model.occ.add_line(s5, s0)

        loop_front_side = gmsh.model.occ.add_curve_loop([line_s01, line_s12, line_s23,
                                                        line_s34, line_s45, line_s50])
        plane_front_side = gmsh.model.occ.add_plane_surface([loop_front_side])
        volume_cut_side  = gmsh.model.occ.extrude(  dimTags     = [(2,plane_front_side)], 
                                                    dx          = 0, 
                                                    dy          = ahm['w_overall'], 
                                                    dz          = 0 )

        body_cut_3    = gmsh.model.occ.cut(   objectDimTags   = [body[1]],
                                            toolDimTags     = [volume_cut_side[1]],
                                            removeObject    = True,
                                            removeTool      = True      )

        #get all points, set mesh size
        points = gmsh.model.occ.getEntities(0)
        gmsh.model.occ.mesh.setSize(points, self.gmsh_mesh_size)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)
        fn_vtk = os.path.join( self.save_path, 'body_full.vtk')
        fn_msh = os.path.join( self.save_path, 'body_full.msh')
        gmsh.write(fn_vtk)
        gmsh.write(fn_msh)

        gmsh.finalize()

    def body_surface_stl_separate(self):

        gmsh.initialize()
        gmsh.clear()
        gmsh.option.setString("Geometry.OCCTargetUnit", "M")
        fn_read = os.path.join(self.save_path, 'body_full.msh')

        gmsh.open(fn_read)
        surfaces = gmsh.model.getEntities(2)

        n_surf = len(surfaces)
        for iSurf in np.arange(n_surf):
            gmsh.clear()
            gmsh.open(fn_read)
            volumes = gmsh.model.getEntities(3)
            n_volumes = len(volumes)
            for iVol in np.arange(n_volumes):
                gmsh.model.removeEntities( [volumes[iVol]], recursive=False)

            for iRemove in np.arange(n_surf):
                if iRemove != iSurf:
                    gmsh.model.removeEntities( [surfaces[iRemove]], recursive=True)

            gmsh.model.mesh.generate(2)

            fn_save = os.path.join(self.save_path, 'wallAhmed_{:1.0f}.stl'.format(iSurf))
            gmsh.write(fn_save)
        gmsh.finalize()

########################################################################################################################

def get_body_dims_mm(   w_overall       = 389,
                        l_overall       = 1044,
                        l_middle        = 640,
                        dl_legs_front   = 202,
                        dl_legs_back    = 372,
                        dw_legs_outer   = 31,
                        r_front         = 100,
                        r_legs          = 15,
                        h_legs          = 50,
                        dh_body         = 288,
                        l_diag          = 222,
                        slant_angle_deg = 25):

    ahm = locals()

    ahm['h_overall'] = ahm['h_legs'] + ahm['dh_body']
    ahm['slang_angle_rad'] = ahm['slant_angle_deg'] * np.pi / 180
    ahm['dx_cut']   = ahm['l_diag'] * np.cos( ahm['slang_angle_rad'])
    ahm['dz_cut']   = ahm['l_diag'] * np.sin( ahm['slang_angle_rad'])
    ahm['p0_z']     = ahm['h_overall'] - ahm['dz_cut']

    return ahm