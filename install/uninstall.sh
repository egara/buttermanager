#!/bin/bash

# Script for uninstalling ButterManager
# -------------------------------------
#
# @author: Eloy García Almadén
# @email: eloy.garcia.pca@gmail.com
# -------------------------------------

# Removing old installations
echo "Removing old installation..."

installed_files=/opt/buttermanager/installed_files.txt

if test -f "$installed_files"; then
    echo "ButterManager was installed natively. Removing libraries..."
    cat $installed_files | xargs sudo rm -rf
fi

sudo rm -rf /opt/buttermanager/
rm ${HOME}/.local/share/applications/buttermanager.desktop

echo "Uninstallation process has been successfully completed. You are good to go!"
