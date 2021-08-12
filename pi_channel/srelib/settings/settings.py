import json
import logging
import os
import socket
from abc import abstractmethod, ABCMeta

class SREApplicationSettings(metaclass=ABCMeta):
    """ Defines the interface that a class must implement
    in order to be an api to read settings values.
    """

    @abstractmethod
    def get_value(self, key):
        """  Get the settings value for a key.
        Args:
            key(str): The key for the setting.
        Returns:
            obj: The value for the setting.
        """
        pass

class JSONSettings(SREApplicationSettings):
    """ Used to represent a JSON settings file.
    """

    def __init__(self, json_dict):
        """
        Args:
            json_dict(dict): The json dictionary containing
            the settings.
        """
        SREApplicationSettings.__init__(self)
        self.json_dict = json_dict

    def get_value(self, key_path_list):
        """  Get the settings value for a key.
        Args:
            key(str): The key for the setting.
        Returns:
            obj: The value for the setting.
        """
        temp_value = self.json_dict
        for key in key_path_list:
            if(key in temp_value):
                temp_value = temp_value[key]
            else:
                return None
        return temp_value

class SettingsReader(metaclass=ABCMeta):

    @abstractmethod
    def get_settings(self):
        """ Returns a settings object.
        Args:
            None
        Returns:
            SREApplicationSettings: Has access to the settings.
        """
        pass

class HostSettingsReader(SettingsReader):
    """ Reads a settings file that includes the host name in the file name.
    For example "myhost_settings.json".
    """

    logger = logging.getLogger(__name__)

    def __init__(self, settings_directory, host_name=None):
        """
        Args:
            settings_directory(str): The directory to search for settings file.
            host_name(str): The target host name.  If the host name is None then
            the hostname where this code is running will be used. 
        """
        SettingsReader.__init__(self)
        self.config_file_path = None
        if(settings_directory is None):
            raise ValueError("Need to provide a path to the directory that contains ")
        
        if(os.path.isdir(settings_directory) is None):
            raise ValueError("The given directory path doesn't exist = {}".format(settings_directory))

        target_hostname = host_name
        if(host_name is None):
            target_hostname = socket.gethostname()
            parts_list = target_hostname.split('.')
            target_hostname = parts_list[0]
        
        #config_file = os.path.join(dirname, dev_settings_path)
        self.config_file_path = settings_directory + "{}_settings.json".format(target_hostname)
        if(os.path.isfile(self.config_file_path) == False):
            #print("Unable to find a settings file in directory = {} for host {}".format(self.config_file_path, target_hostname))
            #print("will attempt to find a dev settings file.")
            self.config_file_path = settings_directory + "dev_settings.json"
            if(os.path.isfile(self.config_file_path) == False):
                self.logger.debug("Unable to find dev file")
                message = "Unable to find a settings file in directory = {}".format(self.config_file_path)
                raise ValueError(message)
            else:
                self.logger.debug("found dev settings file, will use")
                
        else:
            self.logger.debug("Found settings file at = {}".format(self.config_file_path))


    def get_settings(self):
        """  Obtain the object that has access to the settings.
        Args:
            None
        Returns:
            JSONSettings: The object used to access settings values.
        """
        return JSONSettingsReader(self.config_file_path).read_settings()


class JSONSettingsReader(object):
    """ Reads a JSON settings file.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, file_path):
        """
        Args:
            file_path(str): The path to the settings file.
        """
        self.file_path = file_path

    def read_settings(self):
        """  Causes this object to load the settings.
        Args:
            None
        Returns:
            JSONSettings:  Object representing the JSON that was read.
        """
        try:
            if(os.path.isfile(self.file_path) == False):
                self.logger.info("Settings file doesnt exist = {}".format(self.file_path))
                return None
            with open(self.file_path,"r") as fp:
                self.logger.info("Reading settings from file {}".format(self.file_path))
                content = fp.read()
                return JSONSettings(json.loads(content))
        except Exception as e:
            self.logger.warn("Unable to process settings file {}, reason = {}".format(self.file_path, e))
        return None


if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    dev_settings_path = os.path.join(dirname, '../../kpi_framework/config/')
    #settings_dev.json
    reader = HostSettingsReader(dev_settings_path)