#!/bin/bash
#===============================================================================
# Generate the mesh for a single case using cfMesh cartesianMesh

#Args:
#   $1: the slant angle

# Geometry in mm, transformed to m when meshing
# 

#===============================================================================
module load openfoam;
angle=$1;
case_path="${AHMED_SLANT_PATH}/slant_angle_${angle}";

cartesianMesh -case $case_path;
transformPoints -scale "(0.001 0.001 0.001)" -case $case_path;
createPatch -overwrite -case $case_path;
improveSymmetryPlanes -case $case_path;
checkMesh -case $case_path;