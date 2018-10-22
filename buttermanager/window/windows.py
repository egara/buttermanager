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
from PyQt5.QtWidgets import QDesktopWidget, QDialog, QMainWindow, QFileDialog
from PyQt5 import uic, QtCore
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QIcon


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


class SnapshotWindow(QMainWindow):
    """Window to select a subvolume to take a snapshot.

    """
    # pyqtSignal that will be emitted when this class requires that main
    # window refreshes GUI
    refresh_gui = pyqtSignal()

    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()

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
        for subvolume in util.settings.subvolumes:
            subvolumes.append(subvolume)
        self.combobox_subvolumes.addItems(subvolumes)

        # Button events
        self.radiobutton_all_subvolumes.clicked.connect(self.enable_all_subvolumes)
        self.radiobutton_one_subvolume.clicked.connect(self.enable_one_subvolume)
        self.button_ok.clicked.connect(self.take_snapshot)
        self.button_cancel.clicked.connect(self.cancel)

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

    def take_snapshot(self):
        """Takes a snapshot of the selected subvolume.

        """
        if self.radiobutton_all_subvolumes.isChecked():
            for subvolume in util.settings.subvolumes:
                util.settings.subvolumes[subvolume].create_snapshot()
        else:
            subvolume_selected = self.combobox_subvolumes.currentText()
            util.settings.subvolumes[subvolume_selected].create_snapshot()

        # Refreshing GUI
        self.on_refresh_gui()

        # Closes the window
        self.cancel()

    def cancel(self):
        """Closes the window.

        """
        self.close()

    def on_refresh_gui(self):
        """Emits a QT Signal to refresh main window GUI.

        """
        self.refresh_gui.emit()


class SubvolumeWindow(QMainWindow):
    """Window to add a new subvolume to be managed byt the application.

    """
    # pyqtSignal that will be emitted when this class requires that main
    # window refreshes GUI
    refresh_gui = pyqtSignal()

    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()

        # Initializing the window
        self.init_ui()

    def init_ui(self):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/SubvolumeWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Loading icons
        self.button_add_subvolume_orig.setIcon(QIcon('images/open_folder_24px_icon.png'))
        self.button_add_subvolume_orig.setIconSize(QSize(24, 24))
        self.button_add_subvolume_dest.setIcon(QIcon('images/open_folder_24px_icon.png'))
        self.button_add_subvolume_dest.setIconSize(QSize(24, 24))

        # Button events
        self.button_add_subvolume_orig.clicked.connect(self.add_subvolume_orig)
        self.button_ok.clicked.connect(self.add_subvolume)
        self.button_cancel.clicked.connect(self.cancel)

    def add_subvolume_orig(self):
        # directory = str(QFileDialog.getExistingDirectory(self, "Select the subvolume"))
        # print(directory)

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec_():
            self.line_subvolume_origin.setText(dialog.selectedFiles())

    def add_subvolume(self):
        """Adds a new subvolume to be managed by the application.

        """
        # Todo: Do it!!

        # Refreshing GUI
        self.on_refresh_gui()

        # Closes the window
        self.cancel()

    def cancel(self):
        """Closes the window.

        """
        self.close()

    def on_refresh_gui(self):
        """Emits a QT Signal to refresh main window GUI.

        """
        self.refresh_gui.emit()