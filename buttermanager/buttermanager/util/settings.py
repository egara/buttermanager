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
from . import utils
from .. import filesystem
import os
import yaml

# Global module constants
CONF_FILE = "buttermanager.yaml"
VERSION = "2.3"

# Global module attributes
# Application version
application_version = ""
# Application name
application_name = ""
# Application work directory
application_path = ""
# Logs directory
logs_path = ""
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
# Do user want to check for updates at startup? 0=False 1=True
check_at_startup = 1
# The path of the root snapshot that must be within /etc/fstab as / mount point
path_to_consolidate_root_snapshot = "0"
# Do user want to boot the system from GRUB using snapshots? 0=False 1=True
grub_btrfs = 0
# Do user want to save log automatically after upgrading system? 0=False 1=True
save_log = 1
# Subvolumes managed by the application
# It will be a dictionary:
# Key=origin path for the subvolume; Value=Subvolume object
subvolumes = {}
# Properties Manager
properties_manager = None
# Base fot size for all the UI elements
base_font_size = 10
# Location of the UI layouts directory
ui_dir = ""
# Location of the images directory
images_dir = ""
# Desktop environment
desktop_environment = ""
# Installation type
installation_type = ""


class PropertiesManager:
    """Manages the user properties for the application.

    If no user settings are loaded yet, then the yaml file ~/.buttermanager/buttermanager.yaml will be
    read and parsed in self.__user_settings dictionary.

    The keys of the dictionary will be the properties name in the yaml file. The values will be the values
    in the yaml file for every property.
    """
    # Constructor
    def __init__(self):
        # Logger
        self.__logger = utils.Logger(self.__class__.__name__).get()
        # Setting global values related to the application
        self.__conf_file_path = '{application_path}/{conf_file}'.format(application_path=application_path,
                                                                        conf_file=CONF_FILE)
        self.__user_settings = []
        # Reading configuration file (buttermanager.yaml file within ~/.buttermanager directory)
        if os.path.exists(self.__conf_file_path):
            conf_file = open(self.__conf_file_path)
            self.__user_settings = yaml.load(conf_file, Loader=yaml.FullLoader)
            conf_file.close()
        else:
            self.__logger.info("Warning: There is no configuration file...")

    def get_property(self, property):
        """Gets the value of a property.

        Arguments:
            property (string): Property to get its value.

        Returns:
            string: The value of the property. 0 if the property was not found.
        """
        value = ""
        if len(self.__user_settings) > 0:
            value = self.__user_settings.get(property, 0)
        return value

    def set_property(self, property, value):
        """Sets the value of a property.

        Arguments:
            property (string): Property to set its value.
            value (string): Value to be set.
        """
        self.__logger.info("Setting property {property} with value {value}".format(property=property, value=value))
        # Setting property in memory
        self.__user_settings[property] = value

        # Setting property in buttermanager.yaml file
        self.__store_configuration()

    def set_subvolume(self, subvolume_selected, snapshot_where, snapshot_prefix):
        """Sets the value of a subvolume.

        If snapshot_where = None and snapshot_prefix = None, then the subvolume
        will be removed

        Arguments:
            subvolume_selected (string): Subvolume selected to be set with the new values.
            snapshot_where (string): Path where the snapshot is going to be stored. None if the subvolume is removed
            snapshot_prefix (string): Prefix used to store the snapshot of a specific subvolume. None if the subvolume
            is removed
        """
        self.__logger.info("Setting subvolume {subvolume} with new values: where {where}; prefix{prefix}".format(
            subvolume=subvolume_selected, where=snapshot_where, prefix=snapshot_prefix))
        if subvolume_selected in subvolumes:
            if not snapshot_where and not snapshot_prefix:
                # The subvolume has to be removed from memory
                subvolumes.pop(subvolume_selected, 'None')
            else:
                # Modifying subvolume in memory
                subvolumes[subvolume_selected].subvolume_dest = snapshot_where if snapshot_where[-1] == '/' else snapshot_where + '/'
                subvolumes[subvolume_selected].snapshot_name = snapshot_prefix
        else:
            subvolumes[subvolume_selected] = filesystem.snapshot.Subvolume(subvolume_selected,
                                                                           snapshot_where,
                                                                           snapshot_prefix)
        subvolumes_orig = ""
        subvolumes_dest = ""
        subvolumes_prefix = ""
        index = 0

        for subvolume in subvolumes:
            subvolumes_orig += subvolumes[subvolume].subvolume_origin
            subvolumes_dest += subvolumes[subvolume].subvolume_dest
            subvolumes_prefix += subvolumes[subvolume].snapshot_name
            if index + 1 < len(subvolumes):
                subvolumes_orig += "|"
                subvolumes_dest += "|"
                subvolumes_prefix += "|"
            index += 1

        self.__user_settings['subvolumes_orig'] = subvolumes_orig
        self.__user_settings['subvolumes_dest'] = subvolumes_dest
        self.__user_settings['subvolumes_prefix'] = subvolumes_prefix

        # Setting property in buttermanager.yaml file
        self.__store_configuration()

    def __store_configuration(self):
        """Stores configuration file.

        """
        # Setting property in buttermanager.yaml file
        if os.path.exists(self.__conf_file_path):
            conf_file = open(self.__conf_file_path, 'w')
            yaml.dump(self.__user_settings, conf_file)
            conf_file.close()
        else:
            self.__logger.info("Warning: There is no configuration file...")
