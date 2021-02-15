#!/bin/bash

# Script for installing ButterManager
# -----------------------------------
#
# @author: Eloy García Almadén
# @email: eloy.garcia.pca@gmail.com
# -------------------------------------

# Variables
python_bin="python"

# Getting python3 binary
if hash python3 2>/dev/null; then
    python_bin="python3"
fi

# Removing old installations
echo "Removing old installation..."
sudo rm -rf /opt/buttermanager/

# Creating installation directory
echo "Creating installation directory in /opt/buttermanager"
sudo mkdir /opt/buttermanager/
sudo mkdir /opt/buttermanager/buttermanager
sudo mkdir /opt/buttermanager/gui
sudo chown ${USER:=$(/usr/bin/id -run)}:$USER -R /opt/buttermanager

# Copying all the files needed
echo "Copying all the files needed into /opt/buttermanager"
cp -ar ../buttermanager/* /opt/buttermanager/buttermanager
cp -ar ../requirements.txt /opt/buttermanager/
cp -ar ../packaging/buttermanager.svg /opt/buttermanager/gui/

# Creating desktop launcher
echo -e "Creating desktop launcher..."
if [ ! -d "~/.local/share/applications/" ] 
then
    echo "Directory ~/.local/share/applications/ doesn't exist. Creating it to store ButterManager desktop launcher."
    mkdir ~/.local/share/applications/ 
fi
cp ../packaging/buttermanager_venv.desktop ~/.local/share/applications/buttermanager.desktop

# Creating virtual environment
echo "Creating virtual environment..."
cd /opt/buttermanager/
$python_bin -m venv env

# Enabling virtual environment
echo -e "Enabling virtual environment..."
source env/bin/activate

# Installing requirements
echo -e "Installing all the required modules into the virtual environment. Please wait..."
pip install --upgrade pip
pip install -r requirements.txt
echo ""
echo ""
echo '@@@@@@@@@@@@@@@@@@&&&&&&&&&&&&&&&&&&&@@@@@@@@@@@@@+
@@@@@@@@@@@@&&%%#########%%%%%#########%%&&@@@@@@@+
@@@@@@@&&&#((%&&#(/*****************/(%&&%((%&&@@@+
@@@@@@&%(#%#/*****************************/#%##%&@+
@@@@@&#(&(*****************/%%%%/************#%(%&+
@@@@&&##&/***************#%#****%%***********(&(%&+
@@@@@&&#(#%%%%%*******/%%/******#&******%%%%%#(%&&+
@@@@@@@&&&%%(#&*****(%(*******(%#*******&#(%%&&&@@+
@@@@@@@@@@&&(#&**/%%*,.****/%%/*********&##&&@@@@@+
@@@@@@@@@@&&((/(%#**.,.**(%%************&##&&@@@@@+
@@@@@@@@@@&&#%%(****.,,#%/**************&##&&@@@@@+
@@@@@@@@@@&&%/*******%%*****************&##&&@@@@@+
@@@@@@@&&%#(#%%(*/#%(*******************&##&&@@@@@+
@@@@@&%%((((#%&%%%**********************&##&&@@@@@+
@@&&%#(((#%&##&**********************%#*&##&&@@@@@+
&%%((((#&&&&(#&*******************//*%#*&##&&@@@@@+
%#((#%&@@@&&(#&*******************#%*%#*&##&&@@@@@+
@&%%%@@@@@&&(#&///////////////////#%/%#/&##&&@@@@@+
@@@@@@@@@@&&###############################&&@@@@@'
echo ""
echo ""
echo "The installation has finished. Please, review the logs in order to see if everything was OK. Remember that 'python-setuptools' and 'python-virtualenv' packages needs to be installed before executing this script. In addition, if you are on Ubuntu or derivative, 'libxcb-xinerama0' needs to be installed too. Now, you should find a new icon and desktop launcher called ButterManager"
