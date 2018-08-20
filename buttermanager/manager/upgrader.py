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
import window.windows
from PyQt5.QtCore import QThread, pyqtSignal


class Upgrader(QThread):
    """Indepented thread that will run the system upgrading process.

    """
    # Attributes
    # pyqtSignal that will be emitted when this class requires to display
    # a single information window on the screen
    show_one_window = pyqtSignal('bool')

    # Constructor
    def __init__(self):
        QThread.__init__(self)

    # Methods
    def run(self):
        # Main window will be hidden
        self.on_show_one_window(True)
        console_window = window.windows.ConsoleWindow(None)
        # Displaying console window
        console_window.show()

        # Upgrading the filesystem
        # self.__balance_filesystem()
        # Todo:
        #print("This is a tes!!!!!!")

        # Hiding console window
        # console_window.hide()

        # Main window will be shown again
        # self.on_show_one_window(False)

    def on_show_one_window(self, one_window):
        """Emits a QT Signal to hide or show the rest of application windows.

        Arguments:
            one_window (boolean): Information window should be unique?.
        """
        self.show_one_window.emit(one_window)
