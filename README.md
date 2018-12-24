# ButterManager

## Summary ##
ButterManager is a BTRFS tool for managing snapshots, balancing filesystems and upgrading the system safetly.

## Version ##
1.0

## Caveats ##
For using ButterManager, it is important to have a **good BTRFS structure in your filesystem**. If you want some tips and more information, you can [read this](https://github.com/egara/arch-btrfs-installation).

## Managing snpashots ##
You will be able to define all the subvolumes you want to create snapshots and the path for their storage. Then, using ButterManager you will create and delete snapshots of those subvolumes at your will.

## Balancing BTRFS filesystems ##
As new snapshots are created in the system, the free space of the filesystem decreases and it is necessary to perform a system balancing regularly. With ButterManager you can perform these balances at any time and visualize the real space that is occupied.

## Upgrading the system ##
You will be able to upgrade your system and create new snapshots automatically when this operation is performed. Doing so, if something goes wrong, you will have a snapshot before the upgrade you can use to go back. You will be able to set the maximum number of snapshots in your system and ButterManager will maintain this number with every upgrade.

## Installation ##
You can install ButterManager in different ways.

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

4. For running ButterManager just:

  ```
    cd buttermanager/buttermanager
    python buttermanager.py

  ```

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

## Contact ##
If you want to contact me, you can do it using this e-mail address <eloy.garcia.pca@gmail.com>.