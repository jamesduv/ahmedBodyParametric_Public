#!/bin/bash
#===============================================================================
# Copy the case setup files to the case directory

#Args:
#   $1: the slant angle, include all decimal places
#===============================================================================
angle=$1
system_path="${AHMED_REPO_PUB}/case_setup/system"
constant_path="${AHMED_REPO_PUB}/case_setup/constant"
init_path="${AHMED_REPO_PUB}/case_setup/0"
slurm_path="${AHMED_REPO_PUB}/case_setup/slurm"
case_path="${AHMED_SLANT_PATH}/slant_angle_${angle}"

cp -r $system_path $case_path
cp -r $constant_path $case_path
cp -r $init_path $case_path
cp -r $slurm_path $case_path

# replace ANGLE with ${angle} in slurm files
case_slurm_path="${case_path}/slurm"
rep_str="ANGLE"
for file in $case_slurm_path/*; do
    #echo $file
    sed -i -e "s/${rep_str}/${angle}/g" $file;
done