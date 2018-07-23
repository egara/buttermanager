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


class NoCommandFound(Exception):
    """Exception raised when a needed program is not installed in the system.

    """
    pass


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

