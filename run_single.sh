#!/bin/bash
# Copyright 2023, Metropolis Technologies, Inc.
# This script is called in orion-evaluation pipeline to run a specific video test 
# with the installed Orion configuration.
# Usage: "./run_single.sh <config_template_directory_path> <video_filename> <video_directory> <orion_configuration_name> <test_early_export? (ON/OFF)> <output_directory>"
# Example: ""./run_single.sh /home/aim/nvme_data/jenkins/workspace/orion-evaluation/orion-evaluation/AB_TESTING_CONFIG_TEMPLATE/camera_2_config /home/aim/nvme_data/AB_TESTING_VIDEOS 771_entry-2022-02-02.mp4 r201_d130_o540_b2 OFF /home/aim/nvme_data/jenkins/workspace/orion-evaluation/orion-evaluation"
# This will then run Orion for the installed configuration and create an orion_data


CONFIG_TEMPLATE_DIR="$1"
VIDEO_DIRECTORY="$2"
VIDEO_FILENAME="$3"
CRITERIA_NAME="$4"
EARLY_EXPORT="$5"
ORION_DATA_DIR="$6"

CONFIG_DIR="/home/aim/nvme_data/jenkins/workspace/orion-evaluation/orion-evaluation/config"
DEBIAN_PACKAGE_DIR="/home/aim/nvme_data/DEBIAN_PACKAGES"

function test_orion()
{
  systemctl stop orion.service
  template_dir=$1
  test_criteria=$2
  test_video=$3
    rm -rf ${CONFIG_DIR}/*
    python3 $PWD/orion-evaluation/scripts/prepare_config.py -d ${VIDEO_DIRECTORY} \
            -v ${test_video} \
            -i ${template_dir} \
            -c ${CONFIG_DIR} \
            -o ${ORION_DATA_DIR}
    echo "Running Orion with early export = OFF for ${test_criteria} on video ${test_video}"
    /usr/share/metropolis/orion ${CONFIG_DIR}
    rm -rf "${ORION_DATA_DIR}/orion_data/videos"
    move_dir="${ORION_DATA_DIR}/${test_criteria}_orion_data_${test_video}"
    mv "${ORION_DATA_DIR}/orion_data" ${move_dir}
    chown -R jenkins ${move_dir}
    chgrp -R jenkins ${move_dir}
}

function test_early_export_orion()
{
  systemctl stop orion.service
  template_dir=$1
  test_criteria=$2
  test_video=$3

    rm -rf ${CONFIG_DIR}/*
    python3 $PWD/orion-evaluation/scripts/prepare_config.py -d ${VIDEO_DIRECTORY} \
            -v ${test_video} \
            -i ${template_dir} \
            -c ${CONFIG_DIR} \
            -o ${ORION_DATA_DIR} -e
    echo "Running Orion with early export = ON for ${test_criteria} on video ${test_video}"
    /usr/share/metropolis/orion ${CONFIG_DIR}
    rm -rf "${ORION_DATA_DIR}/orion_data/videos"
    move_dir="${ORION_DATA_DIR}/${test_criteria}_ee_orion_data_${test_video}"
    mv "${ORION_DATA_DIR}/orion_data" ${move_dir}
    chown -R jenkins ${move_dir}
    chgrp -R jenkins ${move_dir}
}

if [[ "$EARLY_EXPORT" = "ON" ]]; then
    test_early_export_orion ${CONFIG_TEMPLATE_DIR} ${CRITERIA_NAME} ${VIDEO_FILENAME}
elif [[ "$EARLY_EXPORT" = "OFF" ]]; then
    test_orion ${CONFIG_TEMPLATE_DIR} ${CRITERIA_NAME} ${VIDEO_FILENAME}
else
    echo "Early export value: '$EARLY_EXPORT' invalid. Valid: 'ON' or 'OFF'."
fi