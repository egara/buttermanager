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

import sys
import filesystem.filesystem
import util.buttermanager_utils
import util.settings
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5 import uic


# Class inherited from QMainWindow (Window constructor)
class ButtermanagerMainWindow(QMainWindow):
    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        # Configuring the application
        self.configure()
        # Logger
        self.__logger = util.buttermanager_utils.Logger(self.__class__.__name__).get()
        # Initializing the application
        self.initialize()

    def configure(self):
        """Configures the application.

        """
        buttermanager_configurator = util.buttermanager_utils.ConfigManager()
        buttermanager_configurator.configure()

    def initialize(self):
        """Initializes the Graphic User Interface.

        """
        try:
            # Loading User Interface
            uic.loadUi("ui/MainWindow.ui", self)

            # Setting maximum and minimum  size for the main window
            self.setMinimumHeight(550)
            self.setMinimumWidth(800)
            self.setMaximumHeight(550)
            self.setMaximumWidth(800)

            # Centering the window
            qt_rectangle = self.frameGeometry()
            center_point = QDesktopWidget().availableGeometry().center()
            qt_rectangle.moveCenter(center_point)
            self.move(qt_rectangle.topLeft())

            # Retrieving BTRFS Filesystems uuid
            uuid_filesystems = filesystem.filesystem.get_btrfs_filesystems()
            self.combobox_filesystem.addItems(uuid_filesystems)
            current_filesystem = filesystem.filesystem.Filesystem(uuid_filesystems[0])
            self.__logger.info("BTRFS filesystems found in the system:")
            self.__logger.info(str(current_filesystem))

            # Button event
            self.button_balance.clicked.connect(self.balanceFs)

            # Showing main window
            self.show()

        except util.buttermanager_utils.NoCommandFound:
            # Todo: Logging
            self.__logger.info("The application couldn't start normally. There are some programs needed that are not "
                               "installed.")
            self.__logger.info("Please, install these programs and start ButterManager again.")
            # Exits the application
            sys.exit()

    def balanceFs(self):
        # Todo: Do it right
        list1 = ["One", "Two"]
        self.combobox_filesystem.addItems(list1)


# Creating application instance
application = QApplication(sys.argv)
# Creating main window instance
butter_manager_window = ButtermanagerMainWindow(None)
# Launching the application
application.exec_()