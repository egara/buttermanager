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
def execute_command(command):
    """Executes a shell command.

    Arguments:
        command (string): Command to be executed.

    Returns:
        string: Command line output encoded in UTF-8.
    """

    # Checking if the program executed by the command is installed in the system
    program = command.split()
    single_command = program[0]
    if "sudo" in program:
        sudo_position = program.index("sudo")
        single_command = program[sudo_position + 2]
    path = shutil.which(single_command)
    if path is not None:
        echo = subprocess.Popen(['echo', util.settings.user_password], stdout=subprocess.PIPE)
        # run method receives a list, so it is necessary to convert command string into a list using split
        result = subprocess.Popen(command.split(), stdin=echo.stdout, stdout=subprocess.PIPE)
        # result is Bytes type, so it is needed to decode Unicode string using UTF-8
        commandline_output = result.stdout.read().decode('utf-8')
        return commandline_output
    else:
        # Logger
        logger = util.buttermanager_utils.Logger(sys.modules['__main__'].__file__).get()
        logger.info(single_command + " program does not exist in the system")
        raise NoCommandFound()
