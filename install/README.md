# Installation

## Arch users (or derivatives)
If you are on Arch Linux, Manjaro, EndevourOS, Garuda or any other distribution derived from Arch, ButterManager is in AUR. Just type:

    yay -S buttermanager

> In this example, yay is the package manager installed in the system to manage AUR packages.

## Native Installation
This is the preferred method. It is slimmer because no virtual environment is created in order to execute ButterManager. Just open a terminal and execute:

    git clone https://github.com/egara/buttermanager.git
    cd buttermanager/install
    ./native_install.sh

This installation method will install the dependencies needed in your system natively and create an executable script for running the application. You will be able to execute ButterManager from the terminal typing **buttermanager** or directly via a shortcut created.

## Venv Installation
If the first method doesn't run ButterManager properly, please try this second one. Just open a terminal and type: 

    git clone https://github.com/egara/buttermanager.git
    cd buttermanager/install
    ./venv_install.sh
  
This installation method will create a Python's virtual environment with all the dependencies needed for running ButterManager and create a shortcut to run the application.

# Uninstallation
If you want to remove completely ButterManager, just execute:

    cd buttermanager/install
    ./uninstall.sh