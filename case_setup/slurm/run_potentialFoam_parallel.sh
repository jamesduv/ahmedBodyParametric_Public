#!/bin/bash

#SBATCH --job-name=ANGLE
#SBATCH --output=/home/%u/ahmed_body_slant/slant_angle_ANGLE/%x-%j_potential.log
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
mpirun -np 120 potentialFoam -case $AHMED_SLANT_PATH/slant_angle_ANGLE -parallel;