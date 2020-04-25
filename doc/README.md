# Documentation
This is the documentation related to [Buttermanager](https://github.com/egara/buttermanager) GUI tool for easily management of BTRFS snapshots and system upgrades.

## BTRFS filesystem initial layout
For the purpose of this documentation, we are going to suppose that we have installed [Manjaro]() using a manual partitioning with this requirements:

- Only one disk: **sda**
- Only one partition in the disk: **sda1**
- *sda1* has been formatted using **btrfs**
- The mount point selected for this partition is **/**

After the installation of the operating system, the subvolumes automatically created are two (**@** and **@home**) as you can see in the screenshot below:

<img src="screen-1.png" alt="drawing" width="1420"/>

So the layout is something like this

```
Main Volume (ID 5)
|
|--- @ (Subvolume ID 257)
|
|--- @home (Subvolume ID 258)
```

**Important Note: If you are installing Arch from scratch or want to reshape your default BTRFS layout, you can check out this tips [https://github.com/egara/arch-btrfs-installation](https://github.com/egara/arch-btrfs-installation).**

## Mounting main volume (ID 5)
In order to manage in a proper way all the snapshots created and make things easier if you want to rollback your system to a previous snapshot, we are going to mount the main BTRFS volume in **/mnt/defvol** directory. For this, you first has to create this directory.

<img src="screen-2.png" alt="drawing" width="1420"/>

Include this new mounting point in **/etc/fstab** just to automount it when the system boots. Please, change the UID to the appropriate one or use labels if it is your case.

<img src="screen-3.png" alt="drawing" width="1420"/>

Once **fstab** is changed you can type
    
    sudo mount -a

and go to **/mnt/defvol**. You should see something like this:

<img src="screen-4.png" alt="drawing" width="1420"/>

Create a new subvolume called **snapshots** at top level (as you can see above) using the command:

    sudo btrfs subvolume create snapshots
    
The final layout will be:

```
Main Volume (ID 5)
|
|--- @ (Subvolume ID 257)
|
|--- @home (Subvolume ID 258)
|
|--- snapshots (Subvolume ID 271)
```

<img src="screen-5.png" alt="drawing" width="1420"/>

## Setting up Buttermanager
Yes, finally we are going to configure **Buttermanager**!. The first time you open the application, you will be warned because no subvolumes to create snapshots has been defined yet. You could use the application, but if you upgrade your system, **Buttermanager** won't create any snapshot.

<img src="screen-6.png" alt="drawing" width="1420"/>

Go to **Settings** tab and click on **Add subvolume** button.

<img src="screen-7.png" alt="drawing" width="1420"/>

Now, using the layout defined in this example, we are going to configure two subvolumes to create snapshots of **root** and **home**.

### Subvolume 1 (root)
If you want **Buttermanager** creates a snapshot of your **root** partition everytime it upgrades the system, then you should fill the **Add a subvolume** window like this:

- *Subvolume to manage*: **/mnt/defvol/@**
- *Path where the snapshot will be stored*: **/mnt/defvol/snapshots**
- *Snapshot prefix*: **root**

>Please, use always different prefixes for different subvolumes (prefixes shouldn't even include words contained in other prefixes, i.e. in this example, you should never include root word in other prefixes).

<img src="screen-8.png" alt="drawing" width="1420"/>

This way, everytime **Buttermanager** upgrades the system, it will automatically create a snapshot of the **root** mounted subvolume called **root-[date]-[number]** within **/mnt/defvol/snapshots/** directory. This snapshot will be **read only** by default.

### Subvolume 2 (/home)
If you want **Buttermanager** creates a snapshot of your **home** partition everytime it upgrades the system, then you should fill the **Add a subvolume** window like this:

- *Subvolume to manage*: **/mnt/defvol/@home**
- *Path where the snapshot will be stored*: **/mnt/defvol/snapshots**
- *Snapshot prefix*: **home**

<img src="screen-9.png" alt="drawing" width="1420"/>

This way, everytime **Buttermanager** upgrades the system, it will automatically create a snapshot of the **home** mounted subvolume called **home-[date]-[number]** within **/mnt/defvol/snapshots/** directory. This snapshot will be **read only** by default.