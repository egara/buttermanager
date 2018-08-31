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

"""This module gathers all the utils and tools for buttermanager application.

It provides also NoCommandFound exception class.
"""

import subprocess
import shutil
import util.settings
import pathlib
import os
import logging
import logging.handlers
import sys

# Constants
GB = "GiB"  # Gigabytes
MB = "MiB"  # Megabytes
KB = "KiB"  # Kilobytes
B = "B"     # Bytes
BYTE_SIZE = 1024
OS_DEBIAN = "DEBIAN"
DEBIAN_PM = "apt"
OS_ARCH = "ARCH"
ARCH_PM = "pacman"
SNAP_PM = "snap"

# Classes
class NoCommandFound(Exception):
    """Exception raised when a needed program is not installed in the system.

    """
    pass


class ConfigManager:
    """Manages the configuration.

    """
    # Constants
    APP_NAME = "buttermanager"

    # Constructor
    def __init__(self):
        # Setting global values related to the application
        util.settings.application_name = self.APP_NAME
        application_directory = ".{name}".format(name=util.settings.application_name)
        util.settings.application_path = os.path.join(str(pathlib.Path.home()), application_directory)

    def configure(self):
        """Configures the application.

        """
        # Creating application's directory if it is needed
        if not os.path.exists(util.settings.application_path):
            os.makedirs(util.settings.application_path)

        # Checking OS
        if exist_program(DEBIAN_PM):
            util.settings.user_os = OS_DEBIAN
        elif exist_program(ARCH_PM):
            util.settings.user_os = OS_ARCH

        # Number of snapshots to keep
        # TODO: Obtain this value from a config file
        util.settings.snapshots_to_keep = 2


class Logger(object):
    """Creates the logs of the application.

    """
    def __init__(self, class_name):
        name = os.path.join(util.settings.application_path, "buttermanager.log")
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


# Module's methods
def execute_command(command, console=False):
    """Executes a shell command.

    Arguments:
        command (string): Command to be executed.
        console (boolean): The command output needs to be redirected to the console.

    Returns:
        string: Command line output encoded in UTF-8.
    """

    # Checking if the program executed by the command is installed in the system
    program = command.split()
    single_command = program[0]
    if "sudo" in program:
        sudo_position = program.index("sudo")
        single_command = program[sudo_position + 2]
    if exist_program(single_command):
        echo = subprocess.Popen(['echo', util.settings.user_password], stdout=subprocess.PIPE)
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
        logger = util.utils.Logger(sys.modules['__main__'].__file__).get()
        logger.info(single_command + " program does not exist in the system")
        raise NoCommandFound()


def get_percentage(total, parcial):
    """Calculates the percentage between total amount and parcial amount.

    Arguments:
        total (string): Total amount. It should be specified the unit, f.i.: 30.00GiB
        parcial (string): Parcial amount. It should be specified the unit, f.i.: 3.00GiB
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
        number_unit_string (string): String consisting of amount and unit, f.i.: 30.00GiB

    Returns:
        dictionary (key=:obj:'string', value=:obj:'str' or obj:'int'): all the info. The keys of the dictionary will be:
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


def exist_program(program):
    """Checks if a program is installed on the system.

    Arguments:
        program (string): Program to check

    Returns:
        bool: True if the program is installed, False otherwise

    >>> exist_program('ls')
    True
    """
    path = shutil.which(program)
    return path is not None
