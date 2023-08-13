#!/bin/bash

#SBATCH --job-name=ANGLE
#SBATCH --output=/home/%u/ahmed_body_slant/slant_angle_ANGLE/%x-%j_decompose.log
#SBATCH --mail-user=YOUR_EMAIL
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --get-user-env

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --mem-per-cpu=4000m
#SBATCH --time=14:00:00

#SBATCH --account=YOUR_ACCOUNT
#SBATCH --partition=YOUR_PARTITION

module load openfoam;
decomposePar -case $HOME/ahmed_body_slant/slant_angle_ANGLE;

