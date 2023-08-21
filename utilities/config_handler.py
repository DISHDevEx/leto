"""
ConfigHandler acts as a wrapper for implementing the use of configparser in the Leto repo.
All reconstruction and reduction methods implement this class to handle configuration input
from the config.ini file.  The class also allows for method execution from any level of the
leto directory hierarchy.
"""

from pathlib import Path
import logging
import configparser

class ConfigHandler():

    """
    ConfigHandler handles the master config.ini file and exposes to each r1/r2 method.

    Attributes
    ----------

        method_section: string
            Method section to reference from config.ini for use in r1/r2 method.

        config_path: string
            Absolute file path to the master config.ini file.

        all_configs: dict
            Dictionary containing all configs read in from master config.ini file.

        s3: dict
            Dictionary containing configs from the special 'DEFAULT' section of the master config.ini file.

        method: dict
            Dictionary containing configs from the specific <method_section> of the master config.ini file.

    """

    def __init__(self, method_section):
        self.method_section = method_section
        self.config_path = self.getConfigPath()
        self.all_configs = self.getAllConfigs()
        self.s3 = self.getS3Configs()
        self.method = self.getMethodConfigs()

    def getConfigPath(self):
        """
        Gets and returns the absolute path to the master config.ini file.

         Parameters
        ----------

        None

        Returns
        ----------

        config_path: string
            Absolute path to the master config.ini file.
        """

        method_path = Path(__file__)
        leto_root = method_path.parent.parent.absolute()
        config_path = leto_root.joinpath('config.ini')
        logging.info("config.ini file path identified as: " + str(config_path))
        return config_path

    def getAllConfigs(self):
        """
        Gets and returns a dict containing all configs from the master config file.

         Parameters
        ----------

        None

        Returns
        ----------

        config: dict
            All configs from the master config file.
        """

        config = configparser.ConfigParser(inline_comment_prefixes=';', interpolation=configparser.ExtendedInterpolation())
        config.read(self.config_path)
        return config

    def getS3Configs(self):
        """
        Gets and returns a dict containing configs from the 'DEFAULT' section of the master config file.

         Parameters
        ----------

        None

        Returns
        ----------

        s3_configs: dict
            Configs from the 'DEFAULT' section of the master config file.
        """

        s3_configs = self.all_configs['DEFAULT']
        return s3_configs

    def getMethodConfigs(self):
        """
        Gets and returns a dict containing configs from the <method_section> section of the master config file.

         Parameters
        ----------

        None

        Returns
        ----------

        method_configs: dict
            Configs from the <method_section> section of the master config file.
        """

        method_configs = self.all_configs[self.method_section]
        return method_configs
