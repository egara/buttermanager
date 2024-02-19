#!/bin/bash

# Script for installing ButterManager
# -----------------------------------
#
# @author: Eloy García Almadén
# @email: eloy.garcia.pca@gmail.com
# -------------------------------------


# Displaying requirements
echo "You are about to install ButterManager natively."
echo ""
echo "These packages MUST be installed before executing this script: 'python-setuptools' and 'tkinter'. The name of these packages can be different depending on the distro you are using. Example: On Arch -> 'python-setuptools' and 'tk'. On Fedora 'python3-setuptools' and 'python3-tkinter'. In addition, if you are on Ubuntu or derivative, 'libxcb-xinerama0' needs to be installed too."
echo ""
echo "Do you want to proceed with the installation? [y/n]"
read installButterManager

if [[ "$installButterManager" == "y" ]]; then
    # Installing ButterManager
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
    cp -ar ../setup.py /opt/buttermanager/
    cp -ar ../README.md /opt/buttermanager
    cp -ar ../packaging/buttermanager.svg /opt/buttermanager/gui/

    # Creating desktop launcher
    echo -e "Creating desktop launcher..."
    if [ ! -d "~/.local/share/applications/" ] 
    then
        echo "Directory ~/.local/share/applications/ doesn't exist. Creating it to store ButterManager desktop launcher."
        mkdir ~/.local/share/applications/ 
    fi
    cp ../packaging/buttermanager.desktop ~/.local/share/applications/

    # Installing libraries and ButterManager natively
    echo "Installing libraries and ButterManager natively..."
    cd /opt/buttermanager/
    sudo $python_bin setup.py install --record installed_files.txt
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
    echo "The installation has finished. Please, review the logs in order to see if everything was OK"
    echo ""
    echo ""
    echo "You should find a new icon and desktop launcher called ButterManager. You are good to go."
else
    # Exit
    echo "Ok. Bye!"
fi