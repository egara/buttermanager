#!/bin/sh
# Script for snap packaging ButterManager application. It is not related to the code itself
# Home will be /home/user/snap/buttermanager/current
export HOME=$SNAP_USER_DATA
# First, it is necessary to go to the directory where all the code is stored, i.e. /buttermanager
cd $SNAP/buttermanager
# Then, the main file is executed using desktop-launh wrapper
# Please, note that the paths are absolute because this is a snap in classic confinement mode
$SNAP/bin/desktop-launch $SNAP/usr/bin/python3 buttermanager.py
