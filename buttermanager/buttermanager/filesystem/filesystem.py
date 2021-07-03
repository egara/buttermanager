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

"""This module gathers all the operations related to BTRFS filesystems.

It provides also Filesystem class.
"""
from ..exception import exception
from ..window import windows
import sys
from ..util import utils
from PyQt5.QtCore import QThread, pyqtSignal

# Constants
DEVID = "devid"
LABEL = "Label"
UUID = "uuid:"
DEVICE_SIZE = "Device size:"
DEVICE_ALLOCATED = "Device allocated:"
DATA = "Data,"
METADATA = "Metadata,"
SYSTEM = "System,"
SIZE = "Size:"
USED = "Used:"
BTRFS_SHOW_COMMAND = "sudo -S btrfs filesystem show"
FINDMT_COMMAND = "sudo -S findmnt -nt btrfs"
BTRFS_USAGE_COMMAND = "sudo -S btrfs filesystem usage"
BTRFS_BALANCE_COMMAND = "sudo -S btrfs balance start"
BTRFS_BALANCE_DATA_USAGE_FILTER = "dusage"
BTRFS_BALANCE_METADATA_USAGE_FILTER = "musage"


# Classes
class Filesystem:
    """BTRFS Filesystem.

    """
    # Constructor
    def __init__(self, uuid):

        self.__uuid = uuid
        self.__devices = self.__get_devices()
        self.__mounted_points = self.__get_mounted_points()
        filesystem_info = self.__get_filesystem_info(self.mounted_points[0])
        self.__total_size = filesystem_info['total_size']
        self.__total_allocated = filesystem_info['total_allocated']
        self.__data_size = filesystem_info['data_size']
        self.__data_used = filesystem_info['data_used']
        self.__data_percentage = filesystem_info['data_percentage']
        self.__metadata_size = filesystem_info['metadata_size']
        self.__metadata_used = filesystem_info['metadata_used']
        self.__metadata_percentage = filesystem_info['metadata_percentage']
        self.__system_size = filesystem_info['system_size']
        self.__system_used = filesystem_info['system_used']
        self.__system_percentage = filesystem_info['system_percentage']

    # Private attributes
    # UUID
    @property
    def uuid(self):
        return self.__uuid

    # Devices
    @property
    def devices(self):
        return self.__devices

    # Mounted points
    @property
    def mounted_points(self):
        return self.__mounted_points

    # Total size
    @property
    def total_size(self):
        return self.__total_size

    # Total allocated
    @property
    def total_allocated(self):
        return self.__total_allocated

    # Data size
    @property
    def data_size(self):
        return self.__data_size

    # Data used
    @property
    def data_used(self):
        return self.__data_used

    # Data percentage
    @property
    def data_percentage(self):
        return self.__data_percentage

    # Metadata size
    @property
    def metadata_size(self):
        return self.__metadata_size

    # Metadata used
    @property
    def metadata_used(self):
        return self.__metadata_used

    # Metadata percentage
    @property
    def metadata_percentage(self):
        return self.__metadata_percentage

    # System size
    @property
    def system_size(self):
        return self.__system_size

    # System used
    @property
    def system_used(self):
        return self.__system_used

    # System percentage
    @property
    def system_percentage(self):
        return self.__system_percentage

    # Methods
    # Private methods
    def __get_devices(self):
        """Retrieves all the devices which the BTRFS filesystem is composed.

        Returns:
            list (:obj:`list` of :obj:`str`): devices.
        """
        try:
            devices = []
            commandline_output = utils.execute_command(BTRFS_SHOW_COMMAND, root=True)
            filesystem_found = False

            for line in commandline_output.split("\n"):
                if UUID in line:
                    if filesystem_found:
                        break
                    else:
                        if self.uuid in line:
                            filesystem_found = True
                            continue

                if filesystem_found:
                    # The loop is inside the chosen BTRFS filesystem
                    # It is necessary to find devid to retrieve all the filesystem paths
                    if DEVID in line:
                        path_init = line.find('/')
                        # The device path is appended to the list
                        devices.append(line[path_init:len(line)])

            return devices

        except exception.NoCommandFound as no_command_found_exception:
            raise no_command_found_exception

    def __get_mounted_device(self):
        """Retrieves the device tha contains the BTRFS filesystem and it is mounted.

        Returns:
            string: device path.
        """
        try:
            mounted_device = ''
            commandline_output = utils.execute_command(FINDMT_COMMAND)
            for device in self.devices:
                if device in commandline_output:
                    mounted_device = device
                    break

            return mounted_device

        except exception.NoCommandFound as no_command_found_exception:
            raise no_command_found_exception

    def __get_mounted_points(self):
        """Retrieves all the mounted points of the BTRFS filesystem.

        Returns:
            list (:obj:`list` of :obj:`str`): mounted points.
        """
        try:
            mounted_points = []
            device = self.__get_mounted_device()
            command = "{command} {device}".format(command=FINDMT_COMMAND, device=device)
            commandline_output = utils.execute_command(command)

            for line in commandline_output.split("\n"):
                if len(line) > 0:
                    mounted_points.append(line.split(" ")[0].strip())

            return mounted_points

        except exception.NoCommandFound as no_command_found_exception:
            raise no_command_found_exception

    def __get_filesystem_info(self, mounted_point):
        """Retrieves all the information of the BTRFS filesystem.

        Returns:
            dictionary (key=:obj:'string', value=:obj:'str' or obj:'int'): all the info. The keys of the dictionary
            will be:
                - total_size: Device size
                - total_allocated: Device allocated
                - data_size: Data size
                - data_used: Data used
                - data_percentage: Percentage of data used
                - metadata_size: Metadata size
                - metadata_used: Metadata used
                - metadata_percentage: Percentage of metadata used
                - system_size: System size
                - system_used: System used
                - system_percentage: Percentage of system used
        """
        filesystem_info = {'total_size': '0', 'total_allocated': '0',
                           'data_size': '0', 'data_used': '0', 'data_percentage': 0,
                           'metadata_size': '0', 'metadata_used': '0', 'metadata_percentage': 0,
                           'system_size': '0', 'system_used': '0', 'system_percentage': 0}
        command = "{command} {point}".format(command=BTRFS_USAGE_COMMAND, point=mounted_point)
        commandline_output = utils.execute_command(command, root=True)

        for line in commandline_output.split("\n"):
            if DEVICE_SIZE in line:
                filesystem_info['total_size'] = line.split(DEVICE_SIZE)[1].strip()
            elif DEVICE_ALLOCATED in line:
                filesystem_info['total_allocated'] = line.split(DEVICE_ALLOCATED)[1].strip()
            elif DATA in line:
                data_size = line.split(SIZE)[1].split(',')[0].strip()
                filesystem_info['data_size'] = data_size
                data_used = line.split(USED)[1].strip()
                if '(' in data_used:
                    # New versions of btrfs-progs already include the percentage
                    data_used = data_used.split()[0].strip()
                filesystem_info['data_used'] = data_used
                filesystem_info['data_percentage'] = utils.get_percentage(filesystem_info['data_size'],
                                                                               filesystem_info['data_used'])
            elif METADATA in line:
                metadata_size = line.split(SIZE)[1].split(',')[0].strip()
                filesystem_info['metadata_size'] = metadata_size
                metadata_used = line.split(USED)[1].strip()
                if '(' in metadata_used:
                    # New versions of btrfs-progs already include the percentage
                    metadata_used = metadata_used.split()[0].strip()
                filesystem_info['metadata_used'] = metadata_used
                filesystem_info['metadata_percentage'] = utils.get_percentage(filesystem_info['metadata_size'],
                                                                                   filesystem_info['metadata_used'])
            elif SYSTEM in line:
                system_size = line.split(SIZE)[1].split(',')[0].strip()
                filesystem_info['system_size'] = system_size
                filesystem_info['system_used'] = line.split(USED)[1].strip()
                filesystem_info['system_percentage'] = utils.get_percentage(filesystem_info['system_size'],
                                                                                 filesystem_info['system_used'])

        return filesystem_info

    # Public methods
    def __str__(self):
        """Reimplementation of the str method inherited from object class.

        Returns:
            string: String representation of the Filesystem object.
        """
        return "BTRFS Filesystem -> UUID: {0}; Devices: {1}; Mounted Points: {2}".format(self.uuid, self.devices,
                                                                                         self.mounted_points)


# Module's methods
def get_btrfs_filesystems(mounted=True):
    """Retrieves all the BTRFS filesystems.

    Keyword arguments:
        mounted (bool): Only mounted filesystems will be retrieved (default True).

    Returns:
        list (:obj:`list` of :obj:`str`): filesystems UUID.
    """

    filesystems = []
    command = BTRFS_SHOW_COMMAND

    if mounted:
        command += " --mounted"

    commandline_output = utils.execute_command(command, root=True)

    for line in commandline_output.split("\n"):
        if UUID in line:
            # The uuid is appended to the list
            filesystems.append(line.split(UUID)[1].strip())

    return filesystems


def balance_filesystem(filter, percentage, mounted_point):
    """Balances a specific filesystem.

    Arguments:
        filter (string): filter.
        percentage (int): usage filter.
        mounted_point: path to balance.
    """
    # Logger
    logger = utils.Logger(sys.modules['__main__'].__file__).get()
    logger.info("Balancing {mounted_point} using filter {filter} and "
                "percentage {percentage}".format(mounted_point=mounted_point,
                                                 filter=filter,
                                                 percentage=percentage))

    command = "{command} -{filter}={percentage} {mounted_point}".format(command=BTRFS_BALANCE_COMMAND,
                                                                        filter=filter,
                                                                        percentage=percentage,
                                                                        mounted_point=mounted_point)
    logger.info("Command executed {command}".format(command=command))
    commandline_output = utils.execute_command(command, root=True)
    for line in commandline_output.split("\n"):
        logger.info(line)


class BalanceManager(QThread):
    """Independent thread that will run the filesystem balancing process.

    """
    # Attributes
    # pyqtSignal that will be emitted when this class requires to display
    # a single information window on the screen
    show_one_window = pyqtSignal('bool')

    # pyqtSignal that will be emitted when this class requires that main
    # window refreshes current filesystem statistics
    refresh_filesystem_statistics = pyqtSignal()

    # Constructor
    def __init__(self, data_percentage, metadata_percentage, mounted_point):
        QThread.__init__(self)
        self.__data_percentage = data_percentage
        self.__metadata_percentage = metadata_percentage
        self.__mounted_point = mounted_point

    # Methods
    def run(self):
        # Main window will be hidden
        self.on_show_one_window(True)
        info_dialog = windows.InfoWindow(None, "Balancing '{mounted_point}' mounted point. \n"
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
        # Balancing data
        balance_filesystem(
            BTRFS_BALANCE_DATA_USAGE_FILTER,
            self.__data_percentage,
            self.__mounted_point)
        # Balancing metadata
        balance_filesystem(
            BTRFS_BALANCE_METADATA_USAGE_FILTER,
            self.__metadata_percentage,
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
