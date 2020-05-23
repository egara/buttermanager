#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# Copyright 2018-2019 Eloy García Almadén <eloy.garcia.pca@gmail.com>
#
# This file is part of buttermanager.
#
# This program is free software: you can redistribute it and / or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module gathers all the operations related to BTRFS snapshots.

It provides also Snapshot class.
"""
import filesystem.snapshot
import glob
import os
import re
import sys
import subprocess
import time
import util.settings
import util.utils
import window.windows

# Constants
BTRFS_CREATE_SNAPSHOT_R_COMMAND = "sudo -S btrfs subvolume snapshot -r"
BTRFS_CREATE_SNAPSHOT_RW_COMMAND = "sudo -S btrfs subvolume snapshot"
BTRFS_DELETE_SNAPSHOT_COMMAND = "sudo -S btrfs subvolume delete"
GRUB_BTRFS_COMMAND = "sudo -S grub-mkconfig -o /boot/grub/grub.cfg"


# Classes
class Subvolume:
    """BTRFS Snapshot.

    """
    # Constructor
    def __init__(self, subvolume_origin, subvolume_dest, snapshot_name):
        """ Constructor.

        Arguments:
            subvolume_origin (str): Full path to the subvolume.
            subvolume_dest (str): Full path to the subvolume where all of the subvolumes created from origin are going
            to be stored.
            snapshot_name (str): Prefix for all the subvolumes created from origin
        """
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        self.subvolume_origin = subvolume_origin if subvolume_origin[-1] == '/' else subvolume_origin + '/'
        self.subvolume_dest = subvolume_dest if subvolume_dest[-1] == '/' else subvolume_dest + '/'
        self.snapshot_name = snapshot_name
        self.__current_date = time.strftime('%Y%m%d')

    # Methods
    # Private methods

    # Public methods
    def create_snapshot(self):
        """Creates a snapshot.

        """
        info_message = "Creating a read-only snapshot of {subvolume_origin} in {subvolume_dest}. " \
                       "Please wait...".format(subvolume_origin=self.subvolume_origin,
                                               subvolume_dest=self.subvolume_dest)
        self.__logger.info(info_message)

        # Checking how many snapshots are with the same name
        snapshot_full_name = "{snapshot_name}-{current_date}".format(snapshot_name=self.snapshot_name,
                                                                     current_date=self.__current_date)
        snapshots_with_same_name = [file for file in os.listdir(self.subvolume_dest) if snapshot_full_name in file]

        # Adding number to the full name
        snapshot_full_name = "{snapshot_full_name}-{number}".format(snapshot_full_name=snapshot_full_name,
                                                                    number=len(snapshots_with_same_name))

        # Checks if grub-btrfs integration is enabled
        if util.settings.properties_manager.get_property("grub_btrfs"):
            # Checks if /etc/fstab is in subvolume_origin
            fstab_path = self.subvolume_origin + 'etc/fstab'
            if os.path.isfile(fstab_path):
                # /etc/fstab is in the subvolume, so it is necessary to
                # modify it and add the snapshot's name
                # grep -rnw '/etc/fstab' -e "/_active/rootvol"
                # First, it is necessary to be sure that subvolume_origin is
                # within /etc/fstab
                # First, a list of strings from subvolume_origin is created, including separator /
                subvolume_origin_list = re.split('(/)', self.subvolume_origin)
                # Then, empty strings are removed
                subvolume_origin_list = list(filter(None, subvolume_origin_list))
                # Adding final / it it is necessary
                if subvolume_origin_list[-1] != "/":
                    subvolume_origin_list.append("/")
                subvolume_origin_real = "".join(subvolume_origin_list)
                # while subvolume_origin_real is not null or empty
                while subvolume_origin_real:
                    # First try: subvolume_origin_real with / at the end is searched
                    command_string = """grep -rnw '{fstab_path}' -e '{subvolume_origin_real}'""".format(
                        fstab_path=fstab_path, subvolume_origin_real=subvolume_origin_real)
                    command = [command_string]
                    commandline_output = None
                    try:
                        commandline_output = subprocess.check_output(command, shell=True)
                    except subprocess.CalledProcessError as exception:
                        pass
                    if commandline_output:
                        break
                    else:
                        # Second try: subvolume_origin_real without / at the end is searched
                        subvolume_origin_real = subvolume_origin_real[:-1]
                        command_string = """grep -rnw '{fstab_path}' -e '{subvolume_origin_real}'""".format(
                            fstab_path=fstab_path, subvolume_origin_real=subvolume_origin_real)
                        command = [command_string]
                        commandline_output = None
                        try:
                            commandline_output = subprocess.check_output(command, shell=True)
                        except subprocess.CalledProcessError as exception:
                            pass
                        if commandline_output:
                            break
                        else:
                            del subvolume_origin_list[0]
                            # Adding final / it it is necessary
                            if subvolume_origin_list[-1] != "/":
                                subvolume_origin_list.append("/")

                            subvolume_origin_real = "".join(subvolume_origin_list)

                if subvolume_origin_real != "/":
                    # subvolume_origin_real is in /etc/fstab
                    # Create the snapshot in rw mode
                    everything_ok = True
                    command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
                        command=BTRFS_CREATE_SNAPSHOT_RW_COMMAND,
                        subvolume_origin=self.subvolume_origin,
                        subvolume_dest=self.subvolume_dest,
                        snapshot_full_name=snapshot_full_name
                    )
                    util.utils.execute_command(command, console=True, root=True)

                    # Substitute the entry in fstab for root for the new snapshot created
                    command_string = """sudo -S sed -i 's|{subvolume_origin_real}|{subvolume_dest}{snapshot_full_name}|g' {subvolume_dest}{snapshot_full_name}/etc/fstab""".format(
                        subvolume_origin_real=subvolume_origin_real,
                        subvolume_dest=self.subvolume_dest,
                        snapshot_full_name=snapshot_full_name
                    )
                    command = [command_string]
                    try:
                        subprocess.check_output(command, shell=True)
                    except subprocess.CalledProcessError as exception:
                        self.__logger.error("Error trying to substitute the root's path in fstab with the "
                                            "path of the new snapshot created. Reason: " + + str(exception.reason))
                        everything_ok = False
                    if everything_ok:
                        # subvolume_origin_real will be stored in configuration file in order to let the
                        # user to consolidate the system's rollback to any snapshot different from the main one
                        util.settings.properties_manager.set_property('path_to_consolidate_root_snapshot',
                                                                      subvolume_origin_real)

                        # Run grub-btrfs in order to regenerate GRUB entries
                        self.__logger.info("Regenerating GRUB entries. Please wait...")
                        util.utils.execute_command(GRUB_BTRFS_COMMAND, console=True, root=True)
                else:
                    # subvolume_origin_real in not in /etc/fstab
                    # Create the snapshot in only r mode
                    command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
                        command=BTRFS_CREATE_SNAPSHOT_R_COMMAND,
                        subvolume_origin=self.subvolume_origin,
                        subvolume_dest=self.subvolume_dest,
                        snapshot_full_name=snapshot_full_name
                    )
                    util.utils.execute_command(command, console=True, root=True)

            else:
                command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
                    command=BTRFS_CREATE_SNAPSHOT_R_COMMAND,
                    subvolume_origin=self.subvolume_origin,
                    subvolume_dest=self.subvolume_dest,
                    snapshot_full_name=snapshot_full_name
                )
                util.utils.execute_command(command, console=True, root=True)
        else:
            command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
                command=BTRFS_CREATE_SNAPSHOT_R_COMMAND,
                subvolume_origin=self.subvolume_origin,
                subvolume_dest=self.subvolume_dest,
                snapshot_full_name=snapshot_full_name
            )
            util.utils.execute_command(command, console=True, root=True)

    def delete_snapshots(self, snapshots_to_keep):
        """Deletes all the snapshots needed to keep the desired number set by the user.
        It will delete the related logs if they exist

        Arguments:
            snapshots_to_keep (int): number of snapshots to keep in the filesystem.

        """
        info_message = "Deleting snapshot of {subvolume_origin} in {subvolume_dest}. " \
                       "Please wait...".format(subvolume_origin=self.subvolume_origin,
                                               subvolume_dest=self.subvolume_dest)
        self.__logger.info(info_message)

        # Checking how many snapshots are with the same name ordered by date
        snapshots = self.get_all_snapshots_with_the_same_name()

        # Removing all the snapshots needed starting with the oldest one until reach
        # the limit defined by the user
        snapshots_to_delete = len(snapshots) - snapshots_to_keep
        index = 0
        while snapshots_to_delete > 0:
            # Deletes the snapshot
            command = "{command} {snapshot}".format(command=BTRFS_DELETE_SNAPSHOT_COMMAND, snapshot=snapshots[index])
            util.utils.execute_command(command, console=True, root=True)
            info_message = "Snapshot {snapshot} deleted.\n".format(snapshot=snapshots[index])
            self.__logger.info(info_message)
            # Deletes the log if it exists
            snapshot_name = snapshots[index].split("/")[-1]
            log = "{snapshot_name}-{index}.txt".format(snapshot_name=snapshot_name.split("-")[-2],
                                                       index=snapshot_name.split("-")[-1])
            log_path = os.path.join(util.settings.logs_path, log)
            try:
                os.remove(log_path)
                info_message = "Log {log} deleted.\n".format(log=log)
                self.__logger.info(info_message)
            except OSError as exception:
                info_message = "Error deleting log {log}. Error {exception}\n".format(log=log, exception=str(exception))
                self.__logger.info(info_message)

            snapshots_to_delete -= 1
            index += 1

        # Checks if grub-btrfs integration is enabled
        if util.settings.properties_manager.get_property("grub_btrfs"):
            # Run grub-btrfs in order to regenerate GRUB entries
            util.utils.execute_command(GRUB_BTRFS_COMMAND, console=True, root=True)

    def delete_origin(self):
        """Deletes the original subvolume, i.e. the subvolume in subvolume_origin

        """
        info_message = "Deleting subvolume from origin {subvolume_origin}. " \
                       "Please wait...".format(subvolume_origin=self.subvolume_origin)
        self.__logger.info(info_message)

        # Deletes the subvolume
        command = "{command} {snapshot}".format(command=BTRFS_DELETE_SNAPSHOT_COMMAND, snapshot=self.subvolume_origin)
        util.utils.execute_command(command, console=True, root=True)
        info_message = "Snapshot {snapshot} deleted.\n".format(snapshot=self.subvolume_origin)
        self.__logger.info(info_message)

    def get_all_snapshots_with_the_same_name(self):
        """Retrieves all the snapshots with name self.snapshot_name stored within self.subvolume_dest.

        Returns:
            list (:obj:`list` of :obj:`str`): paths to the snapshots.
        """
        # Checking how many snapshots are with the same name ordered by date
        snapshots = glob.glob("{snapshot_directory}/*".format(snapshot_directory=self.subvolume_dest))
        snapshots.sort(key=os.path.getmtime)
        snapshots_whit_same_name = [file for file in snapshots if self.snapshot_name in file]

        return snapshots_whit_same_name


class RootSnapshotChecker:
    """Checks if the current snapshot used for root is the default or the user has booted the system from
    an alternate snapshot.

    """
    def __init__(self, parent_window):
        # Attributes
        self.__snapshot_to_clone_in_root_full_path = None
        self.__root_subvolume = None
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        self.__logger.info("Checking if the current snapshot used for root is the default. Please wait...")
        self.__parent_window = parent_window

    def check_root_snapshot(self):
        """Checks if the current snapshot used for root is the default or the user has booted the system from
        an alternate snapshot.

        Returns:
            boolean: true if current snapshot used for root is the default; false otherwise.
        """
        # First, it is necessary to check if path_to_consolidate_root_snapshot is defined
        if util.settings.properties_manager.get_property("path_to_consolidate_root_snapshot") != '0':
            # Obtaining the mounted subvolume for root partition
            # mount | grep 'on / ' | grep -o 'subvol=/.*' | cut -f2- -d=
            command_string = """mount | grep 'on / ' | grep -o 'subvol=/.*' | cut -f2- -d="""
            command = [command_string]
            mounted_snapshot_raw = None
            try:
                mounted_snapshot_raw = subprocess.check_output(command, shell=True)
            except subprocess.CalledProcessError as exception:
                pass
            if mounted_snapshot_raw:
                # Removing the last two characters (a /n and a ")")
                mounted_snapshot_raw = mounted_snapshot_raw[:-2]
                # Converting bytes into string
                mounted_snapshot_raw = mounted_snapshot_raw.decode("utf-8")
            if mounted_snapshot_raw != util.settings.properties_manager. \
                    get_property("path_to_consolidate_root_snapshot"):
                # If mounted snapshot is different from the supposed default root subvolume
                # it means that user has booted the system using an alternate snapshot from GRUB.
                # ButterManager will ask to consolidate the current snapshot as the default root
                # subvolume

                # Obtaining the snapshot mounted
                mounted_snapshot_full_path = None
                while mounted_snapshot_full_path is None:
                    for subvolume in util.settings.subvolumes:
                        snapshots = util.settings.subvolumes[subvolume].get_all_snapshots_with_the_same_name()
                        for snapshot in snapshots:
                            if mounted_snapshot_raw in snapshot:
                                mounted_snapshot_full_path = snapshot
                                break

                self.__snapshot_to_clone_in_root_full_path = mounted_snapshot_full_path
                self.__root_subvolume = util.settings.subvolumes[subvolume]
                return False
            else:
                return True
        else:
            # Path to consolidate root snapshot hasn't been defined yet so this part is skipped
            return True

    def open_consolidate_snapshot_window(self):
        """Checks if the current snapshot used for root is the default or the user has booted the system from
        an alternate snapshot.

        Returns:
            QDialog: The dialog window to consolidate the root snapshot.
        """
        info_window = window.windows.ConsolidateSnapshotWindow(self.__parent_window,
                                                               self.__snapshot_to_clone_in_root_full_path,
                                                               self.__root_subvolume)
        return info_window


# Module's methods
def delete_specific_snapshot(snapshot_full_path):
    """Deletes a specific snapshot.

    Arguments:
        snapshot_full_path (string): path to the snapshot that user wants to delete.

    """
    # Logger
    logger = util.utils.Logger(sys.modules['__main__'].__file__).get()
    info_message = "Deleting snapshot {snapshot}".format(snapshot=snapshot_full_path)
    logger.info(info_message)

    command = "{command} {snapshot}".format(command=BTRFS_DELETE_SNAPSHOT_COMMAND, snapshot=snapshot_full_path)
    util.utils.execute_command(command, root=True)
    info_message = "Snapshot {snapshot} deleted.\n".format(snapshot=snapshot_full_path)
    logger.info(info_message)

    # Checks if grub-btrfs integration is enabled
    if util.settings.properties_manager.get_property("grub_btrfs"):
        # Run grub-btrfs in order to regenerate GRUB entries
        util.utils.execute_command(GRUB_BTRFS_COMMAND, console=True, root=True)
        info_message = "Regenerating GRUB entries. Please wait..."
        logger.info(info_message)