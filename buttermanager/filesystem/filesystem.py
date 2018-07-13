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

import subprocess

# Constants
DEVID = "devid"
LABEL = "Label"

class Filesystem():
    # Constructor
    def __init__(self, mounted_point="/", total_size=0, total_allocated=0, data_size=0, data_used=0, metadata_size=0,
                 metadata_used=0, system_size=0, system_used=0):
        """BTRFS Filesystem.

        """

        self.mounted_point = mounted_point
        self.total_size = total_size
        self.total_allocated = total_allocated
        self.data_size = data_size
        self.data_used = data_used
        self.metadata_size = metadata_size
        self.metadata_used = metadata_used
        self.system_size = system_size
        self.system_used = system_used


# TODO: Comment this method
def get_btrfs_filesystems(mounted=True):
    """Retrieves all the BTRFS filesystems.

    Arguments:

    Keyword arguments:
        mounted (bool): Only mounted filesystems will be retrieved (default True)

    Returns:
        list (:obj:`list` of :obj:`str`): Paths where those filesystems are.
    """

    filesystems = []
    command = "sudo btrfs filesystem show"

    if mounted:
        command += " --mounted"

    # run method receives a list, so it is necessary to convert command string into a list using split (by blank space)
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    # result is Bytes type, so it is needed to decode Unicode string using UTF-8
    commandline_output = result.stdout.decode('utf-8')
    filesystem_found = False

    for line in commandline_output.split("\n"):
        if filesystem_found:
            # The loop is inside a new BTRFS filesystem
            # It is necessary to find devid to retrive the filesystem path (only first occurrence)
            if DEVID in line:
                path_init = line.find('/')
                # The path is appended to the list
                filesystems.append(line[path_init:len(line)])
                filesystem_found = False
        if LABEL in line:
            filesystem_found = True

    return filesystems
