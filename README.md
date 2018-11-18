# ButterManager

## Summary ##
ButterManager is a BTRFS tool for managing snapshots, balancing filesystems and upgrading the system safetly.

### Managing snpashots ###
You will be able to define all the subvolumes you want to create snapshots and the path for their storage. Then, using ButterManager you will be able to create and delete snapshots of those subvolumes at your will at any moment.

### Balancing BTRFS filesystems ###
As new snapshots are created in the system, the free space of the filesystem decreases and it is necessary to perform a system balancing regularly. With ButterManager you can perform these balances at any time and visualize the real space that is occupied.

### Upgrading the system ###
With ButterManager you will be able to upgrade your system and create new snapshots automatically when this operation is performed. Doing so, if something goes wrong, you will have a snapshot before the upgrade you can use to go back. You will be able to set the maximum number of snapshots in your system and ButterManager will maintain this number with every upgrade.