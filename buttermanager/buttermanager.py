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
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QDesktopWidget
from PyQt5 import uic


# Class inherited from QMainWindow (Window constructor)
class ButtermanagerMainWindow(QMainWindow):
    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
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

        # Retrieving BTRFS Filesystems
        self.combobox_filesystem.addItems(filesystem.filesystem.get_btrfs_filesystems())

        # Button event
        self.button_balance.clicked.connect(self.balanceFs)

        # Showing main window
        self.show()

    def balanceFs(self):
        list1 = ["One", "Two"]
        self.combobox_filesystem.addItems(list1)


# Creating application instance
application = QApplication(sys.argv)
# Creating main window instance
butter_manager_window = ButtermanagerMainWindow(None)
# Launching the application
application.exec_()