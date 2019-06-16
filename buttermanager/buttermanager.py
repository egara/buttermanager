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

import filesystem.filesystem
import filesystem.snapshot
import manager.upgrader
import os
import sys
import time
import util.utils
import util.settings
import window.windows
from functools import partial
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtGui import QCursor, QTextCursor, QIcon, QPixmap, QDesktopServices
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize, QUrl

# Constants
SNAP_COMMAND = "snap"


class EmittingStream(QObject):

    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass


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

        # Setting the window icon
        self.setWindowIcon(QIcon('images/buttermanager50.png'))

        # Setting maximum and minimum  size for the main window
        self.setMinimumHeight(240)
        self.setMinimumWidth(320)
        self.setMaximumHeight(240)
        self.setMaximumWidth(320)

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

        # Creating main window
        # Main window will only be displayed if everything goes right
        ButtermanagerMainWindow(self)

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
        # Updates checker that will check for updates if it is needed
        self.__updates_checker = None
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

            # Setting the window icon
            self.setWindowIcon(QIcon('images/buttermanager50.png'))

            # Setting maximum and minimum  size for the main window
            self.setMinimumHeight(490)
            self.setMinimumWidth(800)
            self.setMaximumHeight(490)
            self.setMaximumWidth(800)

            # Hiding terminal and buttons
            self.button_close_terminal.hide()
            self.button_save_log.hide()
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
            if len(uuid_filesystems) > 0:
                self.__current_filesystem_uuid = uuid_filesystems[0]
                self.combobox_filesystem.addItems(uuid_filesystems)
                self.__current_filesystem = filesystem.filesystem.Filesystem(self.__current_filesystem_uuid)
                self.__logger.info("BTRFS filesystems found in the system:")
                self.__logger.info(str(self.__current_filesystem))

                # Space labels
                self.label_space_ok.setStyleSheet('color: green')
                self.label_space_danger.setStyleSheet('color: orange')
                self.label_space_ko.setStyleSheet('color: red')
                self.label_space_data_danger.setStyleSheet('color: orange')

                # Displaying all the info related to the filesystem selected by default
                # and labels (show_labels will be invoked within fill_filesystem_info method)
                self.fill_filesystem_info(self.__current_filesystem)

                # Displaying snapshots
                self.fill_snapshots()

                # Displaying logs
                self.fill_logs()

                # Retrieving subvolumes
                self.fill_subvolumes()

                # BEGIN -- Displaying settings options
                # Retrieving snapshots to keep
                self.spinbox_snapshots_to_keep.setValue(util.settings.snapshots_to_keep)

                # Retrieving remove snapshots decision
                if util.settings.remove_snapshots == 0:
                    self.checkbox_dont_remove_snapshots.setChecked(True)
                else:
                    self.checkbox_dont_remove_snapshots.setChecked(False)

                if self.checkbox_dont_remove_snapshots.isChecked():
                    self.label_snapshots_to_keep.hide()
                    self.spinbox_snapshots_to_keep.hide()
                else:
                    self.label_snapshots_to_keep.show()
                    self.spinbox_snapshots_to_keep.show()

                # Retrieving snap packages upgrade decision
                if util.settings.snap_packages == 0:
                    self.checkbox_snap.setChecked(False)
                else:
                    self.checkbox_snap.setChecked(True)

                if util.utils.exist_program(SNAP_COMMAND):
                    self.checkbox_snap.show()
                else:
                    self.checkbox_snap.hide()

                # Retrieving AUR packages upgrade decision
                if util.settings.aur_repository == 0:
                    self.checkbox_aur.setChecked(False)
                else:
                    self.checkbox_aur.setChecked(True)

                if util.settings.user_os == util.utils.OS_ARCH:
                    self.checkbox_aur.show()
                else:
                    self.checkbox_aur.hide()

                # Retrieving check for updates at startup decision
                if util.settings.check_at_startup == 0:
                    self.checkbox_startup.setChecked(False)
                else:
                    self.checkbox_startup.setChecked(True)

                if util.settings.user_os == util.utils.OS_ARCH or \
                        util.settings.user_os == util.utils.OS_DEBIAN or \
                        util.settings.user_os == util.utils.OS_SUSE or \
                        util.settings.user_os == util.utils.OS_FEDORA:
                    self.checkbox_startup.show()
                else:
                    self.checkbox_startup.hide()
                # END -- Displaying settings options

                # Setting buttons and icons
                # Snapshot buttons
                self.button_take_snapshot.setIcon(QIcon('images/add_16px_icon.png'))
                self.button_take_snapshot.setIconSize(QSize(16, 16))
                self.button_delete_snapshot.setIcon(QIcon('images/remove_16px_icon.png'))
                self.button_delete_snapshot.setIconSize(QSize(16, 16))

                # Logs buttons
                self.button_view_log.setIcon(QIcon('images/view_24px_icon.png'))
                self.button_view_log.setIconSize(QSize(24, 24))
                self.button_delete_log.setIcon(QIcon('images/remove_16px_icon.png'))
                self.button_delete_log.setIconSize(QSize(16, 16))

                # Subvolume buttons
                self.button_save_subvolume.setIcon(QIcon('images/accept_16px_icon.png'))
                self.button_save_subvolume.setIconSize(QSize(16, 16))
                self.button_edit_subvolume.setIcon(QIcon('images/edit_16px_icon.png'))
                self.button_edit_subvolume.setIconSize(QSize(16, 16))
                self.button_delete_subvolume.setIcon(QIcon('images/remove_16px_icon.png'))
                self.button_delete_subvolume.setIconSize(QSize(16, 16))
                self.refresh_subvolume_buttons()

                # Displaying logo within About tab
                self.label_logo.setPixmap(QPixmap('images/buttermanager50.png'))

                # Button events
                self.button_balance.clicked.connect(self.balance_filesystem)
                self.button_upgrade_system.clicked.connect(self.upgrade_system)
                self.button_close_terminal.clicked.connect(self.close_terminal)
                self.button_save_log.clicked.connect(self.save_log)
                self.button_take_snapshot.clicked.connect(self.take_snapshot)
                self.button_delete_snapshot.clicked.connect(self.delete_snapshots)
                self.button_delete_log.clicked.connect(self.delete_logs)
                self.button_view_log.clicked.connect(self.view_log)
                self.checkbox_dont_remove_snapshots.clicked.connect(self.dont_remove_snapshots)
                self.spinbox_snapshots_to_keep.valueChanged.connect(self.snapshots_to_keep_valuechange)
                self.checkbox_snap.clicked.connect(self.include_snap)
                self.checkbox_aur.clicked.connect(self.include_aur)
                self.checkbox_startup.clicked.connect(self.include_startup)
                self.button_add_subvolume.clicked.connect(self.add_subvolume)
                self.button_edit_subvolume.clicked.connect(self.edit_subvolume)
                self.button_save_subvolume.clicked.connect(self.save_subvolume)
                self.button_delete_subvolume.clicked.connect(self.delete_subvolume)
                self.combobox_subvolumes.currentTextChanged.connect(self.on_combobox_subvolumes_changed)
                self.button_github.clicked.connect(self.go_to_github)

                # If no subvolumes are defined, warning the user
                if len(util.settings.subvolumes) == 0:
                    info_dialog = window.windows.GeneralInfoWindow(self, "Warning: You don't have any subvolumes "
                                                                         "added.\n"
                                                                         "If you upgrade the filesystem, no snapshots "
                                                                         "will\n"
                                                                         "be created. If you want to create "
                                                                         "automatically\n"
                                                                         "snapshots during the upgrading process, "
                                                                         "go to\n"
                                                                         "Settings and Add a subvolume.")
                    info_dialog.show()

                # If everything goes right, the main window is displayed
                self.show()

                # Show the updates window only if the user wants to and if there are updates
                self.check_updates()

            else:
                self.__logger.info("The application couldn't start normally. No BTRFS file system found.")

                info_dialog = window.windows.ProblemsFoundWindow(self, "No BTRFS file system found. \n"
                                                                       "The application will be closed.")
                info_dialog.show()

        except util.utils.NoCommandFound:
            self.__logger.info("The application couldn't start normally. There are some programs needed that are not "
                               "installed.")
            self.__logger.info("Please, install these programs and start ButterManager again.")

            info_dialog = window.windows.ProblemsFoundWindow(self, "These programs need to be installed for \n"
                                                                   "the proper functioning of ButterManager:\n"
                                                                   "btrfs, findmnt.\n")
            info_dialog.show()

    def check_updates(self):
        """Creates the updates checker that will start in another thread and check system updates.

        """
        self.__updates_checker = manager.upgrader.UpdatesChecker()
        self.__updates_checker.show_updates_window.connect(self.show_updates_window)
        self.__updates_checker.start()

    def show_updates_window(self, command_line_output):
        """ Shows a new window with all the packages to  be updated.

        Once the updates_checker knows all the packages that need to be updated, a new
        UpdatesWindow will be opened from the main GUI thread.

        Arguments:
            command_line_output (list(:obj:`str`)): Packages to be updated. One per line.
        """
        updates_window = window.windows.UpdatesWindow(self, command_line_output)
        updates_window.upgrade_system.connect(self.upgrade_system)
        updates_window.upgrade_system_without_snanpshots.connect(partial(self.upgrade_system, False))
        updates_window.show()

    def balance_filesystem(self):
        """Runs the balance method.

        """
        self.__balancer = filesystem.filesystem.BalanceManager(self.__current_filesystem.data_percentage,
                                                               self.__current_filesystem.metadata_percentage,
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
        # self.progressbar_system.setValue(filesystem.system_percentage)

        # Showing labels
        self.show_space_labels()

    def upgrade_system(self, snapshots=True):
        """Runs the system upgrade operation.

        Arguments:
            snapshots (boolean): Create and delete snapshots when the upgrading process is executed.
        """
        # Setting maximum and minimum  size for the main window
        self.setMinimumHeight(800)
        self.setMinimumWidth(800)
        self.setMaximumHeight(800)
        self.setMaximumWidth(800)

        # Showing terminal and buttons
        self.button_close_terminal.show()
        self.button_save_log.show()
        self.text_edit_console.show()

        # Adjusting the window
        self.adjustSize()

        # Checking if there is any subvolume defined by the user
        if len(util.settings.subvolumes) == 0:
            snapshots = False

        # Gathering user settings
        dont_remove_snapshots = self.checkbox_dont_remove_snapshots.isChecked()
        include_aur = False
        if util.settings.user_os == util.utils.OS_ARCH:
            include_aur = self.checkbox_aur.isChecked()
        include_snap = False
        if util.utils.exist_program(SNAP_COMMAND):
            include_snap = self.checkbox_snap.isChecked()
        # Upgrading the system
        self.__upgrader = manager.upgrader.Upgrader(dont_remove_snapshots, include_aur, include_snap, snapshots)
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.disable_buttons.connect(self.__disable_buttons)
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.enable_buttons.connect(self.__enable_buttons)
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.refresh_gui.connect(self.refresh_gui)

        self.__upgrader.start()

    def close_terminal(self):
        """Closes terminal.

        It will restore the proper windows size

        """
        # Setting maximum and minimum  size for the main window
        self.setMinimumHeight(490)
        self.setMinimumWidth(800)
        self.setMaximumHeight(490)
        self.setMaximumWidth(800)

        # Hiding terminal and buttons
        self.button_close_terminal.hide()
        self.button_save_log.hide()
        self.text_edit_console.hide()

        # Adjusting the window
        self.adjustSize()

    def save_log(self):
        """Saves the current content of the terminal into a file.

        """
        log = self.text_edit_console.toPlainText()
        current_date = time.strftime('%Y%m%d')
        log_name = "{current_date}.txt".format(current_date=current_date)
        log_full_path = os.path.join(util.settings.logs_path, log_name)
        with open(log_full_path, 'a') as file:
            file.write(log)

    def __disable_buttons(self):
        """Disables all the buttons of the GUI.

        """
        self.button_balance.setEnabled(False)
        self.button_upgrade_system.setEnabled(False)
        self.button_close_terminal.setEnabled(False)
        self.checkbox_dont_remove_snapshots.setEnabled(False)
        self.button_take_snapshot.setEnabled(False)
        self.button_delete_snapshot.setEnabled(False)
        self.button_add_subvolume.setEnabled(False)
        self.button_delete_subvolume.setEnabled(False)
        self.button_edit_subvolume.setEnabled(False)
        self.button_save_subvolume.setEnabled(False)

    def __enable_buttons(self):
        """Enable all the buttons of the GUI.

        """
        self.button_balance.setEnabled(True)
        self.button_upgrade_system.setEnabled(True)
        self.button_close_terminal.setEnabled(True)
        self.checkbox_dont_remove_snapshots.setEnabled(True)
        self.button_take_snapshot.setEnabled(True)
        self.button_delete_snapshot.setEnabled(True)
        self.button_add_subvolume.setEnabled(True)
        self.button_delete_subvolume.setEnabled(True)
        self.button_edit_subvolume.setEnabled(True)
        self.button_save_subvolume.setEnabled(True)

    def take_snapshot(self):
        """Takes a BTRFS subvolume snapshot.

        """
        snapshot_window = window.windows.SnapshotWindow(self)
        # Connecting the signal emitted by the snapshot window with this slot
        snapshot_window.refresh_gui.connect(self.refresh_gui)
        # Displaying snapshot window
        snapshot_window.show()

    def delete_snapshots(self):
        """Deletes one or several BTRFS subvolume snapshots.

        """
        snapshots_to_delete = self.list_snapshots.selectedItems()
        for snap in snapshots_to_delete:
            filesystem.snapshot.delete_specific_snapshot(snap.text())

        # Refreshing GUI
        self.refresh_gui()

    def delete_logs(self):
        """Deletes one or several logs.

        """
        logs_to_delete = self.list_logs.selectedItems()
        for log in logs_to_delete:
            os.remove(os.path.join(util.settings.logs_path, log.text()))

        # Refreshing GUI
        self.refresh_gui()

    def view_log(self):
        """Opens the log in a new window to display it.

        """
        logs_to_view = self.list_logs.selectedItems()
        for log in logs_to_view:
            log_window = window.windows.LogViewWindow(self, os.path.join(util.settings.logs_path, log.text()))
            log_window.show()

    def add_subvolume(self):
        """Adds a new subvolume to be managed by the application.

        """
        subvolume_window = window.windows.SubvolumeWindow(self)
        # Connecting the signal emitted by the subvolume window with this slot
        subvolume_window.refresh_gui.connect(self.refresh_gui)
        # Displaying snapshot window
        subvolume_window.show()

    def dont_remove_snapshots(self):
        """Actions when user checks don't remove snapshots.

        """
        # Storing value in settings
        if self.checkbox_dont_remove_snapshots.isChecked():
            self.label_snapshots_to_keep.hide()
            self.spinbox_snapshots_to_keep.hide()
            util.settings.properties_manager.set_property('remove_snapshots', 0)
        else:
            self.label_snapshots_to_keep.show()
            self.spinbox_snapshots_to_keep.show()
            util.settings.properties_manager.set_property('remove_snapshots', 1)

    def snapshots_to_keep_valuechange(self):
        """Actions when user changes the value of the snapshots to keep.

        """
        # Storing value in settings
        util.settings.properties_manager.set_property('snapshots_to_keep', self.spinbox_snapshots_to_keep.value())

    def include_snap(self):
        """Actions when user checks include snap packages.

        """
        # Storing value in settings
        if self.checkbox_snap.isChecked():
            util.settings.properties_manager.set_property('snap_packages', 1)
        else:
            util.settings.properties_manager.set_property('snap_packages', 0)

    def include_aur(self):
        """Actions when user checks include AUR packages.

        """
        # Storing value in settings
        if self.checkbox_aur.isChecked():
            util.settings.properties_manager.set_property('aur_repository', 1)
        else:
            util.settings.properties_manager.set_property('aur_repository', 0)

    def include_startup(self):
        """Actions when user checks check updates at startup.

        """
        # Storing value in settings
        if self.checkbox_startup.isChecked():
            util.settings.properties_manager.set_property('check_at_startup', 1)
        else:
            util.settings.properties_manager.set_property('check_at_startup', 0)

    def on_combobox_subvolumes_changed(self):
        current_subvolume = self.combobox_subvolumes.currentText()
        if current_subvolume:
            self.line_edit_snapshot_where.setText(util.settings.subvolumes[current_subvolume].subvolume_dest)
            self.line_edit_snapshot_prefix.setText(util.settings.subvolumes[current_subvolume].snapshot_name)

    def edit_subvolume(self):
        """Actions when user wants to edit a defined subvolume.

        """
        # Buttons management
        self.button_save_subvolume.show()
        self.button_edit_subvolume.hide()
        self.button_delete_subvolume.hide()
        self.line_edit_snapshot_where.setDisabled(False)
        self.line_edit_snapshot_prefix.setDisabled(False)

    def save_subvolume(self):
        """Actions when user finishes to edit a subvolume.

        """
        # Buttons management
        self.button_save_subvolume.hide()
        self.button_edit_subvolume.show()
        self.button_delete_subvolume.show()
        self.line_edit_snapshot_where.setDisabled(True)
        self.line_edit_snapshot_prefix.setDisabled(True)

        # Storing the modified values
        new_snapshot_where = self.line_edit_snapshot_where.text()
        new_snapshot_prefix = self.line_edit_snapshot_prefix.text()
        subvolume_selected = self.combobox_subvolumes.currentText()
        util.settings.properties_manager.set_subvolume(subvolume_selected, new_snapshot_where, new_snapshot_prefix)

        # Refreshing components
        self.refresh_gui()

    def delete_subvolume(self):
        """Actions when user wants to delete a subvolume.

        """
        # Storing the modified values
        subvolume_selected = self.combobox_subvolumes.currentText()
        util.settings.properties_manager.set_subvolume(subvolume_selected, None, None)

        # Refreshing components
        self.refresh_gui()

    def go_to_github(self):
        """Actions when user clicks on github button.

        """
        url = QUrl('https://github.com/egara/buttermanager')
        QDesktopServices.openUrl(url)

    def fill_snapshots(self):
        """Fills snapshots information in the GUI.

        """
        # Resetting snapshots in the GUI
        # Clearing the list
        self.list_snapshots.clear()

        # Adding the snapshots to the list
        snapshots = []
        self.list_snapshots.addItems(snapshots)
        # Loading the snapshots detected
        for subvolume in util.settings.subvolumes:
            snapshots.extend(util.settings.subvolumes[subvolume].get_all_snapshots_with_the_same_name())
        self.list_snapshots.addItems(snapshots)

    def fill_logs(self):
        """Fills logs in the GUI.

        """
        # Resetting logs in the GUI
        # Clearing the list
        self.list_logs.clear()

        # Adding the logs to the list
        logs = os.listdir(util.settings.logs_path)
        self.list_logs.addItems(logs)

    def fill_subvolumes(self):
        """Fills subvolumes in the GUI.

        """
        # Resetting combo
        self.combobox_subvolumes.clear()
        # Adding the new subvolumes to the combobox
        list_subvolumes = []
        if len(util.settings.subvolumes) > 0:
            for subvolume in util.settings.subvolumes:
                list_subvolumes.append(subvolume)
            self.combobox_subvolumes.addItems(list_subvolumes)
            self.line_edit_snapshot_where.setDisabled(True)
            self.line_edit_snapshot_where.setText(util.settings.subvolumes[list_subvolumes[0]].subvolume_dest)
            self.line_edit_snapshot_prefix.setDisabled(True)
            self.line_edit_snapshot_prefix.setText(util.settings.subvolumes[list_subvolumes[0]].snapshot_name)

    def refresh_subvolume_buttons(self):
        """Shows or hide subvolume buttons in the GUI.

        """
        # They will be shown only if some subvolume is defined by the user
        if len(util.settings.subvolumes) > 0:
            self.button_save_subvolume.hide()
            self.button_edit_subvolume.show()
            self.button_delete_subvolume.show()
            self.combobox_subvolumes.show()
            self.line_edit_snapshot_where.show()
            self.label_settings_subvolumes_where.show()
            self.line_edit_snapshot_prefix.show()
            self.label_settings_subvolumes_prefix.show()
        else:
            self.label_existing_subvolumes.hide()
            self.button_save_subvolume.hide()
            self.button_edit_subvolume.hide()
            self.button_delete_subvolume.hide()
            self.combobox_subvolumes.hide()
            self.line_edit_snapshot_where.hide()
            self.label_settings_subvolumes_where.hide()
            self.line_edit_snapshot_prefix.hide()
            self.label_settings_subvolumes_prefix.hide()

    def refresh_gui(self):
        """Refresh all the GUI elements.

        """
        self.refresh_filesystem_statistics()
        self.fill_snapshots()
        self.fill_logs()
        self.fill_subvolumes()
        self.refresh_subvolume_buttons()
        self.show_space_labels()

    def show_space_labels(self):
        """Shows the appropiate labels related to the space left of the system.

        """
        filesystem_space_pertentage = util.utils.get_percentage(self.__current_filesystem.total_size,
                                                                self.__current_filesystem.total_allocated)
        if filesystem_space_pertentage <= 70:
            self.label_space_ok.show()
            self.label_space_danger.hide()
            self.label_space_ko.hide()
        elif filesystem_space_pertentage > 70 & filesystem_space_pertentage <= 85:
            self.label_space_ok.hide()
            self.label_space_danger.show()
            self.label_space_ko.hide()
        else:
            self.label_space_ok.hide()
            self.label_space_danger.hide()
            self.label_space_ko.show()

        if self.__current_filesystem.data_percentage <= 85:
            self.label_space_data_danger.show()
        else:
            self.label_space_data_danger.hide()


if __name__ == '__main__':
    # Creating application instance
    application = QApplication(sys.argv)
    # Creating main window instance
    password_window = PasswordWindow(None)
    # Launching the application
    application.exec_()
