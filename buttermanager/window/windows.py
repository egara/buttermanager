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
import manager.upgrader
import sys
from PyQt5.QtWidgets import QDesktopWidget, QDialog, QMainWindow, QFileDialog
from PyQt5 import uic, QtCore
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QTextCursor


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


class GeneralInfoWindow(QDialog):
    """Window to display generic information.

    """
    # Constructor
    def __init__(self, parent, information):
        QDialog.__init__(self, parent)
        # Setting window flags, f.i. this window won't have a close button
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.parent = parent

        # Initializing the window
        self.init_ui(information)

    def init_ui(self, information):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/GeneralInfoWindow.ui", self)

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
        self.button_add_subvolume_dest.clicked.connect(self.add_subvolume_dest)
        self.button_ok.clicked.connect(self.add_subvolume)
        self.button_cancel.clicked.connect(self.cancel)

    def add_subvolume_orig(self):
        """Adds the origin path for the subvolume to manage.

        """
        # Creating a QFileDialog to select the directory
        # Only directories will be allowed
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if file_dialog.exec_():
            self.line_subvolume_origin.setText(file_dialog.selectedFiles()[0])

    def add_subvolume_dest(self):
        """Adds the destination where the snapshot of the subvolume will be stored.

        """
        # Creating a QFileDialog to select the directory
        # Only directories will be allowed
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if file_dialog.exec_():
            self.line_subvolume_dest.setText(file_dialog.selectedFiles()[0])

    def add_subvolume(self):
        """Adds a new subvolume to be managed by the application.

        """
        # All the fields must be filled
        origin = self.line_subvolume_origin.text()
        dest = self.line_subvolume_dest.text()
        name = self.line_snapshot_name.text()
        if not origin or not dest or not name:
            info_dialog = GeneralInfoWindow(self, "Please, fill all the fields.")
            info_dialog.show()
        else:
            # Adding a new subvolume
            util.settings.properties_manager.set_subvolume(origin, dest, name)

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


class UpdatesWindow(QMainWindow):
    """Window to check new updates and start the upgrading process.

    """
    # pyqtSignal that will be emitted when this class requires to upgrade
    # the system
    upgrade_system = pyqtSignal()

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
        uic.loadUi("ui/UpdatesWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Checking updates
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

        # TODO: remove
        lines = commandline_output.split("\n")
        self.__logger.info("Heyyyyyyyyy:" + str(lines))
        self.__logger.info("Number of lines:" + str(len(lines)))

        for line in commandline_output.split("\n"):
            self.text_edit_console.moveCursor(QTextCursor.End)
            self.text_edit_console.insertHtml(line + '<br>')
            self.text_edit_console.moveCursor(QTextCursor.End)

        # Button events
        self.button_upgrade_system.clicked.connect(self.full_system_upgrade)
        self.button_cancel.clicked.connect(self.cancel)

    def full_system_upgrade(self):
        """Upgrades the system.

        """
        # The main window will upgrade the system
        self.upgrade_system.emit()

        # Closes the window
        self.cancel()

    def cancel(self):
        """Closes the window.

        """
        self.close()


class ProblemsFoundWindow(QMainWindow):
    """Window to display problems found.

    Those problems will cause the application exits.
    """

    # Constructor
    def __init__(self, parent, information):
        QMainWindow.__init__(self, parent)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.parent = parent

        # Initializing the window
        self.init_ui(information)

    def init_ui(self, information):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/ProblemsFoundWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Setting information
        self.label_info.setText(information)

        # Button events
        self.button_ok.clicked.connect(self.exit)

    def exit(self):
        """Exits the application.

        """
        self.close()
        sys.exit()
