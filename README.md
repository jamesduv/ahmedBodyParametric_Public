# ahmedBodyParametric_Public
A collection of python and bash scripts to:
- generate ahmed body .stl geometry files with varying slant angle using GMSH python API
- generate meshes using the OpenFOAM provided version of cfMesh
- scripts to control decomposing the domain, initializing with potentialFoam, and running the simulation using simpleFoam 

The scripts depend upon 2 environment variables:
- $AHMED_REPO_PUB   : location of this repository
- $AHMED_SLANT_PATH : location to generate subdirectories for each case. Note that the run files in case_setup/slurm assume this is located at /home/%u/ahmed_body_slant, update as required.

Contents
----------------

The repo should contain the following files:  

-----------------------------------
    ahmedBodyParametric_Public
    ├── ahmedPatchDist
        ├── Make
            ├── files
            └── options
        ├── ahmedPatchDist.C
        └── createFields.H
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

Notional Workflow for Parallel Computations
----------------
1. Run copy_case_setup.sh. Copies files from case_setup to case_path = ${AHMED_SLANT_PATH}/slant_angle_${ANGLE}, where ANGLE is the script argument.
2. Generate the geometry .stl files using generate_case_geometry_nolegs.py or generate_case_geometry.py.
3. Merge the .stl files and name regions using modify_stl_patch_merge.sh.
4. Generate the mesh, using case_path/slurm/run_mesh.sh.
5. Decompose the mesh, using case_path/slurm/run_decomp.sh. Modify case_path/system/decomposeParDict  and all parallel slurm scripts to have appropriate number of subdomains and settings.
6. Initialize with potential flow solution, increasing stability and convergence, using case_path/slurm/run_potentialFoam_parallel.sh. 
7. Run the simulation, using case_path/slurm/run_simpleFoam_parallel.sh.
8. Post process, must rename case_path/system/controlDict -> case_path/system/controlDict.solve (to retain) and case_path/system/controlDict.postProcess -> case_path/system/controlDict before running case_path/slurm/run_postProcess_parallel.sh.
   
If not running in parallel, omit step 5 and remove mpirun portions of later commands.

Wall Distance from only the Ahmed body
----------------
These simulations are used to train coordinate-based neural networks as part of my research, and model input includes a signed distance of minimum distance function coordinate as additional input. The files within ahmedPatchDist define a utility to compute the wall distance from only the Ahmed body patch (and not all boundaries) using built-in OpenFOAM functionality. To use it, the folder ahmedPatchDist and its contents should be placed in $WM_PROJECT_USER_DIR/applications. It is compiled and linked by navigating to $WM_PROJECT_USER_DIR/applications/ahmedPatchDist and typing wmake. It should then be available from the command line, with the executable placed in $FOAM_USER_APPBIN. To run it on a specific case, navigate to a case_path where a mesh is present, then run the utility by typing ahmedWallDist. If it is not available from the command line ensure $FOAM_USER_APPBIN is in your $PATH.

For more information on writing your own OpenFOAM applications I recommend the excellent courses and tutorials provided by Hakan Nilsson at https://www.tfd.chalmers.se/~hani/kurser/OS_CFD/. 