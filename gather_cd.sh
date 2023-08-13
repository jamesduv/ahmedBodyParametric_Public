#!/bin/bash
################################################################################
# Read the log file and extract cd
# ARGS:
#   $1: angle
# EFFECTS:
#   Make directory $AHMED_SLANT_PATH/slant_angle_${angle}/residuals, with 
#   separate single column .txt files for ux, uy, uz, p, omega, k, continuity
# REQUIRES:
#   log file named as $AHMED_SLANT_PATH/slant_angle_${angle}/*solve.log
################################################################################
angle=$1
case_path="${AHMED_SLANT_PATH}/slant_angle_${angle}"
res_path="${case_path}/residuals"
fn_log="${case_path}/*solve.log"

mkdir -p $res_path
cat $fn_log | grep 'Cd ' | cut -d':' -f2 | cut -f 1 | cut -d' ' -f2 > $res_path/cd.txt
