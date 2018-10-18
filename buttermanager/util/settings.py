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

"""This module gathers all the global attributes, methods and classes needed for application settings.

"""
import os
import yaml
import util.utils

# Global module attributes
# Application name
application_name = ""
# Application work directory
application_path = ""
# User's password
user_password = ""
# Linux distribution
user_os = ""
# Do user want to remove snapshots? 0=False 1=True
remove_snapshots = 1
# Number of snapshots to keep after the upgrading process
snapshots_to_keep = 2
# Do user want to upgrade snap packages? 0=False 1=True
snap_packages = 1
# Do user want to upgrade packages from AUR? 0=False 1=True
aur_repository = 1
# Subvolumes managed by the application
subvolumes = []
# Properties Manager
properties_manager = None


class PropertiesManager:
    """Manages the user properties for the application.

    If no user settings are loaded yet, then the yaml file ~/.buttermanager/buttermanager.yaml will be
    read and parsed in self.__user_settings dictionary.

    The keys of the dictionary will be the properties name in the yaml file. The values will be te values
    in the yaml file for every property.
    """
    # Constants
    CONF_FILE = "buttermanager.yaml"

    # Constructor
    def __init__(self):
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        # Setting global values related to the application
        conf_file_path = '{application_path}/{conf_file}'.format(application_path=util.settings.application_path,
                                                                 conf_file=self.CONF_FILE)
        self.__user_settings = []
        # Reading configuration file (buttermanager.yaml file within ~/.buttermanager directory)
        if os.path.exists(conf_file_path):
            with open(conf_file_path) as configuration:
                self.__user_settings = yaml.load(configuration)
        else:
            self.__logger.info("Warning: There is no configuration file...")

    def get_property(self, property):
        """Gets the value of a property.

        Arguments:
            property (string): Property to get its value.

        Returns:
            string: The value of the property. Empty string if the property was not found.
        """
        value = ""
        if len(self.__user_settings) > 0:
            value = self.__user_settings.get(property, "")
        return value

    def set_property(self, property, value):
        """Sets the value of a property.

        Arguments:
            property (string): Property to set its value.
            value (string): Value to be set
        """
        pass
