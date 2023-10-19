#!/bin/bash

#"500_entry_2022-03-09.mp4"

VIDEOS1=("771_entry-2022-02-02.mp4"
         "771_exit-2022-02-02.mp4"
         "846_entry-2022-02-25.mp4"
         "846_exit-2022-02-24.mp4")

CONFIG_BASE="/home/aim/nvme_data/AB_TESTING_CONFIG_TEMPLATE"
CONFIG_DIR="/home/aim/nvme_data/AB_TESTING_CONFIG"
ORION_DATA_DIR="/home/aim/nvme_data/AB_TESTING_ORION"
DEBIAN_PACKAGE_DIR="/home/aim/nvme_data/DEBIAN_PACKAGES"

function install_package()
{
  echo "Installing package $1"
  package="${DEBIAN_PACKAGE_DIR}/$1"
  dpkg -i ${package}
}

function uninstall_package()
{
  echo "Uninstalling package $1"
  dpkg -r $1
}

function test_orion()
{
  systemctl stop orion.service
  template_dir=$1
  test_criteria=$2

  for j in ${!VIDEOS1[@]}; do
    rm -rf ${CONFIG_DIR}/*
    video_file=${VIDEOS1[$j]}
    python3 prepare_config.py -v ${video_file} \
            -i ${template_dir} \
            -o ${CONFIG_DIR}
    echo "Running Orion with early export = OFF for ${test_criteria}"
    /usr/share/metropolis/orion ${CONFIG_DIR}
    rm -rf "${ORION_DATA_DIR}/orion_data/videos"
    move_dir="${ORION_DATA_DIR}/${test_criteria}_orion_data_${video_file}"
    mv "${ORION_DATA_DIR}/orion_data" ${move_dir}
  done
}

function test_early_export_orion()
{
  systemctl stop orion.service
  template_dir=$1
  test_criteria=$2

  for j in ${!VIDEOS1[@]}; do
    rm -rf ${CONFIG_DIR}/*
    video_file=${VIDEOS1[$j]}
    python3 prepare_config.py -v ${video_file} \
            -i ${template_dir} \
            -o ${CONFIG_DIR} -e
    echo "Running Orion with early export = ON for ${test_criteria}"
    /usr/share/metropolis/orion ${CONFIG_DIR}
    rm -rf "${ORION_DATA_DIR}/orion_data/videos"
    move_dir="${ORION_DATA_DIR}/${test_criteria}_ee_orion_data_${video_file}"
    mv "${ORION_DATA_DIR}/orion_data" ${move_dir}
  done
}


# 1 Camera testing
uninstall_package orion-detection-b2-fp16_2.0.1_arm64
uninstall_package orion-detection-b2-fp16_1.3.0_arm64
uninstall_package orion-recognition-b2-stn-fp16_1.3.0_arm64
CONFIG_TEMPLATE_DIR="${CONFIG_BASE}/camera_1_config"

install_package orion-recognition-b1-stn-fp16_1.3.0_arm64.deb
install_package orion-detection-b1-fp16_1.3.0_arm64.deb
install_package orion_5.2.0_arm64.deb

test_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o520_b1"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o520_b1"

install_package orion-detection-b1-fp16_2.0.1_arm64.deb
test_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o520_b1"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o520_b1"

install_package orion_5.1.0_arm64.deb

install_package orion-detection-b1-fp16_1.3.0_arm64.deb
test_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o510_b1"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o510_b1"

install_package orion-detection-b1-fp16_2.0.1_arm64.deb
test_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o510_b1"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o510_b1"


# 2 Camera testing
CONFIG_TEMPLATE_DIR="${CONFIG_BASE}/camera_2_config"
uninstall_package orion-detection-b1-fp16_2.0.1_arm64
uninstall_package orion-detection-b1-fp16_1.3.0_arm64
uninstall_package orion-recognition-b1-stn-fp16_1.3.0_arm64

install_package orion-recognition-b2-stn-fp16_1.3.0_arm64.deb

install_package orion_5.2.0_arm64.deb

install_package orion-detection-b2-fp16_2.0.1_arm64.deb
test_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o520_b2"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o520_b2"

install_package orion-detection-b2-fp16_1.3.0_arm64.deb
test_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o520_b2"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o520_b2"


install_package orion_5.1.0_arm64.deb

install_package orion-detection-b2-fp16_2.0.1_arm64.deb
test_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o510_b2"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d201_o510_b2"

install_package orion-detection-b2-fp16_1.3.0_arm64.deb
test_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o510_b2"
test_early_export_orion ${CONFIG_TEMPLATE_DIR} "r130_d130_o510_b2"










