#!/bin/bash
#===============================================================================
# Copy the case setup files to the case directory

#Args:
#   $1: the slant angle
#===============================================================================
angle=$1
system_path="${AHMED_REPO}/case_setup/system"
constant_path="${AHMED_REPO}/case_setup/constant"
init_path="${AHMED_REPO}/case_setup/0"
slurm_path="${AHMED_REPO}/case_setup/slurm"
case_path="${AHMED_SLANT_PATH}/slant_angle_${angle}"

cp -r $system_path $case_path
cp -r $constant_path $case_path
cp -r $init_path $case_path
cp -r $slurm_path $case_path
