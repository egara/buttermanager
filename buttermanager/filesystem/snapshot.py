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
import os
import time
import util.utils

# Constants
BTRFS_SNAPSHOT_COMMAND = "sudo -S btrfs subvolume snapshot -r"


# Classes
class Snapshot:
    """BTRFS Snapshot.

    """
    # Constructor
    def __init__(self, subvolume_origin, subvolume_dest, snapshot_name, snapshots_to_keep):
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        self.__subvolume_origin = subvolume_origin
        self.__subvolume_dest = subvolume_dest
        self.__snapshot_name = snapshot_name
        self.__snapshots_to_keep = snapshots_to_keep
        self.__current_date = time.strftime('%Y%m%d')

    # Private attributes
    # Subvolumen which is going to be backed up
    @property
    def subvolume_origin(self):
        return self.__subvolume_origin

    # Subvolume where the snapshot is going to be created
    @property
    def subvolume_dest(self):
        return self.__subvolume_dest

    # Snapshot name
    @property
    def snapshot_name(self):
        return self.__snapshot_name

    # Number of snapshots to keep
    @property
    def snapshots_to_keep(self):
        return self.__snapshots_to_keep

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
            command=BTRFS_SNAPSHOT_COMMAND,
            subvolume_origin=self.subvolume_origin,
            subvolume_dest=self.subvolume_dest,
            snapshot_full_name=snapshot_full_name
        )
        util.utils.execute_command(command, console=True)

    def delete_snapshot(self):
        """Deletes all the snapshots needed to keep the desired number set by the user.

        """
        info_message = "Deleting snapshot of {subvolume_origin} in {subvolume_dest}. " \
                       "Please wait...".format(subvolume_origin=self.subvolume_origin,
                                               subvolume_dest=self.subvolume_dest)
        self.__logger.info(info_message)

        # Checking how many snapshots are with the same name ordered by date
        # snapshots = os.listdir(self.subvolume_dest).sort(key=os.path.getmtime())

        snapshot_full_name = "{snapshot_name}-{current_date}".format(snapshot_name=self.snapshot_name,
                                                                        current_date=self.__current_date)
        snapshots_with_same_name = [file for file in os.listdir(self.subvolume_dest) if snapshot_full_name in file]

        # Adding number to the full name
        snapshot_full_name = "{snapshot_full_name}-{number}".format(snapshot_full_name=snapshot_full_name,
                                                                    number=len(snapshots_with_same_name))
        command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
            command=BTRFS_SNAPSHOT_COMMAND,
            subvolume_origin=self.subvolume_origin,
            subvolume_dest=self.subvolume_dest,
            snapshot_full_name=snapshot_full_name
        )
        util.utils.execute_command(command, console=True)

# Module's methods
