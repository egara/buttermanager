# ButterManager

## Summary ##
ButterManager is a BTRFS tool for managing snapshots, balancing filesystems and upgrading the system safetly.

## Version ##
2.0

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
- **python-virtualenv** (f.i. the name of the package in Ubuntu is **python3-venv**).
- **grub-btrfs**. Please, go to its GitHub repository [https://github.com/Antynea/grub-btrfs](https://github.com/Antynea/grub-btrfs) and follow the instructions to install it if the package is not in the official repository of your distribution.

Once you meet all the requirements, follow these steps:

1. Clone the repository (install **git** if it is needed first)

  ```
    git clone https://github.com/egara/buttermanager.git

  ```

1. Install ButterManager using the installation script

  ```
    cd buttermanager
    cd install
    ./install.sh

  ```
  
1. The installation process will create a desktop launcher to run ButterManager directly.

1. If you want to uninstall ButterManager:

  ```
    cd buttermanager
    cd install
    ./uninstall.sh

  ```

### From AUR ###
If you are an Arch Linux user or your distribution is a derivative (Manjaro, EndevourOS...), ButterManager is in AUR. Depending on your package manager for AUR, type:

  ```
    yaourt -S buttermanager

  ```

Or
  ```
    trizen -S buttermanager

  ```

Or
  ```
    yay -S buttermanager

  ```
Those are only examples. Use the package manager you have installed for AUR. Once ButterManager is installed, you will be able to run it using the icon created in the main menu.

## Changelog

### Version 2.0
- Now, the installer creates ~/.local/share/applications directory if it didn't exist in order to allocate the ButterManager desktop launcher.
- The method of calculating the default original subvolume to consolidate the system has been reimplemented and improved to avoid some bugs detected.
- Now, the allocation of the original snapshot is stored in fstab instead the mounted point for every snapshot of root created.
- grub-mkconfig will run after consolidating deafult root subvolume

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
