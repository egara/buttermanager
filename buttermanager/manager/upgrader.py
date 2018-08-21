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

"""This module gathers all the managers built for the application.

"""
from PyQt5.QtCore import QThread, pyqtSignal


class Upgrader(QThread):
    """Indepented thread that will run the system upgrading process.

    """
    # Attributes

    # Constructor
    def __init__(self):
        QThread.__init__(self)

    # Methods
    def run(self):
        # Upgrading the filesystem
        # self.__balance_filesystem()
        # Todo:
        print("This is a tes!!!!!!")