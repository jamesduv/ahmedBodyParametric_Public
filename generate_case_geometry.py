import sys
import os

from stl_generator_slant_angle import ahmed_stl_generator_v3_sym

def generate_geometry_slant(slant_angle_deg,
                            is_freestream                   = False,
                            gmsh_body_mesh_size             = 2,
                            gmsh_legs_mesh_size             = 2,
                            gmsh_domain_mesh_size           = None,
                            domain_multiplier_width         = 6,
                            domain_multiplier_height        = 3,
                            domain_multiplier_after_body    = 10,
                            domain_multiplier_before_body   = 3,
                            save_path_base                  = os.environ['AHMED_SLANT_PATH'], ):

    gen_args = locals()
    generator = ahmed_stl_generator_v3_sym( **gen_args)

    generator.generate_body()
    generator.body_surface_stl_separate()
    generator.generate_domain()
    generator.generate_legs()


if __name__ == '__main__':
    slant_angle = float(sys.argv[1])
    generate_geometry_slant( slant_angle_deg = slant_angle)