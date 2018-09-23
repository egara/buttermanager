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

"""This module gathers all the additional windows for displaying information in the application.

"""
import util.settings
from PyQt5.QtWidgets import QDesktopWidget, QDialog
from PyQt5 import uic, QtCore


class InfoWindow(QDialog):
    """Window to display information.

    """
    # Constructor
    def __init__(self, parent, information):
        QDialog.__init__(self, parent)
        # Setting window flags, f.i. this window won't have a close button
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.parent = parent

        # Initializing the window
        self.init_ui(information)

    def init_ui(self, information):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/InfoWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Setting information
        self.label_info.setText(information)


class SnapshotWindow(QDialog):
    """Window to select a subvolume to take a snapshot.

    """
    # Constructor
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.__snapshots = {}
        for subvolume in util.settings.subvolumes:
            self.__snapshots[subvolume.subvolume_origin] = subvolume

        # Initializing the window
        self.init_ui()

    def init_ui(self):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/SnapshotWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Loading GUI components
        self.enable_all_subvolumes()

        # Retrieveing subvolumes
        subvolumes = []
        for subvolume in self.__snapshots:
            subvolumes.append(subvolume)
        self.combobox_subvolumes.addItems(subvolumes)

        # Button events
        self.radiobutton_all_subvolumes.clicked.connect(self.enable_all_subvolumes)
        self.radiobutton_one_subvolume.clicked.connect(self.enable_one_subvolume)

    def enable_all_subvolumes(self):
        """Enables all subvolumes option.

        """
        self.radiobutton_all_subvolumes.setEnabled(True)
        self.radiobutton_all_subvolumes.setChecked(True)
        self.radiobutton_one_subvolume.setEnabled(True)
        self.radiobutton_one_subvolume.setChecked(False)
        self.combobox_subvolumes.setEnabled(False)

    def enable_one_subvolume(self):
        """Enables one subvolume option.

        """
        self.radiobutton_all_subvolumes.setEnabled(True)
        self.radiobutton_all_subvolumes.setChecked(False)
        self.radiobutton_one_subvolume.setEnabled(True)
        self.radiobutton_one_subvolume.setChecked(True)
        self.combobox_subvolumes.setEnabled(True)
