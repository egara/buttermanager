#!/bin/bash

# Script for uninstalling ButterManager
# -------------------------------------
#
# @author: Eloy García Almadén
# @email: eloy.garcia.pca@gmail.com
# -------------------------------------

# Removing old installations
echo "Removing old installation..."
sudo rm -rf /opt/buttermanager/
rm ~/.local/share/applications/buttermanager.desktop
