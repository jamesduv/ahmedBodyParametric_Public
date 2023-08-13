# ahmedBodyParametric_Public
A collection of python and bash scripts to:
- generate ahmed body .stl geometry files with varying slant angle using GMSH python API
- generate meshes using the OpenFOAM provided version of cfMesh
- scripts to control decomposing the domain, initializing with potentialFoam, and running the simulation using simpleFoam 

The scripts depend upon 2 environment variables:
- $AHMED_REPO_PUB : location of this repository
- $AHMED_SLANT_PATH : location to generate subdirectories for each desired case. Note that the run files in case_setup/slurm assume this is located at /home/%u/ahmed_body_slant.

Contents
----------------

The repo should contain the following files:  

-----------------------------------
    ahmedBodyParametric_Public
    ├── case_setup
        ├── 0
            ├── include
                ├── fixedInlet
                ├── initialConditions
                └── slipSymmetryPatches
            ├── k
            ├── nut
            ├── omega
            ├── P
            └── U
        ├── constant
            ├── transportProperties
            └── turbulenceProperties
        ├── slurm
            ├── run_decomp.sh
            ├── run_mesh.sh
            ├── run_postProcess_parallel.sh
            ├── run_potentialFoam_parallel.sh
            └── run_simpleFoam_parallel.sh
        └── system
            ├── controlDict
            ├── controlDict.postProcess
            ├── createPatchDict
            ├── decomposeParDict
            ├── fvSchemes
            ├── fvSolution
            └── meshDict
    ├── copy_case_setup.sh
    ├── gather_cd.sh
    ├── gather_residuals.sh
    ├── generate_case_geometry.py
    ├── generate_case_geometry_nolegs.py
    ├── generate_case_mesh.sh
    ├── modify_stl_patch_merge.sh
    ├── plot_cd.py
    ├── plot_residuals.py
    ├── README.md
    └── stl_generator_slant_angle.py
-----------------------------------