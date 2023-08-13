#!/bin/bash

#SBATCH --job-name=ANGLE
#SBATCH --output=/home/%u/ahmed_body_slant/slant_angle_ANGLE/%x-%j_solve.log
#SBATCH --mail-user=YOUR_EMAIL
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --get-user-env

#SBATCH --nodes=4
#SBATCH --ntasks-per-node=30
#SBATCH --mem-per-cpu=4000m
#SBATCH --time=14:00:00

#SBATCH --account=YOUR_ACCOUNT
#SBATCH --partition=YOUR_PARTITION

module load openfoam;
mpirun -np 120 simpleFoam -case $HOME/ahmed_body_slant/slant_angle_ANGLE -parallel;