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
import util.utils
import util.settings
import manager.upgrader
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtGui import QCursor, QTextCursor
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QObject


class EmittingStream(QObject):

    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))


class PasswordWindow(QMainWindow):
    """Window to let the user type his/her password.

    Class inherited from QMainWindow (Window constructor)
    """
    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        # Configuring the application
        self.__buttermanager_configurator = util.utils.ConfigManager()
        self.__buttermanager_configurator.configure()
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        # Initializing the application
        self.init_ui()

    def init_ui(self):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/PasswordWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Events
        # OK button event
        self.button_ok.clicked.connect(self.load_main_window)

        # Cancel button event
        self.button_cancel.clicked.connect(self.exit)

        # Press enter within QLineEdit
        self.input_password.returnPressed.connect(self.load_main_window)

        # Showing password window
        self.show()

    def load_main_window(self):
        # Storing user's password
        util.settings.user_password = self.input_password.text()

        # Exiting password window
        self.hide()

        # Showing main window
        butter_manager_window = ButtermanagerMainWindow(self)
        butter_manager_window.show()

    def exit(self):
        # Exits the application
        self.hide()
        sys.exit()


class ButtermanagerMainWindow(QMainWindow):
    """Main window.

    Class inherited from QMainWindow (Window constructor)
    """
    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        # Current filesystem (it will be initialize in initialize method)
        self.__current_filesystem = None
        # Current filesystem uuid (it will be initialize in initialize method)
        self.__current_filesystem_uuid = None
        # Balancer that will balance the current filesystem if it is needed
        self.__balancer = None
        # Upgrader that will upgrade the system if it is needed
        self.__upgrader = None
        # Initializing the application
        self.init_ui()

        # Installing the custom output stream to write all the console content to the
        # QTextEdit component
        sys.stdout = EmittingStream(text_written=self.normal_output_written)

    def __del__(self):
        """Restores sys.stdout.

        """
        sys.stdout = sys.__stdout__

    def normal_output_written(self, text):
        """Appends text to the QTextEdit text_edit_console.

        """
        cursor = self.text_edit_console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_edit_console.setTextCursor(cursor)
        self.text_edit_console.ensureCursorVisible()

    def init_ui(self):
        """Initializes the Graphic User Interface.

        """
        try:
            # Loading User Interface
            uic.loadUi("ui/MainWindow.ui", self)

            # Setting maximum and minimum  size for the main window
            self.setMinimumHeight(490)
            self.setMinimumWidth(800)
            self.setMaximumHeight(490)
            self.setMaximumWidth(800)

            # Hiding terminal
            self.button_close_terminal.hide()
            self.text_edit_console.hide()

            # Adjusting the window
            self.adjustSize()

            # Centering the window
            qt_rectangle = self.frameGeometry()
            center_point = QDesktopWidget().availableGeometry().center()
            qt_rectangle.moveCenter(center_point)
            self.move(qt_rectangle.topLeft())

            # Retrieving BTRFS Filesystems uuid
            uuid_filesystems = filesystem.filesystem.get_btrfs_filesystems()
            self.__current_filesystem_uuid = uuid_filesystems[0]
            self.combobox_filesystem.addItems(uuid_filesystems)
            self.__current_filesystem = filesystem.filesystem.Filesystem(self.__current_filesystem_uuid)
            self.__logger.info("BTRFS filesystems found in the system:")
            self.__logger.info(str(self.__current_filesystem))

            # Displaying all the info related to the filesystem selected by default
            self.fill_filesystem_info(self.__current_filesystem)

            # Displaying snapshots
            self.fill_snapshots()

            # Button event
            self.button_balance.clicked.connect(self.balance_filesystem)
            self.button_upgrade_system.clicked.connect(self.upgrade_system)
            self.button_close_terminal.clicked.connect(self.close_terminal)

        except util.utils.NoCommandFound:
            self.__logger.info("The application couldn't start normally. There are some programs needed that are not "
                               "installed.")
            self.__logger.info("Please, install these programs and start ButterManager again.")
            # Exits the application
            sys.exit()

    def balance_filesystem(self):
        """Runs the balance method.

        """
        self.__balancer = filesystem.filesystem.BalanceManager(self.__current_filesystem.data_percentage,
                                                               self.__current_filesystem.mounted_points[0])
        self.__balancer.show_one_window.connect(self.manage_window)
        # Connecting the signal emitted by the balancer with this slot
        self.__balancer.refresh_filesystem_statistics.connect(self.refresh_filesystem_statistics)
        self.__balancer.start()

    def manage_window(self, hide):
        """Shows or hide the main window

        If some important operation (like, f.e. balancing the current filesystem) is being done, then
        the main window should be hidden in order to avoid the user click on any other button and run
        another operation until the current is finished.

        Arguments:
            hide (boolean): Hide or show the main window.
        """
        if hide:
            self.hide()
        else:
            self.show()

    def refresh_filesystem_statistics(self):
        """Refresh current filesystem statistics in the GUI.

        """
        # Calculating new values for the current filesystem
        self.__current_filesystem = filesystem.filesystem.Filesystem(self.__current_filesystem_uuid)
        # Displaying all the info related to the current filesystem
        self.fill_filesystem_info(self.__current_filesystem)

    def fill_filesystem_info(self, filesystem):
        """Fills filesystem information in the GUI.

        Arguments:
            filesystem (obj: Filesystem): Filesystem.
        """
        tooltip = "More info about the filesystem: \n \n" \
                  "Devices: {devices} \n" \
                  "Mounted points: {mounted_points}".format(devices=filesystem.devices,
                                                            mounted_points=filesystem.mounted_points)
        self.label_filesystem_info_more.setToolTip(tooltip)
        self.label_filesystem_info_more.setCursor(QCursor(Qt.WhatsThisCursor))
        self.label_filesystem_size_value.setText(filesystem.total_size)
        self.label_filesystem_allocated_value.setText(filesystem.total_allocated)
        self.progressbar_data.setValue(filesystem.data_percentage)
        self.progressbar_metadata.setValue(filesystem.metadata_percentage)
        self.progressbar_system.setValue(filesystem.system_percentage)

    def upgrade_system(self):
        """Runs the system upgrade operation.

        """
        # Setting maximum and minimum  size for the main window
        self.setMinimumHeight(800)
        self.setMinimumWidth(800)
        self.setMaximumHeight(800)
        self.setMaximumWidth(800)

        # Showing terminal
        self.button_close_terminal.show()
        self.text_edit_console.show()

        # Adjusting the window
        self.adjustSize()

        # Upgrading the system
        self.__upgrader = manager.upgrader.Upgrader()
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.disable_buttons.connect(self.__disable_buttons)
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.enable_buttons.connect(self.__enable_buttons)
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.refresh_filesystem_statistics.connect(self.refresh_filesystem_statistics)

        self.__upgrader.start()

    def close_terminal(self):
        """Runs the system upgrade operation.

        """
        # Setting maximum and minimum  size for the main window
        self.setMinimumHeight(490)
        self.setMinimumWidth(800)
        self.setMaximumHeight(490)
        self.setMaximumWidth(800)

        # Hiding terminal
        self.button_close_terminal.hide()
        self.text_edit_console.hide()

        # Adjusting the window
        self.adjustSize()

    def __disable_buttons(self):
        """Disable all the buttons of the GUI.

        """
        self.button_balance.setEnabled(False)
        self.button_upgrade_system.setEnabled(False)
        self.button_close_terminal.setEnabled(False)

    def __enable_buttons(self):
        """Enable all the buttons of the GUI.

        """
        self.button_balance.setEnabled(True)
        self.button_upgrade_system.setEnabled(True)
        self.button_close_terminal.setEnabled(True)

    def fill_snapshots(self):
        """Fills snapshots information in the GUI.

        """
        list = ['snapshot1', 'snapshot2', 'snapshot3', 'snapshot4']
        self.list_snapshots.addItems(list)


if __name__ == '__main__':
    # Creating application instance
    application = QApplication(sys.argv)
    # Creating main window instance
    password_window = PasswordWindow(None)
    # Launching the application
    application.exec_()
