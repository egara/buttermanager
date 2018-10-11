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
import sys
import util.utils
from PyQt5.QtCore import QThread, pyqtSignal
import util.utils
import util.settings

# Constants
ARCH_PACMAN_REFRESH_REPOSITORIES = "sudo -S pacman -Sy"
ARCH_PACMAN_CHECK_UPDATES = "sudo -S pacman -Qu"
ARCH_PACMAN_UPGRADE_COMMAND = "sudo -S pacman -Syu --noconfirm"
DEBIAN_APT_UPDATE_COMMAND = "sudo -S apt update"
DEBIAN_APT_UPGRADE_COMMAND = "sudo -S apt upgrade -y"
ARCH_YAOURT_UPGRADE_COMMAND = "yaourt -Syua --noconfirm"
ARCH_YAOURT_COMMAND = "yaourt"
ARCH_YAY_UPGRADE_COMMAND = "yay -Syu --noconfirm"
ARCH_YAY_COMMAND = "yay"
ARCH_TRIZEN_UPGRADE_COMMAND = "trizen -Syua --noconfirm"
ARCH_TRIZEN_COMMAND = "trizen"
SNAP_COMMAND = "snap"
SNAP_UPGRADE_COMMAND = "sudo -S snap refresh"


class Upgrader(QThread):
    """Independent thread that will run the system upgrading process.

    """
    # Attributes

    # pyqtSignal that will be emitted when this class requires that main
    # window disables all the buttons
    disable_buttons = pyqtSignal()

    # pyqtSignal that will be emitted when this class requires that main
    # window enables all the buttons
    enable_buttons = pyqtSignal()

    # pyqtSignal that will be emitted when this class requires that main
    # window refreshes GUI
    refresh_gui = pyqtSignal()

    # Constructor
    def __init__(self, dont_remove_snapshots, include_aur, include_snap):
        QThread.__init__(self)
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        # Dont' remove snapshots when upgrading the system
        self.__dont_remove_snapthosts = dont_remove_snapshots
        # Include AUR packages upgrade
        self.__include_aur = include_aur
        # Include snap packages upgrade
        self.__include_snap = include_snap

    # Methods
    def run(self):
        # Upgrading the system
        self.__upgrade_system()

    def __upgrade_system(self):
        """Wraps all the operations to upgrade the system.

        """
        # Check for updates
        if self.__check_updates():
            # There are system updates
            # Starting the upgrading process. Disabling all the buttons.
            self.on_disable_gui_buttons()

            sys.stdout.write("\n")
            sys.stdout.write("--------")
            sys.stdout.write("\n")
            self.__logger.info("Starting system upgrading process.")
            sys.stdout.write("Starting system upgrading process. Please wait...")
            sys.stdout.write("\n")
            sys.stdout.write("--------")
            sys.stdout.write("\n")

            # Creates all the snapshots needed before upgrading the system

            for snapshot in util.settings.subvolumes:
                snapshot.create_snapshot()

            # Upgrades the system
            upgrading_command = ""
            if util.settings.user_os == util.utils.OS_ARCH:
                upgrading_command = ARCH_PACMAN_UPGRADE_COMMAND
            elif util.settings.user_os == util.utils.OS_DEBIAN:
                # First, it is necessary to update the system
                sys.stdout.write("\n")
                sys.stdout.write("--------")
                sys.stdout.write("\n")
                sys.stdout.write("Updating the system. Please wait...")
                sys.stdout.write("\n")
                util.utils.execute_command(DEBIAN_APT_UPDATE_COMMAND, console=True)
                sys.stdout.write("\n")
                upgrading_command = DEBIAN_APT_UPGRADE_COMMAND

            sys.stdout.write("Upgrading the system. Please wait...")
            sys.stdout.write("\n")
            util.utils.execute_command(upgrading_command, console=True)

            # Upgrades AUR if distro is ArchLinux or derivatives
            if util.settings.user_os == util.utils.OS_ARCH:
                if self.__include_aur:
                    sys.stdout.write("\n")
                    sys.stdout.write("--------")
                    sys.stdout.write("\n")
                    sys.stdout.write("Updating AUR packages if it is needed. Please wait...")
                    sys.stdout.write("\n")
                    if util.utils.exist_program(ARCH_YAY_COMMAND):
                        util.utils.execute_command(ARCH_YAY_UPGRADE_COMMAND, console=True)
                    elif util.utils.exist_program(ARCH_TRIZEN_COMMAND):
                        util.utils.execute_command(ARCH_TRIZEN_UPGRADE_COMMAND, console=True)
                    elif util.utils.exist_program(ARCH_YAOURT_COMMAND):
                        util.utils.execute_command(ARCH_YAOURT_UPGRADE_COMMAND, console=True)

            # Upgrades snap packages
            if self.__include_snap:
                if util.utils.exist_program(SNAP_COMMAND):
                    sys.stdout.write("\n")
                    sys.stdout.write("--------")
                    sys.stdout.write("\n")
                    sys.stdout.write("Updating snaps. Please wait...")
                    sys.stdout.write("\n")
                    util.utils.execute_command(SNAP_UPGRADE_COMMAND, console=True)

            # Removes all the snapshots not needed any more it it is needed
            if not self.__dont_remove_snapthosts:
                sys.stdout.write("\n")
                sys.stdout.write("--------")
                sys.stdout.write("\n")
                sys.stdout.write("Removing old snapshots if it is needed. Please wait...")
                sys.stdout.write("\n")
                for snapshot in util.settings.subvolumes:
                    snapshot.delete_snapshots(util.settings.snapshots_to_keep)

            sys.stdout.write("\n")
            sys.stdout.write("--------")
            sys.stdout.write("\n")
            self.__logger.info("System upgrading process finished.")
            sys.stdout.write("System upgrading process finished. You can close the terminal output now.")

            # Refreshing GUI
            self.on_refresh_gui()

        else:
            # There are not system updates
            self.__logger.info("Your system is up to date.")
            sys.stdout.write("Your system is up to date. You can close the terminal output now.")

        # Finishing the upgrading process. Enabling all the buttons.
        self.on_enable_gui_buttons()

    def on_disable_gui_buttons(self):
        """Emits a QT Signal to disable all the buttons in main window.

        """
        self.disable_buttons.emit()

    def on_enable_gui_buttons(self):
        """Emits a QT Signal to enable all the buttons in main window.

        """
        self.enable_buttons.emit()

    def on_refresh_gui(self):
        """Emits a QT Signal to refresh filesystem statistics in main window.

        """
        self.refresh_gui.emit()

    def __check_updates(self):
        self.__logger.info("Checking for system updates.")
        sys.stdout.write("Checking for system updates.")
        sys.stdout.write("\n")
        sys.stdout.write("--------")
        sys.stdout.write("\n")

        updates = False
        if util.settings.user_os == util.utils.OS_ARCH:
            refresh_repositories_command = ARCH_PACMAN_REFRESH_REPOSITORIES
            util.utils.execute_command(refresh_repositories_command)
            check_for_updates_command = ARCH_PACMAN_CHECK_UPDATES
            commandline_output = util.utils.execute_command(check_for_updates_command)

            for line in commandline_output.split("\n"):
                if line:
                    updates = True

        else:
            # TODO: Take into account Debian based distro
            updates = True

        return updates
