# ButterManager

---------------------
## IMPORTANT!: Manual intervention for upgrading ButterManager from 2.3-1 to newer version on Arch and derivatives

Sorry, I made a mistake packaging the version **2.3-1** of ButterManager in AUR. The way the application is installed in this version is different because no virtual environment is required anymore. Because of this, I changed PKGBUILD but I introduced a mistake on it. Now, it is fixed in version **2.3-2**, but manual intervention is required for upgrading. First, try to upgrade normally ButterManager using your AUR package manager. You can see some errors:

```
error: failed to commit transaction (conflicting files)
python-pyqt5: /usr/bin/pylupdate5 exists in filesystem
python-pyqt5: /usr/bin/pyrcc5 exists in filesystem
python-pyqt5: /usr/bin/pyuic5 exists in filesystem
Errors occurred, no packages were upgraded.
==> ERROR: 'pacman' failed to install missing dependencies.
==> Missing dependencies:
  -> python-pyaml
  -> python-pyqt5
==> Checking buildtime dependencies...
==> ERROR: Could not resolve all dependencies.
```

This error is due to in the previous package version (2.3-1) this library was installed by Python itself in the system instead of using the version which is in Arch repository (python-pyqt5). Now, this dependency is included from Arch repository (as well as python-pyaml) but it cannot be installed because the files are already in the filesystem (due to the previous installation). Please, move those files to another location (for example home) and try to upgrade again:

```
sudo mv /usr/bin/pylupdate5 ~/
sudo mv /usr/bin/pyrcc5 ~/
sudo mv /usr/bin/pyuic5 ~/
```

Now, another error can rise:

```
error: failed to commit transaction (conflicting files)
buttermanager: /usr/bin/buttermanager exists in filesystem
Errors occurred, no packages were upgraded.
==> WARNING: Failed to install built package(s).
```

You have to remove this file:

```
sudo rm /usr/bin/buttermanager
```

Try again, and now the upgrading should work. After installation, run ButterManager and see if everything works OK. Again, sorry for the inconveniences. This error shouldn't appear anymore. Thanks to **Solomon Choina** and **Grey Christoforo** for the feedback. Thanks to them I have realized that the PKGBUILD file was wrong and I could fix it.

---------------------

## Summary ##
ButterManager is a BTRFS tool for managing snapshots, balancing filesystems and upgrading the system safetly.

## Version ##
2.4

## Caveats ##
- For using ButterManager, it is important to have a **good BTRFS structure in your filesystem**. If you want some tips and more information, you can [read
this](https://github.com/egara/arch-btrfs-installation).

- ButterManager works with **Debian**, **Ubuntu / derivatives (Linux Mint, KDE Neon, ElementaryOS, Zorin, Deepin...)**, **OpenSUSE / SUSE**, **RHEL / Fedora** and **Arch Linux** so far.

## Main Functionalities ##

### Managing snapshots ###
You will be able to define all the subvolumes you want to create snapshots and the path for their storage. Then, using ButterManager you will create and delete snapshots of those subvolumes at your will.

### Integration with GRUB ###
ButterManager is integrated with [grub-btrfs](https://github.com/Antynea/grub-btrfs) and you will be able to boot your system from any snapshot directly from the GRUB menu.

### Balancing BTRFS filesystems ###
As new snapshots are created in the system, the free space of the filesystem decreases and it is necessary to perform a system balancing regularly. With ButterManager you can perform these balances at any time and visualize the real space that is occupied.

### Upgrading the system ###
You will be able to upgrade your system and create new snapshots automatically when this operation is performed. Doing so, if something goes wrong, you will have a snapshot before the upgrade you can use to go back. You will be able to set the maximum number of snapshots in your system and ButterManager will maintain this number with every upgrade.

### Saving the logs ###
Everytime your system is upgraded using ButterManager, you could save the log indepently. This way, you would be able to see the packages that have been updated in every snapshot if you wish.

## Installation ##
You can install ButterManager in different ways.

### From the source code ###
In order to install ButterManager manually, you have to install these packages (all the packages described below are for **Arch Linux**. Please, take into account that maybe the name is different in your distribution and you have to install them for python3 version):

- Python 3
- **python-setuptool** (f.i. the name of the package in Ubuntu is **python3-setuptools**).
- **python-virtualenv** (f.i. the name of the package in Ubuntu is **python3-venv**). This package will only be needed if you use **venv_install.sh** script (see below).
- **grub-btrfs**. Please, go to its GitHub repository [https://github.com/Antynea/grub-btrfs](https://github.com/Antynea/grub-btrfs) and follow the instructions to install it if the package is not in the official repository of your distribution.
- **libxinerama**: This depency has been reported by some users (thanks Adam!) who install ButterManager on Ubuntu 20.04 (proper) (the name of the package in Ubuntu is **libxcb-xinerama0**)
- **tk** (f.i. the name of the package in Ubuntu is **python3-tk**)

Once you meet all the requirements, follow these steps:

1. Clone the repository (install **git** if it is needed first)

  ```
    git clone https://github.com/egara/buttermanager.git

  ```

1. Install ButterManager using one of the following installation scripts:
	1. **Native Installation**: This is the preferred method. It is slimmer because no virtual environment is created in order to execute ButterManager. This installation method will install the dependencies needed in your system natively and create an executable script for running the application. You will be able to execute ButterManager from the terminal typing **buttermanager** or directly via a shortcut created. In order to install ButterManager just open a terminal and execute:

    ```
      cd buttermanager
      cd install
      ./native_install.sh
      
    ```

	1. **Venv Installation**: If the first method doesn't run ButterManager properly, please try this second one. The installation process will create a virtual environment with all the dependencies needed and a desktop launcher to run ButterManager directly. In order to install ButterManager just open a terminal and type:

    ```
      cd buttermanager
      cd install
      ./venv_install.sh
    ```  

1. If you want to uninstall ButterManager:

  ```
    cd buttermanager
    cd install
    ./uninstall.sh
  ```

### From AUR ###
If you are an Arch Linux user or your distribution is a derivative (Manjaro, EndevourOS...), ButterManager is in AUR. Depending on your package manager for AUR, type:

    yaourt -S buttermanager

Or

    trizen -S buttermanager

Or

    yay -S buttermanager

Those are only examples. Use the package manager you have installed for AUR. Once ButterManager is installed, you will be able to run it using the icon created in the main menu.

## Changelog

### Version 2.4
- Delete log icon button fixed.
- Issue #28 fixed. There is an error for Plasma Desktop (and PyQT5) when the file explorer is opened and the user tries to select a directory when setting subvolumes up. Only for this case, TK will be used as workaround.
- 'Don't remove snapshots' and 'Snapshots to keep' parameters are not global anymore. The user will be able to configure them per subvolume.
- Now, when user deletes a specific snapshot, the log related to it will be removed too if it exists.

### Version 2.3
- Thanks to Fedora guys (Neal Gompa @Conan-Kudo and Michel Alexandre Salim @michel-slm) ButterManager has been restructured in order to be packaged for Fedora. Because of that, now the application won't need to be installed within a virtual environment so the package installation footprint will be very much smaller.
- Two new installation methods have been created for users who wants to install ButterManager from source code: [native and venv](https://github.com/egara/buttermanager/tree/master/install). The first one is the recommended but the second one is still supported just in case native installation doesn't work properly.
- Issue #26 fixed: Now, the **Upgrade with snapshots** button creates snapshots and removes the old ones if needed.
- All the fast action buttons are disabled when a critical operation is executing.

### Version 2.2
- More stability. Some bugs have been fixed and ButterManager should not crashed after upgrading the system.
- Other operations are now Fast actions.
- New fast actions implemented: Upgrade system with/without snapshots and Take snapshots.

### Version 2.1
- Delete icon has been redesigned.
- New button to open a file explorer within a specific snapshot has been implemented.
- New feature to calculate differences between current snapshot and a specified one has been implemented.
- User will be able to calculate full differences (it will take some time to complete) included files modified and files only present in one of the snapshots.
- User will be able to calculate partial differences that will be faster but it will only inlcude files modified.

### Version 2.0
- Now, the installer creates ~/.local/share/applications directory if it didn't exist in order to allocate the ButterManager desktop launcher.
- The method of calculating the default original subvolume to consolidate the system has been reimplemented and improved to avoid some bugs detected.
- Now, the allocation of the original snapshot is stored in fstab instead of  the mounted point for every snapshot of root created.
- grub-mkconfig will run after consolidating deafult root subvolume
- Consolidation process will check the original path of the default subvolume for root and will use it in fstab.

### Version 1.9
- Buttermanager has been integrated with **grub-btrfs** package. It means that, for all these users who use GRUB will be able to boot its system from any snapshot created with this version of the application and above. This integration will be optional and configurable from **Settings** tab.

### Version 1.8 ###
- Font autoscaling implemented in order to let the GUI adapts to the current screen resolution.
- It has been created a new tab for **Documentation** and a **Wiki** at Github repository.
- The text of some tooltips have been fixed.

### Version 1.7 ###
- Bug fixed for Arch Linux and derivatives installing the package from AUR. Now, the application will be installed and run from a virtual environmen with all the modules needed. This causes that the size of the package buttermanager has increased

### Version 1.6 ###
- Logs generated during the upgrade process can be stored
- Logs management implemented
- Version checker implemented. When a new version of ButterManagger is released, a new info window will be display to warn the user

### Version 1.5 ###
- Labels refreshing after balancing the filesystem has been fixed
- Values to show certaing labels have been recalculated

### Version 1.4 ###
- System progress bar has been removed because it doesn't provide any relevant information
- A new button has been implemented in order to upgrade the system whithout managing snapshots
- All the ButterManager windows and dialogs have been reconfigured using fixed pixels in order to avoid the resizing
- The ButterManager icon has been assigned to all windows and dialogs
- When ButterManager is installed for the first time, the updates checker is not checked by default
- A new option added to yay command to check for AUR packages only
- New messages implemented in the main window in order to warn the user about the space of the filesystem
- Internet connection will be checked during 5 minutes. If there is no Internet connection, then the updates checker process will be cancelled

### Version 1.3 ###
- The updates checker is executed in other thread, so now the GUI is not freezed during the process.

### Version 1.2 ###
- Some layouts and texts fixed to fit properly
- New window to list the packages to be updated implemented
- Fixed a problem in the snap package for Wayland environments

### Version 1.1 ###

- RHEL / Fedora, OpenSUSE / SUSE support added.
- New window implemented for displaying serious problems related to the proper functioning of ButterManager.

### Version 1.0 ###

- Initial release.
- It supports Arch Linux, Debian, Ubuntu and derivatives.
- Safely system upgrade.
- BTRFS filesystems detection and visualization.
- Snapshots management.
- BTRFS filesystems balancing.
- Application packaged in AUR.
- Ubuntu Snap Package implemented for universal use in the rest of Linux distributions.

## Contact ##
If you want to contact me, you can do it using this e-mail address <eloy.garcia.pca@gmail.com>.
