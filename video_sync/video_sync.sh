#!/bin/bash
# Copyright 2023, Metropolis Technologies, Inc.
DEFAULT_LOCAL_DIR="/home/metro/Videos/evaluation_videos"
sync_from_s3() {
  echo "Syncing with S3"
  check_packages
  CURRENT_AWS_ACCESS_KEY_ID=$(echo $AWS_ACCESS_KEY_ID)
  CURRENT_AWS_SECRET_ACCESS_KEY=$(echo $AWS_SECRET_ACCESS_KEY)
  CURRENT_AWS_DEFAULT_REGION=$(echo $AWS_DEFAULT_REGION)

  NEW_AWS_ACCESS_KEY_ID=${1:-$(echo $AWS_ACCESS_KEY_ID)}
  NEW_AWS_SECRET_ACCESS_KEY=${2:-$(echo $AWS_SECRET_ACCESS_KEY)}
  NEW_AWS_DEFAULT_REGION=${3:-$(echo $AWS_DEFAULT_REGION)}

  S3_DIR=${4:-"s3://metro-ml-data/test_videos/ab-testing-annotated-videos/videos/merged_videos/evaluation_videos"}
  LOCAL_DIR=${5:-"${DEFAULT_LOCAL_DIR}"}
  DRYRUN=${6:-"yes"}

  export AWS_ACCESS_KEY_ID="$NEW_AWS_ACCESS_KEY_ID"
  export AWS_SECRET_ACCESS_KEY="$NEW_AWS_SECRET_ACCESS_KEY"
  export AWS_DEFAULT_REGION="$NEW_AWS_DEFAULT_REGION"
  temp=$(echo $AWS_ACCESS_KEY_ID)

  if [[ $DRYRUN = "yes" ]]; then
    echo "WARNING: Dry Run, changes will not be applied."
    S3_COMMAND="aws s3 sync ${S3_DIR} ${LOCAL_DIR} --dryrun"
    eval $S3_COMMAND
  else
    S3_COMMAND="aws s3 sync ${S3_DIR} ${LOCAL_DIR}"
    eval $S3_COMMAND
  fi
  export AWS_ACCESS_KEY_ID=$CURRENT_AWS_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY=$CURRENT_AWS_SECRET_ACCESS_KEY
  export AWS_DEFAULT_REGION=$CURRENT_AWS_DEFAULT_REGION
}

sync_to_device() {
  check_packages
  DIR_TO_SYNC=${1:-"${DEFAULT_LOCAL_DIR}"}
  DEVICE_USERNAME=${2:-"aim"}
  DEVICE_IP=${3:-""}
  DEVICE_PASSWORD=${4:-""}
  DEVICE_DIR_TO_SYNC=${5:-"/home/aim/nvme_data/AB_TESTING_VIDEOS"}
  RSYNC_COMMAND="sshpass -p ${DEVICE_PASSWORD} \
  rsync -aP -e 'ssh -o StrictHostKeyChecking=no' ${DIR_TO_SYNC}/* \
  ${DEVICE_USERNAME}@${DEVICE_IP}:${DEVICE_DIR_TO_SYNC}/"
  echo "Syncing to device"
  eval $RSYNC_COMMAND
}

run_copy_script() {
  echo "Creating copies on device"
  DEVICE_USERNAME=${1:-"aim"}
  DEVICE_IP=${2-""}
  DEVICE_PASSWORD=${3:-""}
  SCRIPT_NAME=${4:-"create_copies.sh"}
  LOCAL_SCRIPT_PATH=${5:-"/home/jenkins/workspace/sync-videos/orion-evaluation/scripts/video_sync"}
  DEVICE_SCRIPT_PATH=${6:-"/home/aim/nvme_data/"}
  INPUT_DIR=${7:-""}
  COPY_PREFIX=${8:-""}
  RSYNC_COMMAND="sshpass -p ${DEVICE_PASSWORD} rsync -aP -e 'ssh -o \
  StrictHostKeyChecking=no' ${LOCAL_SCRIPT_PATH}/${SCRIPT_NAME} \
  ${DEVICE_USERNAME}@${DEVICE_IP}:${DEVICE_SCRIPT_PATH}/"
  SCRIPT_COMMAND="sshpass -p ${DEVICE_PASSWORD} ssh -o StrictHostKeyChecking=no \
  ${DEVICE_USERNAME}@${DEVICE_IP} \
  bash ${DEVICE_SCRIPT_PATH}/${SCRIPT_NAME} ${INPUT_DIR} ${COPY_PREFIX}"
  REMOVE_COMMAND="sshpass -p ${DEVICE_PASSWORD} ssh -o StrictHostKeyChecking=no \
  ${DEVICE_USERNAME}@${DEVICE_IP} \
  rm -rf ${DEVICE_SCRIPT_PATH}/${SCRIPT_NAME}"
  echo "Copying copy script to device"
  eval $RSYNC_COMMAND
  echo "Running copy script on device"
  eval $SCRIPT_COMMAND
}

check_packages() {
  echo "Checking for required packages..."
  # Check APT Package(s)
  REQUIRED_PKGS=("sshpass")
  for REQUIRED_PKG in ${REQUIRED_PKGS[@]}; do
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
    echo Checking for $REQUIRED_PKG: $PKG_OK
    if [ "" = "$PKG_OK" ]; then
      echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
      sudo apt-get --yes install $REQUIRED_PKG
      echo ""
    else
      echo "$REQUIRED_PKG installed."
      echo ""
    fi
  done

  # Check AWS CLI
  AWS_CLI_VERSION=$(aws --version 2>&1 | cut -d " " -f1 | cut -d "/" -f2)
  if [[ $AWS_CLI_VERSION = "" ]]; then
    apt-get update
    apt-get install -y curl unzip
    cd /tmp && curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip -q awscliv2.zip && ./aws/install && rm -rf ./aws
  else
    echo "AWS CLI: $AWS_CLI_VERSION installed."
  fi
}

"$@"