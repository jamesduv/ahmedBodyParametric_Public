#!/bin/bash

#SBATCH --job-name=ANGLE_mesh
#SBATCH --output=/home/%u/ahmed_body_slant/slant_angle_ANGLE/%x-%j_mesh.log
#SBATCH --mail-user=YOUR_EMAIL
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --get-user-env

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=30
#SBATCH --mem-per-cpu=4000m
#SBATCH --time=14:00:00

#SBATCH --account=YOUR_ACCOUNT
#SBATCH --partition=YOUR_PARTITION

module load openfoam;
bash $AHMED_REPO/generate_case_mesh_parallel.sh ANGLE;
