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

"""This module gathers all the managers built for the application.

"""
import filesystem.snapshot
import sys
import util.utils
from PyQt5.QtCore import QThread

# Constants
ARCH_PACMAN_COMMAND = "sudo -S pacman -Syu --noconfirm"
DEBIAN_APT_UPDATE_COMMAND = "sudo -S apt update"
DEBIAN_APT_UPGRADE_COMMAND = "sudo -S apt upgrade -y"


class Upgrader(QThread):
    """Independent thread that will run the system upgrading process.

    """
    # Attributes

    # Constructor
    def __init__(self):
        QThread.__init__(self)
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()

    # Methods
    def run(self):
        # Upgrading the system
        self.__upgrade_system()

    def __upgrade_system(self):
        """Wraps all the operations to upgrade the system.

        """
        self.__logger.info("Starting system upgrading process.")
        sys.stdout.write("Starting system upgrading process. Please wait...")
        sys.stdout.write("\n")

        # Creates all the snapshots needed before upgrading the system
        # Todo: Snapshots should be defined in a config file by the user
        snapshot_one = filesystem.snapshot.Snapshot("/mnt/defvol/_active/rootvol/", "/mnt/defvol/_snapshots/", "root")
        snapshots = [snapshot_one]
        for snapshot in snapshots:
            snapshot.create_snapshot()

        # Upgrades the system
        upgrading_command = ""
        if util.settings.user_os == util.utils.OS_ARCH:
            upgrading_command = ARCH_PACMAN_COMMAND
        elif util.settings.user_os == util.utils.OS_DEBIAN:
            # First, it is necessary to update the system
            sys.stdout.write("Updating the system. Please wait...")
            sys.stdout.write("\n")
            util.utils.execute_command(DEBIAN_APT_UPDATE_COMMAND, console=True)
            sys.stdout.write("\n")
            upgrading_command = DEBIAN_APT_UPGRADE_COMMAND

        util.utils.execute_command(upgrading_command, console=True)

        # Todo: Removes all the snapshots not needed any more

        self.__logger.info("System upgrading process finished.")
        sys.stdout.write("System upgrading process finished. You can close the terminal output now.")
