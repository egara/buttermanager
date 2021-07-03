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

"""This module gathers all the operations related to BTRFS snapshots.

It provides also Snapshot class.
"""
from ..exception import exception
from ..util import settings, utils
from ..window import windows
import glob
import os
import shutil
import sys
import subprocess
import time
from PyQt5.QtCore import QThread, pyqtSignal


# Constants
BTRFS_CREATE_SNAPSHOT_R_COMMAND = "sudo -S btrfs subvolume snapshot -r"
BTRFS_CREATE_SNAPSHOT_RW_COMMAND = "sudo -S btrfs subvolume snapshot"
BTRFS_DELETE_SNAPSHOT_COMMAND = "sudo -S btrfs subvolume delete"
BTRFS_FIND_NEW_COMMAND = "sudo -S btrfs subvolume find-new"
GRUB_BTRFS_COMMAND = "sudo -S grub-mkconfig -o /boot/grub/grub.cfg"


# Classes
class Subvolume:
    """BTRFS Snapshot.

    """
    # Constructor
    def __init__(self, subvolume_origin, subvolume_dest, snapshot_name, snapshots_to_keep):
        """ Constructor.

        Arguments:
            subvolume_origin (str): Full path to the subvolume.
            subvolume_dest (str): Full path to the subvolume where all of the subvolumes created from origin are going
            to be stored.
            snapshot_name (str): Prefix for all the subvolumes created from origin
            snapshots_to_keep (str): Number of snapshots to keep for this subvolume
        """
        # Logger
        self.__logger = utils.Logger(self.__class__.__name__).get()
        self.subvolume_origin = subvolume_origin if subvolume_origin[-1] == '/' else subvolume_origin + '/'
        self.subvolume_dest = subvolume_dest if subvolume_dest[-1] == '/' else subvolume_dest + '/'
        self.snapshot_name = snapshot_name
        self.snapshots_to_keep = int(snapshots_to_keep)
        self.__current_date = time.strftime('%Y%m%d')

    # Methods
    # Private methods

    # Public methods
    def create_snapshot(self):
        """Creates a snapshot.

        """
        info_message = "Creating a read-only snapshot of {subvolume_origin} in {subvolume_dest}. " \
                       "Please wait...".format(subvolume_origin=self.subvolume_origin,
                                               subvolume_dest=self.subvolume_dest)
        self.__logger.info(info_message)

        # Checking how many snapshots are with the same name
        snapshot_full_name = "{snapshot_name}-{current_date}".format(snapshot_name=self.snapshot_name,
                                                                     current_date=self.__current_date)
        snapshots_with_same_name = [file for file in os.listdir(self.subvolume_dest) if snapshot_full_name in file]

        # Adding number to the full name
        snapshot_full_name = "{snapshot_full_name}-{number}".format(snapshot_full_name=snapshot_full_name,
                                                                    number=len(snapshots_with_same_name))
        # Checks if grub-btrfs integration is enabled
        if settings.properties_manager.get_property("grub_btrfs"):
            # Checks if /etc/fstab is in subvolume_origin
            fstab_path = self.subvolume_origin + 'etc/fstab'
            if os.path.isfile(fstab_path):
                everything_ok = True
                # /etc/fstab is in the subvolume, so it is necessary to
                # modify it and add the snapshot's name
                # grep -rnw '/etc/fstab' -e "/_active/rootvol"
                # First, it is necessary to obtain the original subvolume
                # for / which is mounted in the system (subvolume_origin_real)
                subvolume_origin_real = None
                command_string = """sudo btrfs subvolume show /"""
                command = [command_string]
                commandline_output = None
                try:
                    commandline_output = subprocess.check_output(command, shell=True)
                except subprocess.CalledProcessError as called_process_error_exception:
                    self.__logger.error("Error retrieving the real and mounted subvolume for / . Reason: " +
                                        str(called_process_error_exception.reason))
                    everything_ok = False
                if everything_ok:
                    commandline_output = commandline_output.decode('utf-8')
                    for line_output in commandline_output.split("\n"):
                        # The original subvolume mounted for / will be always the first line
                        # of the output
                        subvolume_origin_real = line_output
                        break

                    # Creating the snapshot in rw mode
                    command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
                        command=BTRFS_CREATE_SNAPSHOT_RW_COMMAND,
                        subvolume_origin=self.subvolume_origin,
                        subvolume_dest=self.subvolume_dest,
                        snapshot_full_name=snapshot_full_name
                    )
                    utils.execute_command(command, console=True, root=True)

                    # Obtaining the real subvolume for the new snapshot created
                    subvolume_snapshot_created_real = None
                    command_string = """sudo btrfs subvolume show {subvolume_dest}{snapshot_full_name}""".format(
                        subvolume_dest=self.subvolume_dest,
                        snapshot_full_name=snapshot_full_name
                    )
                    command = [command_string]
                    commandline_output = None
                    try:
                        commandline_output = subprocess.check_output(command, shell=True)
                    except subprocess.CalledProcessError as called_process_error_exception:
                        self.__logger.error("Error retrieving the real subvolume for snapshot created. Reason: " +
                                            str(called_process_error_exception.reason))

                    commandline_output = commandline_output.decode('utf-8')
                    for line_output in commandline_output.split("\n"):
                        # The original subvolume mounted for / will be always the first line
                        # of the output
                        subvolume_snapshot_created_real = line_output
                        break

                    # Getting the line in fstab where it is necessary to substitute the subvolume which is going to be
                    # mounted as root. It is necessary to discard all the lines with comments in fstab starting with '#'
                    command_string = """grep -rnw '{fstab_path}' -e '{subvolume_origin_real}'""".format(
                        fstab_path=fstab_path, subvolume_origin_real=subvolume_origin_real)
                    command = [command_string]
                    commandline_output = None
                    try:
                        commandline_output = subprocess.check_output(command, shell=True)
                    except subprocess.CalledProcessError:
                        pass
                    commandline_output = commandline_output.decode('utf-8')
                    # line will be the line where grep has matched subvolume_origin_real. All lines commented with '#'
                    # will be discarded
                    line = "0"
                    for line_output in commandline_output.split("\n"):
                        line_splitted = line_output.split(':')
                        # First element of the list will be the line where subvolume_origin_real has been matched by
                        # grep command. If the second element is '#', this line is commented in fstab and it won't be
                        # taken into account
                        if not line_splitted[1].startswith('#'):
                            line = line_splitted[0]
                            break

                    command_string = """sudo -S sed -i '{line}s|{subvolume_origin_real}|{subvolume_snapshot_created_real}|g' {subvolume_dest}{snapshot_full_name}/etc/fstab""".format(
                        line=line,
                        subvolume_origin_real=subvolume_origin_real,
                        subvolume_snapshot_created_real=subvolume_snapshot_created_real,
                        subvolume_dest=self.subvolume_dest,
                        snapshot_full_name=snapshot_full_name
                    )
                    command = [command_string]
                    try:
                        subprocess.check_output(command, shell=True)
                    except subprocess.CalledProcessError as called_process_error_exception:
                        self.__logger.error("Error trying to substitute the root's path in fstab with the "
                                            "path of the new snapshot created. Reason: " +
                                            str(called_process_error_exception.reason))
                        everything_ok = False
                    if everything_ok:
                        # subvolume_origin_real will be stored in configuration file in order to let the
                        # user to consolidate the system's rollback to any snapshot different from the main one
                        settings.properties_manager.set_property('path_to_consolidate_root_snapshot',
                                                                      subvolume_origin_real)

                        # Run grub-btrfs in order to regenerate GRUB entries
                        self.__logger.info("Regenerating GRUB entries. Please wait...")
                        utils.execute_command(GRUB_BTRFS_COMMAND, console=True, root=True)

                else:
                    # The original subvolume mounted for / couldn't be found
                    # Snapshot won't be created
                    self.__logger.error("The original subvolume mounted for / couldn't be found. "
                                        "Snapshot won't be created: ")
                    pass

            else:
                command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
                    command=BTRFS_CREATE_SNAPSHOT_R_COMMAND,
                    subvolume_origin=self.subvolume_origin,
                    subvolume_dest=self.subvolume_dest,
                    snapshot_full_name=snapshot_full_name
                )
                utils.execute_command(command, console=True, root=True)
        else:
            command = "{command} {subvolume_origin} {subvolume_dest}{snapshot_full_name}".format(
                command=BTRFS_CREATE_SNAPSHOT_R_COMMAND,
                subvolume_origin=self.subvolume_origin,
                subvolume_dest=self.subvolume_dest,
                snapshot_full_name=snapshot_full_name
            )
            utils.execute_command(command, console=True, root=True)

    def delete_snapshots(self):
        """Deletes (or not if user has defined it) all the snapshots needed to keep the desired number set by the user.
        It will delete the related logs if they exist

        """
        info_message = "Deleting snapshot of {subvolume_origin} in {subvolume_dest}. " \
                       "Please wait...".format(subvolume_origin=self.subvolume_origin,
                                               subvolume_dest=self.subvolume_dest)
        self.__logger.info(info_message)

        # If user has selected not delete any snapshot, this operation won't be done
        if self.snapshots_to_keep > -1:
            # Checking how many snapshots are with the same name ordered by date
            snapshots = self.get_all_snapshots_with_the_same_name()

            # Removing all the snapshots needed starting with the oldest one until reach
            # the limit defined by the user
            snapshots_to_delete = len(snapshots) - self.snapshots_to_keep
            index = 0
            while snapshots_to_delete > 0:
                # Deletes the snapshot
                command = "{command} {snapshot}".format(command=BTRFS_DELETE_SNAPSHOT_COMMAND,
                                                        snapshot=snapshots[index])
                utils.execute_command(command, console=True, root=True)
                info_message = "Snapshot {snapshot} deleted.\n".format(snapshot=snapshots[index])
                self.__logger.info(info_message)
                # Deletes the log if it exists
                snapshot_name = snapshots[index].split("/")[-1]
                log = "{snapshot_name}-{index}.txt".format(snapshot_name=snapshot_name.split("-")[-2],
                                                           index=snapshot_name.split("-")[-1])
                log_path = os.path.join(settings.logs_path, log)
                if os.path.exists(log_path):
                    try:
                        os.remove(log_path)
                        info_message = "Log {log} deleted.\n".format(log=log)
                        self.__logger.info(info_message)
                    except OSError as os_error_exception:
                        info_message = "Error deleting log {log}. Error {exception}\n".format(log=log,
                                                                                              exception=str(
                                                                                                  os_error_exception))
                        self.__logger.info(info_message)
                else:
                    info_message = "Log {log} doesn't exist. Skipping...deleted.\n".format(log=log)
                    self.__logger.info(info_message)

                snapshots_to_delete -= 1
                index += 1

            # Checks if grub-btrfs integration is enabled
            if settings.properties_manager.get_property("grub_btrfs"):
                # Run grub-btrfs in order to regenerate GRUB entries
                utils.execute_command(GRUB_BTRFS_COMMAND, console=True, root=True)

    def delete_origin(self):
        """Deletes the original subvolume, i.e. the subvolume in subvolume_origin

        """
        info_message = "Deleting subvolume from origin {subvolume_origin}. " \
                       "Please wait...".format(subvolume_origin=self.subvolume_origin)
        self.__logger.info(info_message)
        errors = False

        # Deletes the subvolume
        command_string = "{command} {snapshot}".format(command=BTRFS_DELETE_SNAPSHOT_COMMAND,
                                                       snapshot=self.subvolume_origin)
        command = [command_string]
        commandline_output = None
        try:
            # This is a special way for executing a command using Python:
            # shell=True allows the execution of complex shell commands
            # stdout=subprocess.PIPE captures the output generated by the command
            # stderr=subprocess.STDOUT captures the errors generated by the command and redirects them to stdout
            commandline_output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            commandline_output = commandline_output.stdout.decode('utf-8')
        except subprocess.CalledProcessError:
            pass

        for line in commandline_output.split("\n"):
            if 'Directory not empty' in line:
                errors = True
                break
        if errors:
            # Subvolume is not empty so it can't be deleted. Exception is thrown
            raise exception.BtrfsSnapshotDeletion("Error: {snapshot} is not empty.\n".
                                                            format(snapshot=self.subvolume_origin))
        else:
            info_message = "Snapshot {snapshot} deleted.\n".format(snapshot=self.subvolume_origin)
            self.__logger.info(info_message)

    def get_all_snapshots_with_the_same_name(self):
        """Retrieves all the snapshots with name self.snapshot_name stored within self.subvolume_dest.

        Returns:
            list (:obj:`list` of :obj:`str`): paths to the snapshots.
        """
        # Checking how many snapshots are with the same name ordered by date
        snapshots = glob.glob("{snapshot_directory}/*".format(snapshot_directory=self.subvolume_dest))
        snapshots.sort(key=os.path.getmtime)
        snapshots_whit_same_name = [file for file in snapshots if self.snapshot_name in file]

        return snapshots_whit_same_name


class RootSnapshotChecker:
    """Checks if the current snapshot used for root is the default or the user has booted the system from
    an alternate snapshot.

    """
    def __init__(self, parent_window):
        # Attributes
        self.__snapshot_to_clone_in_root_full_path = None
        self.__root_subvolume = None
        # Logger
        self.__logger = utils.Logger(self.__class__.__name__).get()
        self.__logger.info("Checking if the current snapshot used for root is the default. Please wait...")
        self.__parent_window = parent_window

    def check_root_snapshot(self):
        """Checks if the current snapshot used for root is the default or the user has booted the system from
        an alternate snapshot.

        Returns:
            boolean: true if current snapshot used for root is the default or this paramenter has not been stored yet;
                     false otherwise.
        """
        # First, it is necessary to check if path_to_consolidate_root_snapshot is defined
        if settings.properties_manager.get_property("path_to_consolidate_root_snapshot") != 0:
            # Obtaining the mounted subvolume for root partition
            # mount | grep 'on / ' | grep -o 'subvol=/.*' | cut -f2- -d=
            command_string = """mount | grep 'on / ' | grep -o 'subvol=/.*' | cut -f2- -d="""
            command = [command_string]
            mounted_snapshot_raw = None
            try:
                mounted_snapshot_raw = subprocess.check_output(command, shell=True)
            except subprocess.CalledProcessError:
                pass
            if mounted_snapshot_raw:
                # Removing the last two characters (a /n and a ")")
                mounted_snapshot_raw = mounted_snapshot_raw[:-2]
                # Converting bytes into string
                mounted_snapshot_raw = mounted_snapshot_raw.decode("utf-8")
                # Removing first / if path_to_consolidate_root_snapshot doesn't start with /
                if not settings.properties_manager.get_property("path_to_consolidate_root_snapshot")\
                        .startswith("/"):
                    mounted_snapshot_raw = mounted_snapshot_raw[1:]
            if mounted_snapshot_raw != settings.properties_manager. \
                    get_property("path_to_consolidate_root_snapshot"):
                # If mounted snapshot is different from the supposed default root subvolume
                # it means that user has booted the system using an alternate snapshot from GRUB.
                # ButterManager will ask to consolidate the current snapshot as the default root
                # subvolume

                # Obtaining the snapshot mounted
                mounted_snapshot_full_path = None
                while mounted_snapshot_full_path is None:
                    for subvolume in settings.subvolumes:
                        snapshots = settings.subvolumes[subvolume].get_all_snapshots_with_the_same_name()
                        for snapshot in snapshots:
                            if mounted_snapshot_raw in snapshot:
                                mounted_snapshot_full_path = snapshot
                                break
                        if mounted_snapshot_full_path is not None:
                            break

                self.__snapshot_to_clone_in_root_full_path = mounted_snapshot_full_path
                self.__root_subvolume = settings.subvolumes[subvolume]
                return False
            else:
                return True
        else:
            # Path to consolidate root snapshot hasn't been defined yet so this check is skipped
            return True

    def open_consolidate_snapshot_window(self):
        """Checks if the current snapshot used for root is the default or the user has booted the system from
        an alternate snapshot.

        Returns:
            QDialog: The dialog window to consolidate the root snapshot.
        """
        info_window = windows.ConsolidateSnapshotWindow(self.__parent_window,
                                                               self.__snapshot_to_clone_in_root_full_path,
                                                               self.__root_subvolume)
        return info_window


class Differentiator(QThread):
    """Independent thread that will calculate the differences between a snapshot and its current state.

    """
    # Constants
    DIFFS_DIR = "diffs"
    DIFF_COMMAND = "sudo -S diff -qr"
    MODIFIED_FILE = "modified.txt"
    OPERATION_FULL = "full_operation"
    OPERATION_PARTIAL = "partial_operation"

    # Attributes
    # pyqtSignal that will be emitted when this class requires to display
    # a single information window on the screen
    show_one_window = pyqtSignal('bool')

    # Constructor
    def __init__(self, snapshot_full_path, operation_type):
        QThread.__init__(self)
        self.__snapshot_full_path = snapshot_full_path
        self.__snapshot_name = snapshot_full_path.split("/")[-1]
        self.__operation_type = operation_type

    # Methods
    def run(self):
        # Main window will be hidden
        self.on_show_one_window(True)
        info_dialog = windows.InfoWindow(None, "Calculating differences in\n"
                                                      "'{snapshot_name}'.\n"
                                                      "Please, be patient. This process\n"
                                                      "can take several minutes. This\n"
                                                      "window will be closed when the\n"
                                                      "operation is done. Calculating..."
                                                      .format(snapshot_name=self.__snapshot_full_path))
        # Displaying info window
        info_dialog.show()

        # Calculates differences
        self.__calculate_differences()

        # Hiding info window
        info_dialog.hide()

        # Main window will be shown again
        self.on_show_one_window(False)

    def __calculate_differences(self):
        """Wraps all the operations to calculate differences.

        """
        # Gets the subvolume of the snapshot
        subvolume = get_subvolume_by_snapshot_name(self.__snapshot_full_path)

        if subvolume:
            # Creating a directory to store all the diff files generated if it doesn't exist
            # or removing and creating it if it existed
            diffs_path = os.path.join(settings.application_path, self.DIFFS_DIR, self.__snapshot_name)

            if os.path.exists(diffs_path):
                shutil.rmtree(diffs_path)

            os.makedirs(diffs_path)

            # Getting the current subvolune name. This subvolume is the current one which is going to be
            # used for the comparison. It is needed to remove all the empty strings within the list
            subvolume_name_list = subvolume.subvolume_origin.split("/")
            subvolume_name = list(filter(None, subvolume_name_list))[-1]

            if self.__operation_type == self.OPERATION_FULL:
                # Full operation
                # Creating 3 different files to store differences
                files_only_in_dir1_path = os.path.join(diffs_path, "{file_name}.txt".format(file_name=subvolume_name))
                files_only_in_dir2_path = os.path.join(diffs_path, "{file_name}.txt".format(
                    file_name=self.__snapshot_name))
                files_in_both_modified_path = os.path.join(diffs_path, self.MODIFIED_FILE)
                files_only_in_dir1 = open(files_only_in_dir1_path, "w+")
                files_only_in_dir2 = open(files_only_in_dir2_path, "w+")
                files_in_both_modified = open(files_in_both_modified_path, "w+")

                files_in_both_modified.write("Files in both snapshots that have been modified" + "\r\n\r\n")
                files_only_in_dir1.write("Files only in ${dir}".format(dir=subvolume.subvolume_origin) + "\r\n\r\n")
                files_only_in_dir2.write("Files only in ${dir}".format(dir=self.__snapshot_full_path) + "\r\n\r\n")

                # Calculating differences
                command = "{command} {dir1} {dir2}".format(command=self.DIFF_COMMAND, dir1=subvolume.subvolume_origin,
                                                           dir2=self.__snapshot_full_path)
                echo = subprocess.Popen(['echo', settings.user_password], stdout=subprocess.PIPE)
                result = subprocess.Popen(command.split(), stdin=echo.stdout, stdout=subprocess.PIPE)

                for line in iter(result.stdout.readline, b''):
                    line_decoded = line.decode('utf-8')
                    if " differ" in line_decoded:
                        file_modified_splitted = line_decoded.split(
                            "Files {path}".format(path=subvolume.subvolume_origin))
                        file_modified = "/" + file_modified_splitted[1].split(" ")[0]
                        files_in_both_modified.write(file_modified + "\r\n")
                    elif "Only in {dir1}".format(dir1=subvolume.subvolume_origin) in line_decoded:
                        file_only_in_dir1_splitted = line_decoded.split("Only in {path}".format(
                            path=subvolume.subvolume_origin))
                        file_only_in_dir1_splitted = file_only_in_dir1_splitted[1].split(":")
                        file_name = file_only_in_dir1_splitted[1].strip()
                        file_only_in_dir1 = "/" + file_only_in_dir1_splitted[0] + "/" + file_name
                        files_only_in_dir1.write(file_only_in_dir1 + "\r\n")
                    elif "Only in {dir2}".format(dir2=self.__snapshot_full_path) in line_decoded:
                        file_only_in_dir2_splitted = line_decoded.split("Only in {path}".format(
                            path=self.__snapshot_full_path))
                        file_only_in_dir2_splitted = file_only_in_dir2_splitted[1].split(":")
                        file_name = file_only_in_dir2_splitted[1].strip()
                        file_only_in_dir2 = file_only_in_dir2_splitted[0] + "/" + file_name
                        files_only_in_dir2.write(file_only_in_dir2 + "\r\n")
                # Closing files
                files_only_in_dir1.close()
                files_only_in_dir2.close()
                files_in_both_modified.close()

                # Opening the file with the default application installed in the OS
                # Warning, xdg-open is not working executing the code from PyCharm so
                # it seems it doesn't work but it is really working
                subprocess.call(['xdg-open', files_only_in_dir1_path])
                subprocess.call(['xdg-open', files_only_in_dir2_path])
                subprocess.call(['xdg-open', files_in_both_modified_path])

            else:
                # Partial operation
                # Creating only one file to store differences
                temp_sorted_modified_path = os.path.join(diffs_path, "tmp.txt")
                temp_sorted_modified = open(temp_sorted_modified_path, "w+")

                # Calculating differences
                # sudo btrfs subvolume find-new /mnt/defvol/_snapshots/root-20201021-0/  '9999999'
                # sudo btrfs subvolume find-new /mnt/defvol/_active/rootvol/ 463579 | sed '$d' | cut -f17- -d' ' |
                # sort | uniq

                # First, old transid is calculated. This ID will be used as a reference for the comparison
                transid = "9999999"
                command = "{command} {dir1} {transid}".format(command=BTRFS_FIND_NEW_COMMAND,
                                                              dir1=self.__snapshot_full_path, transid=transid)
                echo = subprocess.Popen(['echo', settings.user_password], stdout=subprocess.PIPE)
                result = subprocess.Popen(command.split(), stdin=echo.stdout, stdout=subprocess.PIPE)

                for line in iter(result.stdout.readline, b''):
                    line_decoded = line.decode('utf-8')
                    line_splitted = line_decoded.split(" ")
                    transid = line_splitted[-1].strip()

                # Then, the differences are obtained using transid
                command = "{command} {dir1} {transid}".format(
                    command=BTRFS_FIND_NEW_COMMAND,
                    dir1=subvolume.subvolume_origin,
                    transid=transid)
                echo = subprocess.Popen(['echo', settings.user_password], stdout=subprocess.PIPE)
                result = subprocess.Popen(command.split(), stdin=echo.stdout, stdout=subprocess.PIPE)

                temp_sorted_modified.write("- Files in both snapshots that have been modified" + "\r\n")

                for line in iter(result.stdout.readline, b''):
                    line_decoded = line.decode('utf-8')
                    line_splitted = line_decoded.split(" ")
                    file_modified = "/" + line_splitted[-1].strip()
                    temp_sorted_modified.write(file_modified + "\r\n")

                # Closing file
                temp_sorted_modified.close()

                # Sorting file
                files_in_both_modified_path = os.path.join(diffs_path, self.MODIFIED_FILE)
                files_in_both_modified = open(files_in_both_modified_path, "w+")
                command = "sort {file}".format(file=temp_sorted_modified_path)
                subprocess.Popen(command.split(), stdout=files_in_both_modified)

                # Opening the file with the default application installed in the OS
                # Warning, xdg-open is not working executing the code from PyCharm so
                # it seems it doesn't work but it is really working
                subprocess.call(['xdg-open', files_in_both_modified_path])

    def on_show_one_window(self, one_window):
        """Emits a QT Signal to hide or show the rest of application windows.

        Arguments:
            one_window (boolean): Information window should be unique?.
        """
        self.show_one_window.emit(one_window)


# Module's methods
def delete_specific_snapshot(snapshot_full_path):
    """Deletes a specific snapshot.
    It will delete the specific log related if it exists too.

    Arguments:
        snapshot_full_path (string): path to the snapshot that user wants to delete.

    """
    # Logger
    logger = utils.Logger(sys.modules['__main__'].__file__).get()
    info_message = "Deleting snapshot {snapshot}".format(snapshot=snapshot_full_path)
    logger.info(info_message)

    command = "{command} {snapshot}".format(command=BTRFS_DELETE_SNAPSHOT_COMMAND, snapshot=snapshot_full_path)
    utils.execute_command(command, root=True)
    info_message = "Snapshot {snapshot} deleted.\n".format(snapshot=snapshot_full_path)
    logger.info(info_message)

    # Checks if grub-btrfs integration is enabled
    if settings.properties_manager.get_property("grub_btrfs"):
        # Run grub-btrfs in order to regenerate GRUB entries
        utils.execute_command(GRUB_BTRFS_COMMAND, console=True, root=True)
        info_message = "Regenerating GRUB entries. Please wait..."
        logger.info(info_message)

    # Deletes the log if it exists
    snapshot_name = snapshot_full_path.split("/")[-1]
    log = "{snapshot_name}-{index}.txt".format(snapshot_name=snapshot_name.split("-")[-2],
                                               index=snapshot_name.split("-")[-1])
    log_path = os.path.join(settings.logs_path, log)
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
            info_message = "Log {log} deleted.\n".format(log=log)
            logger.info(info_message)
        except OSError as os_error_exception:
            info_message = "Error deleting log {log}. Error {exception}\n".format(log=log,
                                                                                  exception=str(os_error_exception))
            logger.info(info_message)
    else:
        info_message = "Log {log} doesn't exist. Skipping...deleted.\n".format(log=log)
        logger.info(info_message)


def get_subvolume_by_snapshot_name(snapshot_name):
    """Gets a subvolume object using the name of the snapshot.

    Arguments:
        snapshot_name (string): name of the snapshot.

        Returns:
            Subvolume: The subvolume which belongs the snapshot. None if subvolume was not found.
    """
    # Logger
    logger = utils.Logger(sys.modules['__main__'].__file__).get()
    info_message = "Getting subvolume from snapshot's name {snapshot_name}".format(snapshot_name=snapshot_name)
    logger.info(info_message)

    subvolume_found = None

    for subvolume_key in settings.subvolumes:
        subvolume = settings.subvolumes[subvolume_key]
        subvolume_snapshots_prefix = "{subvolume_dest}{subvolume_prefix}".format(
            subvolume_dest=subvolume.subvolume_dest,
            subvolume_prefix=subvolume.snapshot_name)
        if snapshot_name.startswith(subvolume_snapshots_prefix):
            info_message = "Found subvolume {subvolume}".format(subvolume=subvolume.subvolume_origin)
            logger.info(info_message)
            subvolume_found = subvolume
    return subvolume_found
