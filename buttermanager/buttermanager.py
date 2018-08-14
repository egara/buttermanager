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
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QDialog, QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal


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
        # Initializing the application
        self.init_ui()

    def init_ui(self):
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
            self.__current_filesystem_uuid = uuid_filesystems[0]
            self.combobox_filesystem.addItems(uuid_filesystems)
            self.__current_filesystem = filesystem.filesystem.Filesystem(self.__current_filesystem_uuid)
            self.__logger.info("BTRFS filesystems found in the system:")
            self.__logger.info(str(self.__current_filesystem))

            # Displaying all the info related to the filesystem selected by default
            self.fill_filesystem_info(self.__current_filesystem)

            # Button event
            self.button_balance.clicked.connect(self.balance_filesystem)

        except util.utils.NoCommandFound:
            self.__logger.info("The application couldn't start normally. There are some programs needed that are not "
                               "installed.")
            self.__logger.info("Please, install these programs and start ButterManager again.")
            # Exits the application
            sys.exit()

    def balance_filesystem(self):
        """Runs the balance method.

        """
        # Displaying info
        # info_dialog = InfoWindow(self, "In progress: please wait until filesystem is balanced. "
        #                                "It will take a little bit...")
        # info_dialog.show()
        # filesystem.filesystem.balance_filesystem(
        #     filesystem.filesystem.BTRFS_BALANCE_DATA_USAGE_FILTER,
        #     self.__current_filesystem.data_percentage,
        #     self.__current_filesystem.mounted_points[0])
        # filesystem.filesystem.balance_filesystem(
        #     filesystem.filesystem.BTRFS_BALANCE_METADATA_USAGE_FILTER,
        #     self.__current_filesystem.metadata_percentage,
        #     self.__current_filesystem.mounted_points[0])

        # Closing info
        # info_dialog.hide()
        # info_dialog.close()

        # Calculating new values for the filesystem balanced
        # self.__current_filesystem = filesystem.filesystem.Filesystem(self.__current_filesystem_uuid)
        # Displaying all the info related to the filesystem recently balanced
        # self.fill_filesystem_info(self.__current_filesystem)
        self.__balancer = BalanceThread(self.__current_filesystem.data_percentage,
                                        self.__current_filesystem.mounted_points[0])
        self.__balancer.show_one_window.connect(self.manage_window)
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


class BalanceThread(QThread):
    """Indepented thread that will run the filesystem balancing process.

    """

    # Attributes
    # pyqtSignal that will be emitted when this class requires to display
    # a single information window on the screen
    show_one_window = pyqtSignal('bool')
    # pyqtSignal that will be emitted when this class requires that main
    # window refreshes current filesystem statistics
    refresh_filesystem_statistics = pyqtSignal()

    def __init__(self, percentage, mounted_point):
        QThread.__init__(self)
        self.__percentage = percentage
        self.__mounted_point = mounted_point

    def run(self):
        # Main window will be hidden
        self.on_show_one_window(True)
        info_dialog = InfoWindow(None, "Balancing '{mounted_point}' mounted point. \n"
                                       "This window will be closed automatically \n"
                                       "when the operation is done. \n \n"
                                       "Please wait...".format(mounted_point=self.__mounted_point))
        # Displaying info window
        info_dialog.show()

        # Balances the filesystem
        self.__balance_filesystem()

        # Hiding info window
        info_dialog.hide()

        # Main window will be shown again
        self.on_show_one_window(False)

        # Refreshing current filesystem statistics
        self.on_refresh_filesystem_statistics()

    def __balance_filesystem(self):
        """Wraps all the operations to balance the filesystem.

        """
        filesystem.filesystem.balance_filesystem(
            filesystem.filesystem.BTRFS_BALANCE_DATA_USAGE_FILTER,
            self.__percentage,
            self.__mounted_point)
        filesystem.filesystem.balance_filesystem(
            filesystem.filesystem.BTRFS_BALANCE_METADATA_USAGE_FILTER,
            self.__percentage,
            self.__mounted_point)


    def on_show_one_window(self, one_window):
        """Emits a QT Signal to hide or show the rest of application windows.

        Arguments:
            one_window (boolean): Information window should be unique?.
        """
        self.show_one_window.emit(one_window)

    def on_refresh_filesystem_statistics(self):
        """Emits a QT Signal to refresh filesystem statistics in main window.

        """
        self.refresh_filesystem_statistics.emit()

class InfoWindow(QDialog):
    """Window to display information.

    """
    # Constructor
    def __init__(self, parent, information):
        QDialog.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint)
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


if __name__ == '__main__':
    # Creating application instance
    application = QApplication(sys.argv)
    # Creating main window instance
    password_window = PasswordWindow(None)
    # Launching the application
    application.exec_()
