# ButterManager

## Summary ##
ButterManager is a BTRFS tool for managing snapshots, balancing filesystems and upgrading the system safetly.

## Version ##
1.4

## Caveats ##
- For using ButterManager, it is important to have a **good BTRFS structure in your filesystem**. If you want some tips and more information, you can [read
this](https://github.com/egara/arch-btrfs-installation).

- ButterManager works with **Debian**, **Ubuntu / derivatives (Linux Mint, KDE Neon, ElementaryOS, Zorin, Deepin...)**, **OpenSUSE / SUSE**, **RHEL / Fedora** and **Arch Linux** so far.

## Main Functionalities ##

### Managing snapshots ###
You will be able to define all the subvolumes you want to create snapshots and the path for their storage. Then, using ButterManager you will create and delete snapshots of those subvolumes at your will.

### Balancing BTRFS filesystems ###
As new snapshots are created in the system, the free space of the filesystem decreases and it is necessary to perform a system balancing regularly. With ButterManager you can perform these balances at any time and visualize the real space that is occupied.

### Upgrading the system ###
You will be able to upgrade your system and create new snapshots automatically when this operation is performed. Doing so, if something goes wrong, you will have a snapshot before the upgrade you can use to go back. You will be able to set the maximum number of snapshots in your system and ButterManager will maintain this number with every upgrade.

## Installation ##
You can install ButterManager in different ways.

### Snap package ###
Snaps are universal Linux packages that can be used on all major Linux distributions, including Ubuntu, Linux Mint, Debian, Fedora, Arch Linux and more. Please, read [this article](https://docs.snapcraft.io/installing-snapd/6735) for knowing more and installing snap support.

Installing ButterManager using the snap package is very simple. First, download the ButterManager snap [here](https://drive.google.com/file/d/1iFjUiITnj7_pl9EahYuTxwSDpFwWCCnP/view?usp=sharing).

After this, ppen a terminal, go to the directory where the package is downloaded and type:

```
sudo snap install --beta core16
sudo snap install buttermanager_1.5_amd64.snap --classic --dangerous
```

The first time ButterManager is executed after installing the snap package, maybe it will take a little bit to run. Don't worry, it will be only the first time.

### From the source code ###
1. Clone the repository (install **git** if it is needed first)

  ```
    git clone https://github.com/egara/buttermanager.git

  ```

2. Install all the dependencies needed (all the packages described below are for **Arch Linux**. Please, check for those packages and their names in you correspondant distribution):
    - Python 3 (python)
    - Setup Tools for Python 3 (python-setuptools)

3. Install the rest of the dependencies:

  ```
    cd buttermanager
    python setup.py install --user

  ```
  Please note that if you have several versions of python installed on your system, maybe you have to run explicity **python3 setup.py install --user** instead.

4. For running ButterManager just:

  ```
    cd buttermanager/buttermanager
    python buttermanager.py

  ```
  Please note that if you have several versions of python installed on your system, maybe you have to run explicity **python3 buttermanager.py** instead.

### From AUR ###
If you are an Arch Linux user, ButterManager is in AUR. Depending on your package manager for AUR, type:

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

## Changelog ##

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
