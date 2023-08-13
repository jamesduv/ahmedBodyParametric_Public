# ahmedBodyParametric_Public
A collection of python and bash scripts to:
- generate ahmed body .stl geometry files with varying slant angle using GMSH python API
- generate meshes using the OpenFOAM provided version of cfMesh
- scripts to control decomposing the domain, initializing with potentialFoam, and running the simulation using simpleFoam 

The scripts depend upon 2 environment variables:
- $AHMED_REPO : location of this repository
- $AHMED_SLANT_PATH : location to generate subdirectories for each desired case

Contents
----------------

The repo should contain the following files:  

-----------------------------------
    ahmedBodyParametric_Public
    ├── case_setup
        ├── 0
    ├── generate_case_geometry_nolegs.py
    ├── generate_case_geometry.py
    ├── modify_stl_patch_merge.sh
    ├── README.md
    └── stl_generator_slant_angle.py
-----------------------------------