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

"""This module gathers all the utils and tools for buttermanager application.

"""
from . import settings
from ..exception import exception
from ..filesystem import snapshot
from ..window import windows
from PyQt5.QtWidgets import QFileDialog
from tkinter import Tk
from tkinter.filedialog import askdirectory
import logging
import logging.handlers
import os
import pathlib
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
import yaml

# Constants
GB = "GiB"  # Gigabytes
MB = "MiB"  # Megabytes
KB = "KiB"  # Kilobytes
B = "B"     # Bytes
BYTE_SIZE = 1024
ARCH_PM = "pacman"
DEBIAN_PM = "apt"
SUSE_PM = "zypper"
FEDORA_PM = "dnf"
SNAP_PM = "snap"
OS_ARCH = "ARCH"
OS_DEBIAN = "DEBIAN"
OS_SUSE = "SUSE"
OS_FEDORA = "FEDORA"
VERSION_URL = "https://raw.githubusercontent.com/egara/buttermanager/master/version.txt"


class ConfigManager:
    """Manages the configuration.

    """
    # Constants
    APP_NAME = "buttermanager"
    LOGS_DIR = "logs"

    # Constructor
    def __init__(self):
        # Setting global values related to the application
        settings.application_name = self.APP_NAME
        application_directory = ".{name}".format(name=settings.application_name)
        settings.application_path = os.path.join(str(pathlib.Path.home()), application_directory)
        settings.logs_path = os.path.join(settings.application_path, self.LOGS_DIR)

        # Creating application's directory if it is needed
        if not os.path.exists(settings.application_path):
            # Application directory does not exist. Creating directory...
            os.makedirs(settings.application_path)

            # Creating buttermanager.yaml file with default values
            config_file_as_dictionary = '''
                aur_repository: 0
                check_at_startup: 0
                snap_packages: 0
                flatpak_packages: 0
                save_log: 1
                grub_btrfs: 0
                path_to_consolidate_root_snapshot: 0
                subvolumes_dest:
                subvolumes_orig:
                subvolumes_prefix:
                subvolumes_snapshots_to_keep:
                font_size_increment: 0
            '''
            config_file_dictionary = yaml.safe_load(config_file_as_dictionary)
            conf_file_path = '{application_path}/{conf_file}'.format(application_path=settings.application_path,
                                                                     conf_file=settings.CONF_FILE)
            conf_file = open(conf_file_path, 'w')
            yaml.dump(config_file_dictionary, conf_file)
            conf_file.close()

            # Sanitazing config file. All null values will be replaced by blank spaces
            with open(conf_file_path, 'r') as file:
                config_file_data = file.read()
                config_file_data = config_file_data.replace('null', '')

            with open(conf_file_path, 'w') as file:
                file.write(config_file_data)

        # Creating logs directory if it doesn't exist
        if not os.path.exists(settings.logs_path):
            os.makedirs(settings.logs_path)

        # Logger
        self.__logger = Logger(self.__class__.__name__).get()

    def configure(self):
        """Configures the application.

        """
        # Version
        settings.application_version = settings.VERSION

        # Checking OS
        if exist_program(SUSE_PM):
            settings.user_os = OS_SUSE
        elif exist_program(DEBIAN_PM):
            settings.user_os = OS_DEBIAN
        elif exist_program(ARCH_PM):
            settings.user_os = OS_ARCH
        elif exist_program(FEDORA_PM):
            settings.user_os = OS_FEDORA
        self.__logger.info("Checking OS. {os} found".format(os=settings.user_os))

        # Checking Desktop Environment
        settings.desktop_environment = get_desktop_environment()
        self.__logger.info("Checking Desktop Environment. {de} found".format(de=settings.desktop_environment))

        # Checking Installation Type
        if not os.path.exists("/opt/buttermanager/buttermanager"):
            settings.installation_type = "native"
        else:
            settings.installation_type = "venv"
        self.__logger.info("Installation type: {installation}".format(installation=settings.installation_type))

        # Creating a properties manager to manage all the application properties
        self.__logger.info("Creating PropertiesManager...")
        settings.properties_manager = settings.PropertiesManager()

        # Triggering migration process
        self.migrate_properties()

        # Retrieving configuration...
        self.__logger.info("Retrieving user's configuration from buttermanager.yaml file and loading it in memory...")

        # Do the user want to update snap packages during the upgrading process
        settings.snap_packages = int(settings.properties_manager.get_property('snap_packages'))

        # Do the user want to update flatpak packages during the upgrading process
        settings.flatpak_packages = int(settings.properties_manager.get_property('flatpak_packages'))

        # Do the user want to update AUR packages during the upgrading process
        settings.aur_repository = int(settings.properties_manager.get_property('aur_repository'))

        # Do the user want to check for updates at startup
        settings.check_at_startup = int(settings.properties_manager.get_property('check_at_startup'))

        # Do user want to boot the system from GRUB using snapshots
        settings.grub_btrfs = int(settings.properties_manager.get_property('grub_btrfs'))

        # The path of the root snapshot that must be within /etc/fstab as / mount point
        # It will be 0 if this property is not defined yet or it is empty
        settings.path_to_consolidate_root_snapshot = settings.properties_manager.\
            get_property('path_to_consolidate_root_snapshot')

        # Do the user want to save logs automatically
        settings.save_log = int(settings.properties_manager.get_property('save_log'))

        # Font size increment defined by the user
        settings.font_size_increment = int(settings.properties_manager.get_property('font_size_increment'))

        # Subvolumes to manage
        subvolumes_list = get_subvolumes()
        subvolumes = {}
        for subvolume in subvolumes_list:
            subvolumes[subvolume.subvolume_origin] = subvolume

        settings.subvolumes = subvolumes

    def migrate_properties(self):
        """Migrates buttermanager.yaml properties file from one version to another if necessary.

        """
        # Checking if it is necessary to do some migrations to newer versions

        # ##########################################
        # BEGIN Version 2.3 or older -> 2.4 or newer
        # ##########################################
        # Number of snapshots per subvolume have been introduced in version 2.4
        # Filling this property in case the user comes from version 2.3
        snapshots_to_keep = int(settings.properties_manager.get_property('snapshots_to_keep'))
        remove_snapshots = settings.properties_manager.get_property('remove_snapshots')
        if snapshots_to_keep != 0:
            # snapshots_to_keep property is still in buttermanager.yaml
            self.__logger.info("Migrating from version 2.3 or older to version 2.4 or newer. Please wait...")
            self.__logger.info("snapshots_to_keep property and remove_snapshots will be removed from buttermanager.yaml"
                               " configuration file and every subvolume defined will have their own properties")
            subvolumes_orig_raw = settings.properties_manager.get_property('subvolumes_orig')
            subvolumes_snapshots_to_keep_raw = ""
            if subvolumes_orig_raw is not None and subvolumes_orig_raw != "":
                subvolumes_orig = subvolumes_orig_raw.split("|")
                for index, subvolume_orig in enumerate(subvolumes_orig):
                    if remove_snapshots == 0:
                        # From this moment, when snapshots_to_keep is -1, then the user havve decided not to
                        # delete any snapshot
                        snapshots_to_keep = -1
                    subvolumes_snapshots_to_keep_raw += str(snapshots_to_keep)
                    if index + 1 < len(subvolumes_orig):
                        subvolumes_snapshots_to_keep_raw += "|"
            # Adding the new property
            settings.properties_manager.set_property('subvolumes_snapshots_to_keep', subvolumes_snapshots_to_keep_raw)

            # Removing old snapshots_to_keep and remove_snapshots properties
            settings.properties_manager.remove_property('snapshots_to_keep')
            settings.properties_manager.remove_property('remove_snapshots')

        # ########################################
        # END Version 2.3 or older -> 2.4 or newer
        # ########################################

        self.__logger.info("Migration process has finished successfully!")


class Logger(object):
    """Creates the logs of the application.

    """
    def __init__(self, class_name):
        name = os.path.join(settings.application_path, "buttermanager.log")
        logger = logging.getLogger(class_name)
        logger.setLevel(logging.DEBUG)

        # Add the log message handler to the logger
        handler = logging.handlers.RotatingFileHandler(name, maxBytes=1048576, backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s. %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.__logger = logger

    def get(self):
        return self.__logger


class VersionChecker:
    """Checks if there is a newest version of ButterManager available.

    """
    def __init__(self, parent_window):
        # Logger
        self.__logger = Logger(self.__class__.__name__).get()
        self.__logger.info("Checking for a new version of ButterManager. Please wait...")
        self.__version_url = VERSION_URL
        self.__parent_window = parent_window

    def check_version(self):
        """Checks if there is a newest version of ButterManager available.

        """
        try:
            # Retrieving the last version from GitHub
            response = urllib.request.urlopen(self.__version_url)
            last_version = response.read().decode(response.headers.get_content_charset()).strip()

        except urllib.error.HTTPError as exception:
            self.__logger.error("Error checking new versions of ButterManager. Reason: " + str(exception.reason))
        except urllib.error.URLError as exception:
            self.__logger.error("Error checking new versions of ButterManager. Reason: " + str(exception.reason))
        else:
            self.__logger.info("Last version is " + last_version + " and current version is " +
                               settings.application_version)

            if last_version != settings.application_version:
                if settings.user_os == OS_ARCH:
                    info_window = windows.GeneralInfoWindow(self.__parent_window, "New version " +
                                                                   last_version + " is available. Update ButterManager "
                                                                                  "via AUR")
                else:
                    info_window = windows.GeneralInfoWindow(self.__parent_window, "New version " +
                                                                   last_version + " is available. Check the repository "
                                                                   "\nof the project "
                                                                   "(https://github.com/egara/buttermanager)\n "
                                                                   "to get the latest code")

                info_window.show()


# Module's methods
def execute_command(command, console=False, root=False):
    """Executes a shell command.

    Arguments:
        command (str): Command to be executed.
        console (boolean): The command output needs to be redirected to the console.
        root (boolean): The command is only accesible by root user

    Returns:
        str: Command line output encoded in UTF-8.
    """

    # Checking if the program executed by the command is installed in the system
    program = command.split()
    single_command = program[0]
    if "sudo" in program:
        sudo_position = program.index("sudo")
        single_command = program[sudo_position + 2]
    if exist_program(single_command, root=root):
        echo = subprocess.Popen(['echo', settings.user_password], stdout=subprocess.PIPE)
        # run method receives a list, so it is necessary to convert command string into a list using split
        result = subprocess.Popen(command.split(), stdin=echo.stdout, stdout=subprocess.PIPE)

        if not console:
            # The whole output will be returned
            # result is Bytes type, so it is needed to decode Unicode string using UTF-8
            commandline_output = result.stdout.read().decode('utf-8')
        else:
            # The output will be written in stdout in real time
            # It is good for operations that need to display the output
            # in the GUI terminal of the application in real time
            for line in iter(result.stdout.readline, b''):
                sys.stdout.write(line.decode('utf-8'))
            commandline_output = None

        return commandline_output
    else:
        # Logger
        logger = Logger(sys.modules['__main__'].__file__).get()
        logger.info(single_command + " program does not exist in the system")
        raise exception.NoCommandFound()


def get_percentage(total, parcial):
    """Calculates the percentage between total amount and parcial amount.

    Arguments:
        total (str): Total amount. It should be specified the unit, f.i.: 30.00GiB
        parcial (str): Parcial amount. It should be specified the unit, f.i.: 3.00GiB
    Returns:
        int: Percentage between total and parcial, f.i.: 10 (3.00GiB is 10% of 30.00GiB).

    >>> get_percentage("30.00GiB", "3.00GiB")
    10
    """
    total_number_unit = get_number_unit(total)
    parcial_number_unit = get_number_unit(parcial)
    # All the operations will be done using Bytes unit as reference
    total_number = convert_to_bytes(total_number_unit)
    parcial_number = convert_to_bytes(parcial_number_unit)
    percentage = int((parcial_number * 100) / total_number)
    return percentage


def get_number_unit(number_unit_string):
    """Gets the number and the unit present in a specific string.

    Arguments:
        number_unit_string (str): String consisting of amount and unit, f.i.: 30.00GiB

    Returns:
        dictionary (key=:obj:'str', value=:obj:'str' or obj:'int'): all the info. The keys of the dictionary will be:
            - total_size: Device size
            - total_allocated: Device allocated

    >>> get_number_unit("30.00GiB")
    ['number': 30.00, 'unit': 'GiB']
    """
    number_unit = {'number': 0.0, 'unit': 'GiB'}
    number_unit_string_list = number_unit_string.split('.')
    number = float("{integer}.{decimal}".format(integer=number_unit_string_list[0].strip(),
                                                decimal=number_unit_string_list[1][0:2]))
    number_unit['number'] = number
    number_unit['unit'] = number_unit_string_list[1][2:]
    return number_unit


def convert_to_bytes(number_unit):
    """Converts a number into a bytes depending on its unit.

    Arguments:
        number_unit (dictionary): Number and unit to convert

    Returns:
        float: Number in bytes

    >>> number_unit = {'number': 30.00, 'unit': 'GiB'}
    >>> convert_to_bytes(number_unit)
    32212254720
    """
    factor = 1
    if number_unit['unit'] == GB:
        factor = factor * BYTE_SIZE * BYTE_SIZE * BYTE_SIZE
    elif number_unit['unit'] == MB:
        factor = factor * BYTE_SIZE * BYTE_SIZE
    elif number_unit['unit'] == KB:
        factor = factor * BYTE_SIZE
    elif number_unit['unit'] == B:
        factor = factor

    return number_unit['number'] * factor


def exist_program(program, root=False):
    """Checks if a program is installed on the system.

    Some problems have been detected in distributions like SUSE and OpenSUSE using
    shutil.which function. There are some commands, like btrfs, that are only found
    if sudo which is used instead of simply which from current user.
    Because of that, root variable has been declared above. By default, root value
    will be False, i.e. for those commands which are discoverable simply by using
    which without sudo.

    Arguments:
        program (string): Program to check
        root (boolean): The program to be checked is only usable by root user

    Returns:
        bool: True if the program is installed, False otherwise

    >>> exist_program('ls')
    True
    """
    if root:
        command = "sudo -S which " + program
        # Checking if the program executed by the command is installed in the system
        echo = subprocess.Popen(['echo', settings.user_password], stdout=subprocess.PIPE)
        # run method receives a list, so it is necessary to convert command string into a list using split
        result = subprocess.Popen(command.split(), stdin=echo.stdout, stdout=subprocess.PIPE)

        # The whole output will be returned
        # result is Bytes type, so it is needed to decode Unicode string using UTF-8
        commandline_output = result.stdout.read().decode('utf-8')
        exist = not commandline_output.startswith("which:")
        return exist
    else:
        path = shutil.which(program)
        return path is not None


def get_subvolumes():
    """Gets the subvolumes defined by the user in the properties file.

    Returns:
        list (:obj:`list` of :obj:`Subvolume`): subvolumes objects defined by the user.
    """
    subvolumes = []
    subvolumes_orig_raw = settings.properties_manager.get_property('subvolumes_orig')
    subvolumes_dest_raw = settings.properties_manager.get_property('subvolumes_dest')
    subvolumes_prefix_raw = settings.properties_manager.get_property('subvolumes_prefix')
    subvolumes_snapshots_to_keep_raw = settings.properties_manager.get_property('subvolumes_snapshots_to_keep')
    if subvolumes_orig_raw is not None and subvolumes_orig_raw != "":
        subvolumes_orig = subvolumes_orig_raw.split("|")
        subvolumes_dest = subvolumes_dest_raw.split("|")
        subvolumes_prefix = subvolumes_prefix_raw.split("|")
        subvolumes_snapshots_to_keep = subvolumes_snapshots_to_keep_raw.split("|")
        for index, subvolume_orig in enumerate(subvolumes_orig):
            subvolume = snapshot.Subvolume(subvolume_orig, subvolumes_dest[index], subvolumes_prefix[index],
                                           subvolumes_snapshots_to_keep[index])
            subvolumes.append(subvolume)

    return subvolumes


def scale_fonts(ui_elements):
    """Scales all the UI elements fonts in order to fit on the window.

    Arguments:
        ui_elements (list): UI elements to change the font
    """
    font_size = settings.base_font_size + int(settings.properties_manager.get_property('font_size_increment'))
    # Changing the font for every UI element
    for label in ui_elements:
        font = label.font()
        font.setPointSize(font_size)
        label.setFont(font)


def get_desktop_environment():
    """Gets desktop environment.
    """
    desktop_environment = 'generic'
    if os.environ.get('KDE_FULL_SESSION') == 'true':
        desktop_environment = 'kde'
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        desktop_environment = 'gnome'
    else:
        try:
            info = subprocess.getoutput('xprop -root _DT_SAVE_MODE')
            if ' = "xfce4"' in info:
                desktop_environment = 'xfce'
        except (OSError, RuntimeError):
            pass
    return desktop_environment


def open_file_browser_directory(parent_window):
    """Opens a file browser to select a directory.

    A bug has being detected in KDE Plasma native installatiom. When a native file browser is opened to
    select a directory, then the application crashes. This doesn't happen in GNOME for example. So a
    fallback has had to be implemented for this case, suing TKinter.

    Arguments:
        parent_window: Parent window

    Returns:
        str: Path of the directory selected
    """

    # Creating a QFileDialog or Tkinter file browser to select the directory
    # Only directories will be allowed
    selected_path = ""
    if settings.desktop_environment == 'kde' and settings.installation_type == 'native':
        Tk().withdraw()
        filename = askdirectory()

        if filename:
            selected_path = filename
    else:
        file_dialog = QFileDialog(parent_window)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)

        if file_dialog.exec_():
            selected_path = file_dialog.selectedFiles()[0]

    return selected_path
