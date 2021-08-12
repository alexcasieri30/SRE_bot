import os
import json
import logging
from srelib.settings.settings import HostSettingsReader
class SRELibSettings(object):
    """Use to obtain settings for sre lib modules. """

    settings_obj = None
    logger = logging.getLogger(__name__)
    def __init__(self):
        self.json_settings = None

    @staticmethod
    def get_instance(file_name_arg="settings.json"):
        """
        Args:
            file_name_arg(String): The name of the configuration file.
        """
        if(SRELibSettings.settings_obj is None):
            SRELibSettings.settings_obj = SRELibSettings()
            dirname = os.path.dirname(__file__) + os.sep
            SRELibSettings.settings_obj.json_settings = HostSettingsReader(dirname).get_settings()
            
        return SRELibSettings.settings_obj

    def get_temp_location(self):
        """ Returns the directory where temporary data should
        be stored.
        """
        return self.json_settings.get_value(["temp_location"])

    def get_config_location(self):
        """ Returns the direcotry where configuration data is stored.
        """
        return self.json_settings.get_value(["config_location"])

def main():
    lib_settings = SRELibSettings.get_instance()
    print("Temp location = {}".format(lib_settings.get_temp_location()))


if __name__ == '__main__':
    main()