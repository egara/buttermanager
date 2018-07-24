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
        self.__logger = Logger(self.__class__.__name__).get()
        util.settings.application_name = self.APP_NAME
        util.settings.application_path = os.path.join(pathlib.Path.home(), util.settings.application_name)

    def configure(self):
        """Configures the application.

        """
        # Creating application's directory if it is needed
        if not os.path.exists(util.settings.application_path):
            os.makedirs(util.settings.application_path)
            # self.__logger.info("The application directory doesn't exist. Creating " + util.settings.application_path)
            log_filename = os.path.join(util.settings.application_path, "test.log")
            logging.basicConfig(filename=log_filename,level=logging.DEBUG)
            logging.debug('This message should go to the log file')

class Logger(object):
    """Creates the logs of the application.

    """
    def __init__(self, name):
        name = name.replace('.log', '')
        logger = logging.getLogger('log_namespace.%s' % name)  # log_namespace can be replaced with your namespace
        logger.setLevel(logging.DEBUG)
        if not logger.handlers:
            file_name = os.path.join(util.settings.application_path, '%s.log' % name)
            handler = logging.FileHandler(file_name)
            formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s %(message)s')
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
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
        single_command = program[1]
    path = shutil.which(single_command)
    if path is not None:
        # run method receives a list, so it is necessary to convert command string into a list using split
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        # result is Bytes type, so it is needed to decode Unicode string using UTF-8
        commandline_output = result.stdout.decode('utf-8')

        return commandline_output
    else:
        # Todo: Logging
        print(single_command + " program does not exist in the system")
        raise NoCommandFound()

