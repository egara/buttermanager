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
import manager
import sys
import urllib.request
import util.settings
import util.utils
from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError

# Constants
ARCH_PACMAN_REFRESH_REPOSITORIES = "sudo -S pacman -Sy"
ARCH_PACMAN_CHECK_UPDATES = "sudo -S pacman -Qu"
ARCH_PACMAN_UPGRADE_COMMAND = "sudo -S pacman -Syu --noconfirm"
DEBIAN_APT_UPDATE_COMMAND = "sudo -S apt update"
DEBIAN_APT_UPGRADE_COMMAND = "sudo -S apt upgrade -y"
DEBIAN_APT_CHECK_UPDATES = "sudo -S apt list --upgradable"
ARCH_YAOURT_UPGRADE_COMMAND = "yaourt -Syua --noconfirm"
ARCH_YAOURT_COMMAND = "yaourt"
ARCH_YAY_UPGRADE_COMMAND = "yay -Syua --noconfirm"
ARCH_YAY_COMMAND = "yay"
ARCH_TRIZEN_UPGRADE_COMMAND = "trizen -Syua --noconfirm"
ARCH_TRIZEN_COMMAND = "trizen"
SNAP_COMMAND = "snap"
SNAP_UPGRADE_COMMAND = "sudo -S snap refresh"
SUSE_ZYPPER_UPGRADE_COMMAND = "sudo -S zypper -n update"
SUSE_ZYPPER_CHECK_UPDATES = "sudo -S zypper list-updates"
FEDORA_DNF_UPGRADE_COMMAND = "sudo -S dnf upgrade --refresh --assumeyes"
FEDORA_DNF_CHECK_UPDATES = "sudo -S dnf check-update"


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
    def __init__(self, dont_remove_snapshots, include_aur, include_snap, snapshots):
        QThread.__init__(self)
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        # Dont' remove snapshots when upgrading the system
        self.__dont_remove_snapthosts = dont_remove_snapshots
        # Include AUR packages upgrade
        self.__include_aur = include_aur
        # Include snap packages upgrade
        self.__include_snap = include_snap
        # Create and delete snapshots
        self.__snapshots = snapshots

    # Methods
    def run(self):
        # Upgrading the system
        self.__upgrade_system()

    def __upgrade_system(self):
        """Wraps all the operations to upgrade the system.

        """
        # Check for updates
        if check_updates():
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
            # only if it is needed
            if self.__snapshots:
                for snapshot in util.settings.subvolumes:
                    util.settings.subvolumes[snapshot].create_snapshot()

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
            elif util.settings.user_os == util.utils.OS_SUSE:
                upgrading_command = SUSE_ZYPPER_UPGRADE_COMMAND
            elif util.settings.user_os == util.utils.OS_FEDORA:
                upgrading_command = FEDORA_DNF_UPGRADE_COMMAND

            if upgrading_command:
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
            if self.__snapshots:
                if not self.__dont_remove_snapthosts:
                    sys.stdout.write("\n")
                    sys.stdout.write("--------")
                    sys.stdout.write("\n")
                    sys.stdout.write("Removing old snapshots if it is needed. Please wait...")
                    sys.stdout.write("\n")
                    for snapshot in util.settings.subvolumes:
                        util.settings.subvolumes[snapshot].delete_snapshots(util.settings.snapshots_to_keep)

            sys.stdout.write("\n")
            sys.stdout.write("--------")
            sys.stdout.write("\n")
            self.__logger.info("System upgrading process finished.")
            sys.stdout.write("System upgrading process finished. You can close the terminal output now.")
            sys.stdout.write("\n")
            sys.stdout.write("\n")

            # Refreshing GUI
            self.on_refresh_gui()

        else:
            # There are not system updates
            self.__logger.info("Your system is up to date.")
            sys.stdout.write("Your system is up to date. You can close the terminal output now.")
            sys.stdout.write("\n")
            sys.stdout.write("\n")

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


class UpdatesChecker(QThread):
    """Independent thread that will run the system checking for updates.

    """
    # Attributes

    # pyqtSignal that will be emitted when this class requires that main
    # window shows the updates window. The signal will emit an 'object' that,
    # in hits case, will be a list of strings.
    show_updates_window = pyqtSignal(object)

    # Constructor
    def __init__(self):
        QThread.__init__(self)
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()

    # Methods
    def run(self):
        # Checks for updates
        self.__check_updates()

    def __check_updates(self):
        """Wraps all the operations to check updates.

        First, it will check Internet connectivity for doing the operation.
        Emits a signal with the packages found. Otherwise, it won't emit this signal and
        nothing will happen.

        """
        # Checking Internet connection for 5 minutes
        tries = 0
        internet_available = self.__internet_available()

        while (not internet_available) & (tries < 60):
            self.__logger.info("Trying to reach Internet again. If there is no Internet connection in 5 minutes, this"
                               "operation will be canceled")
            self.sleep(5)
            internet_available = self.__internet_available()
            tries += 1

        # Checking updates only if Internet connection is available
        if internet_available:
            # Checking updates only if the user selected the option
            if util.settings.check_at_startup == 1:
                # Emmiting the signal only if there are updates
                if manager.upgrader.check_updates():
                    commandline_output = []
                    if util.settings.user_os == util.utils.OS_ARCH:
                        refresh_repositories_command = manager.upgrader.ARCH_PACMAN_REFRESH_REPOSITORIES
                        util.utils.execute_command(refresh_repositories_command)
                        check_for_updates_command = manager.upgrader.ARCH_PACMAN_CHECK_UPDATES
                        commandline_output = util.utils.execute_command(check_for_updates_command)

                    elif util.settings.user_os == util.utils.OS_DEBIAN:
                        check_for_updates_command = manager.upgrader.DEBIAN_APT_CHECK_UPDATES
                        commandline_output = util.utils.execute_command(check_for_updates_command)

                    elif util.settings.user_os == util.utils.OS_SUSE:
                        check_for_updates_command = manager.upgrader.SUSE_ZYPPER_CHECK_UPDATES
                        commandline_output = util.utils.execute_command(check_for_updates_command)

                    elif util.settings.user_os == util.utils.OS_FEDORA:
                        check_for_updates_command = manager.upgrader.FEDORA_DNF_CHECK_UPDATES
                        commandline_output = util.utils.execute_command(check_for_updates_command)

                    # If there are updates, emits the signal thta will be captured in buttermanager.py
                    self.show_updates_window.emit(commandline_output)
        else:
            self.__logger.error("Timeout. Checking updates process has been cancelled because there is no Intenert"
                                " connection")

    def __internet_available(self):
        """Checks Internet connection.

        Returns:
            boolean: true if there is Internet connection available; false otherwise.
        """
        self.__logger.info("Checking Internet connection. Please wait...")
        try:
            urllib.request.urlopen('https://www.google.com', timeout=1)
            self.__logger.info("Internet connection is available!")
            return True
        except urllib.error.URLError as error:
            self.__logger.error("Internet connection is not available... Error: {error}".format(error=error))
            return False

# Module's methods
def check_updates():
    """Checks for updates.

    Returns:
        boolean: true if there are updates; false otherwise.
    """
    # Logger
    logger = util.utils.Logger(sys.modules['__main__'].__file__).get()
    logger.info("Checking for system updates.")
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

    elif util.settings.user_os == util.utils.OS_DEBIAN:
        check_for_updates_command = DEBIAN_APT_CHECK_UPDATES
        commandline_output = util.utils.execute_command(check_for_updates_command)
        lines = commandline_output.split("\n")
        if len(lines) > 2:
            updates = True

    elif util.settings.user_os == util.utils.OS_SUSE:
        check_for_updates_command = SUSE_ZYPPER_CHECK_UPDATES
        commandline_output = util.utils.execute_command(check_for_updates_command)
        lines = commandline_output.split("\n")
        if len(lines) > 4:
            updates = True

    elif util.settings.user_os == util.utils.OS_FEDORA:
        check_for_updates_command = FEDORA_DNF_CHECK_UPDATES
        commandline_output = util.utils.execute_command(check_for_updates_command)
        lines = commandline_output.split("\n")
        if len(lines) > 2:
            updates = True

    else:
        updates = True

    return updates
