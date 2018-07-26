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

"""This module gathers all the operations related to BTRFS filesystems.

It provides also Filesystem class.
"""

import util.buttermanager_utils

# Constants
DEVID = "devid"
LABEL = "Label"
UUID = "uuid:"
BTRFS_SHOW_COMMAND = "sudo -S btrfs filesystem show"
FINDMT_COMMAND = "sudo -S findmnt -nt btrfs"


# Classes
class Filesystem:
    """BTRFS Filesystem.

    """
    # Constructor
    def __init__(self, uuid):

        self.__uuid = uuid
        self.__devices = self.__get_devices()
        self.__mounted_points = self.__get_mounted_points()
        self.__total_size = 0
        self.__total_allocated = 0
        self.__data_size = 0
        self.__data_used = 0
        self.__metadata_size = 0
        self.__metadata_used = 0
        self.__system_size = 0
        self.__system_used = 0

    # Private attributes
    # UUID
    @property
    def uuid(self):
        return self.__uuid

    # Devices
    @property
    def devices(self):
        return self.__devices

    # Mounted points
    @property
    def mounted_points(self):
        return self.__mounted_points

    # Total size
    @property
    def total_size(self):
        return self.__total_size

    # Total allocated
    @property
    def total_allocated(self):
        return self.__total_allocated

    # Data size
    @property
    def data_size(self):
        return self.__data_size

    # Data used
    @property
    def data_used(self):
        return self.__data_used

    # Metadata size
    @property
    def metadata_size(self):
        return self.__metadata_size

    # Metadata used
    @property
    def metadata_used(self):
        return self.__metadata_used

    # System size
    @property
    def system_size(self):
        return self.__system_size

    # System used
    @property
    def system_used(self):
        return self.__system_used

    # Methods
    # Private methods
    def __get_devices(self):
        """Retrieves all the devices which the BTRFS filesystem is composed.

        Returns:
            list (:obj:`list` of :obj:`str`): devices.
        """
        try:
            devices = []
            commandline_output = util.buttermanager_utils.execute_command(BTRFS_SHOW_COMMAND)
            filesystem_found = False

            for line in commandline_output.split("\n"):
                if UUID in line:
                    if filesystem_found:
                        break
                    else:
                        if self.uuid in line:
                            filesystem_found = True
                            continue

                if filesystem_found:
                    # The loop is inside the chosen BTRFS filesystem
                    # It is necessary to find devid to retrieve all the filesystem paths
                    if DEVID in line:
                        path_init = line.find('/')
                        # The device path is appended to the list
                        devices.append(line[path_init:len(line)])

            return devices

        except util.buttermanager_utils.NoCommandFound as exception:
            raise exception

    def __get_mounted_device(self):
        """Retrieves the device tha contains the BTRFS filesystem and it is mounted.

        Returns:
            string: device path.
        """
        try:
            mounted_device = ''
            commandline_output = util.buttermanager_utils.execute_command(FINDMT_COMMAND)
            for device in self.devices:
                if device in commandline_output:
                    mounted_device = device
                    break

            return mounted_device

        except util.buttermanager_utils.NoCommandFound as exception:
            raise exception

    def __get_mounted_points(self):
        """Retrieves all the mounted points of the BTRFS filesystem.

        Returns:
            list (:obj:`list` of :obj:`str`): mounted points.
        """
        try:
            mounted_points = []
            device = self.__get_mounted_device()
            command = FINDMT_COMMAND + ' ' + device
            commandline_output = util.buttermanager_utils.execute_command(command)

            for line in commandline_output.split("\n"):
                if len(line) > 0:
                    mounted_points.append(line.split(" ")[0].strip())

            return mounted_points

        except util.buttermanager_utils.NoCommandFound as exception:
            raise exception

    # Public methods
    def __str__(self):
        """Reimplementation of the str method inherited from object class.

        Returns:
            string: String representation of the Filesystem object.
        """
        return "BTRFS Filesystem -> UUID: {0}; Devices: {1}; Mounted Points: {2}".format(self.uuid, self.devices,
                                                                                         self.mounted_points)


# Module's methods
def get_btrfs_filesystems(mounted=True):
    """Retrieves all the BTRFS filesystems.

    Keyword arguments:
        mounted (bool): Only mounted filesystems will be retrieved (default True).

    Returns:
        list (:obj:`list` of :obj:`str`): filesystems UUID.
    """

    filesystems = []
    command = BTRFS_SHOW_COMMAND

    if mounted:
        command += " --mounted"

    commandline_output = util.buttermanager_utils.execute_command(command)

    for line in commandline_output.split("\n"):
        if UUID in line:
            # The uuid is appended to the list
            filesystems.append(line.split(UUID)[1].strip())

    return filesystems
