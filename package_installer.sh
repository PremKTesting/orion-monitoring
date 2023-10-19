#!/bin/bash
# Description:
# This script is used to install and uninstall packages to the device.
# 
# Usage:
# This is called in the Jenkins evaluation pipeline before running Orion
# './package_installer.sh <install/uninstall> <debian_package_filename> <debian_package_directory (only for installation)>'
# 
#

FUNCTION="$1"
DEBIAN_PACKAGE_NAME="$2"
DEBIAN_PACKAGE_DIR="$3"

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

if [ "$FUNCTION" = "install" ]; then
  install_package "$DEBIAN_PACKAGE_NAME"
elif [ "$FUNCTION" = "uninstall" ]; then
  uninstall_package "$DEBIAN_PACKAGE_NAME"
else
  echo "Invalid request '$FUNCTION'. Valid: 'install' or 'uninstall'."
  exit 1;
fi

