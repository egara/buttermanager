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
from PyQt5.QtWidgets import QApplication, QMainWindow
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
        self.show()

# Creating application instance
application = QApplication(sys.argv)
# Creating main window instance
butter_manager_window = ButtermanagerMainWindow(None)
# Launching the application
application.exec_()