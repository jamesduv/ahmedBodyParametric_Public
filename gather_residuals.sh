#!/bin/bash
################################################################################
# Read the log file and extract residuals, saving each to a separate file
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
cat $fn_log | grep 'Solving for Ux'     | cut -d' ' -f9 | tr -d ',' > $res_path/ux.txt
cat $fn_log | grep 'Solving for Uy'     | cut -d' ' -f9 | tr -d ',' > $res_path/uy.txt
cat $fn_log | grep 'Solving for Uz'     | cut -d' ' -f9 | tr -d ',' > $res_path/uz.txt
cat $fn_log | grep 'Solving for p'      | cut -d' ' -f9 | tr -d ',' > $res_path/p.txt
cat $fn_log | grep 'sum local '         | cut -d' ' -f9 | tr -d ',' > $res_path/continuity.txt
cat $fn_log | grep 'Solving for omega'  | cut -d' ' -f9 | tr -d ',' > $res_path/omega.txt
cat $fn_log | grep 'Solving for k'      | cut -d' ' -f9 | tr -d ',' > $res_path/k.txt
