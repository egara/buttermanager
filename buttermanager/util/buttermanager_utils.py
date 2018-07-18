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

"""

import subprocess


# Methods
def execute_command(command):
    """Executes a shell command.

    Arguments:
        command (string): Command to be executed.

    Returns:
        string: Output coded in UTF-8.
    """

    # run method receives a list, so it is necessary to convert command string into a list using split (by blank space)
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    # result is Bytes type, so it is needed to decode Unicode string using UTF-8
    commandline_output = result.stdout.decode('utf-8')

    return commandline_output
