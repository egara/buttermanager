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
import glob
import os
import sys
import time
import util.utils

# Constants
BTRFS_CREATE_SNAPSHOT_COMMAND = "btrfs subvolume snapshot -r"
BTRFS_DELETE_SNAPSHOT_COMMAND = "btrfs subvolume delete"


# Classes
class Subvolume:
    """BTRFS Snapshot.

    """
    # Constructor
    def __init__(self, subvolume_origin, subvolume_dest, snapshot_name):
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
        command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
            command=BTRFS_CREATE_SNAPSHOT_COMMAND,
            subvolume_origin=self.subvolume_origin,
            subvolume_dest=self.subvolume_dest,
            snapshot_full_name=snapshot_full_name
        )
        util.utils.execute_command(command, console=True, root=True)

    def delete_snapshots(self, snapshots_to_keep):
        """Deletes all the snapshots needed to keep the desired number set by the user.

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
            command = "{command} {snapshot}".format(command=BTRFS_DELETE_SNAPSHOT_COMMAND, snapshot=snapshots[index])
            util.utils.execute_command(command, console=True, root=True)
            info_message = "Snapshot {snapshot} deleted.\n".format(snapshot=snapshots[index])
            self.__logger.info(info_message)
            snapshots_to_delete -= 1
            index += 1

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
