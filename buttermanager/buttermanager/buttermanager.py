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

from .exception import exception
from .filesystem import filesystem, snapshot
from .manager import upgrader
from .util import utils, settings
from .window import windows
import os
import subprocess
import sys
import time
from functools import partial
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtGui import QCursor, QTextCursor, QIcon, QPixmap, QDesktopServices, QFontMetrics
from PyQt5 import uic, QtTest
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
        self.__buttermanager_configurator = utils.ConfigManager()
        self.__buttermanager_configurator.configure()
        # Locating ui and images directories
        settings.ui_dir = os.path.join(os.path.dirname(__file__), 'ui')
        settings.images_dir = os.path.join(os.path.dirname(__file__), 'images')

        # UI elements
        self.__ui_elements = []
        # Logger
        self.__logger = utils.Logger(self.__class__.__name__).get()
        # Version checker
        self.__version_checker = utils.VersionChecker(self)

        # Initializing the application
        self.init_ui()

    def init_ui(self):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        password_window_ui = os.path.join(settings.ui_dir, 'PasswordWindow.ui')
        uic.loadUi(password_window_ui, self)

        # Setting the window icon
        buttermanager_icon = os.path.join(settings.images_dir, 'buttermanager50.png')
        self.setWindowIcon(QIcon(buttermanager_icon))

        # Calculating the base font size for all UI elements in the application
        settings.base_font_size = self.get_base_font_size()

        # Adjusting font scale
        # UI elements
        self.__ui_elements = [self.label_password, self.button_ok, self.button_cancel, self.button_lock,
                              self.input_password]
        utils.scale_fonts(self.__ui_elements)
        # Tooltips
        self.setStyleSheet(" QToolTip{font: " + str(settings.base_font_size) + "pt}")

        # Setting maximum and minimum  size for the main window
        self.setMinimumHeight(240)
        self.setMinimumWidth(320)
        self.setMaximumHeight(240)
        self.setMaximumWidth(320)

        # Setting lock icon
        lock_icon = os.path.join(settings.images_dir, 'lock_24px_icon.png')
        self.button_lock.setIcon(QIcon(lock_icon))
        self.button_lock.setIconSize(QSize(24, 24))

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

        # Checks for new versions of ButterManager
        self.__version_checker.check_version()

        # Showing password window
        self.show()

    def get_base_font_size(self):
        """Gets the base font size for all the UI elements.

        Returns:
            int: Base font size.

        """
        self.__logger.info("Calculating appropriated base font size for UI elements...")
        font_fits = False

        # Base font size will be calculated using self.label_password attribute
        font = self.label_password.font()
        font_size = font.pointSize()

        while not font_fits:
            fm = QFontMetrics(font)
            pixels_wide = fm.width(self.label_password.text())
            pixels_high = fm.height()

            bound = fm.boundingRect(0, 0, pixels_wide, pixels_high, Qt.TextWordWrap | Qt.AlignLeft,
                                    self.label_password.text())

            if bound.width() <= self.label_password.width() and \
                    bound.height() <= self.label_password.height():
                font_fits = True
            else:
                font.setPointSize(font.pointSize() - 1)
                font_size = font_size - 1

        self.__logger.info("Base font size = " + str(font_size))
        return font_size

    def load_main_window(self):
        # Storing user's password
        settings.user_password = self.input_password.text()

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
        self.__logger = utils.Logger(self.__class__.__name__).get()
        # Current filesystem (it will be initialize in initialize method)
        self.__current_filesystem = None
        # Current filesystem uuid (it will be initialize in initialize method)
        self.__current_filesystem_uuid = None
        # Balancer that will balance the current filesystem if it is needed
        self.__balancer = None
        # Differentiator that will calculate the differences between a snapshot and the current
        # subvolume
        self.__differentiator = None
        # Upgrader that will upgrade the system if it is needed
        self.__upgrader = None
        # Updates checker that will check for updates if it is needed
        self.__updates_checker = None
        # Root snapshot checker
        self.__root_snapshot_checker = snapshot.RootSnapshotChecker(self)
        # UI elements
        self.__ui_elements = []
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
            main_window_ui = os.path.join(settings.ui_dir, 'MainWindow.ui')
            uic.loadUi(main_window_ui, self)

            # Setting the window icon
            buttermanager_icon = os.path.join(settings.images_dir, 'buttermanager50.png')
            self.setWindowIcon(QIcon(buttermanager_icon))

            # Adjusting font scale
            # UI elements
            self.__ui_elements = [self.tab_buttermanager, self.label_filesystem_info, self.label_filesystem_data,
                                  self.label_filesystem_metadata, self.label_filesystem, self.label_other_operations,
                                  self.label_filesystem_size, self.label_filesystem_size_value,
                                  self.label_filesystem_allocated, self.label_filesystem_allocated_value,
                                  self.label_filesystem_lost_info, self.label_filesystem_info_more, self.label_space_ok,
                                  self.label_space_danger, self.label_space_ko, self.label_space_data_danger,
                                  self.label_settings_upgrade, self.label_settings_subvolumes,
                                  self.label_existing_subvolumes, self.label_logo,
                                  self.label_app_name, self.label_app_version, self.label_app_developer,
                                  self.label_app_email, self.label_app_developer_2, self.button_balance,
                                  self.button_upgrade_system, self.button_upgrade_system_without_snapshots,
                                  self.button_fa_take_snapshot, self.button_snapshot, self.button_take_snapshot,
                                  self.button_delete_snapshot, self.button_delete_log, self.button_view_log,
                                  self.button_edit_subvolume, self.button_delete_subvolume, self.button_add_subvolume,
                                  self.button_save_subvolume, self.button_github, self.button_close_terminal,
                                  self.button_save_log, self.text_edit_console, self.progressbar_metadata,
                                  self.progressbar_data, self.combobox_filesystem, self.list_snapshots, self.list_logs,
                                  self.combobox_subvolumes, self.line_edit_snapshot_where,
                                  self.line_edit_snapshot_prefix, self.checkbox_edit_dont_remove_snapshots,
                                  self.spinbox_edit_snapshots_to_keep, self.checkbox_startup, self.checkbox_log,
                                  self.checkbox_snap, self.checkbox_aur, self.button_save_log,
                                  self.button_close_terminal, self.button_wiki, self.label_documentation,
                                  self.checkbox_grub_btrfs, self.button_regenerate_grub]
            utils.scale_fonts(self.__ui_elements)
            self.__ui_elements = [self.label_settings_subvolumes_where, self.label_settings_subvolumes_prefix,
                                  self.label_settings_subvolumes_snapshots_to_keep]
            utils.scale_fonts(self.__ui_elements, 2)
            # Tooltips
            self.setStyleSheet(" QToolTip{font: " + str(settings.base_font_size) + "pt}")

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
            uuid_filesystems = filesystem.get_btrfs_filesystems()
            if len(uuid_filesystems) > 0:
                self.__current_filesystem_uuid = uuid_filesystems[0]
                self.combobox_filesystem.addItems(uuid_filesystems)
                self.__current_filesystem = filesystem.Filesystem(self.__current_filesystem_uuid)
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
                # Retrieving snap packages upgrade decision
                if settings.snap_packages == 0:
                    self.checkbox_snap.setChecked(False)
                else:
                    self.checkbox_snap.setChecked(True)

                if utils.exist_program(SNAP_COMMAND):
                    self.checkbox_snap.show()
                else:
                    self.checkbox_snap.hide()

                # Retrieving AUR packages upgrade decision
                if settings.aur_repository == 0:
                    self.checkbox_aur.setChecked(False)
                else:
                    self.checkbox_aur.setChecked(True)

                if settings.user_os == utils.OS_ARCH:
                    self.checkbox_aur.show()
                else:
                    self.checkbox_aur.hide()

                # Retrieving check for updates at startup decision
                if settings.check_at_startup == 0:
                    self.checkbox_startup.setChecked(False)
                else:
                    self.checkbox_startup.setChecked(True)

                # Retrieving boot the system from GRUB using snapshots decision
                if settings.grub_btrfs == 0:
                    self.checkbox_grub_btrfs.setChecked(False)
                    self.button_regenerate_grub.hide()
                else:
                    self.checkbox_grub_btrfs.setChecked(True)
                    self.button_regenerate_grub.show()

                if settings.user_os == utils.OS_ARCH or \
                        settings.user_os == utils.OS_DEBIAN or \
                        settings.user_os == utils.OS_SUSE or \
                        settings.user_os == utils.OS_FEDORA:
                    self.checkbox_startup.show()
                else:
                    self.checkbox_startup.hide()

                # Retrieving save log decision
                if settings.save_log == 0:
                    self.checkbox_log.setChecked(False)
                else:
                    self.checkbox_log.setChecked(True)

                # END -- Displaying settings options

                # Setting buttons and icons
                # Snapshot buttons
                add_icon = os.path.join(settings.images_dir, 'add_16px_icon.png')
                self.button_take_snapshot.setIcon(QIcon(add_icon))
                self.button_take_snapshot.setIconSize(QSize(16, 16))
                remove_icon = os.path.join(settings.images_dir, 'remove_16px_icon.png')
                self.button_delete_snapshot.setIcon(QIcon(remove_icon))
                self.button_delete_snapshot.setIconSize(QSize(16, 16))
                exchange_arrows_icon = os.path.join(settings.images_dir, 'exchange_arrows_16px_icon.png')
                self.button_diff.setIcon(QIcon(exchange_arrows_icon))
                self.button_diff.setIconSize(QSize(16, 16))
                folder_icon = os.path.join(settings.images_dir, 'folder_16px_icon.png')
                self.button_folder.setIcon(QIcon(folder_icon))
                self.button_folder.setIconSize(QSize(16, 16))

                # Logs buttons
                view_icon = os.path.join(settings.images_dir, 'view_24px_icon.png')
                self.button_view_log.setIcon(QIcon(view_icon))
                self.button_view_log.setIconSize(QSize(24, 24))
                self.button_delete_log.setIcon(QIcon(remove_icon))
                self.button_delete_log.setIconSize(QSize(16, 16))

                # Subvolume buttons
                accept_icon = os.path.join(settings.images_dir, 'accept_16px_icon.png')
                self.button_save_subvolume.setIcon(QIcon(accept_icon))
                self.button_save_subvolume.setIconSize(QSize(16, 16))
                edit_icon = os.path.join(settings.images_dir, 'edit_16px_icon.png')
                self.button_edit_subvolume.setIcon(QIcon(edit_icon))
                self.button_edit_subvolume.setIconSize(QSize(16, 16))
                self.button_delete_subvolume.setIcon(QIcon(remove_icon))
                self.button_delete_subvolume.setIconSize(QSize(16, 16))
                self.refresh_subvolume_buttons()

                # Displaying logo within About tab
                self.label_logo.setPixmap(QPixmap(buttermanager_icon))

                # Button events
                self.combobox_filesystem.currentTextChanged.connect(self.on_combobox_filesystem_changed)
                self.button_balance.clicked.connect(self.balance_filesystem)
                self.button_upgrade_system.clicked.connect(partial(self.upgrade_system, True))
                self.button_upgrade_system_without_snapshots.clicked.connect(partial(self.upgrade_system, False))
                self.button_fa_take_snapshot.clicked.connect(self.take_snapshot)
                self.button_close_terminal.clicked.connect(self.close_terminal)
                self.button_save_log.clicked.connect(self.save_log)
                self.button_take_snapshot.clicked.connect(self.take_snapshot)
                self.button_delete_snapshot.clicked.connect(self.delete_snapshots)
                self.button_diff.clicked.connect(self.find_diffs)
                self.button_folder.clicked.connect(self.open_file_explorer)
                self.button_delete_log.clicked.connect(self.delete_logs)
                self.button_view_log.clicked.connect(self.view_log)
                self.checkbox_edit_dont_remove_snapshots.clicked.connect(self.dont_remove_snapshots)
                self.checkbox_snap.clicked.connect(self.include_snap)
                self.checkbox_aur.clicked.connect(self.include_aur)
                self.checkbox_log.clicked.connect(self.include_log)
                self.checkbox_startup.clicked.connect(self.include_startup)
                self.checkbox_grub_btrfs.clicked.connect(self.include_grub_btrfs)
                self.button_add_subvolume.clicked.connect(self.add_subvolume)
                self.button_edit_subvolume.clicked.connect(self.edit_subvolume)
                self.button_save_subvolume.clicked.connect(self.save_subvolume)
                self.button_delete_subvolume.clicked.connect(self.delete_subvolume)
                self.combobox_subvolumes.currentTextChanged.connect(self.on_combobox_subvolumes_changed)
                self.button_github.clicked.connect(self.go_to_github)
                self.button_wiki.clicked.connect(self.go_to_wiki)
                self.button_regenerate_grub.clicked.connect(self.regenerate_grub)

                # If no subvolumes are defined, warning the user
                if len(settings.subvolumes) == 0:
                    info_dialog = windows.GeneralInfoWindow(self, "Warning: You don't have any subvolumes "
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

                # Checks for root snapshot mounted
                root_snapshot_default = self.__root_snapshot_checker.check_root_snapshot()
                if root_snapshot_default:
                    # Show the updates window only if the user wants to and if there are updates
                    self.check_updates()
                else:
                    consolidate_window = self.__root_snapshot_checker.open_consolidate_snapshot_window()
                    # Hidding the main window and showing the consolodate window in order to proceed
                    self.hide()
                    consolidate_window.show()
                    consolidation = consolidate_window.exec_()
                    if consolidation == 1:
                        # User chose Ok button to consolidate root snapshot and the process finished succesfully
                        info_dialog = windows.ProblemsFoundWindow(self,
                                                                         "The snapshot you choose to boot the system \n"
                                                                         "has been consolidated as the default root \n"
                                                                         "snapshot. Please, reboot the system now.")
                        info_dialog.show()
                    elif consolidation == 2:
                        # User chose Ok button to consolidate root snapshot and the process doesn't finished
                        # successfully
                        info_dialog = windows.ProblemsFoundWindow(self,
                                                                         "Error trying to substitute the root's path \n"
                                                                         "in fstab with the path of the new snapshot \n"
                                                                         "created")
                        info_dialog.show()
                    elif consolidation == 3:
                        # User chose Ok button to consolidate root snapshot and the process doesn't finished
                        # successfully
                        info_dialog = windows.ProblemsFoundWindow(self,
                                                                         "Error removing root snapshot because it is \n"
                                                                         "not empty and there are subvolumes \n"
                                                                         "within it. The consolidation process \n"
                                                                         "couldn't be done.")
                        info_dialog.show()
                    else:
                        # User chose Cancel button so the application must be closed
                        info_dialog = windows.ProblemsFoundWindow(self,
                                                                         "In order to avoid problems, ButterManager \n"
                                                                         "cannot execute any operations under \n"
                                                                         "a non default root snapshot so it will be "
                                                                         "closed.")
                        self.close()
                        info_dialog.show()
            else:
                self.__logger.info("The application couldn't start normally. No BTRFS file system found.")

                info_dialog = windows.ProblemsFoundWindow(self, "No BTRFS file system found. \n"
                                                                       "The application will be closed.")
                info_dialog.show()

        except exception.NoCommandFound:
            self.__logger.info("The application couldn't start normally. There are some programs needed that are not "
                               "installed.")
            self.__logger.info("Please, install these programs and start ButterManager again.")

            info_dialog = windows.ProblemsFoundWindow(self, "These programs need to be installed for \n"
                                                                   "the proper functioning of ButterManager:\n"
                                                                   "btrfs, findmnt.\n")
            info_dialog.show()

    def check_updates(self):
        """Creates the updates checker that will start in another thread and check system updates.

        """
        self.__updates_checker = upgrader.UpdatesChecker()
        self.__updates_checker.show_updates_window.connect(self.show_updates_window)
        self.__updates_checker.start()

    def show_updates_window(self, command_line_output):
        """ Shows a new window with all the packages to  be updated.

        Once the updates_checker knows all the packages that need to be updated, a new
        UpdatesWindow will be opened from the main GUI thread.

        Arguments:
            command_line_output (list(:obj:`str`)): Packages to be updated. One per line.
        """
        updates_window = windows.UpdatesWindow(self, command_line_output)
        updates_window.upgrade_system.connect(self.upgrade_system)
        updates_window.upgrade_system_without_snanpshots.connect(partial(self.upgrade_system, False))
        updates_window.show()

    def balance_filesystem(self):
        """Runs the balance method.

        """
        self.__balancer = filesystem.BalanceManager(self.__current_filesystem.data_percentage,
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
        self.__current_filesystem = filesystem.Filesystem(self.__current_filesystem_uuid)
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
        # Save log button will only be displayed when the logs are
        # not saved automatically
        if settings.save_log == 0:
            self.button_save_log.show()
        else:
            self.button_save_log.hide()
        self.text_edit_console.show()

        # Adjusting the window
        self.adjustSize()

        # Checking if there is any subvolume defined by the user
        if len(settings.subvolumes) == 0:
            snapshots = False

        # Gathering user settings
        include_aur = False
        if settings.user_os == utils.OS_ARCH:
            include_aur = self.checkbox_aur.isChecked()
        include_snap = False
        if utils.exist_program(SNAP_COMMAND):
            include_snap = self.checkbox_snap.isChecked()

        # Upgrading the system
        self.__upgrader = upgrader.Upgrader(include_aur, include_snap, snapshots)
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.disable_buttons.connect(self.__disable_buttons)
        # Connecting the signal emitted by the upgrader with this slot
        self.__upgrader.enable_buttons.connect(self.__enable_buttons)
        # Connecting the signal emitted by the upgrader with this slot
        # Depending on the decision to save or not the logs, the signal
        # will be connected to a different slot
        save_log = self.checkbox_log.isChecked()
        if save_log:
            # Saving log if it is needed
            self.__upgrader.refresh_gui.connect(self.save_log_refresh_gui)
        else:
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
        try:
            current_date = time.strftime('%Y%m%d')
            index = 0
            log_name = "{current_date}-{index}.txt".format(current_date=current_date, index=str(index))
            log_path = os.path.join(settings.logs_path, log_name)
            while os.path.exists(log_path):
                index += 1
                log_name = "{current_date}-{index}.txt".format(current_date=current_date, index=str(index))
                log_path = os.path.join(settings.logs_path, log_name)

            # Gets the content and saves it
            log = self.text_edit_console.toPlainText()
            with open(log_path, 'a') as file:
                file.write(log)
        except Exception as exception:
            self.__logger.info("Error saving the log: " + str(exception))

    def __disable_buttons(self):
        """Disables all the buttons of the GUI.

        """
        self.button_balance.setEnabled(False)
        self.button_upgrade_system.setEnabled(False)
        self.button_upgrade_system_without_snapshots.setEnabled(False)
        self.button_fa_take_snapshot.setEnabled(False)
        self.button_close_terminal.setEnabled(False)
        self.checkbox_startup.setEnabled(False)
        self.checkbox_log.setEnabled(False)
        self.checkbox_snap.setEnabled(False)
        self.checkbox_aur.setEnabled(False)
        self.checkbox_grub_btrfs.setEnabled(False)
        self.button_take_snapshot.setEnabled(False)
        self.button_delete_snapshot.setEnabled(False)
        self.button_diff.setEnabled(False)
        self.button_folder.setEnabled(False)
        self.button_add_subvolume.setEnabled(False)
        self.button_delete_subvolume.setEnabled(False)
        self.button_edit_subvolume.setEnabled(False)
        self.button_save_subvolume.setEnabled(False)
        self.button_view_log.setEnabled(False)
        self.button_delete_log.setEnabled(False)
        self.button_regenerate_grub.setEnabled(False)

    def __enable_buttons(self):
        """Enable all the buttons of the GUI.

        """
        self.button_balance.setEnabled(True)
        self.button_upgrade_system.setEnabled(True)
        self.button_upgrade_system_without_snapshots.setEnabled(True)
        self.button_fa_take_snapshot.setEnabled(True)
        self.button_close_terminal.setEnabled(True)
        self.checkbox_startup.setEnabled(True)
        self.checkbox_log.setEnabled(True)
        self.checkbox_snap.setEnabled(True)
        self.checkbox_aur.setEnabled(True)
        self.checkbox_grub_btrfs.setEnabled(True)
        self.button_take_snapshot.setEnabled(True)
        self.button_delete_snapshot.setEnabled(True)
        self.button_diff.setEnabled(True)
        self.button_folder.setEnabled(True)
        self.button_add_subvolume.setEnabled(True)
        self.button_delete_subvolume.setEnabled(True)
        self.button_edit_subvolume.setEnabled(True)
        self.button_save_subvolume.setEnabled(True)
        self.button_view_log.setEnabled(True)
        self.button_delete_log.setEnabled(True)
        self.button_regenerate_grub.setEnabled(True)

    def take_snapshot(self):
        """Takes a BTRFS subvolume snapshot.

        """
        snapshot_window = windows.SnapshotWindow(self)
        # Connecting the signals emitted by the snapshot window with this slot
        snapshot_window.refresh_gui.connect(self.refresh_gui)
        snapshot_window.enable_buttons.connect(self.__enable_buttons)
        # Disabling buttons
        self.__disable_buttons()
        # Displaying snapshot window
        snapshot_window.show()
        # Enabling buttons
        self.__disable_buttons()

    def delete_snapshots(self):
        """Deletes one or several BTRFS subvolume snapshots.

        """
        # Disabling buttons
        self.__disable_buttons()

        # Waiting 10 msec in order to let self.__disable_buttons to take effect
        QtTest.QTest.qWait(10)

        snapshots_to_delete = self.list_snapshots.selectedItems()
        for snap in snapshots_to_delete:
            snapshot.delete_specific_snapshot(snap.text())

        # Refreshing GUI
        self.refresh_gui()

        # Enabling buttons
        self.__enable_buttons()

    def find_diffs(self):
        """Find differences between the snapshot selected and the current state of the subvolume related to it.

        """
        snapshot_to_diff = self.list_snapshots.selectedItems()
        if len(snapshot_to_diff) != 1:
            # Only one snapshot can be selected
            info_dialog = windows.GeneralInfoWindow(self, "Please, select one (and only one) snapshot\n"
                                                                 "in order to find the differences between\n"
                                                                 "it and the current subvolume.")
            info_dialog.show()
        else:
            # Disabling buttons
            self.__disable_buttons()

            # Waiting 10 msec in order to let self.__disable_buttons to take effect
            QtTest.QTest.qWait(10)

            # The user has to select the kind of operation
            diff_window = windows.DiffWindow()

            # Hidding the main window and showing the diff window in order to proceed
            self.hide()

            diff_window.show()
            diff_process = diff_window.exec_()
            if diff_process == 1:
                # A full operation will be done
                self.__differentiator = snapshot.Differentiator(
                    snapshot_to_diff[0].text(),
                    snapshot.Differentiator.OPERATION_FULL)
            elif diff_process == 2:
                # A partial operation will be done
                self.__differentiator = snapshot.Differentiator(
                    snapshot_to_diff[0].text(),
                    snapshot.Differentiator.OPERATION_PARTIAL)

            self.__differentiator.show_one_window.connect(self.manage_window)
            self.__differentiator.start()

            # Refreshing GUI
            self.refresh_gui()

            # Enabling buttons
            self.__enable_buttons()

            # Showing main window again
            self.show()

    def open_file_explorer(self):
        """Opens a file explorer to see all the files within a snapshot.

        """
        snapshots_selected = self.list_snapshots.selectedItems()
        if len(snapshots_selected) != 1:
            # Only one snapshot can be selected
            info_dialog = windows.GeneralInfoWindow(self, "Please, select one (and only one) snapshot \n"
                                                                 "in order to open the file explorer.")
            info_dialog.show()
        else:
            subprocess.call(['xdg-open', snapshots_selected[0].text()])

    def delete_logs(self):
        """Deletes one or several logs.

        """
        logs_to_delete = self.list_logs.selectedItems()
        for log in logs_to_delete:
            os.remove(os.path.join(settings.logs_path, log.text()))

        # Refreshing GUI
        self.refresh_gui()

    def view_log(self):
        """Opens the log in a new window to display it.

        """
        logs_to_view = self.list_logs.selectedItems()
        for log in logs_to_view:
            log_window = windows.LogViewWindow(self, os.path.join(settings.logs_path, log.text()))
            log_window.show()

    def add_subvolume(self):
        """Adds a new subvolume to be managed by the application.

        """
        subvolume_window = windows.SubvolumeWindow(self)
        # Connecting the signal emitted by the subvolume window with this slot
        subvolume_window.refresh_gui.connect(self.refresh_gui)
        # Displaying snapshot window
        subvolume_window.show()

    def dont_remove_snapshots(self):
        """Actions when user checks don't remove snapshots.
        """
        if self.checkbox_edit_dont_remove_snapshots.isChecked():
            self.spinbox_edit_snapshots_to_keep.hide()
        else:
            self.spinbox_edit_snapshots_to_keep.show()
            self.spinbox_edit_snapshots_to_keep.setValue(1)

    def include_snap(self):
        """Actions when user checks include snap packages.

        """
        # Storing value in settings
        if self.checkbox_snap.isChecked():
            settings.properties_manager.set_property('snap_packages', 1)
        else:
            settings.properties_manager.set_property('snap_packages', 0)

    def include_aur(self):
        """Actions when user checks include AUR packages.

        """
        # Storing value in settings
        if self.checkbox_aur.isChecked():
            settings.properties_manager.set_property('aur_repository', 1)
        else:
            settings.properties_manager.set_property('aur_repository', 0)

    def include_log(self):
        """Actions when user checks include log.

        """
        # Storing value in settings
        if self.checkbox_log.isChecked():
            settings.properties_manager.set_property('save_log', 1)
        else:
            settings.properties_manager.set_property('save_log', 0)

    def include_startup(self):
        """Actions when user checks check updates at startup.

        """
        # Storing value in settings
        if self.checkbox_startup.isChecked():
            settings.properties_manager.set_property('check_at_startup', 1)
        else:
            settings.properties_manager.set_property('check_at_startup', 0)

    def include_grub_btrfs(self):
        """Actions when user checks boot the system from GRUB using snapshots.

        """
        # Storing value in settings
        if self.checkbox_grub_btrfs.isChecked():
            settings.properties_manager.set_property('grub_btrfs', 1)
            self.button_regenerate_grub.show()
        else:
            settings.properties_manager.set_property('grub_btrfs', 0)
            self.button_regenerate_grub.hide()

    def on_combobox_filesystem_changed(self):
        self.__current_filesystem_uuid = self.combobox_filesystem.currentText()
        self.refresh_filesystem_statistics()

    def on_combobox_subvolumes_changed(self):
        current_subvolume = self.combobox_subvolumes.currentText()
        if current_subvolume:
            self.line_edit_snapshot_where.setText(settings.subvolumes[current_subvolume].subvolume_dest)
            self.line_edit_snapshot_prefix.setText(settings.subvolumes[current_subvolume].snapshot_name)

            snapshots_to_keep = int(settings.subvolumes[current_subvolume].snapshots_to_keep)

            if snapshots_to_keep == -1:
                # Enable Don't remove snapshots
                self.checkbox_edit_dont_remove_snapshots.show()
                self.checkbox_edit_dont_remove_snapshots.setChecked(True)
                self.checkbox_edit_dont_remove_snapshots.setDisabled(True)
                # Hide snapshots to keep
                self.spinbox_edit_snapshots_to_keep.hide()
            else:
                # Enable snapshots to keep
                self.spinbox_edit_snapshots_to_keep.show()
                self.spinbox_edit_snapshots_to_keep.setDisabled(True)
                self.spinbox_edit_snapshots_to_keep.setValue(snapshots_to_keep)
                # Show Don't remove snapshots and disable it
                self.checkbox_edit_dont_remove_snapshots.show()
                self.checkbox_edit_dont_remove_snapshots.setDisabled(True)

    def edit_subvolume(self):
        """Actions when user wants to edit a defined subvolume.

        """
        # Buttons management
        self.button_save_subvolume.show()
        self.button_edit_subvolume.hide()
        self.button_delete_subvolume.hide()
        self.line_edit_snapshot_where.setDisabled(False)
        self.line_edit_snapshot_prefix.setDisabled(False)
        self.spinbox_edit_snapshots_to_keep.setDisabled(False)
        self.checkbox_edit_dont_remove_snapshots.setDisabled(False)

    def save_subvolume(self):
        """Actions when user finishes to edit a subvolume.

        """
        # Buttons management
        self.button_save_subvolume.hide()
        self.button_edit_subvolume.show()
        self.button_delete_subvolume.show()
        self.line_edit_snapshot_where.setDisabled(True)
        self.line_edit_snapshot_prefix.setDisabled(True)
        self.spinbox_edit_snapshots_to_keep.setDisabled(True)
        self.checkbox_edit_dont_remove_snapshots.setDisabled(True)

        # Storing the modified values
        new_snapshot_where = self.line_edit_snapshot_where.text()
        new_snapshot_prefix = self.line_edit_snapshot_prefix.text()
        subvolume_selected = self.combobox_subvolumes.currentText()
        snapshots_to_keep = -1
        if not self.checkbox_edit_dont_remove_snapshots.isChecked():
            snapshots_to_keep = self.spinbox_edit_snapshots_to_keep.value()

        settings.properties_manager.set_subvolume(subvolume_selected, new_snapshot_where, new_snapshot_prefix,
                                                  snapshots_to_keep)

        # Refreshing components
        self.refresh_gui()

    def delete_subvolume(self):
        """Actions when user wants to delete a subvolume.

        """
        # Storing the modified values
        subvolume_selected = self.combobox_subvolumes.currentText()
        settings.properties_manager.set_subvolume(subvolume_selected, None, None, None)

        # Refreshing components
        self.refresh_gui()

    def go_to_github(self):
        """Actions when user clicks on github button.

        """
        url = QUrl('https://github.com/egara/buttermanager')
        QDesktopServices.openUrl(url)

    def go_to_wiki(self):
        """Actions when user clicks on github button.

        """
        url = QUrl('https://github.com/egara/buttermanager/wiki')
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
        for subvolume in settings.subvolumes:
            snapshots.extend(settings.subvolumes[subvolume].get_all_snapshots_with_the_same_name())
        self.list_snapshots.addItems(snapshots)

    def fill_logs(self):
        """Fills logs in the GUI.

        """
        # Resetting logs in the GUI
        # Clearing the list
        self.list_logs.clear()

        # Adding the logs to the list
        logs = os.listdir(settings.logs_path)
        self.list_logs.addItems(logs)

    def fill_subvolumes(self):
        """Fills subvolumes in the GUI.

        """
        # Resetting combo
        self.combobox_subvolumes.clear()
        # Adding the new subvolumes to the combobox
        list_subvolumes = []
        if len(settings.subvolumes) > 0:
            for subvolume in settings.subvolumes:
                list_subvolumes.append(subvolume)
            self.combobox_subvolumes.addItems(list_subvolumes)
            self.line_edit_snapshot_where.setDisabled(True)
            self.line_edit_snapshot_where.setText(settings.subvolumes[list_subvolumes[0]].subvolume_dest)
            self.line_edit_snapshot_prefix.setDisabled(True)
            self.line_edit_snapshot_prefix.setText(settings.subvolumes[list_subvolumes[0]].snapshot_name)

            snapshots_to_keep = int(settings.subvolumes[list_subvolumes[0]].snapshots_to_keep)

            if snapshots_to_keep == -1:
                # Enable Don't remove snapshots
                self.checkbox_edit_dont_remove_snapshots.show()
                self.checkbox_edit_dont_remove_snapshots.setChecked(True)
                self.checkbox_edit_dont_remove_snapshots.setDisabled(True)
                # Hide snapshots to keep
                self.spinbox_edit_snapshots_to_keep.hide()
            else:
                # Enable snapshots to keep
                self.spinbox_edit_snapshots_to_keep.show()
                self.spinbox_edit_snapshots_to_keep.setDisabled(True)
                self.spinbox_edit_snapshots_to_keep.setValue(snapshots_to_keep)
                # Show Don't remove snapshots and disable it
                self.checkbox_edit_dont_remove_snapshots.show()
                self.checkbox_edit_dont_remove_snapshots.setDisabled(True)

    def refresh_subvolume_buttons(self):
        """Shows or hide subvolume buttons in the GUI.

        """
        # They will be shown only if some subvolume is defined by the user
        if len(settings.subvolumes) > 0:
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

    def save_log_refresh_gui(self):
        """Save log and refresh all the GUI elements.

        """
        self.save_log()
        self.refresh_gui()

    def show_space_labels(self):
        """Shows the appropiate labels related to the space left of the system.

        """
        filesystem_space_pertentage = utils.get_percentage(self.__current_filesystem.total_size,
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

    def regenerate_grub(self):
        """Regenerates GRUB menu to include the snapshots taken as bootable entries.

        """
        # Disabling buttons
        self.__disable_buttons()

        # Waiting 100 msec in order to let self.__disable_buttons to take effect
        QtTest.QTest.qWait(100)

        # Run grub-btrfs in order to regenerate GRUB entries
        utils.execute_command(snapshot.GRUB_BTRFS_COMMAND, console=True, root=True)

        # Refreshing GUI
        self.refresh_gui()

        # Enabling buttons
        self.__enable_buttons()

        # Displaying info
        info_dialog = windows.GeneralInfoWindow(self, "GRUB menu has been regenerated.")
        info_dialog.show()
